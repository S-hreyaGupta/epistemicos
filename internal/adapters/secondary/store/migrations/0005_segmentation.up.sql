-- Step 3: document segmentation and section-role classification.
--
-- Four entities from specification v2.1 §8. Numbering continues from 0004;
-- 0002 and 0003 are deliberately absent and their numbers are not reused.

-- One run of the segmenter over one approved markdown document.
--
-- The structural constants (title level, supported levels, embedded levels) are
-- persisted rather than assumed, so a node set can be interpreted years later
-- without knowing which rule version produced it. structural_rule_version stays
-- "2.0" through the 2.1 amendments: those were clarifications and changed no
-- behaviour.
CREATE TABLE IF NOT EXISTS segmentation_runs (
    segmentation_run_id     UUID PRIMARY KEY,

    -- The Step 2 run this segmented. §9 walks a pointer chain through
    -- ExtractionRun, which does not exist in this repository yet, so this holds
    -- whatever reference the adapter supplies. See internal/adapters/secondary/
    -- approved for what that currently means.
    extraction_run_id       TEXT        NOT NULL,

    -- SHA-256 of the exact markdown every offset below indexes into. Without a
    -- match, no span in this run may be trusted: the offsets are meaningless
    -- against any other text, and slicing with them yields a plausible,
    -- confidently wrong quote rather than an error.
    approved_markdown_hash  VARCHAR(64) NOT NULL,

    structural_rule_version VARCHAR(16) NOT NULL,
    document_title_level    SMALLINT    NOT NULL,
    supported_node_levels   SMALLINT[]  NOT NULL,
    embedded_levels         SMALLINT[]  NOT NULL,

    -- Detected headings per level, including H5 and H6, which produce no node.
    -- Storing them is what makes the exclusion auditable rather than invisible.
    heading_counts          JSONB       NOT NULL,

    -- §4. All five are the MACHINE determination and are never overwritten; a
    -- human resolution lives on review_decisions and takes effect at read time.
    document_title_text         TEXT,
    document_title_node_id      UUID,
    document_title_source_level SMALLINT,
    document_title_status       VARCHAR(32) NOT NULL,
    document_title_method       VARCHAR(32),

    status                  VARCHAR(16) NOT NULL,
    failure_reason          TEXT,

    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at            TIMESTAMPTZ,

    CONSTRAINT segmentation_runs_status_valid
        CHECK (status IN ('Processing', 'Completed', 'Failed')),

    -- A failure must say why, and a success must not pretend to have one.
    CONSTRAINT segmentation_runs_failure_reason_iff_failed
        CHECK ((status = 'Failed') = (failure_reason IS NOT NULL)),

    CONSTRAINT segmentation_runs_title_status_valid
        CHECK (document_title_status IN ('identified', 'unresolved')),

    CONSTRAINT segmentation_runs_title_method_valid
        CHECK (document_title_method IS NULL
               OR document_title_method IN ('singleton_h1', 'structural_rule'))
);

CREATE INDEX IF NOT EXISTS idx_segmentation_runs_extraction
    ON segmentation_runs (extraction_run_id);

-- One section of one document.
CREATE TABLE IF NOT EXISTS section_nodes (
    section_id          UUID PRIMARY KEY,
    segmentation_run_id UUID NOT NULL
        REFERENCES segmentation_runs (segmentation_run_id) ON DELETE CASCADE,

    -- Structural hierarchy only; implies nothing semantic. The document_title
    -- node IS eligible as a parent (§8, 2.1): it is the H1 ancestor of the
    -- H2-H4 hierarchy, so a first H2 — or an H4 preceding it, as in the
    -- reference fixture — carries the title node's id.
    parent_section_id   UUID REFERENCES section_nodes (section_id) ON DELETE SET NULL,

    -- Document order, 0-based and dense within a run.
    ordinal             INTEGER     NOT NULL,

    node_kind           VARCHAR(16) NOT NULL,
    heading_raw         TEXT        NOT NULL,
    heading_normalized  TEXT        NOT NULL,

    -- NULL, not '', for a bare structural container: there is nothing to
    -- classify, which is a different state from a heading that normalised away
    -- to nothing.
    semantic_heading    TEXT,

    heading_level       SMALLINT    NOT NULL,
    structural_container VARCHAR(16),
    appendix_label      VARCHAR(8),

    -- Byte offsets into the UTF-8 encoding of the markdown named by the run's
    -- approved_markdown_hash. Not rune offsets, not UTF-16 code units; the
    -- three disagree on real Mathpix output. Half-open: [start, end).
    --
    -- The span begins AT the newline terminating the node's own heading line,
    -- so heading text is excluded and the first byte of every span is '\n'.
    -- Heading lines and pre-heading preamble are therefore owned by no node.
    -- That is coverage, not collision: no byte is claimed twice, and some bytes
    -- are claimed by nobody.
    start_offset        INTEGER     NOT NULL,
    end_offset          INTEGER     NOT NULL,

    -- NULL means unresolved and MUST stay NULL. §8's overlay model lets a human
    -- decision take effect at read time without overwriting what the machine
    -- determined, and that only works if the stored value honestly records
    -- having no answer. A placeholder role is indistinguishable from a
    -- confident one once persisted.
    primary_role          VARCHAR(32),
    content_class         VARCHAR(32),
    classification_status VARCHAR(16) NOT NULL,
    classification_method VARCHAR(16),

    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT section_nodes_run_ordinal_unique
        UNIQUE (segmentation_run_id, ordinal),

    CONSTRAINT section_nodes_kind_valid
        CHECK (node_kind IN ('document_title', 'section')),

    CONSTRAINT section_nodes_level_valid
        CHECK (heading_level BETWEEN 1 AND 4),

    CONSTRAINT section_nodes_span_ordered
        CHECK (start_offset >= 0 AND end_offset >= start_offset),

    CONSTRAINT section_nodes_status_valid
        CHECK (classification_status IN ('resolved', 'unresolved')),

    CONSTRAINT section_nodes_method_valid
        CHECK (classification_method IS NULL
               OR classification_method IN ('rule', 'structural')),

    -- The invariant that keeps §8's overlay honest, enforced by the database
    -- rather than by convention: an unresolved node carries no role, no class
    -- and no method, and a resolved one carries a method.
    CONSTRAINT section_nodes_unresolved_is_empty
        CHECK (classification_status <> 'unresolved'
               OR (primary_role IS NULL
                   AND content_class IS NULL
                   AND classification_method IS NULL)),

    CONSTRAINT section_nodes_resolved_has_method
        CHECK (classification_status <> 'resolved'
               OR classification_method IS NOT NULL),

    -- A node is never its own parent. Deeper cycles are prevented by
    -- construction — parents always precede children in document order — and
    -- are not expressible as a CHECK.
    CONSTRAINT section_nodes_not_self_parent
        CHECK (parent_section_id IS NULL OR parent_section_id <> section_id)
);

CREATE INDEX IF NOT EXISTS idx_section_nodes_run
    ON section_nodes (segmentation_run_id, ordinal);

CREATE INDEX IF NOT EXISTS idx_section_nodes_parent
    ON section_nodes (parent_section_id);

-- One open question per unresolved classification, plus one per title
-- ambiguity.
--
-- Heading and section text are deliberately NOT duplicated here; a review
-- surface retrieves them via section_id. §8's read-time context rule then
-- widens that to the node's ancestor headings and its descendants' spans,
-- because a parent node owns only the text before its first child and can
-- otherwise present a reviewer with almost nothing.
CREATE TABLE IF NOT EXISTS review_tasks (
    review_task_id      UUID PRIMARY KEY,
    segmentation_run_id UUID NOT NULL
        REFERENCES segmentation_runs (segmentation_run_id) ON DELETE CASCADE,

    -- NULL only for a title_ambiguity task on a document with no H1 node.
    section_id          UUID REFERENCES section_nodes (section_id) ON DELETE CASCADE,

    review_reason       VARCHAR(32) NOT NULL,

    -- Empty for zero_role_match: nothing matched, so there is no shortlist and
    -- the reviewer chooses from the full role set. Populated only on a tie.
    candidate_roles     TEXT[]      NOT NULL DEFAULT '{}',
    matched_keywords    TEXT[]      NOT NULL DEFAULT '{}',

    status              VARCHAR(16) NOT NULL DEFAULT 'open',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT review_tasks_reason_valid
        CHECK (review_reason IN ('zero_role_match', 'multi_role_match', 'title_ambiguity')),

    CONSTRAINT review_tasks_status_valid
        CHECK (status IN ('open', 'resolved')),

    -- Only a title_ambiguity task may lack a section.
    CONSTRAINT review_tasks_section_required
        CHECK (section_id IS NOT NULL OR review_reason = 'title_ambiguity'),

    -- A tie without candidates is not a tie. This is what stops a
    -- multi_role_match being written as though it were a zero-match, which
    -- would silently deprive the reviewer of the shortlist.
    CONSTRAINT review_tasks_multi_has_candidates
        CHECK (review_reason <> 'multi_role_match' OR cardinality(candidate_roles) > 1),

    CONSTRAINT review_tasks_zero_has_no_candidates
        CHECK (review_reason <> 'zero_role_match' OR cardinality(candidate_roles) = 0),

    -- One open task per node. A rerun replaces the run and cascades.
    CONSTRAINT review_tasks_one_per_section
        UNIQUE (segmentation_run_id, section_id)
);

CREATE INDEX IF NOT EXISTS idx_review_tasks_run_status
    ON review_tasks (segmentation_run_id, status);

-- Exactly one authoritative human decision per task.
--
-- A correction UPDATES this row in place. That is a deliberate and confined
-- exception to the pipeline's append-only discipline, limited to human
-- decisions, because there is never more than one competing human resolution
-- per task. The machine result on section_nodes is never touched: it remains as
-- provenance, and the effective value is computed at read time by preferring
-- this row when it exists.
CREATE TABLE IF NOT EXISTS review_decisions (
    review_decision_id  UUID PRIMARY KEY,

    -- UNIQUE is the single-decision rule, enforced rather than assumed.
    review_task_id      UUID NOT NULL UNIQUE
        REFERENCES review_tasks (review_task_id) ON DELETE CASCADE,

    assigned_role           VARCHAR(32),
    assigned_content_class  VARCHAR(32),

    -- Used only by title_ambiguity decisions.
    assigned_document_title_text    TEXT,
    assigned_document_title_node_id UUID REFERENCES section_nodes (section_id) ON DELETE SET NULL,

    human_review_comment TEXT NOT NULL DEFAULT '',
    reviewer_id          TEXT NOT NULL,

    created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
