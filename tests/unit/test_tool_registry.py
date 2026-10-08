import pytest

from src.application import tools
from src.application.agents import WorkOrderGenerator
from src.domain.workflow import Role


def test_schema_validation_rejects_extra():
    reg = tools.build_tool_registry()
    try:
        reg.invoke("search_manuals", {"query": "x", "limit": 5, "extra": 1}, Role.TECHNICIAN)
        assert False
    except tools.ToolValidationError:
        pass


def test_role_denial():
    reg = tools.build_tool_registry()
    try:
        reg.invoke("search_manuals", {"query": "x", "limit": 5}, Role.SUPERVISOR)
        assert False
    except tools.ToolNotAllowedError:
        pass


def test_unknown_tool():
    reg = tools.build_tool_registry()
    try:
        reg.invoke("nope", {}, Role.TECHNICIAN)
        assert False
    except tools.ToolNotAllowedError:
        pass


def test_agent_allow_lists_refuse_other_agents_tools():
    registry = tools.ToolRegistry()
    side_effects = []
    schema = tools.ToolSchema(
        name="create_work_order_draft",
        required_role=Role.TECHNICIAN,
        read=False,
        schema={
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
                },
            },
        },
    )
    registry.register(schema, lambda **args: side_effects.append(args))
    generator = WorkOrderGenerator(chain=None)

    with pytest.raises(tools.ToolNotAllowedError):
        registry.invoke_for_agent(
            "SymptomMatcher",
            "create_work_order_draft",
            {"run_id": "r", "title": "t", "symptoms": "s", "diagnostic_steps": []},
            Role.TECHNICIAN,
        )
    assert side_effects == []

    with pytest.raises(tools.ApprovalRequiredError):
        generator.invoke_tool(
            registry,
            "create_work_order_draft",
            {"run_id": "r", "title": "t", "symptoms": "s", "diagnostic_steps": []},
        )
    registry.approve_run("r", Role.SUPERVISOR)
    registry.invoke(
        "create_work_order_draft",
        {"run_id": "r", "title": "t", "symptoms": "s", "diagnostic_steps": []},
        Role.SUPERVISOR,
    )
    assert len(side_effects) == 1


@pytest.mark.parametrize(
    ("agent", "tool"),
    [
        (agent, tool)
        for agent, allowed in tools.AGENT_TOOL_ALLOWLISTS.items()
        for tool in set().union(*tools.AGENT_TOOL_ALLOWLISTS.values()) - allowed
    ],
)
def test_every_agent_refuses_tools_outside_its_allow_list(agent, tool):
    with pytest.raises(tools.ToolNotAllowedError):
        tools.ToolRegistry().invoke_for_agent(agent, tool, {}, Role.TECHNICIAN)


def test_schema_validation_happens_before_side_effect():
    registry = tools.ToolRegistry()
    side_effects = []
    registry.register(
        tools.ToolSchema(
            name="create_work_order_draft",
            required_role=Role.TECHNICIAN,
            read=False,
            schema={
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
                    },
                },
            },
        ),
        lambda **args: side_effects.append(args),
    )

    with pytest.raises(tools.ToolValidationError):
        registry.invoke_for_agent(
            "WorkOrderGenerator",
            "create_work_order_draft",
            {"run_id": "r", "title": "t", "symptoms": "s", "diagnostic_steps": [1]},
            Role.TECHNICIAN,
        )
    assert side_effects == []
