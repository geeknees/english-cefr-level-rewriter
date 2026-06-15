# English CEFR Level Rewriter

A Claude skill that rewrites English text to a target CEFR proficiency level (A1–C2), plus Python scripts to validate the output for vocabulary and grammar compliance.

## What it does

- **Rewrites** existing English text so readers at the target CEFR level can understand it
- **Preserves** facts, proper nouns, and original meaning — only the *form* changes
- **Validates** output with two scripts: vocabulary level and grammar/readability heuristics

## Quick start

### Use the skill in Claude

Invoke the skill and provide:

- **target_level**: A1 / A2 / B1 / B2 / C1 / C2
- **source_text**: the text you want to rewrite
- **mode**: `strict` / `balanced` / `learning` (default: `balanced`)
- **output_format**: `text_only` / `with_notes` / `with_validation` (default: `with_notes`)

### Validate the output

```bash
# Install dependencies (first time only)
pip install -r requirements.txt

# Check vocabulary level
python3 skills/english-cefr-level-rewriter/scripts/validate_cefr_vocab.py \
  --text "The scientist investigated the phenomenon." \
  --level B1

# Check grammar/readability
python3 skills/english-cefr-level-rewriter/scripts/validate_cefr_readability.py \
  --text "Although it was raining, she decided to go." \
  --level A2
```

Both scripts exit 0 (pass) / 1 (violations found), so they work in CI.

## Skill parameters

| Parameter | Options | Default |
|---|---|---|
| `target_level` | A1, A2, B1, B2, C1, C2 | — |
| `mode` | `strict`, `balanced`, `learning` | `balanced` |
| `output_format` | `text_only`, `with_notes`, `with_validation` | `with_notes` |

**strict** — replace everything above the target level; meaning first, naturalness second.
**balanced** — keep important terms with a brief inline gloss; restructure grammar only where needed.
**learning** — retain harder items with explanations; good for stretch reading.

## Vocabulary data

Source: [ESL Lounge Word Bank](https://www.esl-lounge.com/student/word-bank.php)
File: `skills/english-cefr-level-rewriter/resources/vocabulary/cefr_vocabulary.csv` (`word, cefr_level, pos`)

Each word is recorded at its *first* CEFR level appearance. The validator accepts any word at or below the target level.

To regenerate the vocabulary CSV:

```bash
python3 skills/english-cefr-level-rewriter/scripts/scrape_esl_lounge.py
```

## Grammar profiles

`skills/english-cefr-level-rewriter/resources/grammar/A1.md` through `C2.md` define, for each level:
- Sentence length limits
- Tense/aspect inventory
- Subordinate clause depth limits
- Passive voice policy
- Allowed modal verbs
- Discourse markers

## Known limitations

| Limitation | Component |
|---|---|
| Word-sense ambiguity (*bank* as finance vs. river) | Vocabulary validator |
| Irregular verb forms (*went*, *better*) not resolved by basic lemmatiser | Vocabulary validator |
| Clause depth is a heuristic count, not a parse tree | Readability validator |
| Passive detection via regex may miss complex constructions | Readability validator |
| Proper nouns appear as "unknown" in vocab output (expected) | Vocabulary validator |

## Repository structure

```
english-cefr-level-rewriter/
  .claude-plugin/plugin.json        # Claude plugin metadata
  .codex-plugin/plugin.json         # Codex plugin metadata
  SKILL.md → skills/english-cefr-level-rewriter/SKILL.md
  README.md                         # This file
  requirements.txt                  # Python dependencies
  pytest.ini                        # Test runner config
  skills/
    english-cefr-level-rewriter/
      SKILL.md                      # Claude skill (main artifact)
      resources/
        vocabulary/
          cefr_vocabulary.csv
          cefr_vocabulary.sample.csv
          README.md
        grammar/
          A1.md … C2.md
      scripts/
        scrape_esl_lounge.py
        validate_cefr_vocab.py
        validate_cefr_readability.py
      examples/
        sample_inputs.md
        sample_outputs.md
      tests/
        test_cases.md
  tests/
    test_scrape_esl_lounge.py
    test_validate_cefr_vocab.py
    test_validate_cefr_readability.py
```

## License

Vocabulary data is sourced from [ESL Lounge](https://www.esl-lounge.com) for educational use.
