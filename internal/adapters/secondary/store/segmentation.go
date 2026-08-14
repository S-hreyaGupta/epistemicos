package store

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/EpistemicOS/epistemicos/internal/core/domain/segment"
	"github.com/EpistemicOS/epistemicos/internal/core/ports"
)

// PostgresSegmentationStore implements ports.SegmentationStore.
type PostgresSegmentationStore struct {
	pool *pgxpool.Pool
}

// NewPostgresSegmentationStore returns a store backed by the given pool.
// The caller owns the pool's lifecycle.
func NewPostgresSegmentationStore(pool *pgxpool.Pool) *PostgresSegmentationStore {
	return &PostgresSegmentationStore{pool: pool}
}

// SaveRun writes a run, its nodes and its review tasks in one transaction.
//
// The transaction is required, not merely tidy. A half-written node set is
// indistinguishable from a document that genuinely has fewer sections, and
// §10's zero-silent-loss invariant — already checked in the domain — would be
// defeated by a store that could persist part of a run and report success. The
// same applies to tasks: nodes without their tasks is a run where open
// questions have quietly disappeared.
//
// Nodes are inserted in ordinal order so that a parent always exists before the
// child referencing it. That ordering is guaranteed by the domain, which
// assigns parents only to earlier nodes, and the foreign key turns any future
// violation into an error here rather than a dangling reference.
func (s *PostgresSegmentationStore) SaveRun(ctx context.Context, run *segment.Run) error {
	if run.ID == "" {
		return errors.New("store: segmentation run has no id; the service layer assigns identifiers before persistence")
	}
	if len(run.Nodes) != 0 && len(run.NodeIDs) != len(run.Nodes) {
		return fmt.Errorf("store: run has %d nodes but %d node ids", len(run.Nodes), len(run.NodeIDs))
	}

	tx, err := s.pool.Begin(ctx)
	if err != nil {
		return fmt.Errorf("begin: %w", err)
	}
	defer func() { _ = tx.Rollback(ctx) }()

	counts, err := json.Marshal(headingCountsJSON(run.HeadingCounts))
	if err != nil {
		return fmt.Errorf("encode heading counts: %w", err)
	}

	var titleNodeID *string
	if run.DocumentTitleOrdinal >= 0 && run.DocumentTitleOrdinal < len(run.NodeIDs) {
		id := run.NodeIDs[run.DocumentTitleOrdinal]
		titleNodeID = &id
	}

	_, err = tx.Exec(ctx, `
		INSERT INTO segmentation_runs (
			segmentation_run_id, extraction_run_id, approved_markdown_hash,
			structural_rule_version, document_title_level,
			supported_node_levels, embedded_levels, heading_counts,
			document_title_text, document_title_node_id, document_title_source_level,
			document_title_status, document_title_method,
			status, failure_reason, completed_at
		) VALUES (
			$1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,NOW()
		)`,
		run.ID, run.ExtractionRunID, run.ApprovedMarkdownHash,
		run.StructuralRuleVersion, run.DocumentTitleLevel,
		toInt16(run.SupportedNodeLevels), toInt16(run.EmbeddedLevels), counts,
		nullIfEmpty(run.DocumentTitleText), titleNodeID, nullIfZero(run.DocumentTitleSourceLevel),
		string(run.DocumentTitleStatus), nullIfEmpty(string(run.DocumentTitleMethod)),
		string(run.Status), nullIfEmpty(run.FailureReason),
	)
	if err != nil {
		return fmt.Errorf("insert segmentation run: %w", err)
	}

	for i, n := range run.Nodes {
		var parentID *string
		if n.ParentOrdinal >= 0 {
			id := run.NodeIDs[n.ParentOrdinal]
			parentID = &id
		}

		c := n.Classification
		_, err = tx.Exec(ctx, `
			INSERT INTO section_nodes (
				section_id, segmentation_run_id, parent_section_id, ordinal,
				node_kind, heading_raw, heading_normalized, semantic_heading,
				heading_level, structural_container, appendix_label,
				start_offset, end_offset,
				primary_role, content_class, classification_status, classification_method
			) VALUES (
				$1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16,$17
			)`,
			run.NodeIDs[i], run.ID, parentID, n.Ordinal,
			string(n.Kind), n.HeadingRaw, n.HeadingNormalized, nullIfEmpty(n.SemanticHeading),
			n.HeadingLevel, nullIfEmpty(string(n.Container)), nullIfEmpty(n.AppendixLabel),
			n.StartOffset, n.EndOffset,
			nullIfEmpty(string(c.Role)), nullIfEmpty(string(c.ContentClass)),
			string(c.Status), nullIfEmpty(string(c.Method)),
		)
		if err != nil {
			return fmt.Errorf("insert section node %d (%q): %w", n.Ordinal, n.HeadingRaw, err)
		}
	}

	for i, task := range run.Tasks {
		var sectionID *string
		if task.SectionOrdinal >= 0 {
			id := run.NodeIDs[task.SectionOrdinal]
			sectionID = &id
		}

		_, err = tx.Exec(ctx, `
			INSERT INTO review_tasks (
				review_task_id, segmentation_run_id, section_id,
				review_reason, candidate_roles, matched_keywords, status
			) VALUES ($1,$2,$3,$4,$5,$6,$7)`,
			run.TaskIDs[i], run.ID, sectionID,
			string(task.Reason), rolesToStrings(task.CandidateRoles), emptyIfNil(task.MatchedKeywords),
			string(task.Status),
		)
		if err != nil {
			return fmt.Errorf("insert review task %d (%s): %w", i, task.Reason, err)
		}
	}

	if err := tx.Commit(ctx); err != nil {
		return fmt.Errorf("commit: %w", err)
	}
	return nil
}

// GetRun reads a run back with its nodes in ordinal order and its tasks.
func (s *PostgresSegmentationStore) GetRun(ctx context.Context, runID string) (*segment.Run, error) {
	run := &segment.Run{ID: runID}

	var (
		counts                []byte
		supported, embedded   []int16
		titleText, titleNode  *string
		titleLevel            *int16
		titleMethod, failure  *string
		titleStatus, runState string
	)

	err := s.pool.QueryRow(ctx, `
		SELECT extraction_run_id, approved_markdown_hash, structural_rule_version,
		       document_title_level, supported_node_levels, embedded_levels, heading_counts,
		       document_title_text, document_title_node_id, document_title_source_level,
		       document_title_status, document_title_method, status, failure_reason
		  FROM segmentation_runs
		 WHERE segmentation_run_id = $1`, runID,
	).Scan(
		&run.ExtractionRunID, &run.ApprovedMarkdownHash, &run.StructuralRuleVersion,
		&run.DocumentTitleLevel, &supported, &embedded, &counts,
		&titleText, &titleNode, &titleLevel,
		&titleStatus, &titleMethod, &runState, &failure,
	)
	if errors.Is(err, pgx.ErrNoRows) {
		return nil, ports.ErrNotFound
	}
	if err != nil {
		return nil, fmt.Errorf("select segmentation run: %w", err)
	}

	run.SupportedNodeLevels = toInt(supported)
	run.EmbeddedLevels = toInt(embedded)
	run.DocumentTitleStatus = segment.TitleStatus(titleStatus)
	run.Status = segment.RunStatus(runState)
	run.DocumentTitleText = deref(titleText)
	run.DocumentTitleMethod = segment.TitleMethod(deref(titleMethod))
	run.FailureReason = deref(failure)
	if titleLevel != nil {
		run.DocumentTitleSourceLevel = int(*titleLevel)
	}

	var byLevel map[string]int
	if err := json.Unmarshal(counts, &byLevel); err != nil {
		return nil, fmt.Errorf("decode heading counts: %w", err)
	}
	run.HeadingCounts = map[int]int{}
	for label, n := range byLevel {
		var level int
		if _, err := fmt.Sscanf(label, "H%d", &level); err == nil {
			run.HeadingCounts[level] = n
		}
	}

	rows, err := s.pool.Query(ctx, `
		SELECT section_id, parent_section_id, ordinal, node_kind,
		       heading_raw, heading_normalized, semantic_heading, heading_level,
		       structural_container, appendix_label, start_offset, end_offset,
		       primary_role, content_class, classification_status, classification_method
		  FROM section_nodes
		 WHERE segmentation_run_id = $1
		 ORDER BY ordinal`, runID)
	if err != nil {
		return nil, fmt.Errorf("select section nodes: %w", err)
	}
	defer rows.Close()

	ordinalOf := map[string]int{}
	var parentIDs []*string

	for rows.Next() {
		var (
			id                         string
			parent                     *string
			n                          segment.SectionNode
			kind, status               string
			semantic, container, label *string
			role, class, method        *string
		)
		if err := rows.Scan(
			&id, &parent, &n.Ordinal, &kind,
			&n.HeadingRaw, &n.HeadingNormalized, &semantic, &n.HeadingLevel,
			&container, &label, &n.StartOffset, &n.EndOffset,
			&role, &class, &status, &method,
		); err != nil {
			return nil, fmt.Errorf("scan section node: %w", err)
		}

		n.Kind = segment.NodeKind(kind)
		n.SemanticHeading = deref(semantic)
		n.Container = segment.StructuralContainer(deref(container))
		n.AppendixLabel = deref(label)
		n.Classification = segment.Classification{
			Role:         segment.Role(deref(role)),
			ContentClass: segment.ContentClass(deref(class)),
			Status:       segment.ClassificationStatus(status),
			Method:       segment.ClassificationMethod(deref(method)),
		}
		n.ParentOrdinal = -1

		ordinalOf[id] = n.Ordinal
		run.NodeIDs = append(run.NodeIDs, id)
		run.Nodes = append(run.Nodes, n)
		parentIDs = append(parentIDs, parent)
	}
	if err := rows.Err(); err != nil {
		return nil, fmt.Errorf("iterate section nodes: %w", err)
	}

	// Parent ordinals are resolved after the full set is read: a parent is
	// always an earlier node, but relying on that during the scan would make
	// the reader depend on an ordering the query happens to provide.
	for i, parent := range parentIDs {
		if parent == nil {
			continue
		}
		if ordinal, ok := ordinalOf[*parent]; ok {
			run.Nodes[i].ParentOrdinal = ordinal
		}
	}

	taskRows, err := s.pool.Query(ctx, `
		SELECT review_task_id, section_id, review_reason,
		       candidate_roles, matched_keywords, status
		  FROM review_tasks
		 WHERE segmentation_run_id = $1
		 ORDER BY created_at, review_task_id`, runID)
	if err != nil {
		return nil, fmt.Errorf("select review tasks: %w", err)
	}
	defer taskRows.Close()

	for taskRows.Next() {
		var (
			id, reason, status string
			sectionID          *string
			candidates         []string
		)
		task := segment.ReviewTask{}
		if err := taskRows.Scan(&id, &sectionID, &reason, &candidates, &task.MatchedKeywords, &status); err != nil {
			return nil, fmt.Errorf("scan review task: %w", err)
		}

		task.Reason = segment.ReviewReason(reason)
		task.Status = segment.TaskStatus(status)
		task.SectionOrdinal = -1
		if sectionID != nil {
			if ordinal, ok := ordinalOf[*sectionID]; ok {
				task.SectionOrdinal = ordinal
			}
		}
		for _, c := range candidates {
			task.CandidateRoles = append(task.CandidateRoles, segment.Role(c))
		}

		run.TaskIDs = append(run.TaskIDs, id)
		run.Tasks = append(run.Tasks, task)
	}
	if err := taskRows.Err(); err != nil {
		return nil, fmt.Errorf("iterate review tasks: %w", err)
	}

	run.DocumentTitleOrdinal = -1
	if titleNode != nil {
		if ordinal, ok := ordinalOf[*titleNode]; ok {
			run.DocumentTitleOrdinal = ordinal
		}
	}

	return run, nil
}

// headingCountsJSON renders counts as {"H1":n,...} for all six levels.
//
// Absent levels are written as zero rather than omitted. A missing key and a
// zero count are the same fact, but only one of them survives a reader that
// treats absence as unknown, and §10 depends on the H5/H6 counts being
// legible as deliberate exclusions rather than as missing data.
func headingCountsJSON(counts map[int]int) map[string]int {
	out := make(map[string]int, 6)
	for level := 1; level <= 6; level++ {
		out[fmt.Sprintf("H%d", level)] = counts[level]
	}
	return out
}

func toInt16(in []int) []int16 {
	out := make([]int16, len(in))
	for i, v := range in {
		out[i] = int16(v)
	}
	return out
}

func toInt(in []int16) []int {
	out := make([]int, len(in))
	for i, v := range in {
		out[i] = int(v)
	}
	return out
}

func rolesToStrings(roles []segment.Role) []string {
	out := make([]string, 0, len(roles))
	for _, r := range roles {
		out = append(out, string(r))
	}
	return out
}

// emptyIfNil keeps a nil slice out of a NOT NULL text[] column.
func emptyIfNil(in []string) []string {
	if in == nil {
		return []string{}
	}
	return in
}

// nullIfEmpty maps Go's zero string onto SQL NULL.
//
// The two are genuinely different states in this schema and the mapping is
// deliberate at every call site: a NULL primary_role means unresolved, and the
// CHECK constraint on section_nodes enforces that an unresolved node has one.
// Writing ” instead would satisfy the column and break the meaning.
func nullIfEmpty(s string) *string {
	if s == "" {
		return nil
	}
	return &s
}

func nullIfZero(n int) *int {
	if n == 0 {
		return nil
	}
	return &n
}

func deref(s *string) string {
	if s == nil {
		return ""
	}
	return *s
}
