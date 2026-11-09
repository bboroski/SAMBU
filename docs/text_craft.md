# SAMBU Text Craft Diagnostics

SAMBU's text-craft layer turns a draft into inspectable evidence without pretending that literature can be reduced to a single quality score. It is useful for lyric writing, spoken-word drafts, prose, and multilingual experiments.

## Design principles

1. **Rhythm before ornament.** Inspect line length and syllable movement before adding more rhyme or vocabulary.
2. **Rhyme as a network.** Look for internal echoes, end-word families, and multisyllabic patterns; do not force every line to rhyme.
3. **Sound carries structure.** Use repeated consonant onsets and vowel nuclei deliberately, then read the line aloud to verify the actual effect.
4. **Meaning may recur with a changed function.** Repetition is useful when the returning word or image develops, not when it merely fills space.
5. **Register shifts need intent.** Conversation, satire, absurdity, technical language, and epic imagery can coexist when the transition is controlled.
6. **Naturalness is a constraint.** A dense line must remain speakable and intelligible; metrics are diagnostic signals, not targets to maximize.
7. **Protect the author's voice.** A deliberate colloquialism, dialect form, stress mark, neologism, or broken phrase must not be auto-corrected as a typo.

## Built-ins

### text_profile(text)

Returns a record containing character_count, line_count, nonempty_line_count, word_count, unique_word_count, lexical_diversity, average_words_per_line, letter_count, punctuation_count, and top_words (up to ten word/count records ordered by frequency).

### prosody_profile(text)

Returns line-level records plus aggregate indicators: syllable_counts, average_syllables_per_line, syllable_variance, syllable_range, rhyme_groups, rhyme_density, alliterative_line_count, alliteration_density, and lines. Each line record contains line_number, text, word_count, syllable_count, end_word, rhyme_key, and has_alliteration.

### syllables(word) and rhyme_key(word)

syllables estimates syllables by counting vowel nuclei. rhyme_key produces a rough spelling-based ending from the final vowel to the end of the word. Both are deterministic and work with common Cyrillic and Latin vowel sets.

## Example

    let draft = "Город хранит недосказанный разговор\nВетер разбудит забытый двор"
    let language = text_profile(draft)
    let sound = prosody_profile(draft)
    print(language.word_count)
    print(language.lexical_diversity)
    print(sound.syllable_counts)
    print(sound.rhyme_groups)
    print(syllables("разговор"))
    print(rhyme_key("разговор"))

## Limits and interpretation

These functions are diagnostics, not a grammar corrector, dictionary, speech recognizer, or literary judge. Syllable counts are estimates based on written vowel nuclei; they do not infer lexical stress, pronunciation, dialect, or elision. Rhyme keys compare written endings from the last vowel and can produce false positives or miss true phonetic rhymes. Alliteration currently checks repeated consonant initials within one line. Read the text aloud and use human judgment before changing a draft.

The analyzer never rewrites the source text. In particular, non-standard spelling, colloquial grammar, profanity, code-switching, marked stress, and intentional phonetic distortion remain the author's decisions.
