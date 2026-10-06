"""src/domain and src/application may only import the standard library."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAYERS = (ROOT / "src" / "domain", ROOT / "src" / "application")
INNER_PACKAGES = ("domain", "application")


def imported_modules(tree: ast.AST) -> list[str]:
    """The absolute module names imported by a parsed module."""
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and not node.level and node.module:
            modules.append(node.module)
    return modules


def is_inside_an_inner_package(module: str) -> bool:
    """True for src.domain.* and src.application.*, false for anything else."""
    parts = module.split(".")
    return len(parts) >= 2 and parts[0] == "src" and parts[1] in INNER_PACKAGES

def is_standard_library(module: str) -> bool:
    """True for `os`, `collections` and also for dotted names like `collections.abc`."""
    return module.split(".")[0] in sys.stdlib_module_names

def test_domain_and_application_import_only_the_standard_library() -> None:
    offenders: list[str] = []
    parsed = 0
    for layer in LAYERS:
        for path in sorted(layer.rglob("*.py")):
            parsed += 1
            relative = path.relative_to(ROOT)
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(relative))
            for module in imported_modules(tree):
                if is_standard_library(module):
                    continue
                if is_inside_an_inner_package(module):
                    continue
                offenders.append(f"{relative.as_posix()} imports {module}")
    assert parsed > 0, "no domain or application module was parsed"
    assert not offenders, offenders


def test_the_parsed_modules_really_do_import_things() -> None:
    """Guard against the architecture test passing because parsing found nothing."""
    imports = 0
    for layer in LAYERS:
        for path in sorted(layer.rglob("*.py")):
            imports += len(imported_modules(ast.parse(path.read_text(encoding="utf-8"))))
    assert imports >= 3, imports


def test_dotted_standard_library_imports_are_accepted_but_other_packages_are_not() -> None:
    assert is_standard_library("collections.abc")
    assert is_standard_library("os")
    assert not is_standard_library("httpx")
    assert not is_standard_library("google.genai")

    