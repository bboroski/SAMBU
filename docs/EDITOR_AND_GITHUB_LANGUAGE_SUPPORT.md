# SAMBU editor and GitHub language identity

SAMBU source files use the `.sambu` extension. The repository includes an original MIT-licensed TextMate grammar at `syntaxes/SAMBU.tmLanguage.json`, using scope `source.sambu`. It is suitable as editor-highlighting groundwork.

## Actual GitHub status (2026-11-10)

GitHub Linguist does not currently recognize SAMBU. The repository's language bar therefore reports the host implementation language (Python), not the language of the `.sambu` source files.

A live GitHub Code Search API snapshot for `extension:sambu` returned **20 indexed files**. All 20 results belonged to **one public repository**, `bboroski/SAMBU`; the repository tree also contains 20 `.sambu` examples. This is useful evidence that the extension works in this project, but it is not broad ecosystem adoption.

- Search: [GitHub Code Search — extension:sambu](https://github.com/search?q=extension%3Asambu&type=code)
- Repository: [bboroski/SAMBU](https://github.com/bboroski/SAMBU)
- Current extension registration in Linguist: not present in `lib/linguist/languages.yml`.

## Why an upstream Linguist registration is not ready yet

The current [Linguist contribution policy](https://github.com/github-linguist/linguist/blob/main/CONTRIBUTING.md#language-extension-and-filename-usage-requirements) says new extensions and filenames must demonstrate sufficient widespread public GitHub usage. Its published thresholds are:

- **2,000 files** indexed in the last year, excluding forks, for an extension expected to appear multiple times per repository (the relevant category for a source-code extension such as `.sambu`).
- **200 files** for filenames expected to occur only once per repository, such as `Makefile`.
- Results must be distributed across distinct user/repository combinations. Linguist may discount a disproportionate share from the language's primary owner.
- The policy explicitly says very new or hobby languages are not accepted.

The current searchable snapshot is 20 files from one repository: about **1% of the 2,000-file threshold**, with no cross-repository distribution demonstrated. An upstream PR now would be premature and risks being closed under the published policy. We will not manufacture dummy files, forks, mirrors, or misleading usage evidence to inflate the count.

## Legitimate path to GitHub language-bar recognition

1. Keep the language implementation, specification, grammar, examples, tests, and package metadata coherent in this repository.
2. Make SAMBU genuinely usable by independent developers: reliable installation, stable CLI, readable diagnostics, versioned language specification, working examples, and editor support.
3. Build real adoption in independent public repositories. Count only actual source files in maintained projects; do not create placeholder repositories or mass-generated copies.
4. Once the search evidence reaches Linguist's thresholds and shows broad distribution, submit an upstream contribution:
   - Add a `SAMBU` programming-language entry to `languages.yml`, initially without a `language_id`.
   - Add the TextMate grammar through Linguist's documented grammar-import process, subject to its accepted-license rules.
   - Add representative SAMBU samples and state their MIT license and source.
   - Run Linguist's test suite and `script/update-ids` as required by its contribution process.
   - Include a GitHub code-search query documenting widespread in-the-wild usage.
5. Wait for upstream review, merge, and Linguist release/deployment. Only then verify that GitHub recognizes `.sambu` files. A repository-level `.gitattributes` override cannot create a language that the central Linguist registry does not know.

## Grammar coverage and maintenance

The grammar covers:
- Canonical control/declaration words and their active SAMBU articulatory spellings.
- All currently implemented articulatory built-in aliases and their canonical callable names.
- Single- and double-quoted strings, escapes, comments, numeric literals, operators, punctuation, function declarations, and class declarations.

This grammar performs token coloring only. It does not parse programs, type-check them, or prove that a name is executable. The SAMBU lexer, parser, resolver, runtime, and tests remain authoritative. Reserved wordbook entries are intentionally not highlighted as implemented built-ins.

## Acceptance gate

Do not claim “SAMBU is displayed as a GitHub language” until all of the following are true:
- Linguist's upstream `languages.yml` contains SAMBU and `.sambu`.
- Its grammar and representative licensed samples are accepted.
- A fresh GitHub repository-language view classifies the repository's `.sambu` files as SAMBU after deployment.
