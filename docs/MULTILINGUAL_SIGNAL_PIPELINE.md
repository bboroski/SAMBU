# Multilingual Signal Pipeline — Contract v1

**Status:** additive specification for SAMBU Text Craft and the seven-repository ecosystem.  
**Canonical schema:** [`schemas/text-signal-envelope.schema.json`](../schemas/text-signal-envelope.schema.json)

## Purpose

Treat multilingual input as structured evidence rather than assuming that every script is a language, every Latin string is a transliteration, or every repeated phrase carries the same meaning. The pipeline separates source representation, writing-system analysis, structural repetition, caller-supplied hints, and human semantic review.

This is a metadata and diagnostics contract. It does not translate text, identify a language with certainty, infer meaning from sound alone, or authorize external actions.

## Processing stages

1. **Capture and provenance.** The caller owns source text and its retention policy. SAMBU diagnostics receive a bounded string and report measurements; the metadata envelope contains opaque references, not source text.
2. **Normalization.** Text Craft currently normalizes its analysis input to Unicode NFC. Do not discard diacritics, punctuation, repeated characters, case patterns, or original source bytes. If byte-for-byte preservation matters, retain the original separately and keep offset mappings in the caller's source layer.
3. **Writing-system profile.** `language_mix_profile(text)` preserves its legacy Latin/Cyrillic counters and now reports named Unicode script counts by character and token, mixed-script lines, and a dominant Unicode-script indicator. Han, Hiragana, Katakana and Hangul are distinct script categories.
4. **Structure and recurrence.** `text_structure_profile(text)` reports section labels and exact repeated blocks. A returning phrase is evidence of recurrence, not proof of a semantic cycle or an instruction to repeat an operation.
5. **Representation hints.** The caller may label a segment as source text, romanization, phonetic transcription, non-lexical vocalization, translation, markup, or unknown. A label such as `Hanyu Pinyin` is metadata supplied by the caller; SAMBU does not infer it from Latin letters.
6. **Semantic review.** Theme, translation quality, language identity, safety classification, and intended meaning remain `not_assessed` until a suitable human or explicitly configured review process supplies evidence.

## Neutral example

The following deliberately short fixture demonstrates script counting. It is not a translation benchmark:

```sambu
let sample = "清晨 qīng\n朝日"
let profile = language_mix_profile(sample)
print(profile.script_character_counts.han)
print(profile.script_character_counts.latin)
print(profile.multi_script_line_count)
print(profile.language_identification)
```

Expected observations: four Han letters, four Latin letters, one line containing both scripts, and `not_performed` for language identification. Character counts are more meaningful than whitespace-token counts for writing systems that commonly omit spaces between words.

A separate structure fixture can express a return pattern without inventing lexical meaning:

```text
[Section: Setup]
reference: item-01
cycle: return
cluster: group-A
object: sample-01
orientation: inbound
fragment: part-01
```

These are neutral field labels. The parser must preserve values and punctuation; a consumer assigns domain-specific semantics.

## Exchange envelope

Contract v1 records:
- a stable record identifier and opaque source references;
- one or more representation kinds;
- caller-supplied language hints and script profiles;
- explicit language-identification, translation, and semantic-review states;
- normalization form and optional structural counters;
- an invariant that raw text is not embedded in the metadata record.

`not_performed`, `not_requested`, `not_assessed`, `caller_supplied`, and `human_reviewed` are intentionally distinct. Do not turn missing evidence into a guessed language or translation.

## Seven-repository responsibility map

| Repository | Role in this pipeline | Boundary |
|---|---|---|
| **SAMBU** | Unicode script diagnostics, text structure, metadata validation, neutral fixtures | No definitive language/meaning claims from script counts alone |
| **Kloz** | Caller-owned bounded memory for byte payloads and offsets | No Unicode decoding or hidden allocation in the platform substrate |
| **CO** | Deterministic init/step/shutdown orchestration for pipeline stages | No implicit retry, thread creation, or hidden scheduling |
| **SaintSI** | Heartbeat and integrity observations for pipeline components | Health signals do not validate linguistic correctness or authorize recovery |
| **ReaperCripple** | Numeric embedded telemetry and manufacturing trace references | Keep raw text and localization outside MCU telemetry buffers |
| **ToolNG** | Localized diagnostic labels and recurrence summaries in local reports | Stable finding IDs remain authoritative; no silent upload or device mutation |
| **Klipot** | Contract discovery, schema navigation, and operator-facing metadata views | Browser demonstrations are not a live analyzer or hardware evidence |

## Compatibility and acceptance rules

- Contract major version changes only when a consumer must change how it interprets a field.
- Additive optional fields are compatible within v1.
- Preserve the existing `latin_word_count`, `cyrillic_word_count`, `other_script_word_count`, `code_switch_lines`, and `dominant_script` fields.
- Script counts must not be represented as language confidence.
- Romanization and translation must be explicit representation kinds with separate provenance.
- Repetition counters must distinguish exact textual recurrence from semantic interpretation and execution retries.
- Metadata records must not contain raw or translated text.

## Verification

Run the SAMBU test suite with `python -m pytest` or the repository's documented test command. The neutral multilingual tests cover Han/Latin co-presence and separate Japanese/Korean script categories. Host tests validate the Python implementation only; they do not validate an external language-identification or translation service.