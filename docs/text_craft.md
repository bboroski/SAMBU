# SAMBU Text Craft Diagnostics

SAMBU's text-craft layer turns a draft into inspectable evidence without pretending that literature can be reduced to a single quality score. It is useful for lyric writing, spoken-word drafts, prose, scripts, and multilingual experiments.

## Design principles

1. **Rhythm before ornament.** Inspect line length and syllable movement before adding more rhyme or vocabulary.
2. **Rhyme as a network.** Look for internal echoes, end-word families, and multisyllabic patterns; do not force every line to rhyme.
3. **Sound carries structure.** Use repeated consonant onsets and vowel nuclei deliberately, then read the line aloud to verify the actual effect.
4. **Meaning may recur with a changed function.** Repetition is useful when the returning word or image develops, not when it merely fills space.
5. **Register shifts need intent.** Conversation, satire, absurdity, technical language, and elevated imagery can coexist when the transition is controlled.
6. **Naturalness is a constraint.** A dense line must remain speakable and intelligible; metrics are diagnostic signals, not targets to maximize.
7. **Protect the author's voice.** A deliberate colloquialism, dialect form, stress mark, neologism, or broken phrase must not be auto-corrected as a typo.
8. **Preserve structure.** Section labels, line order, refrains, punctuation, and authorial casing are source data, not decoration to discard.

## Built-ins

### text_profile(text)

Returns character_count, line_count, nonempty_line_count, word_count, unique_word_count, lexical_diversity, average_words_per_line, letter_count, punctuation_count, and top_words.

### prosody_profile(text)

Returns line-level records plus aggregate indicators: syllable_counts, average_syllables_per_line, syllable_variance, syllable_range, rhyme_groups, rhyme_density, alliterative_line_count, alliteration_density, internal_rhyme_line_count, internal_rhyme_density, marked_case_words, marked_case_word_count, and lines.

Each line record includes its source line number, original text, word count, estimated syllable count, final word, approximate rhyme key, alliteration flag, and internal rhyme groups. Internal rhyme keys are spelling heuristics, not phonetic transcriptions.

Mixed-case tokens such as вОды are surfaced as marked_case_words. This is a preservation cue: the author may be marking emphasis or performance stress. The analyzer does not decide which syllable is stressed, and it never rewrites the token.

### text_structure_profile(text)

Recognizes common bracketed or standalone section markers, including:

- [Intro], [Verse], [Verse 2];
- [Pre-Chorus], [Chorus], [Hook], [Bridge], [Outro];
- [Интро], [Куплет], [Куплет 2], [Припев], [Хук], [Бридж], [Аутро].

It returns section labels and kinds, source line ranges, line and word counts, exact repeated chorus blocks (refrain_groups), and repeated non-empty lines. Text outside a recognized heading is retained as a body section. Unknown bracket labels remain custom; they are not silently discarded.

A refrain is grouped only when its normalized written lines match exactly. Near-duplicate choruses, melodic variants, and paraphrases are not inferred.

### language_mix_profile(text)

Counts words written in Latin, Cyrillic, other, or mixed scripts and identifies lines containing both Latin and Cyrillic words. This detects visible writing-system changes, not a definitive natural language. In particular, Russian and Ukrainian both use Cyrillic; the analyzer does not pretend that script alone can reliably distinguish them.

### syllables(word) and rhyme_key(word)

syllables estimates syllables by counting vowel nuclei. rhyme_key produces a rough spelling-based ending from the final vowel to the end of the word. Both are deterministic and support common Cyrillic and Latin vowel sets.

## Example

    let draft = "[Verse 1]\\nПишу короткий фрагмент\\n[Chorus]\\nA melody returns\\n[Припев]\\nA melody returns"
    let structure = text_structure_profile(draft)
    let mix = language_mix_profile(draft)
    let sound = prosody_profile(draft)

    print(structure.section_count)
    print(structure.refrain_groups[0].repeat_count)
    print(mix.code_switch_line_count)
    print(sound.syllable_counts)
    print(sound.internal_rhyme_density)

## A repeatable refinement loop

1. **Lock intent.** Identify the speaker, target, emotional temperature, core images, and facts that must survive revision.
2. **Map composition.** Mark intro, verses, pre-chorus, chorus, bridge, and outro where they exist. Keep section order explicit.
3. **Write in a speakable voice.** Establish the natural spoken phrase before decorating it.
4. **Tune rhythm first.** Compare line lengths and syllable movement; change pauses, stress placement, and line breaks before adding more words.
5. **Build the sound network.** Strengthen internal echoes, multisyllabic rhyme families, consonant runs, and vowel patterns. Keep end rhymes only where they help.
6. **Track language and register.** Treat code-switching, dialect, colloquial speech, technical vocabulary, satire, and absurdity as intentional possibilities, not automatic errors.
7. **Make each return do new work.** Repeated words, images, and refrains should gain a second meaning, change the scene, or raise the stakes.
8. **Separate error from intention.** Classify unusual spelling, colloquial grammar, marked casing, and neologisms as intentional, accidental, or uncertain. Correct only clear mistakes; ask before normalizing uncertain forms.
9. **Read aloud and re-check.** A line that looks impressive but cannot be performed naturally needs another pass. Re-run the diagnostics after each meaningful revision.

### Reusable refinement instruction

Preserve the author's intent, point of view, section order, and distinctive vocabulary. Prioritize speakable rhythm, then purposeful sound design, then semantic precision. Use internal and multisyllabic rhyme without forcing every line to match. Let humor, absurdity, technical language, satire, and elevated imagery shift registers deliberately. Prefer fresh, concrete phrasing over filler and stock expressions. Treat repetition as development, not padding. Do not silently erase dialect, profanity, code-switching, marked casing, neologisms, or intentional grammatical breaks. Separate objective spelling/grammar errors from stylistic choices, and explain uncertain corrections instead of imposing them. Never optimize a numerical metric at the expense of clarity, meaning, or performance.

## Limits and interpretation

These functions are diagnostics, not a grammar corrector, dictionary, speech recognizer, or literary judge. Syllable counts are estimates based on written vowel nuclei; they do not infer lexical stress, pronunciation, dialect, or elision. Rhyme keys compare written endings from the last vowel and can produce false positives or miss true phonetic rhymes. Alliteration currently checks repeated consonant initials within one line. Section and refrain recognition uses a small explicit heading vocabulary and exact normalized text matching. Language-mix analysis identifies writing systems rather than natural languages.

The analyzer never rewrites the source text. Non-standard spelling, colloquial grammar, profanity, code-switching, marked stress, and intentional phonetic distortion remain the author's decisions.


## Performance and delivery cues

### performance_cues_profile(text)

This built-in extracts explicit written markers that can matter when preparing a performance or arranging a lyric:

- \`*...*\` stage directions (for example, sound effects);
- \`( ... )\` parenthetical asides and ad-lib notation;
- straight, curly or guillemet-quoted phrases;
- repeated hyphenated word segments such as \`О-о-о\` or \`ру-ру-Русско\`.

Every marker includes its kind, source line, and start/end columns. The result is capped at 1,000 returned markers; \`truncated\` reports when more were found. Recognized section headings are not double-counted as parenthetical asides.

\`text_structure_profile\` also accepts parenthesized section labels such as \`(Verse 2)\`, bracketed labels with an internal colon such as \`[Verse:]\`, and explicit delivery labels such as \`[Melody sing Chorus:]\`. A section's \`performance_hint\` is descriptive and only reflects explicit words in its heading (\`melodic\`, \`spoken\`, \`ad_lib\`, \`rap\`, or \`unspecified\`).

These are markup observations only. The analyzer does not identify the speaker, infer emotion, predict vocal delivery, transcribe audio, or decide whether a cue is appropriate. It preserves the exact source text.

### Example

    let draft = "[Verse:]\\nFirst movement\\n[Melody sing Chorus:]\\nA returning line\\n[Chorus:]\\nA returning line\\n(Verse 2)\\nSecond movement"
    let structure = text_structure_profile(draft)
    let cues = performance_cues_profile("*Phone rings*\\n(Mm-mm)\\nру-ру-Русско")

    print(structure.section_kind_counts.verse)
    print(structure.refrain_groups[0].repeat_count)
    print(structure.sections[1].performance_hint)
    print(cues.marker_count)
