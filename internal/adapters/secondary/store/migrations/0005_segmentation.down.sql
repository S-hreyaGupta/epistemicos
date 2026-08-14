-- Dropped in reverse dependency order. review_decisions references both
-- review_tasks and section_nodes, so it goes first.
DROP TABLE IF EXISTS review_decisions;
DROP TABLE IF EXISTS review_tasks;
DROP TABLE IF EXISTS section_nodes;
DROP TABLE IF EXISTS segmentation_runs;
