package store

import (
	"context"
	"errors"
	"fmt"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/EpistemicOS/epistemicos/internal/core/domain/researchunit"
	"github.com/EpistemicOS/epistemicos/internal/core/ports"
)

// PostgresResearchUnitStore implements ports.ResearchUnitStore.
type PostgresResearchUnitStore struct {
	pool *pgxpool.Pool
}

// NewPostgresResearchUnitStore returns a store backed by the given pool.
// The caller owns the pool's lifecycle.
func NewPostgresResearchUnitStore(pool *pgxpool.Pool) *PostgresResearchUnitStore {
	return &PostgresResearchUnitStore{pool: pool}
}

// SaveGate writes a verdict and its evidence in one transaction.
//
// The write is an UPSERT keyed on (paper, markdown hash, rule version), and the
// evidence is deleted and rewritten rather than appended. Both follow from the
// gate being deterministic: those three values fix the answer completely, so a
// second write cannot carry different information, and treating it as an
// addition would record a change that did not occur.
func (s *PostgresResearchUnitStore) SaveGate(ctx context.Context, paperID, markdownHash string, gate researchunit.Gate) error {
	if paperID == "" || markdownHash == "" {
		return errors.New("store: research unit verdict needs a paper id and a markdown hash")
	}

	// Refused rather than defaulted to the current constant.
	//
	// Defaulting would stamp today's version onto a verdict computed by rules we
	// cannot identify, and a row that misreports its own provenance is worse
	// than one that is missing: the first is trusted and wrong, the second is
	// merely absent.
	if gate.RuleVersion == "" {
		return errors.New("store: research unit verdict has no rule version; Detect stamps one, so reaching here means the gate was built by hand")
	}
	if gate.Verdict == "" {
		return errors.New("store: research unit verdict has no verdict")
	}

	tx, err := s.pool.Begin(ctx)
	if err != nil {
		return fmt.Errorf("begin: %w", err)
	}
	defer func() { _ = tx.Rollback(ctx) }()

	var verdictID string
	err = tx.QueryRow(ctx, `
		INSERT INTO research_unit_verdicts (
			research_unit_verdict_id, paper_id, approved_markdown_hash,
			rule_version, verdict, study_count, reason
		) VALUES ($1,$2,$3,$4,$5,$6,$7)
		ON CONFLICT (paper_id, approved_markdown_hash, rule_version) DO UPDATE SET
			verdict     = EXCLUDED.verdict,
			study_count = EXCLUDED.study_count,
			reason      = EXCLUDED.reason
		RETURNING research_unit_verdict_id`,
		uuid.NewString(), paperID, markdownHash,
		gate.RuleVersion, string(gate.Verdict), gate.StudyCount, gate.Reason,
	).Scan(&verdictID)
	if err != nil {
		return fmt.Errorf("upsert research unit verdict for paper %s: %w", paperID, err)
	}

	// Replaced wholesale. An append would leave the previous run's evidence
	// beside this one's, and a reviewer would be shown each label twice with
	// nothing saying why.
	if _, err := tx.Exec(ctx,
		`DELETE FROM research_unit_evidence WHERE research_unit_verdict_id = $1`, verdictID); err != nil {
		return fmt.Errorf("clear research unit evidence: %w", err)
	}

	for i, e := range gate.Evidence {
		if _, err := tx.Exec(ctx, `
			INSERT INTO research_unit_evidence (
				research_unit_evidence_id, research_unit_verdict_id, position,
				kind, label, study_group, found_in, heading_ordinal
			) VALUES ($1,$2,$3,$4,$5,$6,$7,$8)`,
			uuid.NewString(), verdictID, i,
			e.Kind, e.Label, e.Group, e.Text, e.Ordinal,
		); err != nil {
			return fmt.Errorf("insert research unit evidence %d: %w", i, err)
		}
	}

	if err := tx.Commit(ctx); err != nil {
		return fmt.Errorf("commit: %w", err)
	}
	return nil
}

// CurrentGate reads back a stored verdict with its evidence in gate order.
func (s *PostgresResearchUnitStore) CurrentGate(ctx context.Context, paperID, markdownHash, ruleVersion string) (*researchunit.Gate, error) {
	var (
		verdictID string
		g         researchunit.Gate
		verdict   string
	)

	err := s.pool.QueryRow(ctx, `
		SELECT research_unit_verdict_id, rule_version, verdict, study_count, reason
		  FROM research_unit_verdicts
		 WHERE paper_id = $1
		   AND approved_markdown_hash = $2
		   AND rule_version = $3`,
		paperID, markdownHash, ruleVersion,
	).Scan(&verdictID, &g.RuleVersion, &verdict, &g.StudyCount, &g.Reason)
	if err != nil {
		if errors.Is(err, pgx.ErrNoRows) {
			return nil, ports.ErrNotFound
		}
		return nil, fmt.Errorf("select research unit verdict: %w", err)
	}
	g.Verdict = researchunit.Verdict(verdict)

	// ORDER BY position, not by id. The gate's order is meaningful — heading
	// evidence first, then body prose — and it is what tells a reviewer which
	// labels could have settled the verdict and which merely raised it.
	rows, err := s.pool.Query(ctx, `
		SELECT kind, label, study_group, found_in, heading_ordinal
		  FROM research_unit_evidence
		 WHERE research_unit_verdict_id = $1
		 ORDER BY position`, verdictID)
	if err != nil {
		return nil, fmt.Errorf("select research unit evidence: %w", err)
	}
	defer rows.Close()

	for rows.Next() {
		var e researchunit.Evidence
		if err := rows.Scan(&e.Kind, &e.Label, &e.Group, &e.Text, &e.Ordinal); err != nil {
			return nil, fmt.Errorf("scan research unit evidence: %w", err)
		}
		g.Evidence = append(g.Evidence, e)
	}
	if err := rows.Err(); err != nil {
		return nil, fmt.Errorf("iterate research unit evidence: %w", err)
	}

	return &g, nil
}
