# AI Usage Log

This log records how AI tools contributed to Domain Copilot and what I did to
direct and verify that work. AI assistance was part of the process, but the
project's requirements, choices, experiments, reviews, and acceptance
decisions remained mine. Tool names and incidents below reflect the project
notes and records available in this repository; I have not inferred precise
dates or contributions where the notes do not establish them.

## How I worked

I used AI as a set of collaborators with bounded roles, not as an automatic
author of the whole project:

- **ChatGPT** helped turn requirements I supplied into structured task
  specifications, including the "Run A" file. I provided the goals and
  constraints and reviewed the resulting specifications.
- **Claude** was used for planning, design discussion, and review. It offered
  options and identified possible issues; I evaluated those suggestions and
  made the decisions.
- **OpenCode** was used for implementation and corpus-generation tasks based
  on instructions I prepared. I tested the changes and reviewed the results.
- **Codex (this assistant)** was used in this documentation pass to inspect
  the repository, create this log from the supplied account and repository
  evidence, and update stale deliverable-gap references. My work here is
  limited to these documentation edits; I did not implement or test product
  code.

In practice, I described the task, reviewed and amended proposed prompts,
specified files and constraints, then ran the tools and checked what they
changed. I was also the one experimenting with the system: trying commands,
checking their output, comparing behavior to the brief, and asking for
corrections when a result did not make sense. AI-generated plans and reports
were useful inputs, not proof that the work was correct.

## What I delegated

- Drafting bounded task specifications from requirements I provided.
- Implementation of portions of the application and test scaffolding from
  those specifications.
- Generation and revision of synthetic maintenance-corpus material.
- Design consultation, code review suggestions, and documentation drafts.
- Some repository-workflow preparation, such as issue/PR planning; external
  GitHub activity is not claimed here without repository evidence.

The exact share varied by task. These bullets describe assistance, not
end-to-end ownership of the corresponding project outcomes.

## What I did and owned

- I chose the project scope and supplied the requirements, constraints, and
  acceptance expectations. I edited task prompts to identify protected files,
  required outputs, and boundaries before handing work to an implementation
  tool.
- I made and accepted the design decisions after discussion. For example, I
  considered the architecture options before settling on Clean Architecture,
  and evaluated the rationale and alternatives for pgvector and section-based
  chunking rather than accepting suggestions automatically.
- I defined the domain contracts in `src/domain/documents.py`, including the
  document, section, chunk, safety-step, and extraction-error shapes, as
  recorded in my project notes. Those contracts guided downstream work.
- I designed the Docker service arrangement and reviewed the implementation
  details against the intended service ordering and dependencies.
- I personally tried the commands and application paths available during
  development, inspected outputs and test results, read source when reports
  were not convincing, and requested fixes when I found a mismatch.
- I reviewed corpus content against the brief and the expected behavior,
  including cross-references, conflicting values, safety instructions, and
  missing adversarial examples.
- I decided whether a proposed change met the intended scope and whether to
  keep, revise, or revert it. A generated report did not make that decision
  for me.

## Where AI misled me or needed correction

The following are examples from the project notes and handoff records. They
are included because reviewing and correcting AI output was part of the work.

### Planning, configuration, and corpus

- An early Compose configuration put a default database password in the
  repository. I noticed and moved the value into `.env`.
- Dependency versions were initially selected from model memory rather than
  checked. `pip-audit` reported known vulnerabilities; the versions were
  updated and tested.
- Generated corpus material was initially short of the page-count target,
  lacked an embedded-injection example, and contained contradictory or
  ambiguous technical values and broken section references. I compared the
  material with the brief and reviewed the documents, then directed revisions.
- In one task, the tool changed a value in document body prose despite a scope
  instruction to avoid such edits unless needed. I checked the mentions across
  the documents. It also added its working-report filename to `.gitignore`; I
  reverted that unrelated change.

### Ingestion and implementation

- An early chunker did not reset its packing counter after closing a chunk.
  Its tests passed, but the dry-run statistics showed suspiciously small
  chunks. I inspected the source, reproduced the behavior with four 40-character
  blocks and a 100-character limit (`[82, 40, 40]` instead of `[82, 82]`), and
  asked for regression coverage and a fix.
- A dry-run command returned success with no output for a directory that did
  not exist. I found this after mistyping the path; it was corrected to report
  an error and exit with code 2.
- Two corpus tests were described as unrelated or pre-existing failures. I
  traced them to Git line-ending conversion changing PDF hashes on Windows; a
  `.gitattributes` rule was added to keep the files stable.
- A report claimed there were no scope violations even though `.gitignore` had
  been changed, misclassified a chunk's length, and overlooked a practical way
  to exercise page fallback with temporary files. I checked the report against
  the files and reverted the out-of-scope change.
- The application-layer extractor dependency was hidden behind `importlib` to
  satisfy an import-scanning architecture test, while the underlying layer
  dependency remained. I recorded this as a limitation rather than treating
  the passing check as proof that the boundary was clean.
- During a database isolation check, a pasted interactive command was
  corrupted and its output appeared out of order. I did not count that partial
  run as adequate verification; the check was repeated as one script command.

### My own process mistakes

- I switched Git branches and edited other files in the same working tree
  while an implementation task was running. The tool reported external file
  modifications; the overlap came from my own workflow. I should keep
  concurrent work out of one shared working tree.
- In an early review I relied too much on the implementation report and called
  the pipeline essentially correct before reading the chunker source. The bug
  was visible in the code and dry-run data. I changed my review practice to
  inspect the relevant source and evidence directly.
- A design review asserted that CI had passed without checking the actual
  result. I now treat CI status as something to inspect, not infer from a
  summary.

## How I verified work

- I compared generated and edited artifacts to the assignment requirements
  and to source files, rather than relying only on completion summaries.
- I inspected implementation code when output statistics or behavior looked
  suspicious, and built a small reproducer for the chunk-packing defect.
- I asked for regression tests that demonstrate the old behavior fails and
  the corrected behavior passes, then reviewed the test's assertion.
- I checked CI results directly and used Git's stored file version or hashes
  when a working-tree file's integrity was in question.
- I reviewed corpus facts and references for contradictions, missing targets,
  and safety issues.
- I kept scope constraints in task instructions and reverted unrelated edits
  when tools crossed them.
- I treated statements such as "all tests pass" and "no scope violations" as
  claims to verify. A passing test suite is meaningful only when the tests
  exercise the behavior that matters.

## What I learned

AI tools helped me move faster on drafting, implementation, and review, but
they could produce plausible reports alongside incorrect code or incomplete
checks. My role was to define the problem, experiment with the result, notice
when behavior did not match expectations, and decide what evidence was enough
to accept a change. That review and correction work is part of my contribution
to the project, not an afterthought.

This log describes the work recorded so far. It does not claim that every
listed verification was repeated during this documentation pass, or that the
project has no remaining gaps.
