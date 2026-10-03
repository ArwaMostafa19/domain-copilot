"""Deterministic generator for the two-tenant D5 synthetic maintenance corpus.

Usage
-----
    python scripts/generate_corpus.py           # write the corpus
    python scripts/generate_corpus.py --check   # verify it is up to date
    python scripts/export_corpus_pdf.py         # render every document to PDF

The generator contains no randomness and makes no network calls. It renders the
authored documents in ``corpus_docs_alpha`` and ``corpus_docs_beta`` to
Markdown plus a machine readable index at ``corpus/manifest.json``. A small set
of documents listed in ``FORMAT_SAMPLES`` is additionally rendered to PDF beside
its Markdown source, so the corpus exposes a second input format. Markdown is
the source of truth and the PDFs are derived from it.

All organisations, assets, documents and values are fictional.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from corpus_docs import DOCUMENT_TYPES, TENANTS, Document
from corpus_docs_alpha import ALPHA_DOCUMENTS
from corpus_docs_beta import BETA_DOCUMENTS
from export_corpus_pdf import render as render_pdf

ROOT = Path(__file__).resolve().parents[1]
CORPUS_DIR = ROOT / "corpus"
MANIFEST_PATH = CORPUS_DIR / "manifest.json"
GENERATOR_ID = "scripts/generate_corpus.py"
HAND_WRITTEN_FILES = {".gitkeep", "README.md"}

# A few documents are also published as PDF next to their Markdown source so the
# corpus offers a second input format. Markdown stays the source of truth: the
# PDF files are rendered from it and are verified byte for byte by --check.
FORMAT_SAMPLES = (
    "tenant-alpha/hydraulic-press-manual-rev-a.md",
    "tenant-alpha/hydraulic-press-manual-rev-b.md",
    "tenant-alpha/hydraulic-press-lockout-tagout.md",
    "tenant-beta/hydraulic-press-manual-rev-b.md",
    "tenant-beta/hydraulic-press-energy-control.md",
    "tenant-beta/chiller-alarm-troubleshooting.md",
)


def all_documents() -> list[Document]:
    """Return every document in a stable order."""

    return sorted(
        [*ALPHA_DOCUMENTS, *BETA_DOCUMENTS],
        key=lambda doc: (doc.tenant, doc.filename),
    )


def yaml_value(value: str) -> str:
    """Quote a scalar for the front matter block."""

    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def front_matter(doc: Document) -> str:
    tenant = TENANTS[doc.tenant]
    rows = [
        ("tenant", doc.tenant),
        ("tenant_name", tenant["tenant_name"]),
        ("site", tenant["site"]),
        ("doc_id", doc.doc_id),
        ("source_id", doc.source_id),
        ("title", doc.title),
        ("equipment", doc.equipment),
        ("equipment_also_covers", doc.equipment_also_covers),
        ("document_type", doc.doc_type),
        ("document_type_name", DOCUMENT_TYPES[doc.doc_type]),
        ("revision", doc.revision),
        ("effective_date", doc.effective_date),
        ("status", doc.status),
        ("supersedes", doc.supersedes or ""),
        ("applies_to", doc.applies_to or f"Assets listed under equipment for {tenant['tenant_name']}"),
        ("related_documents", ", ".join(doc.related_documents)),
        ("document_owner", doc.owner),
        ("source_format", "markdown"),
        ("generator", GENERATOR_ID),
    ]
    lines = ["---"]
    lines += [f"{key}: {yaml_value(value)}" for key, value in rows]
    lines.append("---")
    return "\n".join(lines)


def control_table(doc: Document) -> str:
    tenant = TENANTS[doc.tenant]
    rows = [
        ("Tenant", f"{tenant['tenant_name']} ({doc.tenant})"),
        ("Site", tenant["site"]),
        ("Document identifier", doc.doc_id),
        ("Source identifier", doc.source_id),
        ("Equipment", doc.equipment),
    ]
    if doc.equipment_also_covers:
        rows.append(("Also covers", doc.equipment_also_covers))
    rows += [
        ("Document type", DOCUMENT_TYPES[doc.doc_type]),
        ("Revision", doc.revision),
        ("Effective date", doc.effective_date),
        ("Status", doc.status),
    ]
    if doc.supersedes:
        rows.append(("Supersedes", doc.supersedes))
    rows.append(("Applies to", doc.applies_to or "Assets listed under equipment"))
    if doc.related_documents:
        rows.append(("Related documents", ", ".join(doc.related_documents)))
    rows.append(("Document owner", doc.owner))

    lines = ["| Field | Value |", "| --- | --- |"]
    lines += [f"| {label} | {value} |" for label, value in rows]
    return "\n".join(lines)


def render(doc: Document) -> str:
    """Render one document to Markdown. Deterministic and idempotent."""

    blocks = [
        front_matter(doc),
        f"# {doc.title}",
        control_table(doc),
    ]
    for section in doc.sections:
        blocks.append(f"## {section.heading}\n\n{section.body}")
    return "\n\n".join(blocks) + "\n"


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def pdf_path(markdown_relative_path: str) -> str:
    """Return the PDF path that belongs to a Markdown sample."""

    return markdown_relative_path[: -len(".md")] + ".pdf"


def pdf_samples(files: dict[str, str]) -> dict[str, bytes]:
    """Return {relative path: PDF bytes} for the sampled documents."""

    samples: dict[str, bytes] = {}
    for relative in FORMAT_SAMPLES:
        if relative not in files:
            raise ValueError(f"format sample is not a corpus document: {relative}")
        data, _pages = render_pdf(files[relative])
        samples[pdf_path(relative)] = data
    return samples


def build() -> tuple[dict[str, str], dict[str, bytes]]:
    """Return ({relative path: text}, {relative path: PDF bytes})."""

    files: dict[str, str] = {}
    documents = all_documents()

    for doc in documents:
        relative = f"{doc.tenant}/{doc.filename}"
        if relative in files:
            raise ValueError(f"duplicate corpus path: {relative}")
        files[relative] = render(doc)

    samples = pdf_samples(files)
    by_path = {f"{doc.tenant}/{doc.filename}": doc for doc in documents}

    manifest = {
        "corpus_id": "d5-industrial-field-maintenance",
        "description": (
            "Synthetic industrial field-maintenance corpus for two fictional tenants. "
            "All organisations, assets and values are fictional."
        ),
        "generator": GENERATOR_ID,
        "document_count": len(documents),
        "tenants": [
            {
                "tenant": tenant_id,
                "tenant_name": meta["tenant_name"],
                "site": meta["site"],
                "unit_system": meta["unit_system"],
                "document_prefix": meta["document_prefix"],
                "document_count": sum(1 for doc in documents if doc.tenant == tenant_id),
            }
            for tenant_id, meta in TENANTS.items()
        ],
        "documents": [
            {
                "doc_id": doc.doc_id,
                "tenant": doc.tenant,
                "tenant_name": TENANTS[doc.tenant]["tenant_name"],
                "path": f"{doc.tenant}/{doc.filename}",
                "title": doc.title,
                "equipment": doc.equipment,
                "document_type": doc.doc_type,
                "revision": doc.revision,
                "effective_date": doc.effective_date,
                "status": doc.status,
                "supersedes": doc.supersedes,
                "source_id": doc.source_id,
                "sections": [section.heading for section in doc.sections],
                "sha256": sha256(files[f"{doc.tenant}/{doc.filename}"]),
            }
            for doc in documents
        ],
        "format_samples": [
            {
                "doc_id": by_path[source].doc_id,
                "tenant": by_path[source].tenant,
                "title": by_path[source].title,
                "revision": by_path[source].revision,
                "status": by_path[source].status,
                "document_format": "pdf",
                "path": pdf_path(source),
                "source_path": source,
                "sha256": hashlib.sha256(samples[pdf_path(source)]).hexdigest(),
            }
            for source in FORMAT_SAMPLES
        ],
    }
    files["manifest.json"] = json.dumps(manifest, indent=2, ensure_ascii=True) + "\n"
    return files, samples


def check_integrity(documents: list[Document]) -> None:
    """Fail loudly on corpus level mistakes before anything is written."""

    doc_ids: set[str] = set()
    for doc in documents:
        if doc.doc_id in doc_ids:
            raise ValueError(f"duplicate doc_id: {doc.doc_id}")
        doc_ids.add(doc.doc_id)

        if doc.tenant not in TENANTS:
            raise ValueError(f"unknown tenant: {doc.tenant}")
        if doc.doc_type not in DOCUMENT_TYPES:
            raise ValueError(f"unknown document_type: {doc.doc_type}")
        if doc.status not in {"current", "superseded"}:
            raise ValueError(f"invalid status on {doc.doc_id}: {doc.status}")
        if not doc.filename.endswith(".md"):
            raise ValueError(f"unexpected filename: {doc.filename}")
        if not doc.sections:
            raise ValueError(f"no sections in {doc.doc_id}")

    by_id = {doc.doc_id: doc for doc in documents}
    for doc in documents:
        if doc.supersedes is None:
            continue
        previous = by_id.get(doc.supersedes)
        if previous is None:
            raise ValueError(f"{doc.doc_id} supersedes unknown document {doc.supersedes}")
        if previous.tenant != doc.tenant:
            raise ValueError(f"{doc.doc_id} supersedes a document from another tenant")
        if previous.effective_date >= doc.effective_date:
            raise ValueError(f"{doc.doc_id} has an effective date before the revision it supersedes")
        if previous.status != "superseded":
            raise ValueError(f"{previous.doc_id} is superseded by {doc.doc_id} but is not marked superseded")

    revision_groups: dict[tuple[str, str], list[Document]] = {}
    for doc in documents:
        if doc.revision in {"Rev A", "Rev B"}:
            revision_groups.setdefault((doc.tenant, doc.doc_id.rsplit("-", 1)[0]), []).append(doc)
    for key, group in revision_groups.items():
        labels = sorted(doc.revision for doc in group)
        if labels != ["Rev A", "Rev B"]:
            raise ValueError(f"unpaired revision group {key}: {labels}")


def write(files: dict[str, str], samples: dict[str, bytes]) -> None:
    for relative, content in sorted(files.items()):
        path = CORPUS_DIR / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
    for relative, data in sorted(samples.items()):
        path = CORPUS_DIR / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    print(f"wrote {len(files) + len(samples)} files under {CORPUS_DIR}")


def verify(files: dict[str, str], samples: dict[str, bytes]) -> int:
    problems: list[str] = []
    for relative, content in sorted(files.items()):
        path = CORPUS_DIR / relative
        if not path.exists():
            problems.append(f"missing: {relative}")
            continue
        if path.read_text(encoding="utf-8") != content:
            problems.append(f"stale: {relative}")

    for relative, data in sorted(samples.items()):
        path = CORPUS_DIR / relative
        if not path.exists():
            problems.append(f"missing: {relative}")
            continue
        if path.read_bytes() != data:
            problems.append(f"stale: {relative}")

    expected = set(files) | set(samples)
    present = {
        path.relative_to(CORPUS_DIR).as_posix()
        for path in CORPUS_DIR.rglob("*")
        if path.is_file() and path.name not in HAND_WRITTEN_FILES
    }
    for extra in sorted(present - expected):
        problems.append(f"unexpected file in corpus: {extra}")

    for problem in problems:
        print(problem, file=sys.stderr)
    if problems:
        print(f"{len(problems)} problem(s) found", file=sys.stderr)
        return 1
    print(f"corpus is up to date: {len(files) + len(samples)} files")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify that the committed corpus matches the generator output",
    )
    arguments = parser.parse_args()

    documents = all_documents()
    check_integrity(documents)
    files, samples = build()

    if arguments.check:
        return verify(files, samples)

    write(files, samples)
    print(f"documents: {len(documents)}")
    for tenant_id in TENANTS:
        count = sum(1 for doc in documents if doc.tenant == tenant_id)
        print(f"  {tenant_id}: {count}")
    print(f"pdf format samples: {len(samples)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())