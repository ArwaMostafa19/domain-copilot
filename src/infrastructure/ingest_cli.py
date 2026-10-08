"""Command line entry point for the ingestion pipeline.

This is the only module of the pipeline that prints.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from src.application.chunk import DEFAULT_MAX_CHARS, chunk_document
from src.application.embedding import GuardedEmbedder
from src.application.ingest import ingest_files
from src.application.safety_steps import extract_safety_steps
from src.domain.documents import DomainError
from src.domain.llm import ConfigError, EmbeddingModelMismatchError
from src.infrastructure.config import load_settings
from src.infrastructure.embedding_registry import PostgresEmbeddingIndexRegistry
from src.infrastructure.extractors import extract
from src.infrastructure.providers.factory import build_embedding_stack
from src.infrastructure.repository import PostgresDocumentRepository


SOURCE_SUFFIXES = (".md", ".pdf")
TENANT_PREFIX = "tenant-"
COLUMNS = ("tenant", "file", "format", "revision", "status", "chunks", "min", "avg", "max", "steps")
INGEST_COLUMNS = ("tenant", "file", "status", "chunks", "steps", "error")
UNKNOWN_TENANT = "-"


def main(argv: list[str] | None = None) -> int:
    """Run the dry run, or ingest every corpus file into PostgreSQL."""
    parser = argparse.ArgumentParser(description="Extract, chunk and read safety steps.")
    parser.add_argument("corpus_dir", type=Path, help="corpus root holding the tenant-* folders")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="report what would be ingested, without writing anything",
    )
    parser.add_argument(
        "--max-chars",
        type=int,
        default=DEFAULT_MAX_CHARS,
        help="largest chunk a section may be packed into (default: %(default)s)",
    )
    args = parser.parse_args(argv)
    if args.dry_run:
        return _dry_run(args.corpus_dir, args.max_chars)
    return _ingest(args.corpus_dir, args.max_chars)


def _ingest(corpus_dir: Path, max_chars: int) -> int:
    """Embed and store every corpus file, then report one row per file."""
    if not os.environ.get("DATABASE_URL"):
        print("error: DATABASE_URL is not set")
        return 2
    if not corpus_dir.is_dir():
        print(f"error: corpus directory does not exist: {corpus_dir.as_posix()}")
        return 2
    if not _tenant_folders(corpus_dir):
        print(
            f"error: corpus directory holds no {TENANT_PREFIX}* folders: "
            f"{corpus_dir.as_posix()}"
        )
        return 2
    files = _corpus_files(corpus_dir)
    if not files:
        print(
            f"error: corpus directory holds no {' or '.join(SOURCE_SUFFIXES)} files under its "
            f"{TENANT_PREFIX}* folders: {corpus_dir.as_posix()}"
        )
        return 2

    try:
        settings = load_settings(os.environ)
        provider, guard = build_embedding_stack(
            settings, PostgresEmbeddingIndexRegistry()
        )
        guard.ensure(settings.embedding_spec())
    except (ConfigError, EmbeddingModelMismatchError) as error:
        print(f"error: {error}")
        return 2

    embedder = GuardedEmbedder(provider, guard, settings.embedding_spec())
    results = ingest_files(
        files,
        embedder,
        PostgresDocumentRepository(),
        max_chars=max_chars,
    )

    rows: list[tuple[str, ...]] = []
    counts: dict[str, int] = dict.fromkeys(("ingested", "skipped", "failed"), 0)
    for path, result in zip(files, results, strict=True):
        counts[result.status] += 1
        rows.append(
            (
                _tenant_of(path, corpus_dir),
                path.name,
                result.status,
                str(result.chunks),
                str(result.steps),
                result.error or "",
            )
        )
    _print_table(INGEST_COLUMNS, rows)
    print()
    print(
        f"totals: ingested={counts['ingested']} skipped={counts['skipped']} "
        f"failed={counts['failed']}"
    )
    print(f"embedding tokens: {embedder.total_usage.total_tokens}")
    return 1 if counts["failed"] else 0



def _dry_run(corpus_dir: Path, max_chars: int) -> int:
    if not corpus_dir.is_dir():
        print(f"error: corpus directory does not exist: {corpus_dir.as_posix()}")
        return 2
    files = _corpus_files(corpus_dir)
    if not _tenant_folders(corpus_dir):
        print(
            f"error: corpus directory holds no {TENANT_PREFIX}* folders: "
            f"{corpus_dir.as_posix()}"
        )
        return 2
    if not files:
        print(
            f"error: corpus directory holds no {' or '.join(SOURCE_SUFFIXES)} files under its "
            f"{TENANT_PREFIX}* folders: {corpus_dir.as_posix()}"
        )
        return 2

    rows: list[tuple[str, ...]] = []
    totals: dict[str, list[int]] = {}
    oversize = 0
    failures: list[tuple[str, str]] = []

    for path in files:
        try:
            doc = extract(path)
            chunks = chunk_document(doc, max_chars=max_chars)
            steps = extract_safety_steps(doc)
        except DomainError as error:
            failures.append((path.as_posix(), str(error)))
            continue
        lengths = [len(chunk.text) for chunk in chunks]
        oversize += sum(1 for length in lengths if length > max_chars)
        tenant = totals.setdefault(doc.meta.tenant_id, [0, 0, 0])
        tenant[0] += 1
        tenant[1] += len(chunks)
        tenant[2] += len(steps)
        rows.append(
            (
                doc.meta.tenant_id,
                path.name,
                doc.meta.source_format,
                doc.meta.revision,
                doc.meta.status,
                str(len(chunks)),
                str(min(lengths)) if lengths else "0",
                f"{sum(lengths) / len(lengths):.1f}" if lengths else "0",
                str(max(lengths)) if lengths else "0",
                str(len(steps)),
            )
        )

    _print_table(COLUMNS, rows)
    _print_totals(totals)
    print(f"chunks longer than {max_chars} characters: {oversize}")
    _print_failures(failures)
    return 1 if failures else 0


def _tenant_folders(corpus_dir: Path) -> list[Path]:
    """The tenant-* sub-directories of a corpus root, sorted, ignoring stray files."""
    return [folder for folder in sorted(corpus_dir.glob(f"{TENANT_PREFIX}*")) if folder.is_dir()]


def _corpus_files(corpus_dir: Path) -> list[Path]:
    files: list[Path] = []
    for folder in _tenant_folders(corpus_dir):
        for path in folder.rglob("*"):
            if path.is_file() and path.suffix.lower() in SOURCE_SUFFIXES:
                files.append(path)
    return sorted(files)


def _tenant_of(path: Path, corpus_dir: Path) -> str:
    """The tenant-* folder holding a file, or '-' when the file has none."""
    try:
        parts = path.relative_to(corpus_dir).parts
    except ValueError:
        return UNKNOWN_TENANT
    return parts[0] if len(parts) > 1 else UNKNOWN_TENANT


def _print_table(columns: tuple[str, ...], rows: list[tuple[str, ...]]) -> None:
    widths = [len(column) for column in columns]
    for row in rows:
        widths = [max(width, len(value)) for width, value in zip(widths, row)]
    print("  ".join(column.ljust(width) for column, width in zip(columns, widths)).rstrip())
    for row in rows:
        print("  ".join(value.ljust(width) for value, width in zip(row, widths)).rstrip())


def _print_totals(totals: dict[str, list[int]]) -> None:
    print()
    print("totals per tenant:")
    for tenant, (files, chunks, steps) in sorted(totals.items()):
        print(f"  {tenant}: files={files} chunks={chunks} safety_steps={steps}")


def _print_failures(failures: list[tuple[str, str]]) -> None:
    print()
    if not failures:
        print("failed files: none")
        return
    print(f"failed files: {len(failures)}")
    for path, message in failures:
        print(f"  {path}: {message}")


if __name__ == "__main__":
    sys.exit(main())
