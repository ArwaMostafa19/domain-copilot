# Hands-on Lab: Find and Verify LLM Security Controls

## Lab details
- **Duration:** 20 minutes in the 90-minute class (the deck reserves 30 minutes for lab and debrief).
- **Mode:** Pairs.
- **Objective:** Trace three risks to controls and evidence in Domain Copilot.
- **Safety:** Use synthetic project data and local/demo accounts only. Do not enter real personal data or credentials; do not use production systems.

## Setup
1. Start local services using the README instructions.
2. Ensure the synthetic corpus is ingested; follow README or `docs/EVALUATION.md` if needed.
3. Sign in with a seeded technician account. Ask the operator for the demo password; do not retrieve secrets from Git.
4. Open `src/application/answering.py`, `src/application/tools.py`, `src/application/rules.py`, `migrations/002_chunks_and_safety.sql`, and `eval/golden.jsonl`.

**Expected setup:** health responds successfully, login works, and Ask Question and Workflow Run tabs appear. If an LLM provider is unavailable, continue with static inspection and label runtime checks as NOT RUN.

## Question 1 - Easy (10 points): trace an output-handling defense
Find one place where a model answer is prevented from becoming an unsafe UI/API result.
1. Locate answer validation and identify what makes a citation acceptable.
2. Locate how dynamic text is inserted into the browser UI.
3. In one or two sentences, explain the risk each control reduces.

**Expected output:** Name files/functions/elements. Example: `answering.py` checks cited chunk IDs against retrieved evidence; `app.js` uses text nodes/`textContent`, not raw HTML.

## Question 2 - Medium (20 points): trace indirect prompt injection
Use the Alpha compressor case.
1. Find the compromised instruction-like text and legitimate lubricant specification in `corpus/tenant-alpha/air-compressor-preventive-maintenance.md`.
2. Find `alpha_indirect_prompt_injection` in `eval/golden.jsonl`; record expected answer, fact and evidence sections.
3. Trace retrieval -> provider prompt -> output validation in `answering.py`. Name one helpful control and one limitation.
4. State whether recorded evaluation proves resistance; cite `docs/EVALUATION.md` or `eval/baseline.json`.

**Expected output:** Approved lubricant is ISO VG 100 synthetic ester, AM-CO-100S. The document also contains a malicious embedded instruction. Evidence labels and citation/output checks help, but the stored report is retrieval-only; answer-level resistance is not proven. Refusal recall is 0/2 for expected refusals.

## Question 3 - Bonus Challenge (30 points): verify the safety gate and tenant boundary
Choose one track or attempt both.

**Track A - Safety gate**
1. Use Workflow Run with a supported Alpha hydraulic-press symptom.
2. Record the required safety-step IDs returned by `POST /runs` and use them to perform the acknowledgement check.
3. Omit one required ID and submit. Record whether generation is blocked.
4. Submit all required IDs; confirm a draft is produced and awaits supervisor approval.
5. Cite the code rule and test.

**Track B - Tenant isolation**
1. Find the RLS tenant policy for chunks/documents.
2. Find where the DB tenant context is set.
3. Find an integration test proving one tenant cannot read another tenant's records.
4. Explain why one Alpha no-data response for Beta content is useful but not complete proof.

**Expected output:** Track A: missing any required ID blocks generation server-side. Track B: RLS compares row tenant to transaction-local `app.tenant_id`; integration tests exercise isolation. A manual response is a smoke test; policies and repeatable tests are stronger evidence.

## Stretch challenges (at least three)
1. **Direct injection:** Add a case to a temporary golden copy; define expected behavior and an answer-level metric that would establish a pass. Do not change the committed benchmark during the lab.
2. **False refusal:** Explain how raising threshold 0.55 may improve refusal recall but reject valid queries. Propose a metric covering expected refusals and answerable questions.
3. **Another OWASP risk:** Pick disclosure, supply chain, poisoning, or unbounded consumption; name one control, one evidence source and one remaining gap.
4. **Indirect-injection invariant:** Propose a test where poisoned manual text tells the model to skip LOTO/approval. Identify server code that must still enforce the safety gate.
5. **Provider disclosure:** Trace question/evidence sent to a hosted provider and redaction; name data formats the narrow regexes may miss.

## Submission checklist
Submit answers to Questions 1 and 2; one bonus track result; responses to at least three stretch challenges; repository paths as evidence; and a clear distinction between runtime observation and static inspection. Do not claim a control passed without a relevant test/run or an enforcement path plus supporting test.
