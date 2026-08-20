-- Reverse of 0010, in dependency order.
--
-- Note what this cannot undo. Dropping the decision column destroys every
-- rejection: a rejected task's row carries its meaning ONLY in that column,
-- since a rejection assigns nothing. Rolling back after any rejection has been
-- recorded silently converts it into an empty resolve. That is stated here
-- rather than guarded against, because a down migration that refuses to run is
-- worse than one that says what it costs.

DROP TABLE IF EXISTS author_return_items;
DROP TABLE IF EXISTS author_returns;

ALTER TABLE segmentation_runs
    DROP COLUMN IF EXISTS decisions_consumed_by;
ALTER TABLE segmentation_runs
    DROP COLUMN IF EXISTS decisions_consumed_at;

ALTER TABLE review_decisions
    DROP CONSTRAINT IF EXISTS review_decisions_reject_assigns_nothing;
ALTER TABLE review_decisions
    DROP CONSTRAINT IF EXISTS review_decisions_reject_needs_comment;
ALTER TABLE review_decisions
    DROP CONSTRAINT IF EXISTS review_decisions_decision_valid;
ALTER TABLE review_decisions
    DROP COLUMN IF EXISTS decision;

-- Any task left in 'rejected' would violate the restored CHECK, so it is
-- reopened first. Reopening is the honest direction: the rejection is being
-- deleted along with the column above, so the question genuinely is unanswered
-- again.
UPDATE review_tasks SET status = 'open' WHERE status = 'rejected';

ALTER TABLE review_tasks
    DROP CONSTRAINT IF EXISTS review_tasks_status_valid;
ALTER TABLE review_tasks
    ADD CONSTRAINT review_tasks_status_valid
        CHECK (status IN ('open', 'resolved'));

-- Same for no_structure tasks: the reason disappears with the constraint, so
-- the tasks that carry it have to go rather than be silently relabelled as some
-- other kind of question.
DELETE FROM review_tasks WHERE review_reason = 'no_structure';

ALTER TABLE review_tasks
    DROP CONSTRAINT IF EXISTS review_tasks_reason_valid;
ALTER TABLE review_tasks
    ADD CONSTRAINT review_tasks_reason_valid
        CHECK (review_reason IN ('zero_role_match', 'multi_role_match', 'title_ambiguity'));
