-- Allow classification_method = 'inherited'.
--
-- A section whose heading matched no keyword now takes its parent's role, and
-- records that it did so. The method is stored separately from 'rule' because
-- an inherited role is a weaker claim: it says "this sits beneath a methodology
-- section", not "this heading says methodology". Folding the two together would
-- make it impossible to count later how many roles were guessed from position,
-- or to check whether the guess was right.
--
-- This relaxes specification §3, which states that classification is
-- parent-independent and that "no promotion or rescue mechanism exists or is
-- needed". It is a rescue mechanism, added after a real paper showed seven of
-- its nine open questions were answered by the parent heading alone.
--
-- Parent-independence still holds where it matters: a heading that matched
-- keeps its own answer, and a heading that matched two roles keeps its
-- shortlist. Only a heading with no evidence at all looks upward.

ALTER TABLE section_nodes
    DROP CONSTRAINT IF EXISTS section_nodes_method_valid;

ALTER TABLE section_nodes
    ADD CONSTRAINT section_nodes_method_valid
    CHECK (classification_method IS NULL
           OR classification_method IN ('rule', 'structural', 'inherited'));
