## Domain Copilot - Industrial Maintenance

# 

# An agentic RAG platform for field maintenance.

# 



# ## Assigned variant

# 

# - Domain: D5 (Industrial - field maintenance)

# - Twist: T0 (Multi-tenancy)

# -Source: derived from the National ID, as the brief allows
 Domain rule: last two digits mod 7 = 5, so D5
- Twist rule: sum of all digits mod 8 = 0, so T0

# 

## Quick start

1. Copy .env.example to .env and fill in the database passwords and `AUTH_SECRET` (at least 32 characters). Use letters and digits only for the database passwords.
2. Run: docker compose up --build
3. Open http://localhost:8000/health or browse the interactive API docs at http://localhost:8000/docs.

Two database users are used. The admin user (POSTGRES_USER) only runs the migrations and can bypass Row-Level Security. The application user (copilot_app, password APP_DB_PASSWORD) is what the API uses, and Row-Level Security always applies to it.

## Status

# 

# Work in progress. Quick start, environment variables and the demo path will be added as features land.

## Switching LLM providers

Chat and embeddings are chosen by configuration only. `LLM_CHAIN` is an ordered,
comma separated list of chat providers: the first one that answers is used, and
the rest are fallbacks. Allowed names are `groq`, `gemini`, `ollama` and `fake`.
The Python configuration default is `groq,gemini,ollama`; Docker defaults to
`ollama` so the bundled local setup works without hosted provider keys.
Embeddings use exactly one provider, chosen by `EMBEDDING_PROVIDER`.

| Variable | Meaning |
| --- | --- |
| `LLM_CHAIN` | Ordered chat providers, comma separated (Docker default `ollama`) |
| `GROQ_API_KEY` | Groq API key (empty until you add one) |
| `GROQ_BASE_URL` | Groq chat base URL (default `https://api.groq.com/openai/v1`) |
| `GROQ_MODEL` | Groq chat model; no default, set it yourself |
| `GROQ_STREAM_USAGE` | `true`/`false`; request stream usage (empty means true) |
| `GEMINI_API_KEY` | Google Gemini API key (empty until you add one) |
| `GEMINI_BASE_URL` | Gemini chat base URL, OpenAI compatible (default `https://generativelanguage.googleapis.com/v1beta/openai`) |
| `GEMINI_MODEL` | Gemini chat model; no default, set it yourself |
| `GEMINI_STREAM_USAGE` | `true`/`false`; request stream usage (empty means true) |
| `OLLAMA_BASE_URL` | Local Ollama base URL (default `http://localhost:11434`) |
| `OLLAMA_CHAT_MODEL` | Ollama chat model; required when `ollama` is in `LLM_CHAIN` |
| `EMBEDDING_PROVIDER` | One of `ollama`, `gemini`, `fake` (default `ollama`) |
| `EMBEDDING_MODEL` | Embedding model recorded on every chunk (default `nomic-embed-text`) |
| `EMBEDDING_DIMENSIONS` | Vector size of the embedding model (default `768`) |
| `LLM_TIMEOUT_SECONDS` | Timeout of one LLM HTTP request (default `180`; connect timeout is 5s) |
| `LLM_COOLDOWN_SECONDS` | Seconds a provider is skipped after quota/auth failure (default `60`) |
| `RETRIEVAL_MIN_SIMILARITY` | Minimum best dense similarity before the model is asked (default `0.55`, to be calibrated) |

Free keys for the hosted providers: create one in the Groq console
(https://console.groq.com) or in Google AI Studio (https://aistudio.google.com).
Free tiers and the exact model names change often, so check the provider page;
no specific limits are promised here.

### Fallback rules

| Error (provider answer) | Behaviour |
| --- | --- |
| `ProviderUnavailableError` (network failure, timeout, 5xx) | Falls back to the next provider |
| `QuotaExceededError` (429 or exhausted free tier) | Falls back; the provider is skipped for `LLM_COOLDOWN_SECONDS` |
| `ProviderAuthError` (401/403) | Falls back with the same cooldown |
| `ProviderResponseError` (malformed answer) | Falls back |
| `ProviderRequestError` (our request is wrong) | Does NOT fall back: the next provider would fail the same way |

If every provider is in cooldown they are all tried anyway. If all of them fail,
`AllProvidersFailedError` is raised and lists every single failure.

Streaming falls back only before the first token. A stream that fails after the
first token raises the error instead of splicing two answers together.

### Embeddings

The whole index uses one fixed embedding model, recorded in the database the
first time ingestion runs. A different model name or size makes ingestion exit
with code 2 before anything is written. Embeddings never fall back: there is no
second embedder. To change the embedding model the index must be rebuilt from
scratch. For `EMBEDDING_PROVIDER=gemini` set `EMBEDDING_MODEL` and
`EMBEDDING_DIMENSIONS` explicitly.

### Running without any key

Use `LLM_CHAIN=ollama` (needs Ollama running, the embedding model pulled, and a
pulled chat model that supports tool calling) or `LLM_CHAIN=fake` (deterministic,
offline, for tests and demos).

Local models are slower and weaker than the hosted ones, and tool-calling support
depends on the pulled model. When a provider does not report token usage, the
count is ESTIMATED (about 4 characters per token) and flagged `estimated`.

## API routes

FastAPI routes are split into modules under `src/api/routers` and included by
`src/api/main.py`:

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Liveness check |
| `GET` | `/ready` | Database readiness check |
| `POST` | `/auth/login` | Log in and receive a bearer token |
| `GET` | `/me` | Return the authenticated user's profile |
| `POST` | `/ask` | Get a tenant-scoped, document-grounded answer |

`/ask` takes `{"question":"..."}` and requires `Authorization: Bearer <token>`.
The tenant comes from the verified token. Workflow request schemas exist, but
workflow HTTP routes have not been implemented yet.

### Smoke tool

The smoke tool tests the provider chain directly. It never loads `.env` itself,
so load it into the shell first (bash):

```
set -a; source .env; set +a
python -m src.infrastructure.llm_smoke --provider groq
```

```
python -m src.infrastructure.llm_smoke --stream        # stream one answer
python -m src.infrastructure.llm_smoke --tools         # ask for one tool call
python -m src.infrastructure.llm_smoke --embed         # one embedding call, no database
python -m src.infrastructure.llm_smoke --provider fake --stream
python -m src.infrastructure.llm_smoke --fail groq     # fake quota error, prove fallback
python -m src.infrastructure.llm_smoke --help
```

`--provider NAME` makes one provider the only chain member. `--fail NAME`
replaces that provider with an offline fake that raises `QuotaExceededError`
once, so the fallback can be seen without a real failure. Exit codes: 0 on
success, 2 on a configuration error, 1 when every provider failed.

Known limits: the cooldown lives inside one process and is not shared between
workers, and the token estimate is approximate.

## Asking a question

`python -m src.cli.ask --tenant tenant-alpha "question"` embeds the question
with the index embedding model, runs the hybrid search (dense plus keyword,
fused with Reciprocal Rank Fusion) and asks the chat fallback chain to answer
only from the retrieved chunks. It prints the answer, the citations
(`[chunk:ID]`), the refusal reason when it refuses, and the token usage. It
refuses without calling the model when nothing is retrieved, or when the best
dense similarity is below `RETRIEVAL_MIN_SIMILARITY`. Exit code is 2 on a
configuration error. Load `.env` into the shell first, as with the smoke tool.

```
python -m src.cli.ask --tenant tenant-alpha "what is the relief set point of the ALPHA-HP-200?"
python -m src.eval.calibrate   # best dense scores and a suggested threshold
```

`python -m src.eval.calibrate` runs a list of in-corpus and out-of-corpus
questions (from `eval/golden.jsonl` once it exists, otherwise a small built-in
list), prints the similarity of the best hit for each, and suggests a threshold:
the midpoint between the lowest in-corpus best score and the highest
out-of-corpus best score, with a warning when the two ranges overlap. It changes
no setting.


