# Common Trainee Mistakes

Use this one-page teaching note. Ask trainees to point to repository evidence, then correct the model with a concrete boundary or test.

## 1. Confusing OWASP LLM Top 10 with OWASP Web Top 10
**Mistake:** Treating them as one checklist or assuming web controls cover LLM risks.
**How it appears:** A trainee points to parameterized SQL and concludes prompt injection or misinformation is solved.
**Correction:** The lists overlap but address different failures. Parameterized SQL helps SQL injection; it does not stop a manual's embedded instruction from influencing a model. Map risks and controls separately. Compare the deck taxonomy with `docs/SECURITY.md`.

## 2. Assuming the model must protect everything
**Mistake:** Expecting a system prompt to reliably stop disclosure, tool misuse, unsafe work orders or bad citations.
**How it appears:** The trainee says the workflow is safe because the model was told not to skip LOTO.
**Correction:** Prompts guide behavior; code and data policies enforce invariants. Inspect RLS migrations, tool allow-lists, schema checks, citation validation, `check_safety_gate` and supervisor approval. Try the missing-ack test instead of trusting wording.

## 3. Assuming every vulnerability has already been fixed here
**Mistake:** Treating a test, security document or successful demo as proof all attacks are handled.
**How it appears:** Claiming indirect-injection resistance because a canary check exists, despite no successful answer-level evaluation.
**Correction:** Separate implemented control, test coverage, measured outcome and residual risk. Current refusal recall is 0/2; answer-level injection resistance is unmeasured. Say exactly what is known and open.

## 4. Treating similarity or citation as proof of correctness
**Mistake:** Assuming high vector score means the source matches exact equipment/revision or all claims are supported.
**How it appears:** Accepting HP-200 evidence for HP-210, or treating 38/38 fact coverage as proof generated answers are safe.
**Correction:** Check tenant, equipment, status/revision, exact chunk and each claim. Similarity is a ranking signal. Baseline has 38/38 expected strings but only 20/23 exact evidence hits and no generated answers.

## 5. Confusing visible UI with server enforcement
**Mistake:** Believing a hidden button, checkbox or tenant selector enforces authorization/safety.
**How it appears:** Saying technicians cannot approve because the tab is hidden, or assuming a UI checkbox alone blocks generation.
**Correction:** Exercise API/server checks. Approval checks role; orchestrator recomputes required safety IDs and blocks generation when missing acknowledgements. UI is usability, not the security boundary.
