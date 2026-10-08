"""JSON schemas for the CP2 tools.

Each schema is the shape the ``tools`` registry validates arguments against.
Validation is simple (only the fields that exist are checked) and deterministic.
"""

from __future__ import annotations

from collections.abc import Mapping


def schema_search_manuals() -> Mapping[str, object]:
    return {
        "name": "search_manuals",
        "required_role": "technician",
        "read": True,
        "schema": {
            "type": "object",
            "required": ["query", "limit"],
            "additionalProperties": False,
            "properties": {
                "query": {"type": "string"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 50},
            },
        },
    }


def schema_get_document_revisions() -> Mapping[str, object]:
    return {
        "name": "get_document_revisions",
        "required_role": "technician",
        "read": True,
        "schema": {
            "type": "object",
            "required": ["doc_id"],
            "additionalProperties": False,
            "properties": {
                "doc_id": {"type": "string"},
            },
        },
    }


def schema_get_safety_prerequisites() -> Mapping[str, object]:
    return {
        "name": "get_safety_prerequisites",
        "required_role": "technician",
        "read": True,
        "schema": {
            "type": "object",
            "required": ["doc_ids"],
            "additionalProperties": False,
            "properties": {
                "doc_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 0,
                },
            },
        },
    }


def schema_create_work_order_draft() -> Mapping[str, object]:
    return {
        "name": "create_work_order_draft",
        "required_role": "technician",
        "read": False,
        "schema": {
            "type": "object",
            "required": ["run_id", "title", "symptoms", "diagnostic_steps"],
            "additionalProperties": False,
            "properties": {
                "run_id": {"type": "string"},
                "title": {"type": "string"},
                "symptoms": {"type": "string"},
                "diagnostic_steps": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 0,
                },
            },
        },
    }


def schema_acknowledge_safety_steps() -> Mapping[str, object]:
    return {
        "name": "acknowledge_safety_steps",
        "required_role": "technician",
        "read": False,
        "schema": {
            "type": "object",
            "required": ["run_id", "step_ids"],
            "additionalProperties": False,
            "properties": {
                "run_id": {"type": "string"},
                "step_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "minItems": 0,
                },
            },
        },
    }
