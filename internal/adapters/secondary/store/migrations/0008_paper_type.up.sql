-- Paper-type classification: the gate that runs BEFORE Step 3.
--
-- One question, asked of a language model: is this paper empirical? Only "A"
-- proceeds. A systematic review, a conceptual paper and a formal-modelling paper
-- are all parked, because everything downstream assumes empirical work and would
-- answer confidently and wrongly otherwise — a review of quantitative studies is
-- saturated with quantitative vocabulary that belongs to the corpus it reviews.
--
-- WHY THIS TABLE STORES SO MUCH MORE THAN THE ANSWER
--
-- Every other determination in this pipeline is reproducible: the same markdown
-- through the same rule version yields the same sections, so a stored answer can
-- be re-derived by re-running the code. This one cannot. The same paper and the
-- same prompt can produce a different verdict from a different model, or from the
-- same model next month.
--
-- So the row carries what would otherwise be unrecoverable: the prompt version,
-- the model name, the input form, and the model's complete response. Without them
-- a disagreement between two verdicts is an argument. With them it is a lookup.
CREATE TABLE IF NOT EXISTS paper_type_verdicts (
    paper_type_verdict_id UUID PRIMARY KEY,

    paper_id UUID NOT NULL REFERENCES papers (id) ON DELETE CASCADE,

    -- The markdown this verdict was reached from, by hash. A paper re-ingested
    -- into different markdown gets a new verdict rather than inheriting one
    -- reached from text that no longer exists.
    approved_markdown_hash VARCHAR(64) NOT NULL,

    primary_type   VARCHAR(16) NOT NULL,
    subtype        VARCHAR(32),
    secondary_type VARCHAR(16),

    decision_rule SMALLINT    NOT NULL,
    confidence    VARCHAR(8)  NOT NULL,

    -- Routing, computed once and stored, so a consumer never re-derives it and
    -- never gets it wrong. TRUE when primary_type = 'A' OR secondary_type = 'A':
    -- a synthesis paper that also carries its own empirical study proceeds.
    empirical BOOLEAN NOT NULL,

    -- QUOTE VERIFICATION. The prompt tells the model its quotes are
    -- machine-verified; these two columns are what makes that true rather than
    -- promised. quotes_expected counts the quotes the model gave,
    -- quotes_verified how many were found in the manuscript after folding
    -- typography. Unequal means the model paraphrased, and a verdict resting on
    -- words that are not in the paper is not evidence of anything.
    quotes_expected SMALLINT NOT NULL,
    quotes_verified SMALLINT NOT NULL,

    -- The quotes themselves, each with its verified flag, and the
    -- counter-evidence marked as such. JSONB rather than a child table because
    -- nothing queries an individual quote: they are read back whole for a person
    -- to look at. A quotes table would be a join to answer no question anyone has.
    evidence JSONB NOT NULL DEFAULT '[]'::jsonb,

    boundary_case         TEXT,
    limits_from_selection TEXT,
    rationale             TEXT        NOT NULL DEFAULT '',
    unclassified_reason   TEXT,

    -- Provenance. See the table comment.
    prompt_version VARCHAR(32) NOT NULL,
    model          TEXT        NOT NULL,
    input_form     VARCHAR(16) NOT NULL,
    raw_response   TEXT        NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT paper_type_primary_valid
        CHECK (primary_type IN ('A', 'B', 'C', 'D', 'UNCLASSIFIED')),

    CONSTRAINT paper_type_secondary_valid
        CHECK (secondary_type IS NULL OR secondary_type IN ('A', 'B', 'C', 'D')),

    -- A secondary equal to the primary is how a model hedges without saying so.
    CONSTRAINT paper_type_secondary_differs
        CHECK (secondary_type IS NULL OR secondary_type <> primary_type),

    CONSTRAINT paper_type_subtype_valid
        CHECK (subtype IS NULL OR subtype IN (
            'systematic_review', 'meta_analysis',
            'mathematical_modelling', 'mathematical_proof')),

    -- A subtype is required exactly where the taxonomy divides and forbidden
    -- elsewhere. "B with no subtype" leaves a meta-analysis and a narrative
    -- systematic review indistinguishable.
    CONSTRAINT paper_type_subtype_iff_b_or_d
        CHECK ((primary_type IN ('B', 'D')) = (subtype IS NOT NULL)),

    CONSTRAINT paper_type_decision_rule_valid
        CHECK (decision_rule BETWEEN 1 AND 5),

    CONSTRAINT paper_type_confidence_valid
        CHECK (confidence IN ('high', 'medium', 'low')),

    CONSTRAINT paper_type_input_form_valid
        CHECK (input_form IN ('FULL', 'SELECTION')),

    -- The routing column must agree with the types it is derived from. Storing a
    -- computed value is a convenience; letting it drift from its inputs would put
    -- a paper through Step 3 that the classifier parked.
    --
    -- COALESCE is load-bearing. Written as `secondary_type = 'A'`, a NULL
    -- secondary makes that comparison NULL, so for a B paper the whole expression
    -- is `FALSE OR NULL` = NULL, and a CHECK that evaluates to NULL PASSES. The
    -- constraint would then have accepted empirical = true on a synthesis paper —
    -- silently, and only for the rows it most needed to catch.
    CONSTRAINT paper_type_empirical_matches_types
        CHECK (empirical = (primary_type = 'A' OR COALESCE(secondary_type, '') = 'A')),

    -- Refusal is a real answer and must say why, or it is indistinguishable from
    -- a model that gave up.
    CONSTRAINT paper_type_unclassified_has_reason
        CHECK ((primary_type = 'UNCLASSIFIED') = (unclassified_reason IS NOT NULL)),

    CONSTRAINT paper_type_quotes_sane
        CHECK (quotes_verified >= 0 AND quotes_verified <= quotes_expected)
);

-- The current verdict for a paper is the newest one for its markdown. Verdicts
-- are APPEND-ONLY: re-running the classifier writes a new row rather than
-- replacing the old, so a change of answer is visible as a change rather than
-- arriving as though it had always been that way.
CREATE INDEX IF NOT EXISTS idx_paper_type_current
    ON paper_type_verdicts (paper_id, approved_markdown_hash, created_at DESC);
