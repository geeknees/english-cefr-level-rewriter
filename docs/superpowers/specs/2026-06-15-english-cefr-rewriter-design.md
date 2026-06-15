# English CEFR Level Rewriter — Design Spec

**Date:** 2026-06-15  
**Status:** Approved

---

## Overview

A Claude skill that rewrites English text so a reader at the target CEFR level (A1–C2) can understand it without losing the original meaning. A companion Python validation suite checks the output for vocabulary and grammar compliance.

Primary users: content creators and teachers/curriculum designers.

---

## Repository Structure

```
english-cefr-level-rewriter/
  SKILL.md                          # Claude-facing skill (entry point)
  README.md                         # English, for humans
  resources/
    vocabulary/
      cefr_vocabulary.csv           # word, cefr_level, pos (scraped from ESL Lounge)
      cefr_vocabulary.sample.csv    # first 100 rows for quick reference
      README.md                     # data provenance, curation notes
    grammar/
      A1.md                         # grammar profile: allowed structures, sentence length limits
      A2.md
      B1.md
      B2.md
      C1.md
      C2.md
  scripts/
    scrape_esl_lounge.py            # one-time scraper to build cefr_vocabulary.csv
    validate_cefr_vocab.py          # checks output text against vocabulary CSV
    validate_cefr_readability.py    # heuristics: sentence length, clause depth, passives, modals
  examples/
    sample_inputs.md
    sample_outputs.md
  tests/
    test_cases.md
```

---

## Skill Parameters

| Parameter | Values | Required | Default |
|-----------|--------|----------|---------|
| `target_level` | A1 / A2 / B1 / B2 / C1 / C2 | Yes | — |
| `source_text` | The English text to rewrite | Yes | — |
| `mode` | `strict` / `balanced` / `learning` | Yes | `balanced` |
| `output_format` | `text_only` / `with_notes` / `with_validation` | Yes | `with_notes` |

### Mode Definitions

- **strict** — replace all vocabulary and grammar above the target level; meaning preservation takes priority over naturalness
- **balanced** — keep important terms with brief inline glosses; restructure grammar only where it clearly exceeds the level
- **learning** — retain slightly harder items with explanation attached; useful for stretch reading at the upper edge of a level

### Output Formats

- **text_only** — rewritten text only, no commentary
- **with_notes** — rewritten text + bulleted list of changes made and why
- **with_validation** — rewritten text + vocabulary table (flagged words, original level, how handled) + grammar table (structures simplified or introduced)

---

## Processing Steps

Claude follows five ordered steps. Steps must not be skipped, even for short texts.

### Step 1 — Analyse the source

Identify and note internally:
- Main claims and facts (must be preserved)
- Causal relationships
- Concrete examples
- Technical / specialist terms
- Proper nouns (names of people, places, organisations, products)
- Sentence structure features: length, clause nesting, passive constructions, modal density

### Step 2 — Detect difficulty for the target level

**Vocabulary check:** Compare each content word against `resources/vocabulary/cefr_vocabulary.csv`. The CSV is cumulative — a word's `cefr_level` is the level at which it first appears. A word is "above level" if its `cefr_level` is higher than the target. Unknown words (not in CSV) are flagged for manual review.

**Grammar check:** Compare sentence structures against the target level's grammar profile in `resources/grammar/<LEVEL>.md`. Flag:
- Sentences exceeding the target word-count threshold
- Tenses or aspects not yet introduced at the target level
- Clause nesting depth above the target limit
- Passive constructions at levels where they are restricted (A1–B1)
- Modals not in the allowed inventory for the target level

### Step 3 — Rewrite in priority order

1. **Vocabulary first:** replace words above target level with level-appropriate synonyms, or keep with a brief inline gloss in balanced/learning mode
2. **Grammar second:** shorten/split sentences, reduce clause depth, convert passive→active for lower levels (A1–B1), or introduce appropriate structures for higher targets (B2+)
3. **Never delete content** — simplify the *form*, not the *substance*; if something is hard, explain it rather than removing it
4. Proper nouns are always kept as-is
5. Domain-specific terms that have no level-appropriate equivalent are kept with a parenthetical explanation

### Step 4 — Post-rewrite check

Scan the output for:
- Remaining vocabulary above the target level
- Sentence lengths or clause depths that still exceed the target profile
- Consistency: proper nouns intact, facts unchanged, no invented examples

### Step 5 — Format output

Produce the output in the format specified by `output_format`.

---

## Grammar Profiles

Each file `resources/grammar/<LEVEL>.md` defines six dimensions:

| Dimension | Description |
|-----------|-------------|
| Sentence length | Target word count per sentence (max and typical) |
| Tense/aspect inventory | Which tenses and aspects are allowed at this level |
| Clause depth | Maximum levels of subordinate clause embedding |
| Passive voice policy | Prohibited / limited / allowed |
| Modal inventory | Which modal verbs are appropriate at this level |
| Discourse markers | Cohesion devices appropriate at this level |

Grammar profiles are hand-authored markdown, drawing on the Council of Europe CEFR descriptor tables and Cambridge Grammar for CEFR levels.

---

## Vocabulary Data

**Source:** ESL Lounge word bank (https://www.esl-lounge.com/student/word-bank.php)  
**Fields:** `word, cefr_level, pos`  
**Example row:** `bank, A2, noun`  
**Curation:** `scrape_esl_lounge.py` generates the CSV as a one-time operation. The resulting file is committed to the repo. The sample file contains the first 100 rows.

**Cumulative semantics:** each word is recorded at its *first* CEFR appearance. The validator accepts any word whose `cefr_level` is at or below the target.

---

## Validation Scripts

### `validate_cefr_vocab.py`

- Tokenises input, strips punctuation, lowercases, applies basic lemmatisation (strip -ing/-ed/-s)
- Looks up each token in `cefr_vocabulary.csv`
- Reports: unknown words and words above target level
- Output table: `word | found_level | target_level | status`
- Exit code: 0 (no violations) / 1 (violations found)

```bash
python3 scripts/validate_cefr_vocab.py --text "..." --level B1
```

### `validate_cefr_readability.py`

- Sentence length: flags sentences exceeding the target level's word-count threshold
- Clause depth: counts subordinating conjunctions and relative pronouns as a proxy for nesting
- Passive voice: regex detection of `be + past participle` patterns
- Modal inventory: checks modals present against the allowed list for the target level
- Output table: flagged sentences with the rule violated
- Exit code: 0 (no violations) / 1 (violations found)

```bash
python3 scripts/validate_cefr_readability.py --text "..." --level B1
```

---

## Known Limitations

| Limitation | Affected component |
|---|---|
| Word-sense ambiguity (*bank* = finance vs. riverbank) | Vocabulary validator |
| Basic lemmatisation misses irregular forms (*went*, *better*) | Vocabulary validator |
| Clause depth is a heuristic, not a parse tree | Readability validator |
| Passive detection via regex may miss complex constructions | Readability validator |
| Proper nouns and domain terms may false-positive as unknown vocabulary | Both validators |

---

## Testing

**`tests/test_cases.md`** — 12 test cases, 2 per CEFR level. Each case includes:
- Source text
- Target level and mode
- Expected rewritten output
- Expected validation output

Edge cases covered: proper nouns surviving intact, domain terms kept with gloss, sentence splitting at A1, passive conversion at B1, passive introduction at B2.

---

## Examples

**`examples/sample_inputs.md`** — 3 realistic source texts:
1. News article excerpt
2. Product manual paragraph
3. Academic abstract

**`examples/sample_outputs.md`** — expected rewrites of each input at A2, B1, B2 for side-by-side comparison.
