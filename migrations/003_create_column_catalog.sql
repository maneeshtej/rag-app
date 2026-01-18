CREATE TABLE column_catalog (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    table_name TEXT NOT NULL,
    column_name TEXT NOT NULL,
    embedding VECTOR(384) NOT NULL
);
