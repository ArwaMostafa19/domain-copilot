# Project work and Git handoff

This file summarizes the implementation work and provides a suggested way to
split the current uncommitted changes into reviewable GitHub branches. No
commits or branches have been created by this handoff. Keep `.env` out of all
staging commands.

## What the project contains

- **Grounded Q&A:** hybrid manual retrieval, embedding-index compatibility
  checks, low-evidence refusal, citations tied to retrieved chunks, and
  prompt-injection/canary checks.
- **Ingestion and tenant data:** Markdown/PDF extraction, chunking, safety-step
  extraction, PostgreSQL storage with tenant row-level security, migrations,
  and an idempotent CLI ingest path.
- **Authentication and API:** scrypt password hashes, technician/supervisor
  roles, signed tenant-bearing tokens, protected endpoints, request limits,
  login rate limiting, correlation IDs, and security headers.
- **Agents and maintenance workflow:** typed contracts for three agents and an
  orchestrator, per-agent tool allow-lists and argument validation, resumable
  workflow phases, code-enforced safety prerequisites, traces, supervisor
  review, and audit entries.
- **Web UI and usage:** login, Q&A with citations, workflow and safety
  checklist, run traces/review, documents, usage, persisted ask history, and
  server-sent progress events. The UI uses DOM text APIs and keeps the token in
  memory.
- **Evaluation:** `eval/golden.jsonl` has 25 fixed Q/A cases, including six
  adversarial cases. `src/eval/run.py` measures retrieval, evidence coverage,
  and the pre-generation refusal gate; `docs/EVALUATION.md` describes the
  method and baseline.
- **Recent hardening:** run ownership checks, bounded model retries and token
  output, cooperative cancellation between workflow stages, narrow-pattern
  PII redaction at model/embedding boundaries, structured work-order
  validation, provider/DB readiness checks, and safer provider errors.

The earlier project history already has merged PRs through PR #40. The current
working tree includes edits across agents, workflow/UI, answering/retrieval,
system documentation, and teaching materials. Review the staged diff before
each commit and do not stage unrelated local changes.

## Verification and measured evaluation

Previously recorded project checks:

- `python -m ruff check src tests --no-cache` - passed.
- `python -m pytest tests -q` - **306 passed, 26 skipped**.
- `python -m compileall -q src tests` - passed.
- `node --check src/api/static/app.js` - passed.

Evaluation additions checked on 2026-10-08:

- Ruff passed for `src/eval/run.py` and `src/eval/questions.py`.
- The golden set contains 25 cases, six adversarial; referenced source
  documents/sections and expected phrases were checked against the corpus.
- `docker compose config --quiet` passed.
- Retrieval-only baseline against the existing index (`nomic-embed-text`,
  `RETRIEVAL_MIN_SIMILARITY=0.55`): hit-rate@6 **20/23 (87.0%)**;
  retrieved-evidence fact coverage **38/38 (100%)**; pre-generation refusal
  accuracy **23/25 (92%)**, refusal recall **0/2 (0%)**.
- Both expected-refusal cases passed the similarity gate. The exact source
  misses and per-case results are in `eval/baseline.json`. These numbers do not
  measure generated answer quality.
- An answer-level run was attempted with local `llama3.2:3b`, but Ollama's
  `/api/chat` timed out even on a short request. No answer-groundedness or
  end-to-end refusal result is claimed. Run with `--with-answers` after chat is
  responsive.

These measurements depend on the existing local database/index and provider
configuration; a live model being reachable is not implied by static checks.

## New branch, commit, and PR plan for the remaining work

The six earlier branches already exist locally. The plans below use **new,
unique branch names** and each starts from `main`; they do not depend on or
target any earlier branch. The current branch is `docs/teaching-materials`.
The commands are prepared for review and have not been run. For every PR,
create the new branch from `main`, stage only its listed files, inspect the
staged names and diff, commit, and open the PR with the title and description
below.

Before starting, preserve this handoff file somewhere safe or copy its final
version to the newly created PR branch that owns the handoff changes (PR 6
below). Do not use `git add .`.

### CI failure on `feat/maintenance-agents-followup`

The attached CI output reports **5 failed, 331 passed**. All five failures
come from the agent changes reading `Evidence.equipment`, while the PR branch's
`Evidence` type does not yet have that field and four new test cases pass
`equipment=` to its constructor. The same test run shows no unrelated failures.
The local working tree now has the missing field in `src/domain/rag.py` and
the search mapper in `src/infrastructure/chunk_search.py`; the focused Ruff
check passed and the agent/orchestrator tests passed (`12 passed`) locally.
The pasted output does not include the Ruff job result, so lint status for the
failed CI run cannot be determined from that attachment.

This mismatch is due to the feature PR being based on `main`, without the
existing retrieval PR that already added the equipment field. Apply this
small compatibility fix on a fresh branch from `main`, and include it with the
agent PR before merge:

#### CI follow-up — `fix/agent-evidence-equipment-field`

```powershell
git switch main
git switch -c fix/agent-evidence-equipment-field
git add src/domain/rag.py src/infrastructure/chunk_search.py
git diff --cached --name-only
git diff --cached --stat
git commit -m "fix: include equipment metadata in retrieval evidence"
```

**PR title:** `Include equipment metadata in retrieved evidence`

**PR description:**

```markdown
## What

Add the equipment identifier to retrieved Evidence and populate it from the
joined document metadata in dense and keyword search results.

## Why

The maintenance agents use retrieved equipment metadata to validate explicit
equipment requests and keep safety planning scoped to the matching procedure.
Without the field, agent tests and workflow execution fail with
`AttributeError`.

## How tested

Run `python -m ruff check .` and
`python -m pytest tests/unit/test_agent_contracts.py tests/unit/test_orchestrator.py -q`.

## Linked issue

Refs #26 and #29
```

For a standalone, non-stacked PR, retarget
`feat/maintenance-agents-followup` to this fix branch after the fix merges into
`main`, then rerun CI. If both PRs are ready together, the agent PR may target
the fix branch temporarily and be retargeted to `main` after the fix merges.

### PR 1 — `feat/maintenance-agents-followup`

```powershell
git switch main
git switch -c feat/maintenance-agents-followup
git add src/application/agents.py src/application/orchestrator.py src/application/ports.py tests/unit/test_agent_contracts.py
git diff --cached --name-only
git diff --cached --stat
git commit -m "feat: refine typed maintenance agents"
```

**Title:** `Refine typed maintenance agents and workflow contracts`

**Description:**

```markdown
## What

Update typed agent contracts, orchestration behavior, application ports, and
agent contract coverage.

## Why

Keep agent inputs, outputs, and workflow coordination aligned with the
maintenance workflow implementation.

## How tested

Run the focused agent contract and orchestrator tests, then run the full test
suite on this branch before merge.

## Linked issue

Refs #26, #28, #29, and #30
```

### PR 2 — `feat/workflow-api-ui-followup`

```powershell
git switch main
git switch -c feat/workflow-api-ui-followup
git add src/api/routers/documents.py src/api/routers/ingest.py src/api/routers/runs.py src/api/static/app.js src/api/static/index.html src/api/static/style.css src/infrastructure/workflow_repository.py tests/api/test_api_runs_ui.py
git diff --cached --name-only
git diff --cached --stat
git commit -m "feat: refine maintenance workflow API and UI"
```

**Title:** `Refine maintenance workflow endpoints and UI`

**Description:**

```markdown
## What

Update the document, ingestion, and maintenance run endpoints, workflow
repository behavior, and browser UI with API/UI regression coverage.

## Why

Keep the technician workflow and supervisor review screens consistent with
the current backend workflow behavior.

## How tested

Run the API UI tests and related workflow ownership and tenant-isolation tests.
Run the full suite before merge.

## Linked issue

Refs #27, #30, and #31
```

### PR 3 — `feat/grounded-answer-retrieval-followup`

```powershell
git switch main
git switch -c feat/grounded-answer-retrieval-followup
git add prompts/answer_system.md src/application/answering.py src/domain/rag.py src/infrastructure/chunk_search.py
git diff --cached --name-only
git diff --cached --stat
git commit -m "feat: refine grounded answer and retrieval behavior"
```

**Title:** `Refine grounded answer and retrieval behavior`

**Description:**

```markdown
## What

Update answer generation and system instructions, retrieval domain types, and
chunk search behavior.

## Why

Keep generated answers tied to retrieved evidence and make retrieval behavior
consistent with the current application contracts.

## How tested

Run the answering and retrieval tests. Review refusal and citation behavior,
then run the full suite before merge.

## Linked issue

Refs #18
```

### PR 4 — `ci/repository-workflow-followup`

```powershell
git switch main
git switch -c ci/repository-workflow-followup
git add .github/workflows/ci.yml
git diff --cached --name-only
git diff --cached --stat
git commit -m "ci: refine repository quality workflow"
```

**Title:** `Refine CI quality checks`

**Description:**

```markdown
## What

Update the repository CI workflow.

## Why

Keep automated checks aligned with the current repository layout and
development workflow.

## How tested

Review the workflow diff and confirm the GitHub Actions run passes after
opening the PR.

## Linked issue

Refs #32
```

### PR 5 — `docs/readme-project-status-followup`

```powershell
git switch main
git switch -c docs/readme-project-status-followup
git add README.md
git diff --cached --name-only
git diff --cached --stat
git commit -m "docs: clarify project status and demo videos"
```

**Title:** `Clarify project status and add demo video links`

**Description:**

```markdown
## What

Update the README status and API summary, and add placeholders for the slide
presentation and project demo videos.

## Why

Give readers an accurate overview of the implemented project and a clear
place to find the two project videos.

## How tested

Review the route list against the API routers and replace both video
placeholders with the final share links before publishing the README.

## Linked issue

Refs (add an issue number if one applies)
```

### PR 6 — `docs/project-handoff-and-usage-followup`

```powershell
git switch main
git switch -c docs/project-handoff-and-usage-followup
git add docs/SYSTEM-DESIGN.md PROJECT-STRUCTURE-GUIDE.md IMPLEMENTATION-AND-HANDOFF.md docs/AI-USAGE-LOG.md
git diff --cached --name-only
git diff --cached --stat
git commit -m "docs: update project handoff and design guides"
```

**Title:** `Update implementation handoff and project design guides`

**Description:**

```markdown
## What

Update the system design and project structure guides, refresh the
implementation handoff, and add the AI usage log.

## Why

Make the current architecture, project status, remaining issues, and AI
contributions easier to review.

## How tested

Compare documentation statements with the source and current Git status.
Documentation-only change; no application tests run.

## Linked issue

Refs #18, #21, #22, and #23
```

Keep `.env`, `implementation_plan.md`, the corpus edit, caches, and database
volumes out of all PRs. README and teaching files are already committed on
existing branches. This plan covers the implementation, CI, and documentation
changes still present in the working tree.

## Current file inventory

Compared `git diff --name-only` and `git ls-files --others --exclude-standard`
on 2026-10-10. All 20 tracked changes and both intended untracked deliverables
are covered by PRs 1–6. Keep `.env`, `implementation_plan.md`,
`corpus/tenant-alpha/air-compressor-preventive-maintenance.md`, caches, and
database volumes local. The previously mentioned tenant-beta corpus file is
not modified in the current status. Do not stage with `git add .`.

Before each PR, check `git status --short`, `git diff --cached --name-only`,
and `git diff --cached`. The PR descriptions below do not claim test results;
run the named checks on each branch before opening its PR.

## Status of the issues discussed earlier

| Issue / requirement | Status | Evidence and remaining work |
| --- | --- | --- |
| Ruff findings and previously reported test collection/runtime errors | Addressed in the earlier code pass | Project-wide Ruff and pytest results are recorded above. Re-run on the final branch tip before merging. |
| Browser login returned `invalid credentials` while terminal login worked | Fixed in the earlier frontend/API pass | Login request now uses the expected tenant/user/password contract. Confirm once in the final running Compose build. |
| Typed agents, orchestrator, contracts, per-agent tool allow-lists, schema-checked arguments, and side-effect/approval handling | Implemented with open gaps | Agent contract/tool tests and workflow code are included in PRs 1–2. Safety prerequisites come from the matched procedure and are enforced before generation. |
| FR-2 retrieval: hybrid search, deliberate chunking, enhancement, citations, low-evidence refusal | Implemented/documented, with a measured weakness | Retrieval design and baseline are in `docs/EVALUATION.md`. Baseline retrieval hit-rate is 87%; both expected-refusal cases passed the threshold, so refusal recall is 0/2 and needs improvement. |
| FR-3: at least 25 expected-answer questions, at least 5 adversarial, runnable metrics and actual baseline | Partial against the detailed #21/#22 criteria | 25 cases and six adversarial cases exist, but the required cross-tenant and missing-information cases, several runner metrics/tests, and answer-level baseline are still missing. Local Ollama chat timed out. |
| Security controls and threat mapping | Documented, with open gaps | `docs/SECURITY.md` maps implemented controls and limitations. Injection resistance is not proven; rate limiting is login-only/in-memory; PII patterns are narrow; full-history secret scan result still needs review. |
| Nine Ruff findings from the pasted command | The earlier full-project Ruff check is recorded as passing | Run `python -m ruff check . --no-cache` again after staging to confirm the current final tree. |

## Issue-by-issue completion and remaining work

“Done” below describes code/evaluation evidence currently present. An issue is
marked complete only when all stated acceptance criteria appear to be met;
otherwise its PR uses `Refs #N`, not `Closes #N`.

| Issue | Completed | Still incomplete / follow-up |
| --- | --- | --- |
| #18 Hybrid retrieval, citations, refusal | Tenant-scoped dense and keyword retrieval, RRF fusion, default current-revision filtering, Markdown/PDF duplicate collapse, structured exact-chunk citations, and rejection of un-retrieved citation IDs are implemented. | No explicit equipment metadata filter. The 0.55 refusal threshold has not been justified by a completed calibration; measured refusal recall is 0/2. Improve the gate and record calibrated ranges/results. |
| #21 Golden set | 25 cases cover both tenants and Rev A/current material; there are three injection cases and one out-of-corpus case. | Required adversarial cross-tenant and missing-information cases are absent (the remaining two are ambiguous/conflicting-revision cases). No unit test checks every expected fact/substring against corpus files. |
| #22 Evaluation runner | Runner reports hit@6, retrieved fact coverage, pre-generation refusal accuracy/recall; `--with-answers` computes groundedness and end-to-end refusal correctness. Retrieval baseline is recorded in `eval/baseline.json` and `docs/EVALUATION.md`. | No separate citation-validity metric, refusal precision, injection-resistance metric, or cross-tenant leakage metric. There are no runner unit tests using a fake provider. No answer-level baseline was recorded because Ollama chat timed out. |
| #23 Refusal threshold calibration | `python -m src.eval.calibrate` prints each in/out-of-corpus best-hit score, overlap, current value, and a suggested threshold. | No actual calibration output (score ranges, overlap, and recommendation) is recorded in `docs/EVALUATION.md`; the selected 0.55 value still needs empirical justification. |
| #25 Login and signed tokens | `/auth/login` and `/me` exist; signed expiry, wrong-secret/tampered/expired rejection, DB role reload, and generic login error behavior are implemented. | No acceptance criterion is known to be missing. Add route-level tests proving unknown-user and wrong-password responses match, and invalid token cases have the same public error, for regression confidence. |
| #26 Workflow contracts and pure rules | Frozen/validated domain contracts and `resolve_revision`, `check_safety_gate`, `next_state`, and `parts_from_evidence` are implemented. | Tests do not enumerate every allowed and forbidden state transition; add a table-driven transition matrix. |
| #27 Run/work-order persistence | `runs`, `run_steps`, `work_orders`, and `audit_log` have tenant RLS; app-role audit grants are select/insert only; integration tests cover audit immutability and tenant isolation. | No known acceptance criterion missing in code. Ensure the DB-backed integration tests run in CI; they are skipped locally without DB URLs. |
| #28 Tool registry | Five tools are registered, including a write tool; JSON-schema arguments, roles, and agent allow-lists are checked and refusal tests exist. | Denials are not recorded in an audit log (the test named “refused and audited” only asserts refusal). Registry tools have no runtime handlers wired in `build_tool_registry`; current workflow operations call repositories directly. |
| #29 Three agents | Three agents have typed inputs/outputs; safety comes from the database and proposed parts are filtered against evidence. | Dedicated prompts for each agent are missing from `prompts/`; the work-order instructions are inlined in Python. Add prompts and the same explicit untrusted-evidence boundary used for grounded Q&A. |
| #30 Orchestrator state machine | Match → plan → acknowledgement → generation → pending approval is implemented with call/token/time limits, cancellation checks at phase boundaries, transient provider retry, and per-agent run-step persistence. | Tests do not cover budget exhaustion, timeout, cancellation, and provider failure as a complete set. Cancellation cannot interrupt a synchronous in-flight provider request. |
| #31 Run/acknowledge/approval API with SSE | SSE run progress, run details, cancellation, acknowledgement, supervisor-only approve/reject/edit, pre-acknowledgement rejection, and audit records are implemented. | The API test file does not directly exercise every run/acknowledge/approval route and SSE branch; add route-level regression tests before treating the HTTP surface as fully verified. |
| #32 API middleware and hardening | Correlation IDs, security headers, empty-by-default CORS allow-list, 1 MiB body limit, login 5/min limit, and safe provider/database error mappings are implemented. | No 60/min general API limit. Early body/rate-limit returns do not attach the generated correlation ID header. Correlation IDs are not in every log line. Generic handlers in `src/api/errors.py` are not registered in `main.py`; register and test consistent JSON errors without leaking exception details. |
| #33 Security test suite | Token tampering/expiry, role checks, tenant RLS, body limit, headers, tool refusal, safety gate rules, and canary/injection-marker rejection have tests. | The SQL-injection test stubs the answer path rather than exercising database queries. No end-to-end poisoned-document test demonstrates model resistance; chat resistance is unmeasured. Add substantive DB and indirect-injection/gate-bypass tests. |

## Does `docker compose up` prepare everything?

With required values set in `.env`, a fresh `docker compose up --build` starts
PostgreSQL, applies migrations, seeds demo users, then starts the API. The UI
is served at `http://localhost:8000/`. Demo usernames are `alpha-tech`,
`alpha-sup`, `beta-tech`, and `beta-sup`; their password comes from
`DEMO_USER_PASSWORD`. Do not commit `.env`.

Compose does not automatically ingest manuals. The UI can open after startup,
but manuals are not searchable until the corpus has been ingested. This is
expected with the current setup:

```powershell
docker compose run --rm api python -m src.infrastructure.ingest_cli corpus
```

It uses the API image, database settings and read-only corpus mount. Ingestion
also needs the configured embedding provider reachable. With the default
Ollama configuration, Ollama must be running on the host with the embedding
model available. Unchanged files are skipped on re-ingest. The supervisor UI
also has a corpus re-ingest action. A one-shot Compose ingest service has not
been added; it would make startup depend on the embedding provider. Use
`docker compose up --build` after source changes so the image contains them.

## Remaining limitations

- The refusal gate missed both expected-refusal cases in the measured baseline
  (0/2 recall); improve and remeasure this before relying on it for unsupported
  questions or direct injection.
- Generated-answer groundedness and end-to-end refusal metrics are not
  measured yet because the local chat request timed out.
- Run/ask token counts are recorded, but monetary cost accounting is not.
- Run cancellation is cooperative at phase boundaries; it cannot immediately
  interrupt an in-flight synchronous provider HTTP request.
- Full-history secret scanning must be run and reviewed before submission; CI
  includes scanning, but no claim of a clean full Git history is made here.
