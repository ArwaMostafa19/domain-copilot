"""Shared model and tenant metadata for the D5 synthetic maintenance corpus.

This module contains dataclasses and tenant metadata only. The authored
document content lives in ``scripts/corpus_docs_alpha.py`` and
``scripts/corpus_docs_beta.py``. Rendering is done by
``scripts/generate_corpus.py``.

All organisations, equipment identifiers and procedures in this corpus are
fictional. They were created for this project and describe no real site,
product, person or service.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

TENANTS: dict[str, dict[str, str]] = {
    "tenant-alpha": {
        "tenant_name": "Alpha Manufacturing",
        "site": "Ridgeway Works, Building 2 (metric documentation)",
        "unit_system": "metric: bar, mm, N.m, l/min, degC",
        "document_prefix": "AM",
    },
    "tenant-beta": {
        "tenant_name": "Beta Manufacturing",
        "site": "Harbor Works, Line 1 (imperial documentation)",
        "unit_system": "imperial: psi, in, lbf.ft, gpm, degF",
        "document_prefix": "BM",
    },
}

DOCUMENT_TYPES: dict[str, str] = {
    "equipment-manual": "Equipment manual",
    "maintenance-procedure": "Preventive maintenance procedure",
    "safety-procedure": "Safety / energy isolation procedure",
    "inspection-procedure": "Inspection procedure",
    "troubleshooting-guide": "Troubleshooting guide",
    "diagnostic-procedure": "Diagnostic procedure",
    "lubrication-schedule": "Lubrication schedule",
    "work-order-rules": "Work order and escalation rules",
}


@dataclass(frozen=True)
class Section:
    """A single titled section of a document body."""

    heading: str
    body: str


@dataclass(frozen=True)
class Document:
    """One synthetic maintenance document for one tenant."""

    doc_id: str
    source_id: str
    filename: str
    title: str
    tenant: str
    equipment: str
    doc_type: str
    revision: str
    effective_date: str
    status: str
    sections: tuple[Section, ...]
    supersedes: str | None = None
    equipment_also_covers: str = ""
    applies_to: str = ""
    related_documents: tuple[str, ...] = ()
    owner: str = "Maintenance Engineering"


def sections(*pairs: Sequence[str]) -> tuple[Section, ...]:
    """Build document sections from (heading, body) pairs.

    Bodies may be triple-quoted literals indented for readability; leading and
    trailing blank lines are removed.
    """

    return tuple(Section(heading, body.strip("\n")) for heading, body in pairs)