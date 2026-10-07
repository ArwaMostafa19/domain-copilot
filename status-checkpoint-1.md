CHECKPOINT 1 - retrieval, answers with citations, refusal

Created:
- src/domain/rag.py (Evidence, Citation, Answer, RefusalReason)
- src/application/retrieval.py (ChunkSearch port, rrf_fuse, keyword_terms,
  wants_superseded_revisions, collapse_duplicates, retrieve)
- src/application/answering.py (refusal gate, citation check, prompt loader)
- src/infrastructure/chunk_search.py (PostgresChunkSearch)
- prompts/answer_system.md (canary CANARY-7f3a9c, injection marker rules)
- src/cli/ask.py, src/eval/questions.py, src/eval/calibrate.py
- tests/unit/test_retrieval.py, tests/unit/test_answering.py,
  tests/unit/test_ask_cli.py, tests/integration/test_chunk_search.py

Modified:
- src/infrastructure/config.py (Settings.retrieval_min_similarity,
  load_settings_from_environ)
- tests/fakes.py (added FakeChunkSearch)
- README.md, .env.example (RETRIEVAL_MIN_SIMILARITY, ask CLI, calibrate)

Verification (all run):
- python -m ruff check . --no-cache: clean.
- python -m pytest tests --ignore=tests/unit/test_health.py -q (no DB env):
  254 passed, 23 skipped.
- Integration against a TEMPORARY pgvector/pgvector:pg16 container (port
  55432, all migrations applied, container and volume removed afterwards):
  23 passed, including the 4 new chunk_search tests (not skipped).
- python -m src.infrastructure.ingest_cli --dry-run corpus: tenant-alpha
  237 chunks / 28 steps, tenant-beta 240 chunks / 29 steps, 3 chunks over
  1800 chars, 0 failed (unchanged).
- Import scan of src/domain and src/application: stdlib and src.* only.
- Key-literal scan (gsk_/AIza/sk-): no real-looking literals.

Deviations / assumptions:
- Status file is .md, per the user instruction; the brief asked for .txt.
- retrieve() takes settings but does not use it (brief signature); typed via
  a RetrievalSettings Protocol.
- Added load_settings_from_environ in config.py so CLI/eval never name
  os.environ, avoiding an edit to test_secrets_architecture's allow-list.
- keyword_terms strips trailing hyphens and drops words under 3 chars so a
  tsquery is always syntactically valid. Empty terms return no rows.
- calibrate keeps its questions in src/eval/questions.py for unit testing.
- ask.py and calibrate.py print, so the ingest_cli docstring claim that it is
  the only printing module is now stale.
- ask.py catches LLMError and returns exit code 1 when the providers fail,
  instead of leaking a traceback. Tested by tests/unit/test_ask_cli.py.

Not verified:
- ask.py end-to-end against a real index and provider (needs Ollama or a
  hosted key). Only --help and the exit-2 configuration-error path were run.
- No git command was run; all changes are uncommitted.