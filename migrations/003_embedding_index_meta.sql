CREATE TABLE embedding_index_meta (
    id         smallint PRIMARY KEY DEFAULT 1 CHECK (id = 1),
    model      text NOT NULL,
    dimensions integer NOT NULL CHECK (dimensions > 0),
    created_at timestamptz NOT NULL DEFAULT now()
);

-- This table is global (no tenant_id), so it has no Row-Level Security.
GRANT SELECT, INSERT ON embedding_index_meta TO copilot_app;