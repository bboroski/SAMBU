"""Deterministic, language-aware text and prosody diagnostics for SAMBU.

The analysis is intentionally descriptive: it reports measurable patterns and
never claims to score literary quality or infer lexical stress from spelling.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import re
import unicodedata
from typing import Callable

from .values import Record


_WORD_RE = re.compile(r"[^\W\d_]+(?:[’'\-][^\W\d_]+)*", re.UNICODE)
_VOWELS = frozenset("аеёиоуыэюяіїєaeiouy")
_MAX_TEXT_LENGTH = 1_000_000


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
    # Preserve one preceding consonant for open-vowel endings (e.g. пора/гора).
    if len(tail) == 1 and vowel_index > 0:
        tail = normalized[vowel_index - 1:]
    return tail


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


def prosody_profile(args: list[object]) -> Record:
    """Report rough syllable rhythm, line endings, rhyme groups and alliteration."""
    text = _text_arg(args, "prosody_profile(text)")
    source_lines = text.splitlines()
    line_records: list[Record] = []
    syllable_counts: list[int] = []
    rhyme_occurrences: dict[str, list[tuple[int, str]]] = defaultdict(list)
    alliterative_line_count = 0
    total_words = 0
    nonempty_line_count = 0

    for line_number, line in enumerate(source_lines, start=1):
        words = _words(line)
        total_words += len(words)
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
        else:
            count = 0
            ending = ""
            key = ""
            has_alliteration = False
        line_records.append(Record({
            "line_number": line_number,
            "text": line,
            "word_count": len(words),
            "syllable_count": count,
            "end_word": ending,
            "rhyme_key": key,
            "has_alliteration": has_alliteration,
        }))

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
        "lines": line_records,
    })


TEXTCRAFT_BUILTINS: dict[str, Callable[[list[object]], object]] = {
    "syllables": syllables,
    "rhyme_key": rhyme_key,
    "text_profile": text_profile,
    "prosody_profile": prosody_profile,
}
