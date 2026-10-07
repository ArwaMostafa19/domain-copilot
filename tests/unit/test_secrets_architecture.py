"""API keys may only be read from the environment, and no key is ever committed.

Two independent checks and one self-test per check, so a checker that cannot
fail is caught here.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
TESTS = ROOT / "tests"
DOCS = ROOT / "docs"

# The only modules allowed to touch os.environ/os.getenv. config.py is listed
# even though it takes an environment mapping as an argument, because it is the
# documented place where keys are read.
ALLOWED_ENVIRONMENT_READERS = {
    "infrastructure/config.py",
    "infrastructure/database.py",
    "infrastructure/ingest_cli.py",
    "infrastructure/llm_smoke.py",
    "infrastructure/migrate.py",
}

ENVIRONMENT_NAMES = {"environ", "environb", "getenv"}

TEXT_SUFFIXES = {
    ".py",
    ".md",
    ".txt",
    ".yml",
    ".yaml",
    ".example",
    ".cfg",
    ".toml",
    ".ini",
}

KEY_PATTERNS = (
    ("gsk_", re.compile(r"gsk_[A-Za-z0-9]{20,}")),
    ("AIza", re.compile(r"AIza[0-9A-Za-z_-]{30,}")),
    ("sk-", re.compile(r"sk-[A-Za-z0-9]{20,}")),
)

KEY_ROOTS = (
    SRC,
    TESTS,
    DOCS,
    ROOT / "README.md",
    ROOT / ".env.example",
    ROOT / "docker-compose.yml",
)


def uses_environment(tree: ast.AST) -> bool:
    """True when a parsed module names os.environ, os.getenv or os.environb."""
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Attribute)
            and node.attr in ENVIRONMENT_NAMES
            and isinstance(node.value, ast.Name)
            and node.value.id == "os"
        ):
            return True
        if isinstance(node, ast.ImportFrom) and node.module == "os" and any(
            alias.name in ENVIRONMENT_NAMES for alias in node.names
        ):
            return True
    return False


def find_environment_readers(root: Path) -> list[str]:
    """The .py files under root that read the environment, relative to root."""
    readers: list[str] = []
    for path in sorted(root.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        if uses_environment(tree):
            readers.append(path.relative_to(root).as_posix())
    return readers


def key_names_in_text(text: str) -> list[str]:
    """The names of every key pattern that matches somewhere in text."""
    return [name for name, pattern in KEY_PATTERNS if pattern.search(text)]


def key_names_in_file(path: Path) -> list[str]:
    return key_names_in_text(path.read_text(encoding="utf-8", errors="replace"))


def files_under(paths) -> list[Path]:
    found: list[Path] = []
    for path in paths:
        if path.is_dir():
            found.extend(p for p in sorted(path.rglob("*")) if p.is_file())
        elif path.is_file():
            found.append(path)
    return found


def scan_for_keys(paths) -> list[tuple[Path, str]]:
    """Every (file, pattern name) where a key-shaped literal was found."""
    findings: list[tuple[Path, str]] = []
    for path in files_under(paths):
        if path.name == ".env" or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        for name in key_names_in_file(path):
            findings.append((path, name))
    return findings


def test_only_the_allow_listed_modules_read_the_environment() -> None:
    readers = set(find_environment_readers(SRC))

    assert readers <= ALLOWED_ENVIRONMENT_READERS, sorted(
        readers - ALLOWED_ENVIRONMENT_READERS
    )
    assert "infrastructure/config.py" in ALLOWED_ENVIRONMENT_READERS
    assert "infrastructure/llm_smoke.py" in readers


def test_no_key_shaped_literal_is_committed() -> None:
    findings = scan_for_keys(KEY_ROOTS)

    assert not findings, [str(path) for path, _ in findings]


def test_the_environment_checker_reports_a_reader(tmp_path: Path) -> None:
    sample = tmp_path / "reader.py"
    sample.write_text('import os\nos.environ["SOMETHING"]\n', encoding="utf-8")

    assert find_environment_readers(tmp_path) == ["reader.py"]


def test_the_key_checker_reports_a_secret(tmp_path: Path) -> None:
    secret = "gsk_" + "a" * 30
    sample = tmp_path / "leaky.py"
    sample.write_text(f'KEY = "{secret}"\n', encoding="utf-8")

    findings = scan_for_keys([tmp_path])

    assert [name for _, name in findings] == ["gsk_"]
