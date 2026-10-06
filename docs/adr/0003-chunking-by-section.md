# ADR 0003: Split documents by section and index both Markdown and PDF

## Status
Accepted

## Context
Retrieval answers questions with maintenance values, intervals and safety prerequisites. A chunk that cuts a table or a numbered list in half can return half a procedure, which is dangerous in this domain. The corpus has 30 documents (15 per tenant) with a regular structure of second-level headings, and 6 of them also exist as PDF.

## Decision
- Split each document at its second-level headings, so a chunk never mixes two sections.
- Never split a table, a numbered list or a bullet list. A section is packed block by block up to 1800 characters, and a single block larger than that stays whole.
- The "Safety prerequisites" section is always one chunk.
- Keep the original text of a chunk separate from a context line (title, section, revision). The context line is added only when the embedding is computed, which keeps citations exact.
- Index both formats. The six PDFs give page numbers for citations and prove the second input path. Hits with the same document and section will be collapsed at retrieval time.
- PDF sections are found by matching lines against the section titles recorded in the corpus manifest. Without titles, each page becomes one section.

## Alternatives considered
- Fixed-size windows with overlap: simple, but they cut tables and procedures at arbitrary points.
- Sentence-level chunks: precise, but they lose the context of a table or a procedure step.
- One chunk per document: too coarse, a question about one interval would retrieve a whole manual.

## Consequences
- Measured on the corpus: 477 chunks, median 794 characters, 90th percentile 1499, and three chunks over the limit, all of them atomic blocks in PDF files.
- No chunk is shorter than 108 characters. Small blocks are packed together with their neighbours up to the limit, so a chunk is never a fragment on its own.
- The six PDF documents appear twice in the index until retrieval collapses the duplicates.
- PDF section names depend on the manifest, so a PDF with no manifest entry loses them.
- The PDF samples come from a hand-written exporter, and pypdf reports a wrong startxref pointer for each of them. It recovers and the extracted text is complete.