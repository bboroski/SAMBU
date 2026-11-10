"""Unicode script inspection for source editors and static-analysis tools.

This module reports writing-system composition without transliterating,
normalizing, rewriting, or rejecting source text. Offsets are zero-based
Unicode code-point offsets, matching sambu.source.
"""
from __future__ import annotations

from dataclasses import dataclass
import unicodedata


@dataclass(frozen=True, slots=True)
class ScriptRun:
    """A contiguous run of characters classified under one script family."""

    script: str
    start_offset: int
    end_offset: int
    text: str


@dataclass(frozen=True, slots=True)
class ScriptProfile:
    """Script composition and conservative mixed-script risk indicators."""

    scripts: tuple[str, ...]
    runs: tuple[ScriptRun, ...]
    mixed: bool
    confusable_mixing: bool


_CONFUSABLE_SCRIPT_SET = frozenset({"Latin", "Greek", "Cyrillic"})


def unicode_script(character: str) -> str:
    """Return a broad, deterministic script family for one Unicode character."""
    if len(character) != 1:
        raise ValueError("unicode_script expects exactly one code point")

    category = unicodedata.category(character)
    if category.startswith("M"):
        return "Inherited"
    if not category.startswith("L"):
        return "Common"

    name = unicodedata.name(character, "")
    if "EGYPTIAN HIEROGLYPH" in name:
        return "Egyptian Hieroglyphic"
    if "COPTIC" in name:
        return "Coptic"

    ordered_families = (
        ("LATIN", "Latin"), ("CYRILLIC", "Cyrillic"),
        ("GREEK", "Greek"), ("ARABIC", "Arabic"),
        ("HEBREW", "Hebrew"), ("HIRAGANA", "Hiragana"),
        ("KATAKANA", "Katakana"), ("HANGUL", "Hangul"),
        ("CJK", "Han"), ("IDEOGRAPH", "Han"),
        ("DEVANAGARI", "Devanagari"), ("THAI", "Thai"),
        ("ARMENIAN", "Armenian"), ("GEORGIAN", "Georgian"),
        ("BENGALI", "Bengali"), ("TAMIL", "Tamil"),
        ("TELUGU", "Telugu"), ("ETHIOPIC", "Ethiopic"),
        ("CHEROKEE", "Cherokee"),
        ("CANADIAN SYLLABICS", "Canadian Aboriginal"),
    )
    for marker, family in ordered_families:
        if marker in name:
            return family
    return "Other"


def inspect_script_profile(text: str) -> ScriptProfile:
    """Inspect script runs and flag suspicious Latin/Greek/Cyrillic mixing.

    Neutral punctuation and digits remain in runs as Common but do not
    contribute to the set of scripts. Inherited marks attach to the previous
    script where possible. The input string is never modified.
    """
    value = str(text)
    raw_runs: list[ScriptRun] = []
    script_order: list[str] = []

    for offset, character in enumerate(value):
        script = unicode_script(character)
        if script == "Inherited" and raw_runs:
            script = raw_runs[-1].script

        if raw_runs and raw_runs[-1].script == script:
            previous = raw_runs[-1]
            raw_runs[-1] = ScriptRun(
                script, previous.start_offset, offset + 1,
                previous.text + character,
            )
        else:
            raw_runs.append(ScriptRun(script, offset, offset + 1, character))

        if script not in {"Common", "Inherited"} and script not in script_order:
            script_order.append(script)

    confusable_scripts = set(script_order) & _CONFUSABLE_SCRIPT_SET
    return ScriptProfile(
        scripts=tuple(script_order),
        runs=tuple(raw_runs),
        mixed=len(script_order) > 1,
        confusable_mixing=len(confusable_scripts) > 1,
    )


__all__ = [
    "ScriptProfile", "ScriptRun",
    "inspect_script_profile", "unicode_script",
]
