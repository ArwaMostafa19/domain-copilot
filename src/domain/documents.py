from dataclasses import dataclass


class DomainError(Exception):
    """Base class for errors the application understands and reports."""


class ExtractionError(DomainError):
    """A source file could not be read or does not have the expected structure."""


@dataclass(frozen=True)
class DocumentMeta:
    """Who owns a document, which document it is, and which version."""

    tenant_id: str
    doc_id: str
    title: str
    revision: str
    status: str
    source_format: str
    source_path: str
    content_sha256: str
    equipment: str | None = None
    document_type: str | None = None


@dataclass(frozen=True)
class Section:
    """One titled part of a document, as read from the file."""

    title: str
    text: str
    page: int | None = None


@dataclass(frozen=True)
class ExtractedDocument:
    """The result of reading one file: its metadata and its sections, in order."""

    meta: DocumentMeta
    sections: tuple[Section, ...]


@dataclass(frozen=True)
class Chunk:
    """A piece of text that is stored, searched and cited on its own."""

    ordinal: int
    section: str
    context: str
    text: str
    revision: str
    page: int | None = None


@dataclass(frozen=True)
class SafetyStep:
    """One numbered safety prerequisite of a procedure."""

    step_no: int
    text: str


