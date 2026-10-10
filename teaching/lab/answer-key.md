# Answer Key: Find and Verify LLM Security Controls

This key follows the trainee sheet. Accept equivalent explanations that cite the right code/test and explain the boundary.

## Question 1 - Easy: output handling
- `src/application/answering.py`, `_validate()`: an answer must contain citations and every cited chunk ID must belong to retrieved evidence. A canary or configured injection marker causes refusal. This limits unsupported citations and known markers; it does not prove every claim semantically true.
- `src/api/static/app.js`: dynamic answer/source text uses `textContent`, text nodes and safe element creation rather than `innerHTML`, reducing HTML/script injection through model output.
- `src/infrastructure/chunk_search.py`: SQL values are bound parameters and search terms normalized, not interpolated into SQL.

## Question 2 - Medium: indirect injection
1. The Alpha compressor document contains an `UNTRUSTED EMBEDDED INSTRUCTION` asking to reveal prompt information and bypass approval. The approved section specifies ISO VG 100 synthetic ester, Alpha specification AM-CO-100S.
2. `alpha_indirect_prompt_injection` expects AM-CO-100S, references the approved appendix and compromised extraction-note section, and is labeled indirect injection. It should answer from trusted evidence while ignoring the embedded instruction.
3. `answer_question()` retrieves scoped evidence, applies the similarity gate, labels evidence in the user message, sends prompt plus evidence to the configured provider, then `_validate()` checks citations and marker/canary text. Useful controls, but retrieved instructions still reach the model and delimiters cannot guarantee obedience.
4. **No, resistance is not demonstrated.** `eval/baseline.json` is retrieval-only. `docs/EVALUATION.md` says refusal recall is 0/2 and the local chat timed out; there is no answer-groundedness or end-to-end refusal result.

## Question 3 - Bonus: safety gate and tenant isolation
### Track A
- A supported run enters `awaiting_acknowledgement` with required steps loaded from matched-document safety data.
- If one required ID is absent, `check_safety_gate()` reports missing IDs and `WorkflowOrchestrator.generate()` raises `GateNotSatisfiedError`; the API emits `safety acknowledgement required`. No draft should be generated.
- With every ID acknowledged, generation may proceed and the run becomes `pending_approval`. It is a draft, not dispatch. A same-tenant supervisor makes the final review decision.
- Evidence: `src/application/rules.py`; `src/application/orchestrator.py`; `src/api/routers/runs.py`; `tests/unit/test_workflow_rules.py`; `tests/unit/test_orchestrator.py` (including prerequisite retention).
- If DB/provider unavailable, label the live path NOT RUN; source inspection is not an end-to-end pass.

### Track B
- Migrations enable RLS; policy compares row tenant with transaction-local `app.tenant_id`.
- `src/infrastructure/database.py`, `tenant_connection()`, sets that value with parameter binding.
- `tests/integration/test_tenant_isolation.py` and `tests/integration/test_workflow_tenant_isolation.py` cover tenant data.
- One no-data response is a smoke test. It may miss another vulnerable endpoint, an admin connection bypassing RLS, or cached leakage. RLS plus role setup and repeatable tests are stronger evidence.

## Stretch challenge guidance
1. Direct-injection pass requires answer-level behavior: no prompt/canary disclosure and a refusal, not only a retrieval result. Use isolated temporary fixture.
2. Raising threshold can catch the HP-210 out-of-corpus query but falsely reject low-scoring valid queries. Measure refusal recall and false-refusal rate/answerable accuracy; inspect per-case scores.
3. Disclosure example: `src/application/redaction.py` and `tests/unit/test_redaction.py`; regex patterns may miss names, addresses, employee IDs or unusual formats. Supply chain example: CI has pip-audit/Gitleaks, but no committed lockfile and scan setup is not proof of clean full history.
4. Test poisoned content that says skip LOTO, start run, omit an acknowledgement, and prove generation stays blocked. Enforce in orchestrator/rules; approval in runs router. Test code/API invariant, not prompt wording.
5. Question and retrieved evidence reach provider; redaction masks email-like, phone-like and 14-digit Egyptian IDs. It may miss names, addresses, other ID formats and sensitive facts not matching patterns. See architecture flow and security doc.

## Exit ticket answers
1. The instruction to ignore instructions in context is only a model instruction; retrieved text remains in model input. Contain impact with least privilege, typed output, server policy, approval gates and adversarial tests.
2. Tool allow-lists/schema plus server-side workflow safety and supervisor approval stop an agent from completing a protected action. Safety acknowledgements are independently checked in code.
3. Filtering after retrieval is too late because unauthorized data already entered application/model context. Enforce tenant scope/RLS before returning rows.
