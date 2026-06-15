# Vocabulary Data

## Source

Words scraped from [ESL Lounge Word Bank](https://www.esl-lounge.com/student/word-bank.php).
Scraper: `scripts/scrape_esl_lounge.py`

## Fields

| Field | Description |
|---|---|
| `word` | Lowercase English word |
| `cefr_level` | A1 / A2 / B1 / B2 / C1 / C2 — the level at which the word *first appears* |
| `pos` | Part of speech: noun / verb / adjective / adverb |

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
python3 scripts/scrape_esl_lounge.py
```

Requires an internet connection. The scraper sleeps 1 second between requests.
