# Architecture — Domain Copilot

**Diagram sources:** All diagrams in this file are **Mermaid** text committed in-repo (render in GitHub, VS Code, or Mermaid Live). Related workflow diagram: `docs/AGENTIC-WORKFLOW.md`. Architecture decision records: `docs/adr/0001`–`0004`.

**Code layering rule (enforced):** `src/domain` and `src/application` import only the Python standard library and each other—not FastAPI, psycopg, or httpx (`tests/unit/test_architecture.py`).

---

## C4 Level 1 — System context

```mermaid
C4Context
    title System Context — Domain Copilot

    Person(tech, "Field Technician", "Asks questions, runs maintenance workflow")
    Person(sup, "Supervisor", "Reviews drafts, ingests corpus")
    System(copilot, "Domain Copilot", "Multi-tenant RAG + agentic maintenance workflow")
    System_Ext(llm, "LLM Providers", "Groq, Gemini, Ollama")
    System_Ext(db, "PostgreSQL", "pgvector, RLS, workflow state")

    Rel(tech, copilot, "HTTPS", "Browser UI / API")
    Rel(sup, copilot, "HTTPS", "Review & ingest")
    Rel(copilot, llm, "HTTPS", "Chat + embeddings (redacted)")
    Rel(copilot, db, "SQL", "Tenant-scoped data")
```

| Element | Description |
| --- | --- |
| **Domain Copilot** | FastAPI application + static UI; enforces auth, retrieval, safety gates, audit |
| **Technicians / Supervisors** | Human operators per manufacturing tenant |
| **LLM providers** | External inference; see trust boundary §5 |
| **PostgreSQL** | Single data store for tenants, manuals, vectors, runs |

---

## C4 Level 2 — Containers

```mermaid
C4Container
    title Containers — MVP deployment (Docker Compose)

    Person(user, "User")

    Container_Boundary(copilot, "Domain Copilot") {
        Container(web, "Static UI", "HTML/CSS/JS", "Tabs: Ask, Workflow, Runs, Documents")
        Container(api, "API Service", "Python/FastAPI", "REST + SSE")
    }

    ContainerDb(pg, "PostgreSQL", "pg16 + pgvector", "RLS, chunks, runs")
    Container_Ext(ollama, "Ollama (host)", "Optional local LLM")

    Rel(user, web, "Uses")
    Rel(web, api, "JSON/SSE", "Bearer token")
    Rel(api, pg, "psycopg")
    Rel(api, ollama, "HTTP", "Default embed/chat")
```

| Container | Technology | Responsibilities |
| --- | --- | --- |
| **Static UI** | `src/api/static/*` | Login, ask, workflow SSE client, supervisor queue |
| **API service** | `src/api/main.py`, routers | Auth, ask, runs, ingest, health, usage |
| **PostgreSQL** | Migrations `001`–`005` | Tenants, documents, chunks, users, runs, ask_log |
| **Ollama (optional)** | Host process | Default embedding + chat when keys absent |

One-shot Compose jobs: **migrate** (admin user), **seed-users** (demo accounts).

---

## C4 Level 3 — Components (API application)

```mermaid
C4Component
    title Components — inside API service

    Container_Boundary(api, "FastAPI Application") {
        Component(routers, "HTTP Routers", "FastAPI", "auth, ask, runs, ingest, ...")
        Component(app_layer, "Application layer", "Python", "answering, retrieval, orchestrator, agents, rules")
        Component(domain, "Domain model", "Python", "workflow, rag, llm types")
        Component(infra, "Infrastructure", "Python", "repos, chunk_search, providers, config")
    }

    ComponentDb(pg, "PostgreSQL")

    Rel(routers, app_layer, "Calls")
    Rel(app_layer, domain, "Uses types")
    Rel(app_layer, infra, "Via ports/adapters")
    Rel(infra, pg, "SQL")
```

| Component | Key modules |
| --- | --- |
| **Routers** | `src/api/routers/*.py`, `deps.py`, `schemas.py` |
| **Application** | `answering.py`, `retrieval.py`, `orchestrator.py`, `agents.py`, `tools.py`, `rules.py`, `redaction.py`, `llm_router.py` |
| **Domain** | `documents.py`, `rag.py`, `llm.py`, `workflow.py` |
| **Infrastructure** | `database.py`, `repository.py`, `workflow_repository.py`, `chunk_search.py`, `providers/*`, `config.py` |

**Dependency direction:** `api` → `application` → `domain`; `application` defines **ports** (`ports.py`); **infrastructure** implements them. Routers wire concrete infrastructure (pragmatic MVP coupling in router factories).

---

## Layer dependency diagram

```mermaid
flowchart TB
    subgraph presentation [Presentation]
        API[src/api]
        CLI[src/cli]
        STATIC[static UI]
    end

    subgraph application [Application]
        APP[src/application]
    end

    subgraph domain [Domain]
        DOM[src/domain]
    end

    subgraph infrastructure [Infrastructure]
        INF[src/infrastructure]
    end

    subgraph eval [Evaluation]
        EVAL[src/eval]
    end

    API --> APP
    API --> INF
    CLI --> APP
    CLI --> INF
    STATIC --> API
    APP --> DOM
    INF --> APP
    INF --> DOM
    EVAL --> APP
    EVAL --> INF

    style DOM fill:#e8f4e8
    style APP fill:#e8eef4
```

| Rule | Enforcement |
| --- | --- |
| Domain has no outward deps | Stdlib only |
| Application has no FastAPI/DB/HTTP | AST import test |
| Infrastructure implements ports | `PostgresChunkSearch`, `PgRunRepository`, providers |

---

## Sequence — full agentic workflow (SSE + approval gate)

Includes: symptom submission, safety acknowledgement gate, draft generation with streaming tokens, supervisor approval.

```mermaid
sequenceDiagram
    autonumber
    actor Tech as Technician
    actor Sup as Supervisor
    participant UI as Web UI
    participant API as runs router
    participant Orch as WorkflowOrchestrator
    participant Match as SymptomMatcher
    participant Plan as DiagnosticSafetyPlanner
    participant Rules as check_safety_gate
    participant Gen as WorkOrderGenerator
    participant DB as PostgreSQL (RLS)
    participant LLM as LLM chain

    Tech->>UI: Enter symptoms + revision
    UI->>API: POST /runs (Bearer)
    API->>Orch: start_run()
    Orch->>DB: INSERT run (running)
    Orch->>Match: match(symptoms)
    Match->>DB: hybrid search chunks
    Match->>LLM: optional completion
    Match-->>Orch: EquipmentMatch + evidence
    Orch->>Plan: plan(match, revision)
    Plan->>DB: load safety_prerequisites
    Plan-->>Orch: required step IDs
    Orch->>DB: UPDATE run awaiting_acknowledgement
    loop SSE progress
        Orch-->>API: event JSON
        API-->>UI: data: {...}
    end

    Tech->>UI: Acknowledge safety checklist
    UI->>API: POST /runs/{id}/acknowledge
    API->>Orch: acknowledge(step_ids)
    Orch->>DB: audit acknowledge
    Orch->>Rules: all required IDs present?
    alt gate fails
        Rules-->>Orch: GateNotSatisfied
        Orch-->>UI: error / refused generation
    else gate passes
        Orch->>Gen: generate draft
        loop SSE tokens
            Gen->>LLM: stream completion
            LLM-->>Gen: token deltas
            Gen-->>API: progress token events
            API-->>UI: SSE
        end
        Gen-->>Orch: WorkOrder JSON + prerequisites attached
        Orch->>DB: INSERT work_order draft, pending_approval
        Orch-->>UI: done event
    end

    Sup->>UI: Open review queue
    UI->>API: GET /runs?status=pending_approval
    API->>DB: SELECT runs (supervisor, tenant)
    Sup->>UI: Approve / reject / edit
    UI->>API: POST /runs/{id}/approval
    API->>Orch: approval(decision)
    Orch->>Rules: re-check safety if needed
    Orch->>DB: UPDATE work_order + run + audit_log
    Orch-->>UI: final status
```

**Streaming elsewhere:** `POST /ask/stream` follows retrieve → refusal gate → LLM token stream → citation validation (`src/api/routers/ask.py`, `stream_answer_question`).

**Cancellation:** `POST /runs/{id}/cancel` sets cooperative cancel flag checked at orchestrator phase boundaries (in-flight HTTP to LLM may continue until timeout — see `docs/SECURITY.md`).

---

## Data-flow diagram — trust boundaries and LLM visibility

```mermaid
flowchart LR
    subgraph TB1 [Trust boundary: Client]
        USER[User browser / CLI]
    end

    subgraph TB2 [Trust boundary: Domain Copilot VPC / host]
        API[FastAPI]
        RED[redaction.py]
        RET[retrieval + answering]
        ORC[orchestrator]
        DB[(PostgreSQL RLS)]
    end

    subgraph TB3 [Trust boundary: Third party]
        PROV[LLM / embedding provider]
    end

    USER -->|HTTPS JWT| API
    API --> RET
    RET --> DB
    ORC --> DB
    API --> ORC
    RET --> RED
    ORC --> RED
    RED -->|Redacted prompts excerpts| PROV
    PROV -->|Completions no tenant DB access| RED
    RED --> RET
    RED --> ORC

    API -->|Stores full question/answer| DB
```

### What the LLM provider sees

| Data | Sent to provider? | Notes |
| --- | --- | --- |
| Raw password / bearer token | **Never** | Auth stays in API |
| Full tenant database | **Never** | Only retrieved chunk text in prompts |
| User question / symptoms | **Yes** | After optional redaction |
| Retrieved manual excerpts | **Yes** | Untrusted-evidence framing in answer prompt |
| Safety step text (workflow) | **Yes** | When generating WO JSON |
| `tenant_id`, internal user IDs | **Typically no** | Not intentionally included in prompts |
| Other tenants’ manuals | **Must not** | Prevented by RLS + tenant-scoped retrieval |
| API keys for provider | **Outbound only** | Read in `config.py` only |

Redaction masks email-like, phone-like, and 14-digit Egyptian national ID patterns before provider calls; originals remain in PostgreSQL (`docs/SECURITY.md`).

---

## Entity-relationship diagram (logical)

```mermaid
erDiagram
    tenants ||--o{ users : has
    tenants ||--o{ documents : owns
    tenants ||--o{ chunks : owns
    tenants ||--o{ safety_prerequisites : owns
    tenants ||--o{ runs : owns
    tenants ||--o{ ask_log : owns
    tenants ||--o{ audit_log : owns

    documents ||--o{ chunks : contains
    documents ||--o{ safety_prerequisites : defines

    users ||--o{ runs : creates
    users ||--o{ ask_log : asks
    users ||--o{ audit_log : acts

    runs ||--o{ run_steps : traces
    runs ||--o{ work_orders : produces

    tenants {
        text id PK
        text name
    }

    users {
        bigint id PK
        text tenant_id FK
        text username
        text role
        text password_hash
        boolean active
    }

    documents {
        bigint id PK
        text tenant_id FK
        text doc_id
        text revision
        text content_sha256
        text ingest_status
    }

    chunks {
        bigint id PK
        text tenant_id FK
        bigint document_id FK
        text section
        vector embedding
        tsvector tsv
    }

    safety_prerequisites {
        bigint id PK
        bigint document_id FK
        int step_no
        text step_text
    }

    embedding_index_meta {
        smallint id PK
        text model
        int dimensions
    }

    runs {
        uuid id PK
        text tenant_id FK
        bigint user_id FK
        text status
        int total_tokens
    }

    run_steps {
        bigint id PK
        uuid run_id FK
        text agent
        bigint[] evidence_ids
    }

    work_orders {
        uuid id PK
        uuid run_id FK
        int version
        jsonb content
        text status
    }

    audit_log {
        bigint id PK
        text action
        jsonb detail
    }

    ask_log {
        bigint id PK
        text question
        text answer_text
        boolean refused
        jsonb citations
    }
```

**Global table:** `embedding_index_meta` has no `tenant_id` (single index metadata row for the deployment).

**RLS:** All tenant-scoped tables use policy `tenant_id = current_setting('app.tenant_id', true)`.

---

## Grounded Q&A path (reference sequence)

```mermaid
sequenceDiagram
    participant C as Client
    participant A as ask router
    participant Q as answering.py
    participant R as retrieval.py
    participant S as PostgresChunkSearch
    participant E as Embedder
    participant L as LLM chain

    C->>A: POST /ask or /ask/stream
    A->>Q: answer_question / stream
    Q->>R: retrieve()
    R->>E: embed query
    R->>S: dense + keyword search
    S-->>R: chunks
    alt refusal gate
        Q-->>C: refused (no LLM call)
    else evidence OK
        Q->>L: completion / stream
        L-->>Q: text + usage
        Q->>Q: validate citations + canary
        Q-->>C: answer + citations
    end
```

---

## Architecture Decision Records (≥4)

Instructor brief §4 asks for ADRs on chunking/retrieval, orchestration pattern, vector store, and the twist. Mapping:

| Brief topic | Committed ADR / doc |
| --- | --- |
| Vector store | ADR 0001 (PostgreSQL + pgvector) |
| Chunking / retrieval | ADR 0003 |
| Twist (T0 multi-tenancy) | ADR 0002 (RLS) |
| Orchestration pattern | **No standalone ADR** — resumable **state machine** is justified in `docs/SYSTEM-DESIGN.md` (SD-6) and `docs/AGENTIC-WORKFLOW.md` |
| LLM / providers | ADR 0004 (also satisfies provider-abstraction requirement) |

| ADR | Title | Status | Link |
| --- | --- | --- | --- |
| 0001 | PostgreSQL with pgvector as single data store | Accepted | [docs/adr/0001-postgresql-with-pgvector.md](adr/0001-postgresql-with-pgvector.md) |
| 0002 | Tenant isolation with Row-Level Security | Accepted | [docs/adr/0002-tenant-isolation-with-row-level-security.md](adr/0002-tenant-isolation-with-row-level-security.md) |
| 0003 | Chunking by section (Markdown + PDF) | Accepted | [docs/adr/0003-chunking-by-section.md](adr/0003-chunking-by-section.md) |
| 0004 | LLM provider abstraction, fallback chain, fixed embeddings | Accepted | [docs/adr/0004-llm-provider-abstraction.md](adr/0004-llm-provider-abstraction.md) |

Additional narrative decisions (SD-5 through SD-10) are in `docs/SYSTEM-DESIGN.md`. A future **ADR 0005 — workflow state machine** would close the orchestration ADR gap explicitly.

---

## Technology summary

| Concern | Choice |
| --- | --- |
| Language | Python 3.12 |
| API framework | FastAPI |
| DB driver | psycopg 3 |
| Vector search | pgvector HNSW + GIN tsvector |
| Auth | HMAC-SHA256 bearer tokens, scrypt passwords |
| UI | Static files, no bundler |
| Testing | pytest, ruff, pip-audit, gitleaks (CI) |

---

## Related documentation

| Document | Purpose |
| --- | --- |
| [BRD.md](BRD.md) | Business requirements and traceability |
| [SYSTEM-DESIGN.md](SYSTEM-DESIGN.md) | Target vs MVP gaps and design decisions |
| [AGENTIC-WORKFLOW.md](AGENTIC-WORKFLOW.md) | Workflow phases and agent contracts |
| [SECURITY.md](SECURITY.md) | Controls and gaps |
| [EVALUATION.md](EVALUATION.md) | Golden set and baseline metrics |

---

*End of Architecture document*
