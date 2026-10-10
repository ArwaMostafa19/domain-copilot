# Project Structure Guide

This guide provides a quick tour of the project. It follows a question from
submission to answer and explains the main folders, files, and code layers. It
is provided for learning and review; the application does not depend on this
file to run.

## The Project in One Sentence

The web interface sends a question to the API; the application layer searches
and applies security rules; the infrastructure layer communicates with
PostgreSQL and model providers; and the API returns an answer with sources.
When a new manual is added, the ingestion flow extracts and chunks its text,
then stores the chunks and metadata in the database.

## Code Layers

| Layer | Location | Responsibility | Example output |
| --- | --- | --- | --- |
| API / presentation | `src/api/` | Receives HTTP requests, validates users and input, and returns JSON or streaming events; also contains the web interface | An `/ask` response or a browser screen |
| Application | `src/application/` | Implements use cases such as retrieval, answering, agents, safety, and workflow coordination; depends on interfaces rather than a specific database or provider | A cited answer or a draft maintenance work order |
| Domain | `src/domain/` | Defines core project types and rules for documents, evidence, model configuration, and workflows | Typed objects passed between layers |
| Infrastructure | `src/infrastructure/` | Implements external details such as PostgreSQL, PDF and Markdown files, runtime configuration, migrations, seeding, and model providers | Stored rows, chunks, or a model response |
| Evaluation | `src/eval/` and `eval/` | Runs the question set and measures retrieval, evidence coverage, and refusal behavior | A JSON report with per-question results |

### Example: Asking a Question

`src/api/routers/ask.py` receives the request →
`src/application/answering.py` coordinates retrieval, answering, and citations →
`src/application/retrieval.py` requests chunks from the search adapter →
`src/infrastructure/chunk_search.py` searches PostgreSQL → the model provider
drafts the response when needed → the API returns the answer and citations.
Each citation points to a chunk and its source.

### Example: Creating a Maintenance Work Order

`src/api/routers/runs.py` starts the run →
`src/application/orchestrator.py` coordinates the agents →
`src/application/agents.py` matches equipment, resolves the revision and safety
requirements, and prepares a structured draft. Safety requirements come from
the documents and database, and application code requires acknowledgement
before generation. A supervisor reviews and approves or rejects the draft.

## Folder and File Map

### Project Root

- `README.md`: Quick start and project setup.
- `IMPLEMENTATION-AND-HANDOFF.md`: Implementation summary, evaluation, Compose instructions, and Git branch plan.
- `PROJECT-STRUCTURE-GUIDE.md`: This project structure guide.
- `implementation_plan.md`: Local work plan; review it for earlier planning details.
- `docs/`: Design documentation and decisions; see `docs/EVALUATION.md` for evaluation and `docs/SECURITY.md` for security controls.
- `eval/`: Reference questions and the baseline result: `golden.jsonl` and `baseline.json`.
- `src/`: Python application code, organized by the layers described below.
- `tests/`: API, unit, integration, and security tests.
- `migrations/`: SQL files that define the database schema and policies.
- `corpus/`: Maintenance manuals organized by tenant, such as `tenant-alpha/` and `tenant-beta/`. The ingestion flow reads these files.
- `teaching/`: Teaching materials stored in the repository; they are not part of application runtime or the evaluation harness.
- `prompts/`: Model instructions stored as files.
- `scripts/`: Corpus setup, generation, and export tools; these are not part of the normal request path.
- `.github/workflows/ci.yml`: CI steps such as code checks, tests, dependency auditing, and secret scanning.
- `Dockerfile`, `docker-compose.yml`: Build the application image and run the services together.
- `requirements.txt`, `requirements-dev.txt`: Runtime and development dependencies.
- `.env.example`: Example setting names and values; `.env` contains local secrets and must not be committed to Git.
- `.gitignore`, `.dockerignore`: Files excluded from Git or the Docker image.
- `CONTRIBUTING.md`: Contribution guidelines; `LICENSE`: Project license.
- `.gitattributes`, `.gitleaksignore`: Git rules and secret-scanning configuration.
- `status-checkpoint-1.md`: Earlier project status notes.

### `src/api/` — Connects the Web Interface to the Application

- `main.py`: Creates the FastAPI application, configures CORS, middleware, and headers, and registers routers and static files.
- `schemas.py`: Defines accepted request and response data shapes.
- `deps.py`: Shared dependencies such as the current user.
- `errors.py`: Centralized error handling.
- `serve.py`: Server entry point inside the application image.
- `routers/auth.py`: Login endpoints.
- `routers/ask.py`: Questions, answers, and streamed responses.
- `routers/runs.py`: Maintenance workflows, safety acknowledgement, and approval.
- `routers/documents.py`: Lists tenant documents.
- `routers/ingest.py`: Requests corpus ingestion with the required role.
- `routers/usage.py`: Returns available usage and token summaries.
- `routers/health.py`: Service health checks.
- `static/index.html`, `app.js`, `style.css`: Browser page, behavior, and styling.

### `src/application/` — Use-Case Logic

- `answering.py`: Coordinates evidence-based responses, refusals, and citation validation.
- `retrieval.py`: Combines search results and applies relevance rules.
- `chunk.py`, `clean.py`, `ingest.py`: Clean, chunk, and prepare documents.
- `agents.py`, `orchestrator.py`: Specialist agents and workflow coordination.
- `tools.py`, `tool_schemas.py`: Allowed tools and input validation.
- `rules.py`: Deterministic revision, safety, and workflow-state rules.
- `safety_steps.py`: Extracts safety steps from documents.
- `auth.py`, `security.py`: Login rules and token validation.
- `redaction.py`: Redacts a limited set of data patterns before text is sent to a model provider.
- `embedding.py`, `embedding_guard.py`: Wraps embeddings and verifies configuration compatibility.
- `llm_router.py`: Selects and retries model providers.
- `ports.py`: Interfaces describing the external capabilities required by the application.

### `src/domain/` — Domain Types

- `documents.py`: Document and document-section types.
- `rag.py`: Chunks, evidence, and retrieval result types.
- `llm.py`: Model messages, requests, and errors.
- `workflow.py`: Workflow states, users, roles, and maintenance data types.

### `src/infrastructure/` — Databases and External Services

- `config.py`: Reads and validates environment settings.
- `database.py`: Opens PostgreSQL connections with tenant context.
- `repository.py`, `workflow_repository.py`: Store and retrieve documents, workflow data, and audit records.
- `chunk_search.py`: Runs searches in PostgreSQL.
- `extractors.py`: Reads PDF and Markdown files.
- `ingest_cli.py`: Imports, chunks, embeds, and stores the corpus.
- `migrate.py`: Applies SQL migrations; `seed_users.py` creates demo users.
- `embedding_registry.py`: Stores embedding-index compatibility information.
- `passwords.py`, `tokens.py`: Provide infrastructure for password storage and token validation.
- `providers/`: Model provider adapters; `factory.py` selects providers, `ollama_provider.py` connects to Ollama, `openai_compatible.py` connects to compatible providers, and `fake.py` supports tests.
- `llm_smoke.py`: Runs a basic model-provider connectivity check.

### Evaluation, Tests, and Database

- `src/eval/questions.py`: Loads and validates the reference question set.
- `src/eval/run.py`: Runs evaluation against the database and index and writes a JSON report; `--with-answers` also requests model completions.
- `src/eval/calibrate.py`: Helps calibrate the retrieval threshold.
- `eval/golden.jsonl`: Expected questions, answers or facts, and evidence references for each case.
- `eval/baseline.json`: The measured baseline, including failures.
- `migrations/001_schema.sql` through `005_asks_and_usage.sql`: Create tables, RLS policies, indexes, workflow data, asks, and usage records.
- `tests/unit/`, `tests/api/`, `tests/integration/`, `tests/security/`: Test individual logic, endpoints, component interactions, and security controls.

## Main Outputs

| Operation | Output |
| --- | --- |
| A question | An answer or refusal, with citations to retrieved evidence |
| Corpus ingestion | Cleaned and chunked documents, embeddings, and safety steps in PostgreSQL |
| Maintenance workflow | A traced run, safety acknowledgements, and a draft work order awaiting supervisor review |
| Evaluation | A JSON report with retrieval, evidence coverage, and refusal results for each case |

Some folders may contain local files or generated caches. This map describes
the intended source files. `__pycache__`, `.pytest_cache`, and `.ruff_cache`
are not project source code and do not need manual edits.
