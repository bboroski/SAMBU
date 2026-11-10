"""Deterministic, language-aware text and prosody diagnostics for SAMBU.

The analysis is descriptive: it reports measurable patterns and never claims
to score literary quality, identify a definitive language, or infer lexical
stress from spelling.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import re
import unicodedata
from typing import Callable

from .values import Record


_WORD_RE = re.compile(r"[^\W\d_]+(?:[’'\-][^\W\d_]+)*", re.UNICODE)
_HEADER_RE = re.compile(r"^\s*\[\s*([^\]]+?)\s*\]\s*:?\s*$")
_PAREN_HEADER_RE = re.compile(r"^\s*\(\s*([^()]+?)\s*\)\s*:?\s*$")
_BARE_HEADER_RE = re.compile(
    r"^\s*(intro|verse(?:\s+\d+)?|pre[ -]?chorus|chorus|hook|bridge|outro|"
    r"интро|куплет(?:\s+\d+)?|предприпев|припев|хук|бридж|аутро)\s*:?\s*$",
    re.IGNORECASE,
)
_VOWELS = frozenset("аеёиоуыэюяіїєaeiouy")
_MAX_TEXT_LENGTH = 1_000_000

_SECTION_ALIASES = {
    "intro": "intro", "интро": "intro",
    "verse": "verse", "куплет": "verse",
    "pre chorus": "pre_chorus", "pre-chorus": "pre_chorus",
    "предприпев": "pre_chorus",
    "chorus": "chorus", "hook": "chorus", "припев": "chorus", "хук": "chorus",
    "melody sing chorus": "chorus", "melodic chorus": "chorus",
    "bridge": "bridge", "бридж": "bridge",
    "outro": "outro", "аутро": "outro",
}


def _text_arg(args: list[object], signature: str) -> str:
    if len(args) != 1:
        raise TypeError(f"{signature} expects 1 argument")
    value = args[0]
    if not isinstance(value, str):
        raise TypeError(f"{signature} expects a string")
    if len(value) > _MAX_TEXT_LENGTH:
        raise ValueError(f"{signature} accepts at most {_MAX_TEXT_LENGTH:,} characters")
    return unicodedata.normalize("NFC", value)


def _words(text: str) -> list[str]:
    return [match.group(0).casefold() for match in _WORD_RE.finditer(text)]


def _raw_words(text: str) -> list[str]:
    return [match.group(0) for match in _WORD_RE.finditer(text)]


def _syllable_count(word: str) -> int:
    """Estimate syllables by counting vowel nuclei; lexical stress is not inferred."""
    count = 0
    previous_was_vowel = False
    for character in unicodedata.normalize("NFC", word).casefold():
        is_vowel = character in _VOWELS
        if is_vowel and not previous_was_vowel:
            count += 1
        previous_was_vowel = is_vowel
    return count


def _rhyme_key(word: str) -> str:
    """Return an approximate spelling-based tail from the final vowel nucleus."""
    normalized = unicodedata.normalize("NFC", word).casefold().rstrip("ьъ")
    vowel_index = max((i for i, char in enumerate(normalized) if char in _VOWELS), default=-1)
    if vowel_index < 0:
        return ""
    tail = normalized[vowel_index:]
    if len(tail) == 1 and vowel_index > 0:
        tail = normalized[vowel_index - 1:]
    return tail


def _section_kind(label: str) -> str:
    normalized = re.sub(r"\s+", " ", label.casefold().replace("_", " ").strip())
    normalized = re.sub(r":+$", "", normalized).strip()
    normalized = re.sub(r"\s+\d+$", "", normalized)
    return _SECTION_ALIASES.get(normalized, "custom")


def _section_performance_hint(label: str) -> str:
    """Extract only explicit delivery hints written in a section label."""
    normalized = label.casefold()
    if "melod" in normalized or "sing" in normalized:
        return "melodic"
    if "spoken" in normalized or "talk" in normalized:
        return "spoken"
    if "adlib" in normalized or "ad-lib" in normalized:
        return "ad_lib"
    if "rap" in normalized:
        return "rap"
    return "unspecified"


def _section_header(line: str) -> str | None:
    for pattern in (_HEADER_RE, _PAREN_HEADER_RE, _BARE_HEADER_RE):
        match = pattern.fullmatch(line)
        if match:
            return match.group(1).strip()
    return None


def syllables(args: list[object]) -> int:
    """Return an approximate syllable count for one word."""
    word = _text_arg(args, "syllables(word)").strip()
    if not word:
        return 0
    return _syllable_count(word)


def rhyme_key(args: list[object]) -> str:
    """Return a rough final-vowel spelling key for rhyme exploration."""
    word = _text_arg(args, "rhyme_key(word)").strip()
    if not word:
        return ""
    tokens = _words(word)
    return _rhyme_key(tokens[-1]) if tokens else ""


def text_profile(args: list[object]) -> Record:
    """Summarize line, word, lexical-diversity and punctuation statistics."""
    text = _text_arg(args, "text_profile(text)")
    lines = text.splitlines()
    nonempty_lines = [line for line in lines if line.strip()]
    words = _words(text)
    frequencies = Counter(words)
    punctuation_count = sum(unicodedata.category(char).startswith("P") for char in text)
    letter_count = sum(char.isalpha() for char in text)
    top_words = [
        Record({"word": word, "count": count})
        for word, count in sorted(frequencies.items(), key=lambda item: (-item[1], item[0]))[:10]
    ]
    word_count = len(words)
    return Record({
        "character_count": len(text),
        "line_count": len(lines),
        "nonempty_line_count": len(nonempty_lines),
        "word_count": word_count,
        "unique_word_count": len(frequencies),
        "lexical_diversity": len(frequencies) / word_count if word_count else 0.0,
        "average_words_per_line": word_count / len(nonempty_lines) if nonempty_lines else 0.0,
        "letter_count": letter_count,
        "punctuation_count": punctuation_count,
        "top_words": top_words,
    })


def language_mix_profile(args: list[object]) -> Record:
    """Count writing systems and lines that visibly switch between Latin and Cyrillic."""
    text = _text_arg(args, "language_mix_profile(text)")
    latin_words = 0
    cyrillic_words = 0
    other_script_words = 0
    mixed_script_words = 0
    switched_lines: list[int] = []

    for line_number, line in enumerate(text.splitlines(), start=1):
        line_scripts: set[str] = set()
        for token in _words(line):
            scripts = set()
            for character in token:
                if not character.isalpha():
                    continue
                name = unicodedata.name(character, "")
                if name.startswith("LATIN "):
                    scripts.add("latin")
                elif name.startswith("CYRILLIC "):
                    scripts.add("cyrillic")
                elif name:
                    scripts.add("other")
            if len(scripts) > 1:
                mixed_script_words += 1
            elif scripts == {"latin"}:
                latin_words += 1
                line_scripts.add("latin")
            elif scripts == {"cyrillic"}:
                cyrillic_words += 1
                line_scripts.add("cyrillic")
            elif scripts == {"other"}:
                other_script_words += 1
                line_scripts.add("other")
        if "latin" in line_scripts and "cyrillic" in line_scripts:
            switched_lines.append(line_number)

    counts = {"latin": latin_words, "cyrillic": cyrillic_words, "other": other_script_words}
    maximum = max(counts.values(), default=0)
    leaders = [name for name, count in counts.items() if count == maximum and count > 0]
    dominant = leaders[0] if len(leaders) == 1 else "balanced" if leaders else "none"
    total = latin_words + cyrillic_words + other_script_words + mixed_script_words
    return Record({
        "word_count": total,
        "latin_word_count": latin_words,
        "cyrillic_word_count": cyrillic_words,
        "other_script_word_count": other_script_words,
        "mixed_script_word_count": mixed_script_words,
        "code_switch_line_count": len(switched_lines),
        "code_switch_lines": switched_lines,
        "dominant_script": dominant,
        "scope": "writing_systems_not_language_identification",
    })


def text_structure_profile(args: list[object]) -> Record:
    """Extract common song/prose sections and exact repeated refrain blocks."""
    text = _text_arg(args, "text_structure_profile(text)")
    lines = text.splitlines()
    sections: list[Record] = []
    current_label = "Body"
    current_kind = "body"
    current_lines: list[tuple[int, str]] = []
    header_count = 0

    def flush() -> None:
        if not current_lines:
            return
        section_text = "\n".join(line for _, line in current_lines)
        normalized = "\n".join(" ".join(_words(line)) for _, line in current_lines).strip()
        sections.append(Record({
            "index": len(sections),
            "label": current_label,
            "kind": current_kind,
            "performance_hint": _section_performance_hint(current_label),
            "start_line": current_lines[0][0],
            "end_line": current_lines[-1][0],
            "line_count": len(current_lines),
            "word_count": len(_words(section_text)),
            "text": section_text,
            "normalized_text": normalized,
        }))

    for line_number, line in enumerate(lines, start=1):
        header = _section_header(line)
        if header is not None:
            flush()
            current_lines = []
            current_label = header
            current_kind = _section_kind(header)
            header_count += 1
        else:
            current_lines.append((line_number, line))
    flush()

    kind_counts = Counter(str(section.get("kind")) for section in sections)
    refrain_occurrences: dict[str, list[Record]] = defaultdict(list)
    for section in sections:
        normalized = str(section.get("normalized_text") or "")
        if section.get("kind") == "chorus" and normalized:
            refrain_occurrences[normalized].append(section)

    refrain_groups = []
    for normalized, occurrences in refrain_occurrences.items():
        if len(occurrences) < 2:
            continue
        refrain_groups.append(Record({
            "repeat_count": len(occurrences),
            "section_indices": [item.get("index") for item in occurrences],
            "labels": [item.get("label") for item in occurrences],
            "line_count": occurrences[0].get("line_count"),
            "normalized_text": normalized,
        }))
    refrain_groups.sort(key=lambda group: (-int(group.get("repeat_count")), str(group.get("normalized_text"))))

    line_occurrences: dict[str, list[int]] = defaultdict(list)
    line_originals: dict[str, str] = {}
    for line_number, line in enumerate(lines, start=1):
        normalized = " ".join(_words(line))
        if normalized:
            line_occurrences[normalized].append(line_number)
            line_originals.setdefault(normalized, line.strip())
    repeated_line_groups = [
        Record({"text": line_originals[key], "lines": locations, "repeat_count": len(locations)})
        for key, locations in line_occurrences.items()
        if len(locations) > 1
    ]
    repeated_line_groups.sort(key=lambda group: (-int(group.get("repeat_count")), str(group.get("text"))))

    return Record({
        "line_count": len(lines),
        "header_count": header_count,
        "section_count": len(sections),
        "has_section_headers": header_count > 0,
        "section_kind_counts": Record(dict(sorted(kind_counts.items()))),
        "sections": sections,
        "refrain_groups": refrain_groups,
        "repeated_line_groups": repeated_line_groups,
    })


def prosody_profile(args: list[object]) -> Record:
    """Report rough syllable rhythm, rhyme groups, internal echoes and marked casing."""
    text = _text_arg(args, "prosody_profile(text)")
    source_lines = text.splitlines()
    line_records: list[Record] = []
    syllable_counts: list[int] = []
    rhyme_occurrences: dict[str, list[tuple[int, str]]] = defaultdict(list)
    alliterative_line_count = 0
    internal_rhyme_line_count = 0
    total_words = 0
    nonempty_line_count = 0
    marked_case_words: list[str] = []

    for line_number, line in enumerate(source_lines, start=1):
        words = _words(line)
        raw_words = _raw_words(line)
        total_words += len(words)
        line_internal_groups = []
        if words:
            nonempty_line_count += 1
            count = sum(_syllable_count(word) for word in words)
            syllable_counts.append(count)
            ending = words[-1]
            key = _rhyme_key(ending)
            if key:
                rhyme_occurrences[key].append((line_number, ending))

            consonant_onsets = [
                word[0] for word in words
                if word[0].isalpha() and word[0] not in _VOWELS
            ]
            has_alliteration = (
                len(consonant_onsets) > 1
                and len(set(consonant_onsets)) < len(consonant_onsets)
            )
            if has_alliteration:
                alliterative_line_count += 1

            internal_occurrences: dict[str, list[str]] = defaultdict(list)
            for word in words:
                word_key = _rhyme_key(word)
                if word_key:
                    internal_occurrences[word_key].append(word)
            for rhyme, matches in internal_occurrences.items():
                unique_matches = list(dict.fromkeys(matches))
                if len(unique_matches) >= 2:
                    line_internal_groups.append(Record({
                        "key": rhyme,
                        "words": unique_matches,
                        "line_number": line_number,
                    }))
            if line_internal_groups:
                internal_rhyme_line_count += 1
        else:
            count = 0
            ending = ""
            key = ""
            has_alliteration = False

        for raw in raw_words:
            letters = [character for character in raw if character.isalpha()]
            # A normal sentence-initial capital is not an authorial cue.
            # Detect an uppercase letter after the first character instead.
            if any(character.islower() for character in letters) and any(
                character.isupper() for character in letters[1:]
            ):
                marked_case_words.append(raw)

        line_records.append(Record({
            "line_number": line_number,
            "text": line,
            "word_count": len(words),
            "syllable_count": count,
            "end_word": ending,
            "rhyme_key": key,
            "has_alliteration": has_alliteration,
            "internal_rhyme_groups": line_internal_groups,
        }))

        if len(marked_case_words) > 256:
            marked_case_words = marked_case_words[:256]

    rhyme_groups: list[Record] = []
    participating_lines: set[int] = set()
    for key, occurrences in rhyme_occurrences.items():
        distinct_endings = list(dict.fromkeys(word for _, word in occurrences))
        if len(distinct_endings) < 2:
            continue
        line_numbers = [line_number for line_number, _ in occurrences]
        participating_lines.update(line_numbers)
        rhyme_groups.append(Record({
            "key": key,
            "words": distinct_endings,
            "lines": line_numbers,
            "count": len(occurrences),
        }))
    rhyme_groups.sort(key=lambda group: (-int(group.get("count")), str(group.get("key"))))

    if syllable_counts:
        average = sum(syllable_counts) / len(syllable_counts)
        variance = sum((value - average) ** 2 for value in syllable_counts) / len(syllable_counts)
        syllable_range = max(syllable_counts) - min(syllable_counts)
    else:
        average = 0.0
        variance = 0.0
        syllable_range = 0

    return Record({
        "line_count": len(source_lines),
        "nonempty_line_count": nonempty_line_count,
        "word_count": total_words,
        "syllable_counts": syllable_counts,
        "average_syllables_per_line": average,
        "syllable_variance": variance,
        "syllable_range": syllable_range,
        "rhyme_groups": rhyme_groups,
        "rhyme_density": len(participating_lines) / nonempty_line_count if nonempty_line_count else 0.0,
        "alliterative_line_count": alliterative_line_count,
        "alliteration_density": alliterative_line_count / nonempty_line_count if nonempty_line_count else 0.0,
        "internal_rhyme_line_count": internal_rhyme_line_count,
        "internal_rhyme_density": internal_rhyme_line_count / nonempty_line_count if nonempty_line_count else 0.0,
        "marked_case_words": marked_case_words,
        "marked_case_word_count": len(marked_case_words),
        "lines": line_records,
    })




def performance_cues_profile(args: list[object]) -> Record:
    """Report explicit stage, parenthetical, quoted and elongated-word cues.

    This is a markup detector, not speech recognition. It does not infer
    speaker identity, emotion, pronunciation, or whether a cue should be used.
    """
    text = _text_arg(args, "performance_cues_profile(text)")
    patterns = (
        ("stage_direction", re.compile(r"\*([^*\n]{1,160})\*")),
        ("parenthetical_aside", re.compile(r"\(([^()\n]{1,160})\)")),
        ("quoted_phrase", re.compile(r'"([^"\n]{1,160})"|“([^”\n]{1,160})”|«([^»\n]{1,160})»')),
        ("elongated_spelling", re.compile(
            r"\b(?:[^\W\d_]{1,4}[-–]){2,}[^\W\d_]{1,4}\b",
            re.IGNORECASE,
        )),
    )
    markers: list[Record] = []
    counts: Counter[str] = Counter()
    truncated = False

    for line_number, line in enumerate(text.splitlines(), start=1):
        # Parenthesized and bracketed section headings belong to composition
        # structure, not to the performance-cue stream.
        if _section_header(line) is not None:
            continue
        for kind, pattern in patterns:
            for match in pattern.finditer(line):
                value = next((group for group in match.groups() if group is not None), "")
                if not value.strip():
                    continue
                counts[kind] += 1
                if len(markers) < 1000:
                    markers.append(Record({
                        "kind": kind,
                        "line_number": line_number,
                        "start_column": match.start() + 1,
                        "end_column": match.end() + 1,
                        "text": value.strip(),
                    }))
                else:
                    truncated = True

    return Record({
        "marker_count": sum(counts.values()),
        "stage_direction_count": counts["stage_direction"],
        "parenthetical_aside_count": counts["parenthetical_aside"],
        "quoted_phrase_count": counts["quoted_phrase"],
        "elongated_spelling_count": counts["elongated_spelling"],
        "kind_counts": Record(dict(sorted(counts.items()))),
        "markers": markers,
        "truncated": truncated,
        "scope": "explicit_written_cues_not_performance_or_emotion_inference",
    })


TEXTCRAFT_BUILTINS: dict[str, Callable[[list[object]], object]] = {
    "syllables": syllables,
    "rhyme_key": rhyme_key,
    "text_profile": text_profile,
    "prosody_profile": prosody_profile,
    "language_mix_profile": language_mix_profile,
    "text_structure_profile": text_structure_profile,
    "performance_cues_profile": performance_cues_profile,
}
