"""clean_text normalises whitespace and never changes content."""

from __future__ import annotations

from src.application.clean import clean_text

SAMPLE = "## Purpose\r\n\r\nText   with   spacing.\r\n\r\n\r\n\r\n## Notes\r\nEnd   \r\n"


def test_crlf_becomes_lf() -> None:
    assert "\r" not in clean_text("alpha\r\nbeta\r\n")


def test_lone_cr_becomes_lf() -> None:
    assert clean_text("alpha\rbeta") == "alpha\nbeta"


def test_non_breaking_space_becomes_a_normal_space() -> None:
    assert clean_text("240\u00a0bar") == "240 bar"


def test_trailing_whitespace_is_removed_from_every_line() -> None:
    assert clean_text("one   \ntwo\t\nthree \n") == "one\ntwo\nthree"


def test_three_or_more_blank_lines_collapse_to_one() -> None:
    assert clean_text("one\n\n\n\n\ntwo") == "one\n\ntwo"
    assert clean_text("one\n\n\ntwo") == "one\n\ntwo"


def test_leading_and_trailing_blank_lines_are_stripped() -> None:
    assert clean_text("\n\n\n\nbody\n\n\n\n") == "body"


def test_content_is_preserved() -> None:
    cleaned = clean_text(SAMPLE)
    assert "Text   with   spacing." in cleaned
    assert cleaned.split() == SAMPLE.replace("\r\n", "\n").split()


def test_markdown_syntax_is_untouched() -> None:
    source = "## Title\n\n| a | b |\n| --- | --- |\n| 1 | 2 |\n\n- item\n  - nested"
    assert clean_text(source) == source
    assert clean_text(source + "\n\n") == source


def test_is_idempotent() -> None:
    for source in ("", "  \n\n", SAMPLE, "\u00a0nbsp\u00a0", "one\n\n\n\ntwo\n"):
        once = clean_text(source)
        assert clean_text(once) == once


def test_empty_input_stays_empty() -> None:
    assert clean_text("") == ""
    assert clean_text("\n\r\n \n") == ""