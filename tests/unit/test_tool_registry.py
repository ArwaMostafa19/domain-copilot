from src.application import tools
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