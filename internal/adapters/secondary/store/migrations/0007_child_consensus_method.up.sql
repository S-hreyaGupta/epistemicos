-- Allow classification_method = 'child_consensus'.
--
-- A section whose heading matched no keyword, and which sits too high in the
-- document to inherit anything downward, now takes the role that every one of
-- its subsections independently matched.
--
-- The motivating case was "5 EMPIRICAL ANALYSIS": no keyword hit, parent was
-- the document title so there was nothing above it to inherit from, and it was
-- the last open question in a 46-page paper. Its three subsections were
-- "5.1 Regression results", "5.2 Robustness checks" and "5.3 Robustness
-- checks", all three of which matched RESULTS from their own headings. The
-- answer was already written down; asking a person for it was asking for
-- something the document had said three times.
--
-- Stored as its own method rather than folded into 'inherited', because the
-- evidence runs the other way and the two are different claims. "This sits
-- under a methodology section" and "everything underneath this says results"
-- are not interchangeable, and a reader who cannot tell them apart cannot
-- audit either one.
--
-- The rule requires UNANIMITY among at least two children, each of which
-- reached its role by 'rule' — that is, from its own heading. A child that
-- inherited its role is not a second opinion, it is an echo, and counting
-- echoes as agreement is how a system talks itself into confidence it has not
-- earned. That restriction also makes the rule self-limiting: it fires at most
-- once per node and never chains.

ALTER TABLE section_nodes
    DROP CONSTRAINT IF EXISTS section_nodes_method_valid;

ALTER TABLE section_nodes
    ADD CONSTRAINT section_nodes_method_valid
    CHECK (classification_method IS NULL
           OR classification_method IN ('rule', 'structural', 'inherited', 'child_consensus'));
