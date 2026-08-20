-- Record whether a section's heading existed in the document, or was inferred.
--
-- Rule version 2.9 recovers a bibliography heading that Mathpix emitted as plain
-- text. Four of the ten ingested papers need it: without it, no citation_source
-- node is created and the reference list is absorbed by whatever section comes
-- before it. On those papers the absorbing section was 85% to 91% bibliography.
--
-- The column exists so that an inferred heading is never mistaken for one the
-- document actually had. That is the same discipline as classification_method:
-- a role read off a heading, one taken from a parent, and one taken from a
-- heading we supplied ourselves are three different claims, and a reader who
-- cannot tell them apart cannot audit any of them.
--
-- NULL is the honest value for rows written before 2.9. Those runs did not
-- record the distinction because every heading was detected, and back-filling
-- 'detected' would assert something we merely believe rather than something the
-- run stated. A default would erase the difference between "we know this was a
-- real heading" and "this predates the question".
ALTER TABLE section_nodes
    ADD COLUMN IF NOT EXISTS heading_source VARCHAR(16);

ALTER TABLE section_nodes
    DROP CONSTRAINT IF EXISTS section_nodes_heading_source_valid;

ALTER TABLE section_nodes
    ADD CONSTRAINT section_nodes_heading_source_valid
        CHECK (heading_source IS NULL OR heading_source IN ('detected', 'inferred'));
