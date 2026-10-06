"""Read corpus files into :class:`ExtractedDocument` objects.

Markdown and PDF are dispatched on the file suffix. This is the only module
that is allowed to import ``pypdf``.
"""

from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path

from pypdf import PdfReader

from src.domain.documents import (
    DocumentMeta,
    ExtractedDocument,
    ExtractionError,
    Section,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_NAME = "manifest.json"
FRONT_MATTER_DELIMITER = "---"
H1_PREFIX = "# "
H2_PREFIX = "## "
TABLE_PREFIX = "|"
REQUIRED_KEYS = ("tenant", "doc_id", "title", "revision", "status")


def extract(path: Path) -> ExtractedDocument:
    """Read one corpus file and return its metadata and sections."""
    path = Path(path)
    if not path.is_file():
        raise ExtractionError(f"source file does not exist: {path}")
    suffix = path.suffix.lower()
    if suffix == ".md":
        return _extract_markdown(path)
    if suffix == ".pdf":
        return _extract_pdf(path)
    raise ExtractionError(f"unsupported source format {suffix!r}: {path}")


# --- markdown ------------------------------------------------------------------


def _extract_markdown(path: Path) -> ExtractedDocument:
    data = path.read_bytes()
    lines = data.decode("utf-8").split("\n")
    values = _front_matter(path, lines)
    body = _drop_leading_tables(path, lines[_front_matter_end(lines) + 1 :])
    sections = _markdown_sections(body, values["title"])
    meta = DocumentMeta(
        tenant_id=values["tenant"],
        doc_id=values["doc_id"],
        title=values["title"],
        revision=values["revision"],
        status=values["status"],
        source_format="markdown",
        source_path=_source_path(path),
        content_sha256=hashlib.sha256(data).hexdigest(),
        equipment=values.get("equipment") or None,
        document_type=values.get("document_type") or None,
    )
    return ExtractedDocument(meta=meta, sections=tuple(sections))


def _front_matter(path: Path, lines: list[str]) -> dict[str, str]:
    """Parse the ``key: "value"`` lines between the first two ``---`` lines."""
    start = _front_matter_start(path, lines)
    end = _front_matter_end(lines)
    values: dict[str, str] = {}
    for line in lines[start + 1 : end]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, separator, value = line.partition(":")
        if not separator:
            continue
        values[key.strip()] = value.strip().strip('"').strip()
    missing = [key for key in REQUIRED_KEYS if not values.get(key)]
    if missing:
        raise ExtractionError(
            f"front matter is missing required key(s) {', '.join(missing)}: {path}"
        )
    return values


def _front_matter_start(path: Path, lines: list[str]) -> int:
    for index, line in enumerate(lines):
        if line.strip() == FRONT_MATTER_DELIMITER:
            return index
    raise ExtractionError(f"no front matter delimiter found: {path}")


def _front_matter_end(lines: list[str]) -> int:
    seen = 0
    for index, line in enumerate(lines):
        if line.strip() != FRONT_MATTER_DELIMITER:
            continue
        seen += 1
        if seen == 2:
            return index
    raise ExtractionError("unterminated front matter block")


def _drop_leading_tables(path: Path, lines: list[str]) -> list[str]:
    """Drop the H1 line and the field/value table directly below it."""
    index = 0
    while index < len(lines) and not lines[index].strip():
        index += 1
    if index < len(lines) and lines[index].startswith(H1_PREFIX):
        index += 1
    while index < len(lines) and not lines[index].strip():
        index += 1
    while index < len(lines) and lines[index].startswith(TABLE_PREFIX):
        index += 1
    if index >= len(lines):
        raise ExtractionError(f"no document body found below the front matter: {path}")
    return lines[index:]


def _markdown_sections(lines: list[str], document_title: str) -> list[Section]:
    """Split the body at ``## `` lines, keeping ``### `` lines in their parent."""
    sections: list[Section] = []
    title = document_title
    buffer: list[str] = []

    def close() -> None:
        text = "\n".join(buffer)
        if text.strip():
            sections.append(Section(title=title, text=text))

    for line in lines:
        if line.startswith(H2_PREFIX):
            close()
            title = line[len(H2_PREFIX) :].strip()
            buffer = []
            continue
        buffer.append(line)
    close()
    return sections


# --- pdf -----------------------------------------------------------------------


def _extract_pdf(path: Path) -> ExtractedDocument:
    sibling = path.with_suffix(".md")
    if not sibling.is_file():
        raise ExtractionError(f"PDF has no sibling Markdown file for its metadata: {path}")
    source = _extract_markdown(sibling)
    data = path.read_bytes()
    pages = _pdf_pages(path, data)
    titles = _manifest_section_titles(path)
    sections = _pdf_sections(pages, titles, source.meta.title)
    meta = DocumentMeta(
        tenant_id=source.meta.tenant_id,
        doc_id=source.meta.doc_id,
        title=source.meta.title,
        revision=source.meta.revision,
        status=source.meta.status,
        source_format="pdf",
        source_path=_source_path(path),
        content_sha256=hashlib.sha256(data).hexdigest(),
        equipment=source.meta.equipment,
        document_type=source.meta.document_type,
    )
    return ExtractedDocument(meta=meta, sections=tuple(sections))


def _pdf_pages(path: Path, data: bytes) -> list[str]:
    try:
        reader = PdfReader(io.BytesIO(data))
        pages = [(page.extract_text() or "") for page in reader.pages]
    except Exception as error:
        raise ExtractionError(f"could not read PDF {path}: {error}") from error
    if not any(page.strip() for page in pages):
        raise ExtractionError(f"PDF has no extractable text: {path}")
    return pages


def _pdf_sections(pages: list[str], titles: list[str], document_title: str) -> list[Section]:
    known = set(titles)
    if not known:
        return [
            Section(title=f"Page {number}", text=text, page=number)
            for number, text in enumerate(pages, start=1)
            if text.strip()
        ]
    sections: list[Section] = []
    title = document_title
    page_number = 1
    buffer: list[str] = []
    for number, page_text in enumerate(pages, start=1):
        for line in page_text.split("\n"):
            stripped = line.strip()
            if stripped in known:
                if "\n".join(buffer).strip():
                    sections.append(Section(title=title, text="\n".join(buffer), page=page_number))
                title = stripped
                page_number = number
                buffer = []
                continue
            buffer.append(line)
    if "\n".join(buffer).strip():
        sections.append(Section(title=title, text="\n".join(buffer), page=page_number))
    return sections


def _manifest_section_titles(path: Path) -> list[str]:
    """Section titles the manifest records for the document this PDF is."""
    manifest_path = _find_manifest(path)
    if manifest_path is None:
        return []
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    documents = manifest.get("documents") or []
    doc_id = _manifest_doc_id(path, manifest_path.parent, manifest, documents)
    if doc_id is None:
        return []
    for entry in documents:
        if entry.get("doc_id") == doc_id:
            return [str(title) for title in (entry.get("sections") or [])]
    return []


def _manifest_doc_id(
    path: Path, folder: Path, manifest: dict, documents: list
) -> str | None:
    pdf_relative = _relative_to(path, folder)
    for sample in manifest.get("format_samples") or []:
        if sample.get("path") == pdf_relative and sample.get("doc_id"):
            return str(sample["doc_id"])
    markdown_relative = _relative_to(path.with_suffix(".md"), folder)
    for entry in documents:
        if entry.get("path") == markdown_relative:
            doc_id = entry.get("doc_id")
            return str(doc_id) if doc_id else None
    return None


def _find_manifest(path: Path) -> Path | None:
    for folder in (path.parent, *path.parent.parents):
        candidate = folder / MANIFEST_NAME
        if candidate.is_file():
            return candidate
    return None


# --- shared --------------------------------------------------------------------


def _source_path(path: Path) -> str:
    return _relative_to(path, REPO_ROOT)


def _relative_to(path: Path, folder: Path) -> str:
    try:
        return path.resolve().relative_to(folder.resolve()).as_posix()
    except ValueError:
        return path.as_posix()