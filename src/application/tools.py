"""A tiny tool registry with schema validation and role checks.

Tools are executed only after their arguments are validated and the caller's
role is allowed. Tool results are treated as untrusted: callers must wrap them
the same way evidence is wrapped before putting them into a prompt.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass

from src.domain.workflow import Role, WorkflowError


class ToolValidationError(WorkflowError):
    """The arguments do not match a tool's schema."""


class ToolNotAllowedError(WorkflowError):
    """The role is not allowed to use this tool, or the tool does not exist."""


@dataclass(frozen=True)
class ToolSchema:
    """The contract for one tool: who may run it and what its arguments are."""

    name: str
    required_role: Role
    read: bool
    schema: Mapping[str, object]

    def __post_init__(self) -> None:
        if not self.name:
            raise WorkflowError("a tool needs a name")


class ToolRegistry:
    """A registry of tools that can be invoked from the agent layer."""

    def __init__(self) -> None:
        self._schemas: dict[str, ToolSchema] = {}
        self._handlers: dict[str, Callable[..., object]] = {}

    def register(
        self,
        schema: ToolSchema,
        handler: Callable[..., object] | None = None,
    ) -> None:
        self._schemas[schema.name] = schema
        if handler is not None:
            self._handlers[schema.name] = handler

    def get_schema(self, name: str) -> ToolSchema | None:
        return self._schemas.get(name)

    def handlers(self) -> Mapping[str, Callable[..., object]]:
        return self._handlers

    def invoke(self, name: str, args: Mapping[str, object], role: Role) -> object:
        schema = self._schemas.get(name)
        if schema is None:
            raise ToolNotAllowedError(f"unknown tool: {name}")
        if role != schema.required_role and not (
            schema.required_role == Role.TECHNICIAN and role == Role.SUPERVISOR
        ):
            # Technicians and supervisors both cover technician tools per intent;
            # explicit: supervisor may also do technician tools.
            pass  # keep simple: require exact match as per brief's "required role"
        if role != schema.required_role:
            raise ToolNotAllowedError(f"role {role.value} may not use {name}")
        if not validate_args(args, schema.schema):
            raise ToolValidationError(f"invalid arguments for {name}")
        handler = self._handlers.get(name)
        if handler is None:
            raise WorkflowError(f"tool {name} is not implemented")
        return handler(**args)

    def allowed_for(self, role: Role) -> list[str]:
        allowed: list[str] = []
        for schema in self._schemas.values():
            if role == schema.required_role or (
                schema.required_role == Role.TECHNICIAN
            ):
                allowed.append(schema.name)
        return sorted(allowed)


def validate_args(args: Mapping[str, object], schema: Mapping[str, object]) -> bool:
    """Very small JSON-schema validator for the shapes we need."""
    required = schema.get("required", [])
    properties = schema.get("properties", {})
    additional = schema.get("additionalProperties", True)
    for key in required:
        if key not in args:
            return False
    for key, value in args.items():
        if additional is False and key not in properties:
            return False
        prop = properties.get(key)
        if prop is None:
            continue
        ptype = prop.get("type")
        if ptype == "string":
            if not isinstance(value, str):
                return False
        elif ptype == "integer":
            if not isinstance(value, int) or isinstance(value, bool):
                return False
            minimum = prop.get("minimum")
            if minimum is not None and value < minimum:
                return False
            maximum = prop.get("maximum")
            if maximum is not None and value > maximum:
                return False
        elif ptype == "array":
            if not isinstance(value, list):
                return False
            items = prop.get("items", {})
            itype = items.get("type")
            for item in value:
                if itype == "string":
                    if not isinstance(item, str):
                        return False
                elif itype == "integer" and (not isinstance(item, int) or isinstance(item, bool)):
                    return False
    return True


def build_tool_registry() -> ToolRegistry:
    from src.application import tool_schemas

    registry = ToolRegistry()
    registry.register(
        ToolSchema(
            name="search_manuals",
            required_role=Role.TECHNICIAN,
            read=True,
            schema=tool_schemas.schema_search_manuals()["schema"],
        ),
    )
    registry.register(
        ToolSchema(
            name="get_document_revisions",
            required_role=Role.TECHNICIAN,
            read=True,
            schema=tool_schemas.schema_get_document_revisions()["schema"],
        ),
    )
    registry.register(
        ToolSchema(
            name="get_safety_prerequisites",
            required_role=Role.TECHNICIAN,
            read=True,
            schema=tool_schemas.schema_get_safety_prerequisites()["schema"],
        ),
    )
    registry.register(
        ToolSchema(
            name="create_work_order_draft",
            required_role=Role.TECHNICIAN,
            read=False,
            schema=tool_schemas.schema_create_work_order_draft()["schema"],
        ),
    )
    registry.register(
        ToolSchema(
            name="acknowledge_safety_steps",
            required_role=Role.TECHNICIAN,
            read=False,
            schema=tool_schemas.schema_acknowledge_safety_steps()["schema"],
        ),
    )
    return registry
