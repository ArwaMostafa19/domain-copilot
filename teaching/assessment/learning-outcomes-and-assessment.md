# Learning Outcomes and Assessment Map

## Session context
- Session: OWASP LLM Top 10 in Practice
- Duration: 90 minutes
- Audience: Post-graduate trainees
- Approach: formative source tracing, paired lab evidence, individual exit ticket. No single score is proof of application security.

## Learning outcomes and evidence
| ID | By the end, a trainee can... | Teaching / practice | Assessment evidence and success criterion |
| --- | --- | --- | --- |
| LO-1 | Distinguish direct/indirect prompt injection and explain why prompt wording cannot guarantee prevention. | Slides 5-10; lab Q2. | Names entry point for each; explains retrieved text is still model input; cites one containment control. |
| LO-2 | Trace trust boundaries through user, corpus, retrieval, provider, tools, DB and UI. | Slides 4, 8, 10, 13; repo walkthrough. | Correct data path; identifies what goes to hosted/local provider. |
| LO-3 | Identify code-enforced output, tenant, least-privilege and approval controls. | Slides 11-14, 17; lab Q1/bonus. | Names exact code/policy/test, not only a prompt/UI affordance. |
| LO-4 | Run or inspect adversarial evaluation and interpret failures honestly. | Slide 18; lab Q2/stretch 1-2. | Distinguishes retrieval-only from answer-level metrics and calls refusal recall 0/2 a failure. |
| LO-5 | Propose a defense-in-depth improvement with a testable acceptance criterion. | Slides 9, 15-18; stretch. | Names threat, enforcement point, test input, expected result and residual limitation. |

## Assessment schedule
| Phase | Assessment |
| --- | --- |
| Opening, 0-10 min | Diagnostic prompt: What can go wrong if retrieved manuals are trusted? Ungraded. |
| Concepts/demo, 10-60 min | Source-location checks: trainee identifies actual code/test enforcement. |
| Lab, 60-80 min | Pair work from `teaching/lab/lab-sheet.md`: Q1 10 points, Q2 20 points, Q3 bonus 30 points, plus at least three stretch responses. |
| Debrief, 80-85 min | Pair states one effective control and one gap with repository evidence. |
| Exit, 85-90 min | Individual answers to slide 21 questions. |

## Exit-ticket rubric (3 points)
1. Why is the instruction to ignore instructions in context insufficient? 1 point: retrieved text remains in model input; prompt wording is not enforcement.
2. Which control stops a hijacked agent from writing a work order? 1 point: tool allow-list/schema and server-side safety/approval gate; supervisor final approval.
3. Why is filtering by tenant after retrieval not isolation? 1 point: data already crossed boundary into application/model; RLS/tenant scope must apply before rows are returned.

## Pass guidance
Two of three exit-ticket points plus substantially correct Q1/Q2 indicates core understanding. Bonus recognizes deeper verification, not memorization. If a trainee claims injection resistance is proven, ask them to reconcile the claim with retrieval-only baseline and absent answer-level result. Detailed key: `teaching/lab/answer-key.md`.
