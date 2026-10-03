"""Deterministic Markdown to PDF export for the synthetic corpus.

Usage
-----
    python scripts/export_corpus_pdf.py
    python scripts/export_corpus_pdf.py --out build/corpus-pdf
    python scripts/export_corpus_pdf.py --tenant tenant-alpha

The committed corpus is Markdown. This script produces a second, byte
identical on every run, PDF rendition of the same corpus so that the ingestion
stage can be exercised against two input formats without adding a dependency
to the project. It uses only the Python standard library.

The exporter is a preview tool, not a typesetting engine: it uses one font,
left aligned text, and a fixed layout, so page breaks fall where they fall.
"""

from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS_DIR = ROOT / "corpus"
DEFAULT_OUT = CORPUS_DIR / "_export" / "pdf"

PAGE_WIDTH = 595
PAGE_HEIGHT = 842
MARGIN_X = 50
MARGIN_TOP = 792
LINE_HEIGHT = 12
BODY_SIZE = 9
MAX_CHARS_PER_LINE = 96

NARROW = set("iljtfrI.,:;'|!()[]{}-")


def char_width(char: str) -> float:
    """Rough Helvetica advance width as a fraction of the font size."""

    if char in NARROW:
        return 0.30
    if char.isupper():
        return 0.68
    if char.isdigit():
        return 0.56
    return 0.53


def text_width(text: str, size: float) -> float:
    return sum(char_width(char) for char in text) * size


def wrap(text: str, size: float, width: float) -> list[str]:
    words = text.split()
    if not words:
        return [""]
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if text_width(candidate, size) <= width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def strip_inline(text: str) -> str:
    for token in ("**", "__", "`"):
        text = text.replace(token, "")
    return text


def markdown_lines(markdown: str) -> list[tuple[str, int, str]]:
    """Convert Markdown to (font, size, text) display lines."""

    lines: list[tuple[str, int, str]] = []
    usable = PAGE_WIDTH - 2 * MARGIN_X

    in_front_matter = False
    front_matter_seen = False
    for raw in markdown.splitlines():
        stripped = raw.rstrip()

        if not front_matter_seen and stripped == "---":
            in_front_matter = True
            front_matter_seen = True
            continue
        if in_front_matter:
            if stripped == "---":
                in_front_matter = False
                lines.append(("F1", 4, ""))
            continue

        if not stripped:
            lines.append(("F1", BODY_SIZE, ""))
            continue

        if stripped.startswith("## "):
            lines.append(("F1", 4, ""))
            lines.extend(("F2", 11, part) for part in wrap(strip_inline(stripped[3:]), 11, usable))
            lines.append(("F1", 4, ""))
        elif stripped.startswith("# "):
            lines.extend(("F2", 14, part) for part in wrap(strip_inline(stripped[2:]), 14, usable))
            lines.append(("F1", 4, ""))
        elif stripped.startswith("### "):
            lines.extend(("F2", 10, part) for part in wrap(strip_inline(stripped[4:]), 10, usable))
        elif stripped.startswith("| "):
            lines.extend(("F1", BODY_SIZE, part) for part in wrap(strip_inline(stripped), BODY_SIZE, usable))
        elif stripped.startswith("- "):
            body = f"    {strip_inline(stripped[2:])}"
            lines.extend(("F1", BODY_SIZE, part) for part in wrap(body, BODY_SIZE, usable))
        else:
            lines.extend(("F1", BODY_SIZE, part) for part in wrap(strip_inline(stripped), BODY_SIZE, usable))

    return lines


def paginate(lines: list[tuple[str, int, str]]) -> list[list[tuple[str, int, float, str]]]:
    pages: list[list[tuple[str, int, float, str]]] = []
    page: list[tuple[str, int, float, str]] = []
    y = MARGIN_TOP

    for font, size, text in lines:
        if y < 56:
            pages.append(page)
            page = []
            y = MARGIN_TOP
        page.append((font, size, y, text))
        y -= LINE_HEIGHT if size <= BODY_SIZE else LINE_HEIGHT + 2

    if page:
        pages.append(page)
    return pages


def escape(text: str) -> bytes:
    encoded = text.encode("cp1252", "replace")
    out = bytearray()
    for byte in encoded:
        if byte in (0x28, 0x29, 0x5C):
            out.append(0x5C)
        out.append(byte)
    return bytes(out)


def content_stream(page: list[tuple[str, int, float, str]]) -> bytes:
    parts = [b"BT"]
    for font, size, y, text in page:
        parts.append(f"/{font} {size} Tf".encode("ascii"))
        parts.append(f"1 0 0 1 {MARGIN_X} {y:.1f} Tm".encode("ascii"))
        parts.append(b"(" + escape(text) + b") Tj")
    parts.append(b"ET")
    return b"\n".join(parts)


def build_pdf(pages: list[list[tuple[str, int, float, str]]]) -> bytes:
    objects: list[bytes] = []
    page_count = len(pages)

    kids = " ".join(f"{5 + index * 2} 0 R" for index in range(page_count))

    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    objects.append(f"<< /Type /Pages /Kids [{kids}] /Count {page_count} >>".encode("ascii"))
    objects.append(
        (
            "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>"
        ).encode("ascii")
    )
    objects.append(
        (
            "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>"
        ).encode("ascii")
    )

    for page in pages:
        stream = content_stream(page)
        objects.append(
            (
                "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 "
                f"{PAGE_WIDTH} {PAGE_HEIGHT}] /Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> "
                f"/Contents {len(objects) + 2} 0 R >>"
            ).encode("ascii")
        )
        objects.append(b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream")

    out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets: list[int] = []
    for number, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{number} 0 obj\n".encode("ascii") + body + b"\nendobj\n"

    xref_offset = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode("ascii")
    out += b"0000000000 65535 f \n"
    for offset in offsets:
        out += f"{offset:010d} 00000 n \n".encode("ascii")
    out += f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("ascii")
    return bytes(out)


def render(markdown: str) -> tuple[bytes, int]:
    """Render Markdown text to (PDF bytes, page count). Deterministic."""

    pages = paginate(markdown_lines(markdown))
    return build_pdf(pages), len(pages)


def export(source: Path, destination: Path) -> int:
    data, page_count = render(source.read_text(encoding="utf-8"))
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    return page_count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="output directory")
    parser.add_argument("--tenant", help="limit the export to one tenant directory")
    arguments = parser.parse_args()

    sources = sorted(path for path in CORPUS_DIR.glob("*/*.md"))
    if arguments.tenant:
        sources = [path for path in sources if path.parent.name == arguments.tenant]
    if not sources:
        print("no Markdown documents found")
        return 1

    total_pages = 0
    for source in sources:
        relative = source.relative_to(CORPUS_DIR).with_suffix(".pdf")
        total_pages += export(source, arguments.out / relative)
        print(f"{relative} -> {arguments.out / relative}")

    print(f"{len(sources)} documents, {total_pages} pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())