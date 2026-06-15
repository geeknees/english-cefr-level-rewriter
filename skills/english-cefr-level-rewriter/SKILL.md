---
name: english-cefr-level-rewriter
description: Use when rewriting English text to match a target CEFR level — A1 (Beginner) through C2 (Proficiency). Applies when the user wants to simplify or adapt English text for ESL learners, adjust vocabulary and grammar to a specific level, or validate whether a passage is appropriate for a given CEFR stage. Vocabulary data: CEFR-J (Yukio Tono, TUFS) + Octanove Vocabulary Profile, CC BY-SA 4.0.
---

# English CEFR Level Rewriter

## Overview

Rewrites English text so a reader at the target CEFR level can understand it **without losing the original meaning**. The goal is accessibility, not dumbing down. Facts, claims, and important terms are preserved; only the *form* is adjusted to match what the reader can realistically handle.

Vocabulary reference: `resources/vocabulary/cefr_vocabulary.csv`
Grammar reference: `resources/grammar/<LEVEL>.md`

---

## Input Specification

| Parameter | Values | Required | Default |
|-----------|--------|----------|---------|
| `target_level` | A1 / A2 / B1 / B2 / C1 / C2 | Yes | — |
| `source_text` | The English text to rewrite | Yes | — |
| `mode` | `strict` / `balanced` / `learning` | Yes | `balanced` |
| `output_format` | `text_only` / `with_notes` / `with_validation` | Yes | `with_notes` |

**If any parameter is missing**, ask the user before proceeding.

### Mode definitions

- **strict** — replace all vocabulary and grammar above the target level; meaning preservation takes priority over naturalness
- **balanced** — keep important terms with a brief inline gloss (e.g., "acquire (get)"); restructure grammar only where it clearly exceeds the level
- **learning** — retain slightly harder vocabulary with explanation attached; useful for stretch reading at the upper edge of a level

---

## Processing Steps

Follow these steps in order. Do not skip steps even for short texts.

### Step 1 — Analyse the source

Identify and note internally (not necessarily in the output):

1. **Main claims and facts** — what the text asserts; must be preserved
2. **Causal relationships** — A leads to B
3. **Concrete examples** — specific cases
4. **Technical / specialist terms** — domain vocabulary
5. **Proper nouns** — names of people, places, organisations, products
6. **Sentence structure features** — length, clause nesting, passive voice, modal density

### Step 2 — Detect difficulty

**Vocabulary:** Compare each content word against `resources/vocabulary/cefr_vocabulary.csv`. The `cefr_level` field records the level at which the word *first appears* — words at or below the target level are fine; words above it or absent from the CSV are flagged.

**Grammar:** Compare sentence structures against `resources/grammar/<TARGET_LEVEL>.md`. Flag:
- Sentences exceeding the target word-count limit
- Tenses or aspects not yet introduced at the target level
- Subordinate clause nesting depth above the target limit
- Passive constructions where the profile says not permitted
- Modal verbs outside the allowed inventory

### Step 3 — Rewrite in priority order

1. **Vocabulary first:** replace words above target level with level-appropriate synonyms. In `balanced`/`learning` mode, keep the original term with a brief gloss: *acquire (get)*, *phenomenon (thing that happens)*.
2. **Grammar second:** shorten and split sentences; reduce clause depth; convert passive to active for lower levels (A1–B1); introduce richer structures at higher targets (B2+).
3. **Never delete content.** If something is hard to express simply, explain it; do not remove it.
4. **Proper nouns are always kept as-is.**
5. **Domain terms with no level-appropriate equivalent** are kept with a parenthetical explanation.

### Step 4 — Post-rewrite check

Scan the output for:
- Vocabulary still above the target level
- Sentences still exceeding the target word-count
- Proper nouns intact and unchanged
- No facts altered or removed

### Step 5 — Format output

Produce output in the format specified by `output_format`.

---

## Output Formats

### `text_only`

Output only the rewritten English text. No commentary.

---

### `with_notes`

```
[Rewritten text]

**Changes made:**
- (bullet list of changes and why)
```

---

### `with_validation`

```
[Rewritten text]

**Target level:** (level)

**Vocabulary changes:**
| Original | Replacement | Reason |
|---|---|---|

**Grammar changes:**
| Original structure | Rewritten structure | Rule applied |
|---|---|---|

**Retained above-level items:**
| Term | Level | Reason kept |
|---|---|---|
```

---

## Level-by-Level Guidance

### A1
- Max 10 words per sentence. Split aggressively.
- Present simple and present continuous only.
- No subordinate clauses. No passives.
- Modals: *can*, *can't* only.
- Make the subject explicit in every clause.
- Replace abstract nouns with concrete descriptions.

### A2
- Max 15 words per sentence.
- Past simple, going-to future, and will-future available.
- One subordinate clause per sentence (*because*, *when*, *if*) is fine.
- No passives. Modals: *can*, *could*, *will*, *would*.
- Prefer common phrasal verbs over formal equivalents (*find out* not *ascertain*).

### B1
- Max 20 words per sentence.
- Present perfect, past continuous available.
- One relative clause or subordinate clause per sentence.
- Passives permitted in present and past simple.
- All common modals available.
- Technical terms can appear with a brief inline definition on first use.

### B2
- Max 25 words per sentence.
- Past perfect, conditionals (2nd and 3rd) available.
- Up to two levels of clause embedding.
- All passives permitted, including reporting structures (*It is believed that…*).
- *need* and *ought to* available.
- Nominalisations acceptable if the meaning is clear.

### C1
- Max 35 words per sentence.
- Mixed conditionals, subjunctive, complex passives all available.
- Up to three levels of clause embedding.
- All modals and semi-modals freely used.
- Stance markers and hedging language appropriate.

### C2
- No restrictions on length, tense, clause depth, or modal choice.
- Preserve stylistic choices; only rewrite where genuinely ambiguous.

---

## Important Constraints

1. **Never change facts.** The rewritten text must make the same claims as the source.
2. **Never remove information to make it simpler.** Simplify the form, not the content.
3. **Proper nouns are always kept as-is.** Names, brands, place names do not change.
4. **Do not invent examples** not implied by the source.
5. **Signal uncertainty.** If you are unsure whether a term is level-appropriate, note it in `with_notes` or `with_validation` output.

---

## Validation Scripts

To programmatically check the rewritten text:

```bash
# Check vocabulary
ruby scripts/validate_cefr_vocab.rb --text "..." --level B1

# Check grammar/readability
ruby scripts/validate_cefr_readability.rb --text "..." --level B1
```

Both scripts exit 0 (no violations) / 1 (violations found).

**Known limitations:**
- Vocab script uses basic lemmatisation; irregular forms (went, better) may not be resolved
- Readability script uses heuristics, not a full parser; clause depth is approximate
- Proper nouns will appear as "unknown" in vocab output — this is expected

---

## Data Sources and Licenses

### Vocabulary data

`resources/vocabulary/cefr_vocabulary.csv` is derived from two datasets, both licensed under **Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)**:

| Dataset | Author | Scope | URL |
|---|---|---|---|
| CEFR-J Vocabulary Profile 1.5 | Yukio Tono, Tokyo University of Foreign Studies | A1–B2 | https://github.com/openlanguageprofiles/olp-en-cefrj |
| Octanove Vocabulary Profile C1/C2 1.0 | Octanove Labs | C1–C2 | https://github.com/openlanguageprofiles/olp-en-cefrj |

If you distribute or adapt this skill, you must:
1. Credit the authors above.
2. Link to the CC BY-SA 4.0 license: https://creativecommons.org/licenses/by-sa/4.0/
3. Release any derivative vocabulary data under the same license.

### Grammar profiles

`resources/grammar/*.md` are original documents authored for this skill and carry no third-party license obligations.
