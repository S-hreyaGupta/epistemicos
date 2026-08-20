-- Step 3R: the human review gate.
--
-- Step 3 could already ask questions and store answers. What it could not do was
-- END: there was no way for a reviewer to say "I looked and this cannot be
-- answered", no state that meant "every question is settled", and nothing for
-- Step 4 to refuse. This migration adds those three things and nothing else.
--
-- The gate itself is NOT stored. review_state is computed at read time from the
-- tasks, exactly as the effective classification is computed from the decisions.
-- A stored copy would be a second place for the same fact to live, and the two
-- would eventually disagree.

-- ---------------------------------------------------------------------------
-- 1. review_reason gains no_structure
-- ---------------------------------------------------------------------------
--
-- A document with no headings at all produces one synthetic whole-document node
-- (Step 3 §5) and, because it has no H1 either, exactly one title_ambiguity
-- task. So it could never pass the gate unlooked-at. But that task asks what the
-- paper is CALLED, and a reviewer can answer it correctly while the document
-- still has no structural signal whatsoever. The question was wrong, not
-- missing.
--
-- no_structure is a SEPARATE task rather than extra words on the title task
-- because there is one decision per task. "The paper is called X" and "this
-- document is unusable" are different answers, and a reviewer may well want to
-- give the first and reject on the second. Merged, they could only do one.
ALTER TABLE review_tasks
    DROP CONSTRAINT IF EXISTS review_tasks_reason_valid;

ALTER TABLE review_tasks
    ADD CONSTRAINT review_tasks_reason_valid
        CHECK (review_reason IN (
            'zero_role_match',
            'multi_role_match',
            'title_ambiguity',
            'no_structure'
        ));

-- A no_structure task always carries the synthetic node, so the existing
-- "only a title task may lack a section" rule is unchanged and still correct.

-- ---------------------------------------------------------------------------
-- 2. A task can now end rejected as well as resolved
-- ---------------------------------------------------------------------------
--
-- Three states, and the third is the point of this migration. Without it,
-- "nobody has looked at this yet" and "somebody looked and could not answer"
-- are the same row, and the run cannot tell an unfinished review from a
-- finished one that failed.
ALTER TABLE review_tasks
    DROP CONSTRAINT IF EXISTS review_tasks_status_valid;

ALTER TABLE review_tasks
    ADD CONSTRAINT review_tasks_status_valid
        CHECK (status IN ('open', 'resolved', 'rejected'));

-- ---------------------------------------------------------------------------
-- 3. A decision says which of the two things it is
-- ---------------------------------------------------------------------------
--
-- DEFAULT 'resolve' is for the rows that already exist. Every decision written
-- before this migration was an assignment, because rejection had no way to be
-- expressed, so backfilling them as resolve is a restatement of what they are
-- rather than a guess about what they meant.
ALTER TABLE review_decisions
    ADD COLUMN IF NOT EXISTS decision VARCHAR(16) NOT NULL DEFAULT 'resolve';

ALTER TABLE review_decisions
    DROP CONSTRAINT IF EXISTS review_decisions_decision_valid;

ALTER TABLE review_decisions
    ADD CONSTRAINT review_decisions_decision_valid
        CHECK (decision IN ('resolve', 'reject'));

-- The comment is MANDATORY on a rejection, enforced here rather than left to
-- the domain.
--
-- It is not a note. It is the sentence the author reads when the manuscript
-- comes back, and a rejection with no reason gives them nothing to act on. This
-- is the same discipline as UNCLASSIFIED being required to state why: a refusal
-- that does not say what it refused is not a refusal anyone can respond to.
--
-- Written as a CHECK because the domain constructor can be bypassed by an
-- import script and the database cannot.
ALTER TABLE review_decisions
    DROP CONSTRAINT IF EXISTS review_decisions_reject_needs_comment;

ALTER TABLE review_decisions
    ADD CONSTRAINT review_decisions_reject_needs_comment
        CHECK (decision <> 'reject' OR length(btrim(human_review_comment)) > 0);

-- A rejection assigns nothing. Recording both a rejection and a role would make
-- the effective view's branch ambiguous, and the overlay is the one place in
-- this system where ambiguity is served to consumers as fact.
ALTER TABLE review_decisions
    DROP CONSTRAINT IF EXISTS review_decisions_reject_assigns_nothing;

ALTER TABLE review_decisions
    ADD CONSTRAINT review_decisions_reject_assigns_nothing
        CHECK (
            decision <> 'reject'
            OR (assigned_role IS NULL
                AND assigned_content_class IS NULL
                AND assigned_document_title_text IS NULL
                AND assigned_document_title_node_id IS NULL)
        );

-- ---------------------------------------------------------------------------
-- 4. When decisions stop being editable
-- ---------------------------------------------------------------------------
--
-- Corrections update a decision in place. The question is when that stops.
--
-- The obvious answer — freeze when the last task is decided — has a trap in it:
-- closure then happens at the instant the final decision is written, so that
-- decision is frozen the moment it exists and can never be corrected. On a
-- returned run the final decision is often a rejection, and a rejection comment
-- is the sentence the author reads. A typo in it would be permanent.
--
-- So decisions freeze on CONSUMPTION, not on closure. consumed_at is set when
-- Step 4 reads the run, or when the AuthorReturn is materialized. Both are real
-- events with a timestamp, and until one of them happens nothing downstream has
-- acted on the decisions, so nothing is retroactively changed by correcting one.
ALTER TABLE segmentation_runs
    ADD COLUMN IF NOT EXISTS decisions_consumed_at TIMESTAMPTZ;

ALTER TABLE segmentation_runs
    ADD COLUMN IF NOT EXISTS decisions_consumed_by TEXT;

COMMENT ON COLUMN segmentation_runs.decisions_consumed_at IS
    'Set when Step 4 reads the run or an AuthorReturn is materialized. Non-null means the review decisions on this run are frozen.';

-- ---------------------------------------------------------------------------
-- 5. Return to author
-- ---------------------------------------------------------------------------
--
-- One record per run, append-only, materialized when the gate computes
-- "returned". Its items are the rejections, so the author-facing report names
-- the specific headings rather than saying the paper was unclear.
--
-- The items are COPIED rather than joined at render time. A join would be less
-- code, but the report is a thing that was sent, and it must keep saying what it
-- said even if a decision is later corrected on a re-run. Snapshotting is what
-- makes the sent report and the stored report the same document.
CREATE TABLE IF NOT EXISTS author_returns (
    author_return_id    UUID PRIMARY KEY,

    -- UNIQUE: a run is returned once. Materializing twice would mean two
    -- reports exist for one decision set, and nothing says which was sent.
    segmentation_run_id UUID NOT NULL UNIQUE
        REFERENCES segmentation_runs (segmentation_run_id) ON DELETE CASCADE,

    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS author_return_items (
    author_return_item_id UUID PRIMARY KEY,

    author_return_id    UUID NOT NULL
        REFERENCES author_returns (author_return_id) ON DELETE CASCADE,

    -- The task this came from, kept for provenance. The text below is a
    -- snapshot and this is how a reader gets back to the live row.
    review_task_id      UUID NOT NULL
        REFERENCES review_tasks (review_task_id) ON DELETE CASCADE,

    review_reason       VARCHAR(32) NOT NULL,

    -- heading_raw of the node, and its ancestors outermost-first, so the author
    -- can find the section. Snapshotted, per the comment above.
    heading_raw         TEXT        NOT NULL DEFAULT '',
    ancestor_headings   TEXT[]      NOT NULL DEFAULT '{}',

    -- The reviewer's own words. NOT NULL and non-empty: an item with no reason
    -- is exactly what the CHECK on review_decisions exists to prevent, and
    -- allowing it here would reintroduce it one table later.
    human_review_comment TEXT       NOT NULL,

    CONSTRAINT author_return_items_comment_present
        CHECK (length(btrim(human_review_comment)) > 0),

    CONSTRAINT author_return_items_one_per_task
        UNIQUE (author_return_id, review_task_id)
);

CREATE INDEX IF NOT EXISTS idx_author_return_items_return
    ON author_return_items (author_return_id);
