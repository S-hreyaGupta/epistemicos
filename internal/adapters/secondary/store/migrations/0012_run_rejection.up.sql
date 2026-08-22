-- Run-level rejection: objecting to a determination the machine made confidently.
--
-- WHAT THIS FIXES
--
-- The review gate shipped able to handle "the machine was uncertain" and unable
-- to handle "the machine was certain and wrong". A rejection required a review
-- task; a task existed only where a heading matched zero or several roles; so a
-- run where everything resolved cleanly had no surface a human could object
-- through, and passed immediately and permanently.
--
-- That is not a gap about bibliographies, though a bibliography is where it was
-- noticed. It is every determination the machine was confident about.
--
-- WHY THIS IS STORED WHEN THE GATE IS NOT
--
-- §5 of the review spec computes review_state at read time from tasks and their
-- decisions, deliberately, so that one fact does not live in two places.
--
-- A run-level rejection is not derivable from tasks — it exists precisely
-- because there were none — so it has to be a stored fact. The gate stays
-- computed; it simply gains one more input, in the same way it already reads
-- review_decisions rather than recomputing them.
CREATE TABLE IF NOT EXISTS run_rejections (
    run_rejection_id    UUID PRIMARY KEY,

    -- UNIQUE: a run is rejected once. A second objection to an already-rejected
    -- run is not a second fact, and two rows would leave nothing to say which
    -- comment the author received.
    segmentation_run_id UUID NOT NULL UNIQUE
        REFERENCES segmentation_runs (segmentation_run_id) ON DELETE CASCADE,

    -- Mandatory, and for the same reason it is mandatory on a task rejection:
    -- this is the sentence the author reads. A run returned with no reason is a
    -- manuscript sent back saying nothing.
    human_review_comment TEXT NOT NULL,

    reviewer_id          TEXT NOT NULL,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT run_rejections_comment_present
        CHECK (length(btrim(human_review_comment)) > 0),

    CONSTRAINT run_rejections_reviewer_present
        CHECK (length(btrim(reviewer_id)) > 0)
);

-- A REJECTION IS ALLOWED AFTER CONSUMPTION, AND THAT IS NOT A CONTRADICTION.
--
-- Migration 0010 freezes review DECISIONS once a run is consumed, so that a late
-- edit cannot retroactively change what Step 4 already read. That rule stands
-- and is not relaxed here.
--
-- A run-level rejection is a different kind of act. It does not edit what Step 4
-- read; it records that what Step 4 read was wrong. History is preserved and
-- superseded rather than rewritten, which is why `passed` can mean "currently
-- accepted" without meaning "permanently final".
--
-- So: no check against decisions_consumed_at here, on purpose. The one
-- consequence is that anything already derived from this run is now stale, which
-- is what the column below exists to make computable.

-- Downstream artefacts record the run they were derived from. When that run is
-- rejected, they are superseded.
--
-- Stored on the run rather than tracked per artefact because the question a
-- consumer asks is "is the structure I built on still accepted?", and the answer
-- belongs with the structure.
ALTER TABLE segmentation_runs
    ADD COLUMN IF NOT EXISTS superseded_at TIMESTAMPTZ;

COMMENT ON COLUMN segmentation_runs.superseded_at IS
    'Set when the run is rejected at run level. Anything derived from this run, identified by its section map hash, is stale from this moment.';

CREATE INDEX IF NOT EXISTS idx_run_rejections_run
    ON run_rejections (segmentation_run_id);

-- An author return can now carry an item that belongs to no task.
--
-- 0010 made review_task_id NOT NULL, which was right when every rejection came
-- from a task. A run-level objection has no task by definition, so the report
-- that carries it cannot be written without this.
--
-- The CHECK keeps the original guarantee everywhere else: only a run_rejected
-- item may lack a task, so a task rejection that lost its reference still fails
-- loudly rather than becoming an anonymous complaint.
ALTER TABLE author_return_items
    ALTER COLUMN review_task_id DROP NOT NULL;

ALTER TABLE author_return_items
    DROP CONSTRAINT IF EXISTS author_return_items_task_required;

ALTER TABLE author_return_items
    ADD CONSTRAINT author_return_items_task_required
        CHECK (review_task_id IS NOT NULL OR review_reason = 'run_rejected');
