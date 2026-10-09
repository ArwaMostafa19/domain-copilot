# Security controls and known gaps

This document records controls visible in the current code and their limits. It
is an implementation inventory, not a claim of OWASP certification or a
completed penetration test. Re-check it when the application or deployment
configuration changes.

## Authentication and access control

| Control | Threat addressed | Current implementation and scope |
| --- | --- | --- |
| Password hashing | Credential disclosure after database exposure | Passwords are stored with salted `scrypt`; verification uses constant-time comparison. Unknown users receive a dummy hash check and login returns a generic error. |
| Signed expiring tokens | Forged or indefinitely reused credentials | Tokens use HMAC-SHA256 signatures, expiry, and a configured secret of at least 32 characters. The payload is encoded, not encrypted. User role and active status are reloaded from the database. |
| Tenant isolation | Cross-tenant data access | Tenant-scoped database connections and PostgreSQL row-level security protect tenant records. API run access also checks tenant and technician ownership; supervisors have tenant-wide run review. Integration tests cover tenant isolation. |
| Role and ownership checks | Unauthorized workflow actions and IDOR | Run handlers enforce tenant/owner visibility; approval requires supervisor role. The database query layer also receives tenant IDs. Review any new endpoint against the same rule. |
| Parameterized SQL | SQL injection | Repository and search queries use bound parameters. Search terms are normalized before full-text query construction. |

## Web/API and upload controls

- CORS origins come from `CORS_ORIGINS` and default to an empty list. Allowed
  methods and headers are explicitly listed. Configure exact production origins.
- Middleware limits request bodies to 1 MiB, checks `Content-Length` and the
  actual body, and adds CSP, `X-Content-Type-Options`, `X-Frame-Options`, and
  cache controls for the UI. CSP currently permits inline styles.
- Login is limited to five attempts per client IP per 60 seconds. This counter
  is in-memory, per process, and login-only; it is not a distributed or general
  API abuse control.
- Ingestion validates supported file types and size (default 10 MiB) and reads
  from the configured corpus; user-supplied arbitrary filesystem paths are not
  exposed as an ingest parameter. Keep corpus mounts read-only in deployment.
- The browser uses text DOM APIs for dynamic content and does not place model
  output in `innerHTML`.

## LLM and output handling

- The answer flow instructs the model to treat retrieved evidence as data,
  checks citations against retrieved chunk IDs, and rejects configured canary
  or injection-marker output. These are defense-in-depth checks, not a
  complete prompt-injection sanitizer.
- The work-order generator validates JSON shape and field lengths, and code
  attaches safety prerequisites from the matched documents to the result.
  Tool arguments are checked against registered schemas and each agent has an
  allow-list. Review `src/application/agents.py`: its work-order prompts do
  not currently provide the same explicit untrusted-evidence boundary as the
  grounded answer prompt.
- The golden set has three injection cases (one direct, two indirect). The
  measured pre-generation refusal gate failed both expected-refusal cases
  (recall 0/2); generated-answer resistance was not measured because the local
  chat endpoint timed out. Do not treat prompt-injection resistance as proven.
- Work orders remain drafts for supervisor review. Approval is checked by
  role and workflow state; no external destructive action is performed by the
  current flow.
- The UI does not execute model text as shell, SQL, or a filesystem path.
  Database commands use parameterized queries and tool inputs have schema
  validation before invocation.

## Privacy and provider data flow

- `src/application/redaction.py` masks email-like strings, phone-like number
  strings, and 14-digit Egyptian national ID patterns in prompts, embedding
  text, and nested tool arguments immediately before provider calls. This is
  narrow pattern-based redaction, not general PII detection; other identifiers
  and unusual formats can pass through.
- Ask history and workflow data are stored in tenant-scoped PostgreSQL tables.
  Redaction at the provider boundary does not mean the original request is
  absent from application storage.
- With hosted chat or embedding providers selected, the redacted prompt or
  document text and query are sent to that configured provider. With Ollama,
  those calls go to the configured local endpoint. Operators must choose
  providers and settings appropriate to their data-handling requirements.
- Secrets belong in environment configuration such as `.env`, which is ignored
  by Git. Do not commit real credentials, including in earlier Git history.

## Abuse limits, workflow safety, and logging

- Workflow runs have configured token budgets, model-call limits, run and
  step time limits, and provider HTTP timeouts. Cancellation is cooperative at
  workflow boundaries; a synchronous in-flight provider call may continue
  until its HTTP timeout.
- Safety prerequisites are loaded in application code from the matched
  documents. The workflow checks acknowledgements before generating a work
  order; the model cannot remove the required list. Approval is gated to
  supervisors.
- Correlation IDs are returned in response headers and included in selected
  workflow logs. Workflow actions and approvals are recorded in the audit
  table. Provider/database error handlers log exception types rather than
  exception messages.
- Security logging is not yet comprehensive: failed login events and all
  rejected requests are not consistently written to a durable audit log.
  Preserve the rule that logs contain no passwords, bearer tokens, API keys,
  or raw prompts.

## Dependencies, CI, and verification

- Direct runtime and development dependencies are pinned in requirements
  files. There is no committed generated lockfile at present.
- CI runs `pip-audit`, tests, Ruff, and Gitleaks; the Gitleaks job fetches full
  Git history. CI configuration is evidence that scans are scheduled, not a
  statement that the current repository or its entire history passed. Review
  the current CI result and scan all history before submission. If a secret is
  found, revoke/rotate it and remove it from history before publishing.
- Evaluation includes three injection prompts, but answer-level resistance
  still needs a successful `--with-answers` run. See `docs/EVALUATION.md` and
  retain failed cases in the report.

## Priority gaps to track

1. Improve refusal behavior for the two failed expected-refusal cases and
   measure again; current pre-generation refusal recall is 0/2.
2. Add an explicit untrusted-content boundary for work-order generation and
   measure all direct and indirect injection cases with a functioning model.
3. Decide whether login rate limiting must be shared across API replicas and
   whether broader endpoints need abuse limits.
4. Expand PII detection/redaction to the actual data types and formats in use.
5. Complete and review a full-history secret scan before public submission;
   configure a committed lockfile if the submission requires one.
6. Expand durable security audit coverage while preserving secret and prompt
   confidentiality.
