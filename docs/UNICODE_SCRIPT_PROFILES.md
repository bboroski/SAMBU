# Unicode Script Profiles

SAMBU can preserve multilingual source while giving editors and static-analysis
tools a deterministic view of the writing systems used in a token or text
fragment. The implementation lives in sambu.script_profiles.

## What it does

inspect_script_profile(text) returns the script families in first-seen order,
contiguous ScriptRun ranges with zero-based, end-exclusive code-point offsets,
a mixed flag, and a conservative confusable_mixing warning for combinations
of Latin, Greek and Cyrillic letters.

The classifier distinguishes Latin, Greek, Cyrillic, Arabic, Hebrew, Coptic,
Egyptian Hieroglyphic, Han, Hiragana, Katakana, Hangul, Devanagari and several
other Unicode script families. Combining marks inherit the preceding run when
possible. Digits, punctuation and symbols are classified as Common.

## Safety and compatibility contract

This is a reporting API, not a source transformation:

- source text is never transliterated, case-folded, normalized or rewritten;
- offsets follow the Unicode code-point convention used by sambu.source;
- mixed-script output is a review signal, not proof of spoofing or maliciousness;
- multilingual comments and string literals are valid data and must not be
  rejected merely because they contain more than one script;
- the module does not claim to decode hieratic or demotic handwriting, parse
  ancient Egyptian grammar, or transliterate hieroglyphs into a historical
  pronunciation.

The historical progression from hieroglyphic, hieratic and demotic writing to
Coptic illustrates why software must distinguish semantic grammar from the
script used to represent it. SAMBU applies that lesson as an explicit Unicode
inspection layer, not as a claim that these writing systems share one
interchangeable encoding.

## Usage

~~~python
from sambu.script_profiles import inspect_script_profile

profile = inspect_script_profile("pаypal")  # second character is Cyrillic
if profile.confusable_mixing:
    print("Review identifier for mixed-script lookalikes")
~~~

Run the focused tests with:

~~~bash
python -m unittest tests.test_script_profiles -v
~~~

## Extension rules

New script families must be covered by representative Unicode code points,
retain source offsets, and avoid classifying punctuation as a letter script.
Do not silently normalize source during lexing: canonical-equivalence policy
must be an explicit, separately versioned language decision.
