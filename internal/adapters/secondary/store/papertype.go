package store

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/EpistemicOS/epistemicos/internal/core/domain/papertype"
	"github.com/EpistemicOS/epistemicos/internal/core/ports"
)

// PostgresPaperTypeStore implements ports.PaperTypeStore.
type PostgresPaperTypeStore struct {
	pool *pgxpool.Pool
}

// NewPostgresPaperTypeStore returns a store backed by the given pool.
func NewPostgresPaperTypeStore(pool *pgxpool.Pool) *PostgresPaperTypeStore {
	return &PostgresPaperTypeStore{pool: pool}
}

// Stated here rather than left to the composition root. A signature that drifts
// from its port should break in the file that broke it, not three packages away
// in whichever command happened to wire it up.
var _ ports.PaperTypeStore = (*PostgresPaperTypeStore)(nil)

// evidenceJSON is how the quotes are stored.
//
// As JSON in raw_response's sibling rather than as rows, because nothing queries
// an individual quote. They are read back whole, for a person to look at, and the
// verified flag is what a reader actually needs from them. A quotes table would be
// four joins to answer no question anybody has.
type evidenceJSON struct {
	Quote    string `json:"quote"`
	Signals  string `json:"signals,omitempty"`
	Verified bool   `json:"verified"`
	Counter  bool   `json:"counter,omitempty"`
	PointsTo string `json:"points_to,omitempty"`
}

// SaveVerdict appends a verdict. Verdicts are never updated or deleted.
func (s *PostgresPaperTypeStore) SaveVerdict(ctx context.Context, r *ports.PaperTypeRecord) error {
	if r == nil {
		return errors.New("store: nil paper-type record")
	}
	if r.ID == "" {
		return errors.New("store: paper-type verdict has no id; the service layer assigns identifiers before persistence")
	}
	if r.PaperID == "" || r.MarkdownHash == "" {
		return errors.New("store: paper-type verdict needs a paper id and a markdown hash")
	}
	if r.RawResponse == "" {
		return errors.New("store: refusing to store a verdict with no raw response; without it the answer cannot be re-examined")
	}

	quotes, err := json.Marshal(marshalEvidence(r.Verdict))
	if err != nil {
		return fmt.Errorf("encode evidence: %w", err)
	}

	v := r.Verdict
	_, err = s.pool.Exec(ctx, `
		INSERT INTO paper_type_verdicts (
			paper_type_verdict_id, paper_id, approved_markdown_hash,
			primary_type, subtype, secondary_type,
			decision_rule, confidence, empirical,
			quotes_expected, quotes_verified,
			boundary_case, limits_from_selection, rationale, unclassified_reason,
			prompt_version, model, input_form, raw_response, evidence
		) VALUES (
			$1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16,$17,$18,$19,$20
		)`,
		r.ID, r.PaperID, r.MarkdownHash,
		string(v.PrimaryType), nullIfEmpty(string(v.Subtype)), nullIfEmpty(string(v.SecondaryType)),
		v.DecisionRule, v.Confidence, v.Empirical(),
		r.QuotesExpected, r.QuotesVerified,
		nullIfEmpty(v.BoundaryCase), nullIfEmpty(v.LimitsFromSelection), v.Rationale, nullIfEmpty(v.UnclassifiedReason),
		r.PromptVersion, r.Model, string(r.InputForm), r.RawResponse, quotes,
	)
	if err != nil {
		return fmt.Errorf("insert paper-type verdict for %s: %w", r.PaperID, err)
	}
	return nil
}

// CurrentVerdict returns the newest verdict for this paper and this markdown.
//
// Newest rather than only: the table is append-only, so asking again leaves both
// answers in place. A reader who wants the history queries the table; a caller who
// wants to know whether to proceed wants the latest, which is this.
func (s *PostgresPaperTypeStore) CurrentVerdict(ctx context.Context, paperID, markdownHash string) (*ports.PaperTypeRecord, error) {
	var (
		r                   ports.PaperTypeRecord
		primary, confidence string
		inputForm           string
		subtype, secondary  *string
		boundary, limits    *string
		unclassified        *string
		quotes              []byte

		// int16 rather than int because these are SMALLINT columns, and the one
		// other place this schema reads a SMALLINT (document_title_source_level)
		// scans into int16 too. Matching the column width is not a style
		// preference here: it removes any dependence on which integer widths the
		// driver happens to accept.
		decisionRule, expected, verified int16
	)

	err := s.pool.QueryRow(ctx, `
		SELECT paper_type_verdict_id, paper_id, approved_markdown_hash,
		       primary_type, subtype, secondary_type,
		       decision_rule, confidence,
		       quotes_expected, quotes_verified,
		       boundary_case, limits_from_selection, rationale, unclassified_reason,
		       prompt_version, model, input_form, raw_response, evidence
		  FROM paper_type_verdicts
		 WHERE paper_id = $1 AND approved_markdown_hash = $2
		 ORDER BY created_at DESC, paper_type_verdict_id DESC
		 LIMIT 1`, paperID, markdownHash,
	).Scan(
		&r.ID, &r.PaperID, &r.MarkdownHash,
		&primary, &subtype, &secondary,
		&decisionRule, &confidence,
		&expected, &verified,
		&boundary, &limits, &r.Verdict.Rationale, &unclassified,
		&r.PromptVersion, &r.Model, &inputForm, &r.RawResponse, &quotes,
	)
	if errors.Is(err, pgx.ErrNoRows) {
		return nil, ports.ErrNotFound
	}
	if err != nil {
		return nil, fmt.Errorf("select paper-type verdict for %s: %w", paperID, err)
	}

	r.Verdict.DecisionRule = int(decisionRule)
	r.QuotesExpected = int(expected)
	r.QuotesVerified = int(verified)

	r.Verdict.PrimaryType = papertype.Type(primary)
	r.Verdict.Subtype = papertype.Subtype(deref(subtype))
	r.Verdict.SecondaryType = papertype.Type(deref(secondary))
	r.Verdict.Confidence = confidence
	r.Verdict.BoundaryCase = deref(boundary)
	r.Verdict.LimitsFromSelection = deref(limits)
	r.Verdict.UnclassifiedReason = deref(unclassified)
	r.InputForm = papertype.InputForm(inputForm)

	var stored []evidenceJSON
	if len(quotes) > 0 {
		if err := json.Unmarshal(quotes, &stored); err != nil {
			return nil, fmt.Errorf("decode evidence for %s: %w", paperID, err)
		}
	}
	for _, e := range stored {
		if e.Counter {
			r.Verdict.CounterEvidence = &papertype.CounterEvidence{
				Quote:    e.Quote,
				PointsTo: papertype.Type(e.PointsTo),
				Verified: e.Verified,
			}
			continue
		}
		r.Verdict.Evidence = append(r.Verdict.Evidence, papertype.Evidence{
			Quote:    e.Quote,
			Signals:  e.Signals,
			Verified: e.Verified,
		})
	}

	return &r, nil
}

func marshalEvidence(v papertype.Verdict) []evidenceJSON {
	out := make([]evidenceJSON, 0, len(v.Evidence)+1)
	for _, e := range v.Evidence {
		out = append(out, evidenceJSON{
			Quote:    e.Quote,
			Signals:  e.Signals,
			Verified: e.Verified,
		})
	}
	if v.CounterEvidence != nil {
		out = append(out, evidenceJSON{
			Quote:    v.CounterEvidence.Quote,
			Verified: v.CounterEvidence.Verified,
			Counter:  true,
			PointsTo: string(v.CounterEvidence.PointsTo),
		})
	}
	return out
}
