-- Rolling back narrows the allowed set, so any row already recording an
-- inherited role must be reconciled first. Rewriting them to 'rule' would erase
-- the distinction this migration exists to preserve, and setting them NULL
-- would violate section_nodes_resolved_has_method. Both are worse than a loud
-- failure, so the constraint is simply restored and a conflicting row will
-- block it.
ALTER TABLE section_nodes
    DROP CONSTRAINT IF EXISTS section_nodes_method_valid;

ALTER TABLE section_nodes
    ADD CONSTRAINT section_nodes_method_valid
    CHECK (classification_method IS NULL
           OR classification_method IN ('rule', 'structural'));
