-- Checkpoint 2: users, runs, per-step accounting and work orders.
-- Every tenant-owned table carries the same Row-Level Security policy as
-- documents/chunks, so the application role can only ever see one tenant.

CREATE TABLE users (
    id            bigserial PRIMARY KEY,
    tenant_id     text NOT NULL REFERENCES tenants (id),
    username      text NOT NULL,
    role          text NOT NULL CHECK (role IN ('technician', 'supervisor')),
    password_hash text NOT NULL,
    active        boolean NOT NULL DEFAULT true,
    created_at    timestamptz NOT NULL DEFAULT now(),
    UNIQUE (tenant_id, username)
);

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON users
    USING (tenant_id = current_setting('app.tenant_id', true));

CREATE TABLE runs (
    id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id        text NOT NULL REFERENCES tenants (id),
    user_id          bigint NOT NULL REFERENCES users (id),
    question         text NOT NULL,
    status           text NOT NULL CHECK (status IN (
                         'running', 'awaiting_acknowledgement', 'pending_approval',
                         'approved', 'rejected', 'cancelled', 'failed', 'completed')),
    created_at       timestamptz NOT NULL DEFAULT now(),
    finished_at      timestamptz,
    total_tokens     integer NOT NULL DEFAULT 0 CHECK (total_tokens >= 0),
    estimated_tokens boolean NOT NULL DEFAULT false
);

ALTER TABLE runs ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON runs
    USING (tenant_id = current_setting('app.tenant_id', true));

CREATE TABLE run_steps (
    id                bigserial PRIMARY KEY,
    tenant_id         text NOT NULL REFERENCES tenants (id),
    run_id            uuid NOT NULL REFERENCES runs (id) ON DELETE CASCADE,
    ordinal           integer NOT NULL,
    agent             text NOT NULL,
    tools_used        text[] NOT NULL DEFAULT '{}',
    evidence_ids      bigint[] NOT NULL DEFAULT '{}',
    prompt_tokens     integer NOT NULL DEFAULT 0,
    completion_tokens integer NOT NULL DEFAULT 0,
    estimated         boolean NOT NULL DEFAULT false,
    duration_ms       integer NOT NULL DEFAULT 0,
    outcome           text NOT NULL,
    summary           text CHECK (summary IS NULL OR char_length(summary) <= 500),
    created_at        timestamptz NOT NULL DEFAULT now(),
    UNIQUE (run_id, ordinal)
);

ALTER TABLE run_steps ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON run_steps
    USING (tenant_id = current_setting('app.tenant_id', true));

CREATE TABLE work_orders (
    id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id  text NOT NULL REFERENCES tenants (id),
    run_id     uuid NOT NULL REFERENCES runs (id) ON DELETE CASCADE,
    version    integer NOT NULL,
    status     text NOT NULL CHECK (status IN ('draft', 'pending_approval', 'approved', 'rejected')),
    content    jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (run_id, version)
);

ALTER TABLE work_orders ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON work_orders
    USING (tenant_id = current_setting('app.tenant_id', true));

CREATE TABLE audit_log (
    id            bigserial PRIMARY KEY,
    tenant_id     text NOT NULL REFERENCES tenants (id),
    actor_user_id bigint REFERENCES users (id),
    action        text NOT NULL,
    subject_type  text NOT NULL,
    subject_id    text,
    detail        jsonb,
    created_at    timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON audit_log
    USING (tenant_id = current_setting('app.tenant_id', true));

GRANT SELECT, INSERT, UPDATE ON users TO copilot_app;
GRANT SELECT, INSERT, UPDATE ON runs TO copilot_app;
GRANT SELECT, INSERT ON run_steps TO copilot_app;
GRANT SELECT, INSERT, UPDATE ON work_orders TO copilot_app;
GRANT SELECT, INSERT ON audit_log TO copilot_app;
GRANT USAGE, SELECT ON SEQUENCE
    users_id_seq, run_steps_id_seq, audit_log_id_seq TO copilot_app;