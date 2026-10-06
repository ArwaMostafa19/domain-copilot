CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE chunks (
    id              bigserial PRIMARY KEY,
    tenant_id       text NOT NULL REFERENCES tenants (id),
    document_id     bigint NOT NULL REFERENCES documents (id) ON DELETE CASCADE,
    ordinal         integer NOT NULL,
    section         text NOT NULL,
    page            integer,
    revision        text NOT NULL,
    context         text NOT NULL,
    content         text NOT NULL,
    embedding_model text NOT NULL,
    embedding       vector(768) NOT NULL,
    tsv             tsvector GENERATED ALWAYS AS
                        (to_tsvector('english', context || ' ' || content)) STORED,
    UNIQUE (document_id, ordinal)
);

CREATE INDEX chunks_tsv_idx ON chunks USING gin (tsv);
CREATE INDEX chunks_embedding_idx ON chunks USING hnsw (embedding vector_cosine_ops);
CREATE INDEX chunks_document_idx ON chunks (document_id);

CREATE TABLE safety_prerequisites (
    id          bigserial PRIMARY KEY,
    tenant_id   text NOT NULL REFERENCES tenants (id),
    document_id bigint NOT NULL REFERENCES documents (id) ON DELETE CASCADE,
    step_no     integer NOT NULL,
    step_text   text NOT NULL,
    UNIQUE (document_id, step_no)
);


ALTER TABLE chunks ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON chunks
    USING (tenant_id = current_setting('app.tenant_id', true));

ALTER TABLE safety_prerequisites ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON safety_prerequisites
    USING (tenant_id = current_setting('app.tenant_id', true));

GRANT SELECT, INSERT, UPDATE, DELETE ON chunks, safety_prerequisites TO copilot_app;
GRANT USAGE, SELECT ON SEQUENCE chunks_id_seq, safety_prerequisites_id_seq TO copilot_app;