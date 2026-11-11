"""Dependency-free, evidence-aware linguistic heritage core."""
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Dict, Iterable, List

class ClaimStatus(str, Enum):
    ESTABLISHED = "established"
    QUALIFIED = "qualified"
    HYPOTHESIS = "hypothesis"
    UNSUPPORTED = "unsupported"

@dataclass(frozen=True)
class Claim:
    id: str
    statement: str
    status: ClaimStatus
    rationale: str
    sources: tuple = ()

LETTER_YERY: Dict[str, object] = {
    "id": "cyrillic-yery", "glyph": "Ы", "lowercase": "ы",
    "historical_name": "еры (yery)",
    "unicode": {"uppercase": "U+042B", "lowercase": "U+044B"},
    "ipa_russian": "/ɨ/",
    "description": "A high central unrounded vowel in Russian, conventionally represented as /ɨ/; realization varies by speaker and context.",
    "historical_graphic_analysis": {
        "components": ["Ъ (yer)", "І (iže / i)"],
        "interpretation": "A Cyrillic compound/ligature traditionally analyzed as ъ + і.",
        "caution": "Historical manuscript forms vary; do not reduce every form to one modern shape."
    },
    "language_notes": {
        "russian": "Ы represents a phonemic vowel, typically after non-palatalized consonants.",
        "belarusian": "Ы is a regular alphabetic letter with its own phonological role.",
        "ukrainian": "Modern standard Ukrainian uses И, not Ы; historical orthographies require separate treatment.",
        "south_slavic": "Most modern South Slavic standards do not use Ы as a regular alphabetic letter."
    }
}

CLAIMS: List[Claim] = [
    Claim("yery-ligature", "The Cyrillic letter ы is traditionally analyzed as a compound of ъ and і.",
          ClaimStatus.ESTABLISHED,
          "The component analysis is reflected in Ukrainian linguistic encyclopedia material and historical descriptions.",
          ("https://litopys.org.ua/ukrmova/um16.htm", "https://www.unicode.org/notes/tn41/tn41-1.pdf")),
    Claim("turkic-causation", "Turkic contact caused the original emergence of the Slavic vowel /ɨ/.",
          ClaimStatus.HYPOTHESIS,
          "Contact may be investigated as a hypothesis, but phonetic similarity or geographic proximity alone cannot establish causation."),
    Claim("peter-ban", "Peter I prohibited the letter ы during the civil-script reform.",
          ClaimStatus.UNSUPPORTED,
          "The available scholarly account describes selective removal of other letters from secular printing; it does not substantiate a ban on ы.",
          ("https://www.cambridge.org/core/journals/slavic-review/article/handwriting-and-bureaucracy/54CEF0271483BD8E73A91A8D619D966D",))
]

def analyze_yery() -> Dict[str, object]:
    """Return a JSON-serializable profile with explicit evidence labels."""
    return {
        "letter": LETTER_YERY,
        "claims": [{**asdict(c), "status": c.status.value, "sources": list(c.sources)} for c in CLAIMS],
        "methodology": [
            "Separate grapheme history from phoneme history.",
            "Label hypotheses and unsupported claims explicitly.",
            "Attach sources to historical assertions.",
            "Do not infer borrowing from similarity alone."
        ]
    }

def compare_vowels(symbols: Iterable[str]) -> Dict[str, Dict[str, str]]:
    """Return cautious reference labels for common high unrounded vowels."""
    reference = {
        "i": {"ipa": "[i]", "label": "close front unrounded vowel"},
        "ɨ": {"ipa": "[ɨ]", "label": "close central unrounded vowel"},
        "ɯ": {"ipa": "[ɯ]", "label": "close back unrounded vowel"}
    }
    return {symbol: reference[symbol] for symbol in symbols if symbol in reference}
