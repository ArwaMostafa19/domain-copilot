"""Normalise extracted text without changing its content."""

from __future__ import annotations

import re

NON_BREAKING_SPACE = "\u00a0"
_EXTRA_BLANK_LINES = re.compile(r"\n{3,}")


def clean_text(text: str) -> str:
    """Return the text with normalised line endings, spacing and blank lines.

    The function only rewrites whitespace, so no word is ever added, removed or
    reworded, and calling it twice returns the same string as calling it once.
    """
    lines = text.replace("\r\n", "\n").replace("\r", "\n").replace(NON_BREAKING_SPACE, " ")
    return _EXTRA_BLANK_LINES.sub("\n\n", "\n".join(line.rstrip() for line in lines.split("\n"))).strip(
        "\n"
    )





