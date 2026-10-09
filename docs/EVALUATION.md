# Evaluation

## Golden set

`eval/golden.jsonl` contains 25 fixed questions with reference answers, exact
document and section references, and key facts used by the harness. Six cases
are adversarial: an out-of-corpus value, an ambiguous symptom, three prompt
injections (one direct and two embedded in retrieved documents), and a
conflicting-revision question. The loader checks the minimum case counts and
required injection categories before connecting to the index.

The corpus is the source of truth for the expected answers. Update a reference
when a controlled document changes, and keep the adversarial cases when adding
ordinary questions. The fixture does not edit or generate training material.

## Run the harness

The database must be running, migrations applied, the corpus ingested, and the
configured embedding index available. From the repository root, start the app
services and run the evaluation in the API container:

```powershell
docker compose up -d --build
docker compose exec api python -m src.eval.run --with-answers --output /app/eval/baseline.json
```

To score only the six adversarial cases with a local model, add
`--only-adversarial` and use a separate output path. The full golden set is
still validated before the subset is selected.

`--with-answers` calls the configured chat provider for each case. This needs
the same provider configuration as `/ask`. To measure search and the
pre-generation refusal gate without chat completions, omit that flag:

```powershell
docker compose exec api python -m src.eval.run --output /app/eval/baseline.json
```

When the corpus has not yet been loaded into the database, ingest it once before
the evaluation:

```powershell
docker compose run --rm api python -m src.infrastructure.ingest_cli corpus
```

The `eval` directory is mounted into the API container so the golden set is
available and the JSON report is written back to the project. The report stores
the configuration, aggregate counts and per-case outcomes. Do not replace a
previous report until its run configuration and results have been reviewed.

## Metrics

- **Retrieval hit-rate@6:** a case is a hit when every expected `(doc_id,
  section)` is present in the top six retrieved chunks. Cases without a
  reference source (for example, an out-of-corpus question) are excluded.
- **Evidence groundedness:** the share of expected key fact strings found in
  the retrieved chunks. This is a deterministic evidence-coverage measure; it
  does not claim that generated prose is semantically supported.
- **Pre-generation refusal-gate accuracy and recall:** compares the real
  no-evidence/low-similarity gate with each case's expected refusal label,
  before the language model is called.
- **Answer groundedness** (`--with-answers`): a case passes when the response
  is not refused, includes every expected fact, cites at least one expected
  source, and every cited chunk was retrieved. Exact phrase matching is used,
  so a semantically correct paraphrase can be scored as a miss.
- **End-to-end refusal correctness** (`--with-answers`): compares the
  application's refusal result with the expected refusal label.

The report also prints each case so misses remain visible. Aggregate numbers
are not a substitute for reviewing weak and adversarial cases.

## Baseline

The initial retrieval-only baseline was measured on 2026-10-08 against the
existing index with `nomic-embed-text` and `RETRIEVAL_MIN_SIMILARITY=0.55`:

| Metric | Result |
| --- | ---: |
| Cases / adversarial cases | 25 / 6 |
| Retrieval hit-rate@6 | 20/23 (87.0%) |
| Evidence groundedness | 38/38 facts (100.0%) |
| Pre-generation refusal-gate accuracy | 23/25 (92.0%) |
| Pre-generation refusal recall | 0/2 (0.0%) |

The misses are retained in `eval/baseline.json`. Rev A retrieval, the Beta
current relief-setting source, and the two-source revision comparison missed
their exact expected chunk references. Both expected-refusal cases retrieved
evidence above the configured threshold, so the pre-generation gate did not
refuse either one. This shows that the current similarity threshold alone does
not reliably identify unsupported or malicious requests. The Beta crane
ground-truth phrase was normalized to the source wording ("six monthly") and
the baseline was rerun after that correction.

This is a retrieval-only baseline; it does not measure generated answer quality.
The local answer run was attempted with `llama3.2:3b`, but Ollama's `/api/chat`
timed out even on a short local request, so no answer-groundedness or
end-to-end refusal numbers are claimed. Once local chat is responsive, run with
`--with-answers` (and optionally `--only-adversarial`) to record those metrics.
