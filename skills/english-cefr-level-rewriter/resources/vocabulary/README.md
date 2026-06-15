# Vocabulary Data

## Source

Words from two open datasets, both under **Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)**:

- [CEFR-J Vocabulary Profile 1.5](https://github.com/openlanguageprofiles/olp-en-cefrj/blob/master/cefrj-vocabulary-profile-1.5.csv)
  — compiled by Yukio Tono, Tokyo University of Foreign Studies. Covers A1–B2.
- [Octanove Vocabulary Profile C1/C2 1.0](https://github.com/openlanguageprofiles/olp-en-cefrj/blob/master/octanove-vocabulary-profile-c1c2-1.0.csv)
  — compiled by Octanove Labs. Covers C1–C2.

Both published at: https://github.com/openlanguageprofiles/olp-en-cefrj

## Fields

| Field | Description |
|---|---|
| `word` | Lowercase English headword |
| `cefr_level` | A1 / A2 / B1 / B2 / C1 / C2 — the level at which the word *first appears* |
| `pos` | Part of speech (noun / verb / adjective / adverb / pronoun / preposition / determiner / conjunction / number / modal auxiliary / be-verb / interjection / do-verb / have-verb / infinitive-to) |

## Cumulative semantics

A word at level A2 is also valid vocabulary at B1, B2, C1, and C2.
The validator accepts any word whose `cefr_level` is at or below the target level.

## Known limitations

- Multi-word expressions (e.g., "ice cream") appear as written; the validator matches them only if the full string is present
- Proper nouns are not included — the validator flags them as "unknown" (expected behaviour)
- Word-sense ambiguity is not handled (e.g., *bank* as noun appears once at A2 regardless of sense)
- Basic lemmatisation strips common suffixes (-ing, -ed, -s) but does not handle irregular forms or consonant doubling

## Regenerating

```bash
python3 scripts/build_cefr_vocab.py
```

Downloads the source CSVs from GitHub, merges them, deduplicates by (word, pos) keeping the lowest CEFR level, and writes `cefr_vocabulary.csv`.
