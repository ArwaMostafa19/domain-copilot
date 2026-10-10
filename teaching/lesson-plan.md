# Lesson Plan: OWASP LLM Top 10 in Practice

## Session
- Audience: Post-graduate software/security trainees
- Duration: 90 minutes
- Topic: Applying OWASP Top 10 for LLM Applications to Domain Copilot
- Prerequisites: Basic HTTP/API, SQL, Python, and familiarity with LLM/RAG concepts
- Materials: Repository, Docker Compose, browser, terminal, and `teaching/slides/OWASP-LLM-in-Practice-Slides.pptx`

## Learning outcomes
By the end, trainees can:
1. Distinguish direct from indirect prompt injection and explain why prompt wording alone cannot guarantee prevention.
2. Trace trust boundaries from user/document through retrieval, provider, tools, database, and UI.
3. Identify code-enforced controls for tenant isolation, tool permissions, output validation, and human approval.
4. Run adversarial evaluation and interpret failures without overstating assurance.
5. Propose a defense-in-depth improvement and a test that would provide evidence it works.

## 90-minute facilitation plan
| Time | Slides | Instructor activity | Learner activity / evidence |
| --- | --- | --- | --- |
| 0-10 min | 1-3 | Frame the safety setting; ask which components trainees trust; introduce outcomes and agenda. | State one security assumption to test. |
| 10-20 min | 4-6 | Draw trust boundaries; distinguish OWASP LLM Top 10 from OWASP Web Top 10. | Identify one overlapping and one LLM-specific risk. |
| 20-40 min | 7-10 | Compare direct/indirect injection; trace poisoned compressor note; explain why delimiters are not a hard boundary. | Predict what the model sees and which controls act before/after generation. |
| 40-60 min | 11-17 | Walk through output validation, least privilege, provider disclosure, RLS, limits, supply chain, misinformation; state implemented controls and gaps. | Locate one control and one limitation in source/docs. |
| 60-80 min | 18-19 | Facilitate paired lab: baseline, injection, tool/gate and tenant checks. | Complete easy and medium tasks; try bonus; record evidence. |
| 80-85 min | 20 | Summarize operational rules. | Name one enforced control and one residual risk. |
| 85-90 min | 21 | Run exit ticket. | Individually answer three questions. |

## Teaching approach
Use the repository as a case study, not proof of OWASP certification. Ask the class to identify what enforces each control, and require code, a database policy, a test, or a measured evaluation as evidence. Real controls include tenant RLS, schemas, output checks and workflow approval. Real gaps include missing answer-level injection results, refusal recall 0/2, no lockfile, and limited redaction/rate limiting. Present both.

Assessment uses lab observations and the exit ticket. See `teaching/assessment/learning-outcomes-and-assessment.md` and `teaching/lab/answer-key.md`.
