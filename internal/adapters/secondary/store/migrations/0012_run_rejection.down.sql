-- Reverse of 0012.
--
-- Dropping run_rejections destroys every run-level objection along with the
-- comment the author was given. Unlike 0011, none of this is recomputable: a
-- rejection is a human judgement, not a function of the markdown.

-- Run-level items must go before the column can be made NOT NULL again: they are
-- precisely the rows that have no task, and there is nothing to fill in.
DELETE FROM author_return_items WHERE review_reason = 'run_rejected';

ALTER TABLE author_return_items
    DROP CONSTRAINT IF EXISTS author_return_items_task_required;

ALTER TABLE author_return_items
    ALTER COLUMN review_task_id SET NOT NULL;

DROP TABLE IF EXISTS run_rejections;

ALTER TABLE segmentation_runs
    DROP COLUMN IF EXISTS superseded_at;
