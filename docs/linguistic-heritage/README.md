# Linguistic Heritage Engine

An evidence-aware research module and interactive reference for historical linguistics. The first case study is Cyrillic **Ы / ы**.

## Implemented

- Dependency-free Python core in `linguistic_heritage/`.
- Structured letter profile with Unicode and IPA metadata.
- Evidence labels: `established`, `qualified`, `hypothesis`, `unsupported`.
- Cautious vowel reference for [i], [ɨ], and [ɯ].
- Static interactive encyclopedia at [index.html](./index.html).
- Unit tests in `tests/test_linguistic_heritage.py`.

## Research guardrails

The source essay is a set of claims to investigate, not a verified authority.

1. The traditional Cyrillic component analysis of ы is **ъ + і**, not ь + ъ.
2. Turkic influence on the emergence or strengthening of the Slavic vowel /ɨ/ remains a hypothesis unless supported by specific historical-linguistic evidence.
3. The Peter I civil-script reform should not be described as a prohibition of ы without primary evidence. Scholarly summaries describe removal of selected other letters from secular printing.
4. Modern Ukrainian uses И rather than Ы in the corresponding standard-language comparison; the historical phonological development is more nuanced than a one-to-one substitution.
5. Grapheme history, phoneme history, and language contact are separate research questions.

## Run tests

From the repository root:

~~~sh
python -m unittest discover -s tests -v
~~~

No third-party runtime dependency is required.

## Initial sources

- Ukrainian linguistic encyclopedia, “Єр, єри”: https://litopys.org.ua/ukrmova/um16.htm
- Unicode Consortium, *Church Slavonic Typography in the Unicode Standard*: https://www.unicode.org/notes/tn41/tn41-1.pdf
- Cambridge, *Handwriting and Bureaucracy* (Petrine civil-script reform): https://www.cambridge.org/core/journals/slavic-review/article/handwriting-and-bureaucracy/54CEF0271483BD8E73A91A8D619D966D

## Next modules

Historical manuscript corpus, grapheme-variant timeline, regional phonology records, source-quality metadata, and a versioned read-only API.
