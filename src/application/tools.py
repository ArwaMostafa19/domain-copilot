"""A tiny tool registry with schema validation and role checks.

Tools are executed only after their arguments are validated and the caller's
role is allowed. Tool results are treated as untrusted: callers must wrap them
the same way evidence is wrapped before putting them into a prompt.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass

from src.domain.workflow import Role, WorkflowError

AGENT_TOOL_ALLOWLISTS: Mapping[str, frozenset[str]] = {
    "SymptomMatcher": frozenset({"search_manuals", "get_document_revisions"}),
    "DiagnosticSafetyPlanner": frozenset({"get_safety_prerequisites"}),
    "WorkOrderGenerator": frozenset({"create_work_order_draft"}),
    "WorkflowOrchestrator": frozenset({"acknowledge_safety_steps"}),
}


class ToolValidationError(WorkflowError):
    """The arguments do not match a tool's schema."""


class ApprovalRequiredError(WorkflowError):
    """A side-effecting tool requires a recorded supervisor approval."""


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
        self._approved_runs: set[str] = set()

    def approve_run(self, run_id: str, role: Role) -> None:
        if role != Role.SUPERVISOR:
            raise ToolNotAllowedError("only a supervisor may authorize a write tool")
        self._approved_runs.add(run_id)

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
            name == "create_work_order_draft" and role == Role.SUPERVISOR
        ):
            raise ToolNotAllowedError(f"role {role.value} may not use {name}")
        if not validate_args(args, schema.schema):
            raise ToolValidationError(f"invalid arguments for {name}")
        if not schema.read and name == "create_work_order_draft":
            run_id = args.get("run_id")
            if role != Role.SUPERVISOR or run_id not in self._approved_runs:
                raise ApprovalRequiredError("supervisor approval is required before this write")
        handler = self._handlers.get(name)
        if handler is None:
            raise WorkflowError(f"tool {name} is not implemented")
        return handler(**args)

    def invoke_for_agent(
        self,
        agent: str,
        name: str,
        args: Mapping[str, object],
        role: Role,
    ) -> object:
        """Enforce the named agent's allow-list before normal schema/role checks."""
        allowed = AGENT_TOOL_ALLOWLISTS.get(agent)
        if allowed is None or name not in allowed:
            raise ToolNotAllowedError(f"agent {agent!r} may not use {name!r}")
        return self.invoke(name, args, role)

    def allowed_for(self, role: Role) -> list[str]:
        allowed: list[str] = []
        for schema in self._schemas.values():
            if role == schema.required_role:
                allowed.append(schema.name)
        return sorted(allowed)


def validate_args(args: Mapping[str, object], schema: Mapping[str, object]) -> bool:
    """Validate JSON values recursively against the supported JSON Schema subset."""
    return _matches_schema(dict(args), schema)


def _matches_schema(value: object, schema: Mapping[str, object]) -> bool:
    expected = schema.get("type")
    if expected == "object":
        if not isinstance(value, Mapping):
            return False
        properties = schema.get("properties", {})
        if not isinstance(properties, Mapping):
            return False
        if any(key not in value for key in schema.get("required", [])):
            return False
        if schema.get("additionalProperties") is False and any(key not in properties for key in value):
            return False
        for key, item in value.items():
            nested = properties.get(key)
            if nested is not None and not _matches_schema(item, nested):
                return False
    elif expected == "array":
        if not isinstance(value, list):
            return False
        if len(value) < schema.get("minItems", 0):
            return False
        maximum = schema.get("maxItems")
        if maximum is not None and len(value) > maximum:
            return False
        items_schema = schema.get("items", {})
        if isinstance(items_schema, Mapping) and any(not _matches_schema(item, items_schema) for item in value):
            return False
    elif expected == "string":
        if not isinstance(value, str):
            return False
        if len(value) < schema.get("minLength", 0):
            return False
        maximum = schema.get("maxLength")
        if maximum is not None and len(value) > maximum:
            return False
    elif expected == "integer":
        if not isinstance(value, int) or isinstance(value, bool):
            return False
    elif expected == "number":
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return False
    elif expected == "boolean" and not isinstance(value, bool) or expected == "null" and value is not None:
        return False
    minimum = schema.get("minimum")
    maximum = schema.get("maximum")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if minimum is not None and value < minimum:
            return False
        if maximum is not None and value > maximum:
            return False
    enum = schema.get("enum")
    return enum is None or value in enum


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
