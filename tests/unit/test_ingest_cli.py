"""The dry run rejects a corpus directory it cannot ingest."""

from __future__ import annotations

from pathlib import Path

from src.infrastructure.ingest_cli import main


def test_a_corpus_directory_that_does_not_exist_is_an_error(tmp_path: Path, capsys) -> None:
    missing = tmp_path / "does-not-exist"

    assert main(["--dry-run", str(missing)]) == 2

    out = capsys.readouterr().out
    assert "does not exist" in out
    assert "does-not-exist" in out
    assert "failed files: none" not in out


def test_a_corpus_directory_without_tenant_folders_is_an_error(tmp_path: Path, capsys) -> None:
    (tmp_path / "documents").mkdir()
    (tmp_path / "README.md").write_text("not a tenant folder\n", encoding="utf-8")

    assert main(["--dry-run", str(tmp_path)]) == 2

    out = capsys.readouterr().out
    assert "no tenant-* folders" in out
    assert "failed files: none" not in out


def test_a_tenant_folder_without_source_files_is_an_error(tmp_path: Path, capsys) -> None:
    tenant = tmp_path / "tenant-x"
    tenant.mkdir()
    (tenant / "notes.txt").write_text("not an ingestible source\n", encoding="utf-8")

    assert main(["--dry-run", str(tmp_path)]) == 2

    out = capsys.readouterr().out
    assert "no .md or .pdf files" in out
    assert "failed files: none" not in out