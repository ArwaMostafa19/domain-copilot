
CREATE TABLE tenants (
    id   text PRIMARY KEY,
    name text NOT NULL
);

INSERT INTO tenants (id, name) VALUES
    ('tenant-alpha', 'Alpha Manufacturing'),
    ('tenant-beta', 'Beta Manufacturing');

CREATE TABLE documents (
    id             bigserial PRIMARY KEY,
    tenant_id      text NOT NULL REFERENCES tenants (id),
    doc_id         text NOT NULL,
    title          text NOT NULL,
    equipment      text,
    document_type  text,
    revision       text NOT NULL,
    status         text NOT NULL,
    source_format  text NOT NULL,
    source_path    text NOT NULL,
    content_sha256 text NOT NULL,
    ingest_status  text NOT NULL DEFAULT 'pending',
    ingest_error   text,
    UNIQUE (tenant_id, doc_id, source_format)
);

ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON documents
    USING (tenant_id = current_setting('app.tenant_id', true));


GRANT USAGE ON SCHEMA public TO copilot_app;
GRANT SELECT ON tenants TO copilot_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON documents TO copilot_app;
GRANT USAGE, SELECT ON SEQUENCE documents_id_seq TO copilot_app;