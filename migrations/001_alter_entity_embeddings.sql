BEGIN;

ALTER TABLE entity_embeddings
ADD COLUMN source_col text NOT NULL;

COMMIT;
