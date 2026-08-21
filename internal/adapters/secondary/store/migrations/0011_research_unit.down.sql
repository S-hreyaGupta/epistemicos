-- Reverse of 0011, in dependency order.
--
-- Nothing is lost that cannot be recomputed. That is the one advantage of
-- storing a deterministic computation rather than a judgement: the same markdown
-- under the same rule version reproduces every row here exactly, so this drop
-- costs a re-run and nothing more.

DROP TABLE IF EXISTS research_unit_evidence;
DROP TABLE IF EXISTS research_unit_verdicts;
