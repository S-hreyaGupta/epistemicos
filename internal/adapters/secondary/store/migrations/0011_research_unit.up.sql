-- The multi-study gate's verdict, stored.
--
-- Until now this gate printed and forgot. That was tolerable while it only
-- refused papers, and stopped being tolerable the moment a human was asked to
-- settle an `uncertain`: a reviewer needs to see what the machine saw, and
-- "re-run the command and read the terminal" is not a review surface.
--
-- WHY THIS LOOKS DIFFERENT FROM paper_type_verdicts
--
-- That table is append-only and stores the model's entire response, because that
-- gate is not deterministic: the same paper and prompt can yield a different
-- verdict from a different model, or from the same model next month, and only
-- the raw text makes a disagreement investigable rather than arguable.
--
-- This gate is deterministic. The same markdown under the same rule version
-- always produces the same verdict, so there is nothing to disagree with and
-- nothing unrecoverable to preserve. One row per (paper, markdown, rule version)
-- is therefore complete AND idempotent: re-running writes the same row, and a
-- rules change appears as a new row rather than as a duplicate.
--
-- That is the whole practical difference between storing a judgement and storing
-- a computation, and it is worth the two tables looking unalike.

CREATE TABLE IF NOT EXISTS research_unit_verdicts (
    research_unit_verdict_id UUID PRIMARY KEY,

    paper_id UUID NOT NULL REFERENCES papers (id) ON DELETE CASCADE,

    -- The markdown this verdict was reached from. Same rule as paper-type: a
    -- paper re-ingested into different markdown gets a new verdict rather than
    -- inheriting one reached from text that no longer exists.
    approved_markdown_hash VARCHAR(64) NOT NULL,

    -- The rules that produced it. Without this a stored verdict cannot say what
    -- it was computed by, which for a deterministic gate is the one piece of
    -- provenance that matters — it is exactly what makes the answer
    -- reproducible.
    rule_version VARCHAR(16) NOT NULL,

    verdict VARCHAR(16) NOT NULL,

    -- Distinct study GROUPS found in headings, not labels. "Study 1A" and
    -- "Study 1B" are two labels and one group, and counting labels would report
    -- a two-part study as two studies.
    study_count INTEGER NOT NULL,

    -- The gate's own sentence, stored rather than re-derived. A reviewer reads
    -- this first, and regenerating it later from the columns would risk showing
    -- them a different explanation than the one the gate actually gave.
    reason TEXT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT research_unit_verdicts_verdict_valid
        CHECK (verdict IN ('single', 'multi', 'uncertain')),

    CONSTRAINT research_unit_verdicts_count_sane
        CHECK (study_count >= 0),

    -- Idempotence, enforced rather than assumed. Re-running the gate over
    -- unchanged text under unchanged rules must not accumulate rows: the answer
    -- did not change, so there is no second fact to record.
    CONSTRAINT research_unit_verdicts_one_per_version
        UNIQUE (paper_id, approved_markdown_hash, rule_version)
);

CREATE INDEX IF NOT EXISTS idx_research_unit_verdicts_paper
    ON research_unit_verdicts (paper_id);

-- Uncertain verdicts are the ones a human has to settle, so they are the ones
-- worth finding quickly.
CREATE INDEX IF NOT EXISTS idx_research_unit_verdicts_verdict
    ON research_unit_verdicts (verdict);

-- Every label the gate found, as ROWS rather than as a blob.
--
-- A JSON column would have been fewer lines and would have answered exactly one
-- question: "what did this paper trip on?" Rows answer the question that will
-- actually be asked as the corpus grows — "which papers tripped on a phase
-- heading rather than a study heading?" — which is how we would learn whether
-- the weak-vocabulary rule is earning its place.
--
-- The cost is small and measured: the Frontiers paper, which reports three
-- studies, produces five rows.
CREATE TABLE IF NOT EXISTS research_unit_evidence (
    research_unit_evidence_id UUID PRIMARY KEY,

    research_unit_verdict_id UUID NOT NULL
        REFERENCES research_unit_verdicts (research_unit_verdict_id) ON DELETE CASCADE,

    -- Position in the gate's own evidence order: headings first, then body
    -- prose. Stored because that order is meaningful — heading evidence can
    -- settle the verdict and body evidence never can — and a reader sorting by
    -- id would lose it.
    position INTEGER NOT NULL,

    -- "study", "experiment", "phase", "sample", "dataset", "wave", "round".
    -- Deliberately NOT constrained to the strong pair: the split between strong
    -- and weak kinds is a rule of the gate, and freezing it into the schema
    -- would mean a vocabulary change needed a migration.
    kind  VARCHAR(16) NOT NULL,

    -- As printed: "1", "2", "1A", "II".
    label VARCHAR(8)  NOT NULL,

    -- The top-level number the label belongs to. Stored rather than derived so
    -- that a query for "papers with two or more study groups" does not have to
    -- reimplement the grouping rule in SQL and get it subtly different.
    study_group VARCHAR(8) NOT NULL,

    -- The heading or line it was found in, verbatim. This is what a reviewer
    -- actually reads.
    found_in TEXT NOT NULL,

    -- The heading's ordinal, or -1 when the label was found in body prose.
    --
    -- The distinction is the gate's central rule: a heading is the document's
    -- own structural claim about itself, while a sentence may be discussing
    -- somebody else's study. Body evidence can raise a question and never
    -- settles one, so a reviewer must be able to tell the two apart at a glance.
    heading_ordinal INTEGER NOT NULL,

    CONSTRAINT research_unit_evidence_one_per_position
        UNIQUE (research_unit_verdict_id, position)
);

CREATE INDEX IF NOT EXISTS idx_research_unit_evidence_verdict
    ON research_unit_evidence (research_unit_verdict_id);

-- The query this table exists for.
CREATE INDEX IF NOT EXISTS idx_research_unit_evidence_kind
    ON research_unit_evidence (kind);
