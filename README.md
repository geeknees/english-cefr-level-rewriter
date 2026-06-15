# English CEFR Level Rewriter

An AI skill that rewrites English text to match a target CEFR proficiency level (A1–C2).  
Vocabulary data: [CEFR-J Vocabulary Profile](https://github.com/openlanguageprofiles/olp-en-cefrj) (Yukio Tono, TUFS) + [Octanove Vocabulary Profile C1/C2](https://github.com/openlanguageprofiles/olp-en-cefrj), CC BY-SA 4.0. Grammar profiles based on the Common European Framework of Reference for Languages.

## What it does

- Rewrites English text to the vocabulary and grammar of a specified CEFR level (A1–C2)
- Preserves facts, proper nouns, and original meaning — only the *form* changes
- Controls how out-of-level words are handled with `strict` / `balanced` / `learning` modes
- Keeps important or technical terms with a brief inline gloss (`balanced` / `learning`)
- Selectable output format: `text_only` / `with_notes` / `with_validation`
- Validates rewritten text automatically with `scripts/validate_cefr_vocab.py` and `scripts/validate_cefr_readability.py`

---

## Installation

### Claude Code

```
/plugin install english-cefr-level-rewriter@https://github.com/geeknees/english-cefr-level-rewriter.git
```

After installation, just say "Rewrite this for B1 learners" and the skill activates automatically.

**Update**

```
/plugin update english-cefr-level-rewriter
```

**Uninstall**

```
/plugin uninstall english-cefr-level-rewriter
```

---

### Codex

```
/plugin install english-cefr-level-rewriter@https://github.com/geeknees/english-cefr-level-rewriter.git
```

After installation, just say "Rewrite this for B1 learners" and the skill activates automatically.

**Update**

```
/plugin update english-cefr-level-rewriter
```

**Uninstall**

```
/plugin uninstall english-cefr-level-rewriter
```

---

## Usage

After installation you can make requests in natural language:

```
Rewrite this for A2 learners (balanced mode, with_notes format):

"The scientist investigated the phenomenon using a sophisticated methodology."
```

You can also specify parameters explicitly:

| Parameter | Options | Default |
|-----------|---------|---------|
| `target_level` | A1 / A2 / B1 / B2 / C1 / C2 | (required) |
| `mode` | `strict` / `balanced` / `learning` | `balanced` |
| `output_format` | `text_only` / `with_notes` / `with_validation` | `with_notes` |

**strict** — replace everything above the target level; meaning first, naturalness second.  
**balanced** — keep important terms with a brief inline gloss; restructure grammar only where needed.  
**learning** — retain harder items with explanations; good for stretch reading.

---

## Validation scripts

Check that rewritten text contains no out-of-level vocabulary or grammar patterns:

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

Both scripts exit `0` (pass) / `1` (violations found), so they work in CI pipelines.

To regenerate the vocabulary CSV from the upstream open datasets:

```bash
python3 skills/english-cefr-level-rewriter/scripts/build_cefr_vocab.py
```

---

## Repository structure

```
english-cefr-level-rewriter/
├── .claude-plugin/
│   └── plugin.json                        # Claude Code plugin metadata
├── .codex-plugin/
│   └── plugin.json                        # Codex plugin metadata
├── README.md
├── requirements.txt
├── pytest.ini
└── skills/
    └── english-cefr-level-rewriter/
        ├── SKILL.md                        # Skill definition
        ├── resources/
        │   ├── vocabulary/
        │   │   ├── cefr_vocabulary.csv     # CEFR-J + Octanove word list (word, cefr_level, pos)
        │   │   ├── cefr_vocabulary.sample.csv
        │   │   └── README.md
        │   └── grammar/
        │       └── A1.md … C2.md           # Grammar profiles per level
        ├── scripts/
        │   ├── build_cefr_vocab.py         # Regenerate vocabulary CSV from upstream datasets
        │   ├── validate_cefr_vocab.py      # Vocabulary compliance checker
        │   └── validate_cefr_readability.py # Grammar/readability checker
        ├── examples/
        │   ├── sample_inputs.md
        │   └── sample_outputs.md
        └── tests/
            └── test_cases.md
```

---

## Known limitations

1. **Word-sense ambiguity** — *bank* (finance vs. river) is not disambiguated; the validator uses the lowest recorded CEFR level for the token.
2. **Irregular verb forms** — *went*, *better*, *worse* are not resolved by the basic lemmatiser and may appear as unknown.
3. **Clause depth is a heuristic** — subordinate clause nesting is counted by conjunction tokens, not a parse tree.
4. **Passive detection via regex** — complex constructions (*was said to have been seen*) may be missed.
5. **Proper nouns** — appear as "unknown" in vocabulary output; this is expected and not treated as a violation.

---

## License

MIT

**Vocabulary data** is derived from [CEFR-J Vocabulary Profile 1.5](https://github.com/openlanguageprofiles/olp-en-cefrj) (Yukio Tono, Tokyo University of Foreign Studies) and [Octanove Vocabulary Profile C1/C2 1.0](https://github.com/openlanguageprofiles/olp-en-cefrj) (Octanove Labs), both licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). If you distribute or adapt this project, you must credit the authors and release any derivative vocabulary data under the same license.
