"""Command line entry point for the ingestion dry run.

This is the only module of the pipeline that prints.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.application.chunk import DEFAULT_MAX_CHARS, chunk_document
from src.application.safety_steps import extract_safety_steps
from src.domain.documents import DomainError
from src.infrastructure.extractors import extract

SOURCE_SUFFIXES = (".md", ".pdf")
TENANT_PREFIX = "tenant-"
DATABASE_NOT_YET = "Database writing arrives in the next change; this run wrote nothing."
COLUMNS = ("tenant", "file", "format", "revision", "status", "chunks", "min", "avg", "max", "steps")


def main(argv: list[str] | None = None) -> int:
    """Run the dry run, or report that database writing is not implemented yet."""
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
    if not args.dry_run:
        print(DATABASE_NOT_YET)
        return 2
    return _dry_run(args.corpus_dir, args.max_chars)


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