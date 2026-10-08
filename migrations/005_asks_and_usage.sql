-- Checkpoint 5: ask history logging and usage accounting.
-- Isolated per tenant via Row-Level Security.

CREATE TABLE IF NOT EXISTS ask_log (
    id                bigserial PRIMARY KEY,
    tenant_id         text NOT NULL REFERENCES tenants (id),
    user_id           bigint REFERENCES users (id),
    correlation_id    text,
    question          text NOT NULL,
    answer_text       text NOT NULL,
    refused           boolean NOT NULL DEFAULT false,
    reason            text,
    citations         jsonb,
    prompt_tokens     integer NOT NULL DEFAULT 0,
    completion_tokens integer NOT NULL DEFAULT 0,
    estimated         boolean NOT NULL DEFAULT false,
    created_at        timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE ask_log ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolation ON ask_log;
CREATE POLICY tenant_isolation ON ask_log
    USING (tenant_id = current_setting('app.tenant_id', true));

GRANT SELECT, INSERT ON ask_log TO copilot_app;
GRANT USAGE, SELECT ON SEQUENCE ask_log_id_seq TO copilot_app;
