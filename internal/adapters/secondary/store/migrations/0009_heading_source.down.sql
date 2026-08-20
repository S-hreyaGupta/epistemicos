ALTER TABLE section_nodes
    DROP CONSTRAINT IF EXISTS section_nodes_heading_source_valid;

ALTER TABLE section_nodes
    DROP COLUMN IF EXISTS heading_source;
