ALTER TABLE papers ADD COLUMN markdown_hash varchar NOT NULL DEFAULT '';

UPDATE papers
   SET markdown_hash = encode(sha256(convert_to(markdown, 'UTF8')), 'hex')
 WHERE markdown <> '';