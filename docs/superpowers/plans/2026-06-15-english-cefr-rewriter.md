# English CEFR Level Rewriter — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Claude skill that rewrites English text to a target CEFR level (A1–C2), with vocabulary and grammar validation scripts.

**Architecture:** A SKILL.md gives Claude detailed rewriting instructions, backed by a vocabulary CSV (scraped from ESL Lounge) and per-level grammar profiles. Two Python scripts validate output: one checks vocabulary level, one checks grammar/readability heuristics.

**Tech Stack:** Python 3.10+, `requests`, `beautifulsoup4`, `pytest`, `re`, `csv`

---

## File Map

| Path | Purpose |
|---|---|
| `requirements.txt` | Python dependencies |
| `pytest.ini` | Test runner config |
| `scripts/scrape_esl_lounge.py` | One-time scraper → `cefr_vocabulary.csv` |
| `scripts/validate_cefr_vocab.py` | CLI: check vocabulary level of a text |
| `scripts/validate_cefr_readability.py` | CLI: check grammar/sentence complexity |
| `tests/test_scrape_esl_lounge.py` | Tests for scraper parsing logic |
| `tests/test_validate_cefr_vocab.py` | Tests for vocabulary validator |
| `tests/test_validate_cefr_readability.py` | Tests for readability validator |
| `resources/vocabulary/cefr_vocabulary.csv` | Generated: word, cefr_level, pos |
| `resources/vocabulary/cefr_vocabulary.sample.csv` | First 100 rows |
| `resources/vocabulary/README.md` | Data provenance notes |
| `resources/grammar/A1.md` | Grammar profile for A1 |
| `resources/grammar/A2.md` | Grammar profile for A2 |
| `resources/grammar/B1.md` | Grammar profile for B1 |
| `resources/grammar/B2.md` | Grammar profile for B2 |
| `resources/grammar/C1.md` | Grammar profile for C1 |
| `resources/grammar/C2.md` | Grammar profile for C2 |
| `SKILL.md` | Claude-facing skill (main artifact) |
| `README.md` | Human-facing documentation |
| `examples/sample_inputs.md` | Three realistic source texts |
| `examples/sample_outputs.md` | Expected rewrites at various levels |
| `tests/test_cases.md` | 12 manual test cases |

---

### Task 1: Project structure and dependencies

**Files:**
- Create: `requirements.txt`
- Create: `pytest.ini`
- Create: `scripts/.gitkeep`, `tests/.gitkeep`, `resources/vocabulary/.gitkeep`, `resources/grammar/.gitkeep`, `examples/.gitkeep`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p scripts tests resources/vocabulary resources/grammar examples docs/superpowers/plans
touch scripts/.gitkeep tests/.gitkeep resources/vocabulary/.gitkeep resources/grammar/.gitkeep examples/.gitkeep
```

Expected: no errors.

- [ ] **Step 2: Write `requirements.txt`**

```
requests>=2.28
beautifulsoup4>=4.11
pytest>=7.0
```

- [ ] **Step 3: Write `pytest.ini`**

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

- [ ] **Step 4: Install dependencies**

```bash
pip install -r requirements.txt
```

Expected output contains: `Successfully installed` (or `already satisfied` for each package).

- [ ] **Step 5: Commit**

```bash
git add requirements.txt pytest.ini scripts/.gitkeep tests/.gitkeep resources/vocabulary/.gitkeep resources/grammar/.gitkeep examples/.gitkeep
git commit -m "chore: project structure and dependencies"
```

---

### Task 2: Vocabulary scraper (TDD)

**Files:**
- Create: `tests/test_scrape_esl_lounge.py`
- Create: `scripts/scrape_esl_lounge.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_scrape_esl_lounge.py`:

```python
# ABOUTME: Tests for ESL Lounge scraper — parsing and URL construction
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from scrape_esl_lounge import build_url, fetch_words, write_csv


def test_build_url():
    assert build_url("a1", "nouns") == (
        "https://www.esl-lounge.com/student/reference/"
        "a1-cefr-vocabulary-word-list-nouns.php"
    )


def test_build_url_b2_verbs():
    assert build_url("b2", "verbs") == (
        "https://www.esl-lounge.com/student/reference/"
        "b2-cefr-vocabulary-word-list-verbs.php"
    )


def _mock_response(html: str) -> MagicMock:
    resp = MagicMock()
    resp.text = html
    resp.raise_for_status = MagicMock()
    return resp


def test_fetch_words_parses_table():
    html = """
    <html><body>
    <table>
      <tr><td>apple</td><td>I eat an apple.</td><td>/ˈæp.əl/</td></tr>
      <tr><td>book</td><td>Read this book.</td><td>/bʊk/</td></tr>
    </table>
    </body></html>
    """
    with patch("scrape_esl_lounge.requests.get", return_value=_mock_response(html)):
        words = fetch_words("a1", "nouns")
    assert "apple" in words
    assert "book" in words


def test_fetch_words_lowercases():
    html = "<html><body><table><tr><td>Apple</td><td>ex</td><td>ipa</td></tr></table></body></html>"
    with patch("scrape_esl_lounge.requests.get", return_value=_mock_response(html)):
        words = fetch_words("a1", "nouns")
    assert "apple" in words
    assert "Apple" not in words


def test_fetch_words_skips_empty_first_cell():
    html = """
    <html><body><table>
      <tr><td></td><td>empty</td><td>ipa</td></tr>
      <tr><td>cat</td><td>The cat sat.</td><td>/kæt/</td></tr>
    </table></body></html>
    """
    with patch("scrape_esl_lounge.requests.get", return_value=_mock_response(html)):
        words = fetch_words("a1", "nouns")
    assert "cat" in words
    assert "" not in words


def test_fetch_words_skips_numeric_first_cell():
    html = """
    <html><body><table>
      <tr><td>1</td><td>num</td><td>ipa</td></tr>
      <tr><td>dog</td><td>A dog.</td><td>/dɒɡ/</td></tr>
    </table></body></html>
    """
    with patch("scrape_esl_lounge.requests.get", return_value=_mock_response(html)):
        words = fetch_words("a1", "nouns")
    assert "dog" in words
    assert "1" not in words


def test_write_csv(tmp_path):
    rows = [
        {"word": "apple", "cefr_level": "A1", "pos": "noun"},
        {"word": "run", "cefr_level": "A1", "pos": "verb"},
    ]
    out = tmp_path / "vocab.csv"
    write_csv(rows, out)
    content = out.read_text()
    assert "word,cefr_level,pos" in content
    assert "apple,A1,noun" in content
    assert "run,A1,verb" in content
```

- [ ] **Step 2: Run tests, verify they fail**

```bash
pytest tests/test_scrape_esl_lounge.py -v
```

Expected: `ModuleNotFoundError: No module named 'scrape_esl_lounge'`

- [ ] **Step 3: Write `scripts/scrape_esl_lounge.py`**

```python
# ABOUTME: Scrapes CEFR vocabulary word lists from ESL Lounge and outputs cefr_vocabulary.csv
import csv
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.esl-lounge.com/student/reference"
LEVELS = ["a1", "a2", "b1", "b2", "c1", "c2"]
POS_MAP = {
    "nouns": "noun",
    "verbs": "verb",
    "adjectives": "adjective",
    "adverbs": "adverb",
}


def build_url(level: str, pos: str) -> str:
    return f"{BASE_URL}/{level}-cefr-vocabulary-word-list-{pos}.php"


def fetch_words(level: str, pos: str) -> list:
    url = build_url(level, pos)
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    words = []
    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if not cells:
                continue
            word = cells[0].get_text(strip=True).lower()
            if word and not word.isdigit():
                words.append(word)
    return words


def scrape_all() -> list:
    rows = []
    for level in LEVELS:
        for pos_key, pos_label in POS_MAP.items():
            print(f"  Fetching {level.upper()} {pos_key}...", file=sys.stderr)
            try:
                words = fetch_words(level, pos_key)
                for word in words:
                    rows.append({
                        "word": word,
                        "cefr_level": level.upper(),
                        "pos": pos_label,
                    })
                time.sleep(1)
            except Exception as e:
                print(f"  ERROR {level} {pos_key}: {e}", file=sys.stderr)
    return rows


def write_csv(rows: list, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["word", "cefr_level", "pos"])
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    out = Path(__file__).parent.parent / "resources" / "vocabulary" / "cefr_vocabulary.csv"
    print("Scraping ESL Lounge...", file=sys.stderr)
    rows = scrape_all()
    write_csv(rows, out)
    print(f"Written {len(rows)} rows to {out}", file=sys.stderr)

    sample = out.parent / "cefr_vocabulary.sample.csv"
    with open(sample, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["word", "cefr_level", "pos"])
        writer.writeheader()
        writer.writerows(rows[:100])
    print(f"Sample written to {sample}", file=sys.stderr)
```

- [ ] **Step 4: Run tests, verify they pass**

```bash
pytest tests/test_scrape_esl_lounge.py -v
```

Expected: `6 passed`

- [ ] **Step 5: Commit**

```bash
git add scripts/scrape_esl_lounge.py tests/test_scrape_esl_lounge.py
git commit -m "feat: vocabulary scraper with tests"
```

---

### Task 3: Generate vocabulary CSV

**Files:**
- Create: `resources/vocabulary/cefr_vocabulary.csv` (generated)
- Create: `resources/vocabulary/cefr_vocabulary.sample.csv` (generated)
- Create: `resources/vocabulary/README.md`

- [ ] **Step 1: Run the scraper**

```bash
python3 scripts/scrape_esl_lounge.py
```

Expected: lines like `Fetching A1 nouns...` for each level+POS combination. Final line: `Written NNNN rows to resources/vocabulary/cefr_vocabulary.csv`

This takes ~90 seconds (1 second sleep × 24 requests).

- [ ] **Step 2: Verify the output**

```bash
wc -l resources/vocabulary/cefr_vocabulary.csv
head -5 resources/vocabulary/cefr_vocabulary.csv
```

Expected: header + several hundred rows. First lines:
```
word,cefr_level,pos
actor,A1,noun
actress,A1,noun
adult,A1,noun
...
```

- [ ] **Step 3: Write `resources/vocabulary/README.md`**

```markdown
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
```

- [ ] **Step 4: Commit**

```bash
git add resources/vocabulary/
git commit -m "data: vocabulary CSV from ESL Lounge and provenance README"
```

---

### Task 4: Vocabulary validator (TDD)

**Files:**
- Create: `tests/test_validate_cefr_vocab.py`
- Create: `scripts/validate_cefr_vocab.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_validate_cefr_vocab.py`:

```python
# ABOUTME: Tests for CEFR vocabulary level validator
import csv
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from validate_cefr_vocab import load_vocab, is_above_level, tokenise, lemmatise, validate


@pytest.fixture
def mini_csv(tmp_path):
    path = tmp_path / "vocab.csv"
    path.write_text(
        "word,cefr_level,pos\n"
        "apple,A1,noun\n"
        "bank,A2,noun\n"
        "acquire,C1,verb\n"
        "run,A1,verb\n"
    )
    return path


def test_load_vocab(mini_csv):
    vocab = load_vocab(mini_csv)
    assert vocab["apple"] == "A1"
    assert vocab["bank"] == "A2"
    assert vocab["acquire"] == "C1"


def test_is_above_level_higher():
    assert is_above_level("B2", "A1") is True


def test_is_above_level_lower():
    assert is_above_level("A1", "B2") is False


def test_is_above_level_equal():
    assert is_above_level("A1", "A1") is False


def test_tokenise_strips_punctuation():
    assert tokenise("Hello, world!") == ["hello", "world"]


def test_tokenise_lowercases():
    assert tokenise("The Cat") == ["the", "cat"]


def test_lemmatise_ed():
    assert lemmatise("walked") == "walk"


def test_lemmatise_s():
    assert lemmatise("cats") == "cat"


def test_lemmatise_ing():
    # Basic strip — documented limitation: running → runn (not run)
    assert lemmatise("walking") == "walk"


def test_lemmatise_short_word_unchanged():
    assert lemmatise("is") == "is"


def test_validate_ok_word_not_in_results(mini_csv):
    vocab = load_vocab(mini_csv)
    results = validate("I eat an apple.", "A2", vocab)
    words_flagged = [r["word"] for r in results]
    assert "apple" not in words_flagged


def test_validate_above_level_flagged(mini_csv):
    vocab = load_vocab(mini_csv)
    results = validate("I want to acquire skills.", "A1", vocab)
    statuses = {r["word"]: r["status"] for r in results}
    assert statuses["acquire"] == "above_level"


def test_validate_unknown_flagged(mini_csv):
    vocab = load_vocab(mini_csv)
    results = validate("The scientist discovered a new element.", "B1", vocab)
    statuses = {r["word"]: r["status"] for r in results}
    assert statuses.get("scientist") == "unknown"


def test_validate_deduplicates(mini_csv):
    vocab = load_vocab(mini_csv)
    results = validate("apple apple apple", "B1", vocab)
    # apple is A1 → ok; no violations at all, and no duplicates
    assert results == []


def test_validate_lemmatised_form_accepted(mini_csv):
    vocab = load_vocab(mini_csv)
    # "runs" → lemmatised "run" → A1, target A2 → ok
    results = validate("She runs fast.", "A2", vocab)
    words_flagged = [r["word"] for r in results]
    assert "runs" not in words_flagged
```

- [ ] **Step 2: Run tests, verify they fail**

```bash
pytest tests/test_validate_cefr_vocab.py -v
```

Expected: `ModuleNotFoundError: No module named 'validate_cefr_vocab'`

- [ ] **Step 3: Write `scripts/validate_cefr_vocab.py`**

```python
# ABOUTME: Validates English text vocabulary against a CEFR level using cefr_vocabulary.csv
import argparse
import csv
import re
import sys
from pathlib import Path

CEFR_ORDER = ["A1", "A2", "B1", "B2", "C1", "C2"]
_DEFAULT_CSV = Path(__file__).parent.parent / "resources" / "vocabulary" / "cefr_vocabulary.csv"


def load_vocab(csv_path: Path) -> dict:
    vocab = {}
    with open(csv_path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            word = row["word"].lower()
            level = row["cefr_level"].upper()
            if word not in vocab:
                vocab[word] = level
    return vocab


def is_above_level(word_level: str, target_level: str) -> bool:
    if word_level not in CEFR_ORDER or target_level not in CEFR_ORDER:
        return False
    return CEFR_ORDER.index(word_level) > CEFR_ORDER.index(target_level)


def tokenise(text: str) -> list:
    return [t.lower() for t in re.findall(r"[a-zA-Z']+", text)]


def lemmatise(word: str) -> str:
    for suffix in ("ing", "ed", "s"):
        if word.endswith(suffix) and len(word) > len(suffix) + 2:
            return word[: -len(suffix)]
    return word


def validate(text: str, target_level: str, vocab: dict) -> list:
    target = target_level.upper()
    results = []
    seen = set()
    for token in tokenise(text):
        if token in seen:
            continue
        seen.add(token)
        found_level = vocab.get(token) or vocab.get(lemmatise(token))
        if found_level is None:
            status = "unknown"
        elif is_above_level(found_level, target):
            status = "above_level"
        else:
            continue
        results.append({
            "word": token,
            "found_level": found_level or "—",
            "target_level": target,
            "status": status,
        })
    return results


def _print_table(results: list) -> None:
    if not results:
        print("No violations found.")
        return
    print(f"{'word':<20} {'found_level':<12} {'target_level':<12} {'status'}")
    print("-" * 56)
    for r in results:
        print(f"{r['word']:<20} {r['found_level']:<12} {r['target_level']:<12} {r['status']}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate CEFR vocabulary level of English text")
    parser.add_argument("--text", required=True, help="Text to validate")
    parser.add_argument("--level", required=True, choices=CEFR_ORDER, help="Target CEFR level")
    parser.add_argument("--vocab", default=str(_DEFAULT_CSV), help="Path to vocabulary CSV")
    args = parser.parse_args()

    vocab = load_vocab(Path(args.vocab))
    results = validate(args.text, args.level, vocab)
    _print_table(results)
    return 1 if results else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests, verify they pass**

```bash
pytest tests/test_validate_cefr_vocab.py -v
```

Expected: `12 passed`

- [ ] **Step 5: Smoke-test the CLI**

```bash
python3 scripts/validate_cefr_vocab.py \
  --text "The scientist investigated the phenomenon." \
  --level A1
```

Expected: table showing `scientist`, `investigated`, `phenomenon` flagged as `unknown` or `above_level`.

- [ ] **Step 6: Commit**

```bash
git add scripts/validate_cefr_vocab.py tests/test_validate_cefr_vocab.py
git commit -m "feat: CEFR vocabulary validator with tests"
```

---

### Task 5: Readability validator (TDD)

**Files:**
- Create: `tests/test_validate_cefr_readability.py`
- Create: `scripts/validate_cefr_readability.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_validate_cefr_readability.py`:

```python
# ABOUTME: Tests for CEFR grammar/readability validator
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from validate_cefr_readability import (
    PROFILES,
    split_sentences,
    count_words,
    count_subordinate_clauses,
    has_passive,
    check_modals,
    validate_readability,
)


def test_split_sentences_periods():
    assert len(split_sentences("Hello world. How are you?")) == 2


def test_split_sentences_single():
    assert split_sentences("One sentence.") == ["One sentence."]


def test_count_words():
    assert count_words("The cat sat on the mat.") == 6


def test_count_subordinate_clauses_that():
    assert count_subordinate_clauses("I think that you are right.") == 1


def test_count_subordinate_clauses_none():
    assert count_subordinate_clauses("She runs fast.") == 0


def test_count_subordinate_clauses_multiple():
    assert count_subordinate_clauses("I know that she said that he left.") == 2


def test_has_passive_true():
    assert has_passive("The book was written by her.") is True


def test_has_passive_false():
    assert has_passive("She wrote the book.") is False


def test_has_passive_present():
    assert has_passive("The report is reviewed every week.") is True


def test_profiles_a1_can():
    assert "can" in PROFILES["A1"]["allowed_modals"]


def test_profiles_a1_must_not_allowed():
    assert "must" not in PROFILES["A1"]["allowed_modals"]


def test_profiles_b1_must_allowed():
    assert "must" in PROFILES["B1"]["allowed_modals"]


def test_profiles_c1_no_modal_restriction():
    assert PROFILES["C1"]["allowed_modals"] is None


def test_check_modals_allowed_returns_empty():
    assert check_modals("You can do it.", PROFILES["A1"]["allowed_modals"]) == []


def test_check_modals_disallowed_returned():
    result = check_modals("You must do it.", PROFILES["A1"]["allowed_modals"])
    assert "must" in result


def test_validate_readability_sentence_too_long():
    text = "This is a really very long sentence that goes well beyond the A1 word count limit."
    violations = validate_readability(text, "A1")
    rules = [v["rule"] for v in violations]
    assert "sentence_length" in rules


def test_validate_readability_passive_at_a1():
    violations = validate_readability("The cake was eaten by the boy.", "A1")
    rules = [v["rule"] for v in violations]
    assert "passive_voice" in rules


def test_validate_readability_passive_ok_at_b1():
    violations = validate_readability("The cake was eaten by the boy.", "B1")
    rules = [v["rule"] for v in violations]
    assert "passive_voice" not in rules


def test_validate_readability_subordinate_at_a1():
    violations = validate_readability("I think that she said that he left.", "A1")
    rules = [v["rule"] for v in violations]
    assert "clause_depth" in rules


def test_validate_readability_modal_violation():
    violations = validate_readability("You must leave now.", "A1")
    rules = [v["rule"] for v in violations]
    assert "modal_verb" in rules


def test_validate_readability_clean_a1():
    violations = validate_readability("I can swim. She is here.", "A1")
    assert violations == []
```

- [ ] **Step 2: Run tests, verify they fail**

```bash
pytest tests/test_validate_cefr_readability.py -v
```

Expected: `ModuleNotFoundError: No module named 'validate_cefr_readability'`

- [ ] **Step 3: Write `scripts/validate_cefr_readability.py`**

```python
# ABOUTME: Validates English text grammar complexity against a CEFR level using heuristic rules
import argparse
import re
import sys

CEFR_ORDER = ["A1", "A2", "B1", "B2", "C1", "C2"]

PROFILES = {
    "A1": {
        "max_words_per_sentence": 10,
        "max_clause_depth": 0,
        "passive_allowed": False,
        "allowed_modals": {"can", "can't", "cannot"},
    },
    "A2": {
        "max_words_per_sentence": 15,
        "max_clause_depth": 1,
        "passive_allowed": False,
        "allowed_modals": {"can", "can't", "cannot", "could", "will", "won't", "would"},
    },
    "B1": {
        "max_words_per_sentence": 20,
        "max_clause_depth": 1,
        "passive_allowed": True,
        "allowed_modals": {
            "can", "can't", "cannot", "could", "will", "won't", "would",
            "must", "should", "may", "might", "shall",
        },
    },
    "B2": {
        "max_words_per_sentence": 25,
        "max_clause_depth": 2,
        "passive_allowed": True,
        "allowed_modals": {
            "can", "can't", "cannot", "could", "will", "won't", "would",
            "must", "should", "may", "might", "shall", "need", "ought",
        },
    },
    "C1": {
        "max_words_per_sentence": 35,
        "max_clause_depth": 3,
        "passive_allowed": True,
        "allowed_modals": None,
    },
    "C2": {
        "max_words_per_sentence": 999,
        "max_clause_depth": 999,
        "passive_allowed": True,
        "allowed_modals": None,
    },
}

_SUBORDINATORS = re.compile(
    r"\b(that|which|who|whom|whose|when|where|while|because|although|"
    r"since|unless|until|if|though|so that|in order that)\b",
    re.IGNORECASE,
)
_PASSIVE = re.compile(
    r"\b(am|is|are|was|were|be|been|being)\s+\w+ed\b", re.IGNORECASE
)
_ALL_MODALS = {
    "can", "could", "will", "would", "must", "should", "may", "might",
    "shall", "need", "ought", "can't", "cannot", "won't",
}


def split_sentences(text: str) -> list:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]


def count_words(sentence: str) -> int:
    return len(re.findall(r"\b\w+\b", sentence))


def count_subordinate_clauses(sentence: str) -> int:
    return len(_SUBORDINATORS.findall(sentence))


def has_passive(sentence: str) -> bool:
    return bool(_PASSIVE.search(sentence))


def check_modals(sentence: str, allowed) -> list:
    if allowed is None:
        return []
    pattern = r"\b(" + "|".join(re.escape(m) for m in _ALL_MODALS) + r")\b"
    found = re.findall(pattern, sentence, re.IGNORECASE)
    return [m for m in found if m.lower() not in allowed]


def validate_readability(text: str, target_level: str) -> list:
    profile = PROFILES[target_level.upper()]
    violations = []
    for sentence in split_sentences(text):
        word_count = count_words(sentence)
        if word_count > profile["max_words_per_sentence"]:
            violations.append({
                "sentence": sentence[:80],
                "rule": "sentence_length",
                "detail": f"{word_count} words (max {profile['max_words_per_sentence']})",
            })
        depth = count_subordinate_clauses(sentence)
        if depth > profile["max_clause_depth"]:
            violations.append({
                "sentence": sentence[:80],
                "rule": "clause_depth",
                "detail": f"{depth} subordinate clause(s) (max {profile['max_clause_depth']})",
            })
        if not profile["passive_allowed"] and has_passive(sentence):
            violations.append({
                "sentence": sentence[:80],
                "rule": "passive_voice",
                "detail": "passive construction not allowed at this level",
            })
        for modal in check_modals(sentence, profile["allowed_modals"]):
            violations.append({
                "sentence": sentence[:80],
                "rule": "modal_verb",
                "detail": f"'{modal}' not in allowed modal inventory for {target_level.upper()}",
            })
    return violations


def _print_violations(violations: list) -> None:
    if not violations:
        print("No violations found.")
        return
    for v in violations:
        print(f"[{v['rule']}] {v['detail']}")
        print(f"  → {v['sentence']}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate CEFR grammar/readability level")
    parser.add_argument("--text", required=True, help="Text to validate")
    parser.add_argument("--level", required=True, choices=CEFR_ORDER, help="Target CEFR level")
    args = parser.parse_args()

    violations = validate_readability(args.text, args.level)
    _print_violations(violations)
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests, verify they pass**

```bash
pytest tests/test_validate_cefr_readability.py -v
```

Expected: `20 passed`

- [ ] **Step 5: Run full test suite**

```bash
pytest -v
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add scripts/validate_cefr_readability.py tests/test_validate_cefr_readability.py
git commit -m "feat: CEFR readability/grammar validator with tests"
```

---

### Task 6: Grammar profiles (A1–C2)

**Files:**
- Create: `resources/grammar/A1.md` through `resources/grammar/C2.md`

- [ ] **Step 1: Write `resources/grammar/A1.md`**

```markdown
# A1 Grammar Profile

## Sentence length
- Target: 5–8 words per sentence
- Maximum: 10 words

## Tense/aspect inventory
- Present simple (I eat, she works)
- Present continuous (I am eating)
- No past tenses

## Clause depth
- No subordinate clauses
- Coordination only: and, but, or, so

## Passive voice
- Not permitted

## Modal verbs
- can (ability): I can swim.
- can't / cannot (inability): I can't drive.

## Discourse markers
- and, but, or, so, then, also
```

- [ ] **Step 2: Write `resources/grammar/A2.md`**

```markdown
# A2 Grammar Profile

## Sentence length
- Target: 8–12 words per sentence
- Maximum: 15 words

## Tense/aspect inventory
- All A1 tenses plus:
- Past simple (I went, she worked)
- Going to future (I am going to eat)
- Will for predictions (It will rain)

## Clause depth
- Up to 1 subordinate clause per sentence
- Conjunctions: because, when, if, before, after

## Passive voice
- Not permitted

## Modal verbs
- can, can't, cannot (A1)
- could (past ability, polite requests)
- will, won't (future)
- would (conditional, polite requests)

## Discourse markers
- and, but, so, because, when, although, however (simple)
```

- [ ] **Step 3: Write `resources/grammar/B1.md`**

```markdown
# B1 Grammar Profile

## Sentence length
- Target: 12–18 words per sentence
- Maximum: 20 words

## Tense/aspect inventory
- All A2 tenses plus:
- Present perfect (I have worked here for two years)
- Past continuous (I was working when she called)
- Used to (I used to play football)

## Clause depth
- Up to 1 subordinate clause per sentence
- Relative clauses (who, which, that, where)
- Conjunctions: because, although, since, unless, while

## Passive voice
- Permitted in present and past simple
- The report is written every week.
- The letter was sent yesterday.

## Modal verbs
- All A2 modals plus:
- must (obligation): You must wear a helmet.
- should (advice): You should rest.
- may / might (possibility): It may rain.
- shall (offers, formal): Shall I help?

## Discourse markers
- however, therefore, although, despite, on the other hand, for example, firstly, finally
```

- [ ] **Step 4: Write `resources/grammar/B2.md`**

```markdown
# B2 Grammar Profile

## Sentence length
- Target: 15–22 words per sentence
- Maximum: 25 words

## Tense/aspect inventory
- All B1 tenses plus:
- Past perfect (She had already left when I arrived)
- Future perfect (By 2030, scientists will have discovered …)
- Second conditional (If I had more time, I would …)
- Third conditional (If she had studied, she would have passed)

## Clause depth
- Up to 2 levels of embedded subordinate clauses
- e.g. "She said that she thought that he was right."

## Passive voice
- Permitted in all tenses
- Reporting structures: It is believed that… / It has been shown that…

## Modal verbs
- All B1 modals plus:
- need (necessity): You needn't worry.
- ought to (obligation/advice): You ought to apologise.

## Discourse markers
- moreover, consequently, furthermore, whereas, in contrast, as a result, nevertheless, in addition, on the contrary
```

- [ ] **Step 5: Write `resources/grammar/C1.md`**

```markdown
# C1 Grammar Profile

## Sentence length
- Target: 18–30 words per sentence
- Maximum: 35 words

## Tense/aspect inventory
- All B2 tenses plus:
- Mixed conditionals
- Perfect conditionals (would have been, might have had)
- Subjunctive mood (It is essential that he be present)

## Clause depth
- Up to 3 levels of embedded subordinate clauses
- Complex nominalisations: "The fact that…", "What is clear is that…"

## Passive voice
- All passive constructions permitted
- Complex passives: "is said to have been…", "is believed to be…"

## Modal verbs
- All modals and semi-modals freely used
- dare, used to, be able to, be supposed to, be likely to

## Discourse markers
- thereby, nonetheless, hitherto, accordingly, inasmuch as, to the extent that, by virtue of
- Stance markers: arguably, it could be contended that, it is worth noting that
```

- [ ] **Step 6: Write `resources/grammar/C2.md`**

```markdown
# C2 Grammar Profile

## Sentence length
- No limit — follows rhetorical effect and style

## Tense/aspect inventory
- All tenses and aspects with full pragmatic nuance
- Archaic and literary forms where stylistically appropriate

## Clause depth
- No limit — complex embedding used for precision, not avoided

## Passive voice
- All constructions; chosen for discourse effect, not avoidance

## Modal verbs
- Full modal system with fine-grained epistemic and deontic distinctions
- Semi-modals, quasi-modals, and modal idioms (be bound to, be apt to)

## Discourse markers
- Full repertoire including academic, literary, and formal registers
- Cleft sentences: "It was not until 1989 that…"
- Inversion for emphasis: "Not only did she…", "Rarely has such…"
```

- [ ] **Step 7: Commit**

```bash
git add resources/grammar/
git commit -m "docs: CEFR grammar profiles A1 through C2"
```

---

### Task 7: SKILL.md

**Files:**
- Create: `SKILL.md`

- [ ] **Step 1: Write `SKILL.md`**

```markdown
---
name: english-cefr-level-rewriter
description: Use when rewriting English text to match a target CEFR level — A1 (Beginner) through C2 (Proficiency). Applies when the user wants to simplify or adapt English text for ESL learners, adjust vocabulary and grammar to a specific level, or validate whether a passage is appropriate for a given CEFR stage. References ESL Lounge vocabulary data and CEFR grammar profiles.
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
python3 scripts/validate_cefr_vocab.py --text "..." --level B1

# Check grammar/readability
python3 scripts/validate_cefr_readability.py --text "..." --level B1
```

Both scripts exit 0 (no violations) / 1 (violations found).

**Known limitations:**
- Vocab script uses basic lemmatisation; irregular forms (went, better) may not be resolved
- Readability script uses heuristics, not a full parser; clause depth is approximate
- Proper nouns will appear as "unknown" in vocab output — this is expected
```

- [ ] **Step 2: Commit**

```bash
git add SKILL.md
git commit -m "feat: SKILL.md — English CEFR level rewriter for Claude"
```

---

### Task 8: Examples

**Files:**
- Create: `examples/sample_inputs.md`
- Create: `examples/sample_outputs.md`

- [ ] **Step 1: Write `examples/sample_inputs.md`**

```markdown
# Sample Inputs

Three realistic source texts for testing and demonstration.

---

## Input 1: News article excerpt (estimated C1)

> Scientists have demonstrated that regular physical exercise has a significant positive impact on cognitive function, potentially reducing the risk of neurodegenerative diseases such as Alzheimer's by stimulating neuroplasticity in key brain regions.

---

## Input 2: Product manual paragraph (estimated B1/B2)

> Prior to installation, ensure that the power supply has been disconnected and that all relevant components have been verified as compatible with the existing infrastructure.

---

## Input 3: Academic abstract (estimated C1/C2)

> This paper examines the socioeconomic determinants of educational attainment in post-industrial societies, with particular emphasis on the mediating role of cultural capital in perpetuating intergenerational inequality.
```

- [ ] **Step 2: Write `examples/sample_outputs.md`**

````markdown
# Sample Outputs

Expected rewrites of the three sample inputs at various CEFR levels.

---

## Input 1 (news article) → A2 | balanced | with_notes

**Rewritten text:**

Exercise is good for your brain. Scientists say that regular exercise can lower the risk of brain diseases like Alzheimer's. Exercise helps your brain cells (neurons) grow and connect better.

**Changes made:**
- "demonstrated" → "say" (A2 verb)
- "significant positive impact" → "is good for" (A2 phrasing)
- "cognitive function" → "brain" (A1 noun; concept preserved)
- "neurodegenerative diseases" → "brain diseases" with "Alzheimer's" retained as proper noun example
- "stimulating neuroplasticity" → "helps your brain cells (neurons) grow and connect better" (concept explained; *neurons* kept with gloss as B1+ term, flagged for review in strict mode)
- Source sentence (34 words) split into three A2-length sentences

---

## Input 2 (product manual) → A1 | strict | with_notes

**Rewritten text:**

Stop. Turn off the power first. Then check all parts. Make sure they work together.

**Changes made:**
- "Prior to installation" → "Stop. … first." (A1 imperative structure)
- "ensure that the power supply has been disconnected" → "Turn off the power" (active, A1 vocabulary)
- "all relevant components" → "all parts" (A1 noun)
- "verified as compatible with the existing infrastructure" → "Make sure they work together" (A1 phrasing)
- Passive constructions removed (not permitted at A1)
- Single source sentence (28 words) split into four A1-length sentences

---

## Input 3 (academic abstract) → B1 | balanced | with_notes

**Rewritten text:**

This paper looks at why some people do better in school than others. It focuses on two things: money and culture. The main question is whether parents' education and wealth affect how well their children do in school, and whether this continues from one generation (group of people born at the same time) to the next.

**Changes made:**
- "socioeconomic determinants" → "money and culture" (B1 vocabulary; concept preserved)
- "educational attainment" → "how well their children do in school" (B1 phrasing)
- "post-industrial societies" → "(these are) modern societies" — retained context
- "mediating role of cultural capital" → "education and wealth" (C1/C2 term simplified)
- "perpetuating intergenerational inequality" → "continues from one generation … to the next" with *generation* glossed in parentheses
- Source sentence (32 words) split into three B1-length sentences
````

- [ ] **Step 3: Commit**

```bash
git add examples/
git commit -m "docs: sample inputs and outputs for three CEFR levels"
```

---

### Task 9: Test cases and README

**Files:**
- Create: `tests/test_cases.md`
- Create: `README.md`

- [ ] **Step 1: Write `tests/test_cases.md`**

````markdown
# Manual Test Cases

12 cases, 2 per CEFR target level. Each case specifies source text, target level, mode, expected rewritten output, and key validation checks.

---

## TC-01 | Target: A1 | Mode: strict

**Source:** "The government has implemented new legislation to reduce carbon emissions."

**Expected rewrite:** "The government made a new rule. This rule helps the air stay clean."

**Key checks:**
- No words above A1 (government, rule, air, clean all A1)
- No passive voice
- Max 10 words per sentence
- "legislation" removed and concept explained
- "carbon emissions" → "the air stay clean"

---

## TC-02 | Target: A1 | Mode: balanced

**Source:** "She acquired several professional qualifications during her studies."

**Expected rewrite:** "She got many certificates (official documents) during her studies."

**Key checks:**
- "acquired" → "got" (A1 verb)
- "professional qualifications" → "certificates" with gloss
- No passive; no subordinate clauses
- Proper nouns (none here): N/A

---

## TC-03 | Target: A2 | Mode: strict

**Source:** "The renovation of the apartment was completed ahead of schedule due to efficient project management."

**Expected rewrite:** "They finished fixing the apartment early. Good planning helped them do this."

**Key checks:**
- Passive removed ("was completed" → active)
- "renovation" → "fixing"
- "efficient project management" → "Good planning"
- Each sentence ≤ 15 words

---

## TC-04 | Target: A2 | Mode: balanced

**Source:** "Despite the adverse weather conditions, the expedition reached its destination."

**Expected rewrite:** "The weather was very bad. But the group still arrived at the place they wanted to go."

**Key checks:**
- "adverse" → "very bad" (A2 phrasing)
- "expedition" → "group" (A2 noun)
- "destination" → "the place they wanted to go" (A2 explanation)
- "Despite" → "But" (A2 discourse marker)

---

## TC-05 | Target: B1 | Mode: balanced

**Source:** "The CEO announced that the company would be restructuring its operations to enhance profitability."

**Expected rewrite:** "The CEO said that the company would change how it works to make more money."

**Key checks:**
- "restructuring" → "change how it works"
- "enhance profitability" → "make more money"
- CEO kept as proper noun/abbreviation
- One subordinate clause ("that…") — within B1 limit

---

## TC-06 | Target: B1 | Mode: learning

**Source:** "Air pollution is exacerbated by industrial emissions from fossil fuel combustion."

**Expected rewrite:** "Air pollution is made worse (exacerbated) by pollution from factories. These factories burn fossil fuels (coal, oil, gas)."

**Key checks:**
- "exacerbated" kept with gloss in parentheses (learning mode)
- "industrial emissions" → "pollution from factories"
- "fossil fuels" kept with examples
- Passive ("is made worse") permitted at B1

---

## TC-07 | Target: B2 | Mode: balanced

**Source:** "The study conclusively demonstrates a causal relationship between sleep deprivation and impaired decision-making."

**Expected rewrite:** "The study clearly shows that lack of sleep causes people to make worse decisions."

**Key checks:**
- "conclusively" → "clearly" (B2 adverb)
- "demonstrates a causal relationship between" → "shows that … causes" (clearer phrasing)
- "sleep deprivation" → "lack of sleep"
- "impaired decision-making" → "make worse decisions"

---

## TC-08 | Target: B2 | Mode: strict

**Source:** "Notwithstanding the aforementioned limitations, the methodology remains robust and replicable."

**Expected rewrite:** "Although there are some limitations, the method is still strong and can be repeated."

**Key checks:**
- "Notwithstanding" → "Although"
- "aforementioned" → "some" (reference clarified in context)
- "methodology" → "method"
- "robust" → "strong"; "replicable" → "can be repeated"
- Sentence ≤ 25 words

---

## TC-09 | Target: C1 | Mode: balanced

**Source:** "The bill was unanimously rejected by the legislature after protracted negotiations failed to yield a workable compromise."

**Expected rewrite:** "The legislature unanimously rejected the bill after lengthy negotiations failed to produce a workable compromise."

**Key checks:**
- "protracted" → "lengthy" (C1-appropriate synonym)
- Passive inverted to active ("was rejected" → "rejected") for clarity while remaining within C1 passive allowance
- "yield" → "produce" (clearer at C1)
- Sentence within C1 word-count limit

---

## TC-10 | Target: C1 | Mode: learning

**Source:** "The policy has inadvertently exacerbated socioeconomic disparities."

**Expected rewrite:** "The policy has inadvertently (without meaning to) exacerbated (made worse) socioeconomic (relating to income and society) disparities (differences)."

**Key checks:**
- All technical terms retained with glosses (learning mode)
- No structural changes needed — sentence is already C1-appropriate

---

## TC-11 | Target: C2 | Mode: balanced

**Source:** "He told me that you told him that she had said that the meeting was cancelled."

**Expected rewrite:** (Preserve as-is — already C2 level structure)

**Key checks:**
- Three-level embedding detected
- C2 has no clause-depth limit — no rewrite needed
- with_validation output shows "no violations"

---

## TC-12 | Target: C2 | Mode: strict | Proper noun test

**Source:** "Apple's CEO Tim Cook announced that the company had acquired a UK-based AI startup called DeepMind for an undisclosed sum."

**Expected rewrite:** "Apple's CEO Tim Cook announced that the company had bought a UK-based AI startup called DeepMind for an unknown amount of money."

**Key checks:**
- "acquired" → "bought" in strict mode (C1 word → C2 context, but strict mode replaces if simpler synonym exists)
- "undisclosed" → "unknown"
- Proper nouns preserved: Apple, Tim Cook, DeepMind, UK
- No factual changes
````

- [ ] **Step 2: Write `README.md`**

```markdown
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
python3 scripts/validate_cefr_vocab.py \
  --text "The scientist investigated the phenomenon." \
  --level B1

# Check grammar/readability
python3 scripts/validate_cefr_readability.py \
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
File: `resources/vocabulary/cefr_vocabulary.csv` (`word, cefr_level, pos`)

Each word is recorded at its *first* CEFR level appearance. The validator accepts any word at or below the target level.

To regenerate the vocabulary CSV:

```bash
python3 scripts/scrape_esl_lounge.py
```

## Grammar profiles

`resources/grammar/A1.md` through `C2.md` define, for each level:
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
  SKILL.md                          # Claude skill (main artifact)
  README.md                         # This file
  requirements.txt                  # Python dependencies
  resources/
    vocabulary/
      cefr_vocabulary.csv           # Vocabulary data
      cefr_vocabulary.sample.csv    # First 100 rows
      README.md                     # Data provenance
    grammar/
      A1.md … C2.md                 # Grammar profiles
  scripts/
    scrape_esl_lounge.py
    validate_cefr_vocab.py
    validate_cefr_readability.py
  examples/
    sample_inputs.md
    sample_outputs.md
  tests/
    test_cases.md
    test_scrape_esl_lounge.py
    test_validate_cefr_vocab.py
    test_validate_cefr_readability.py
```

## License

Vocabulary data is sourced from [ESL Lounge](https://www.esl-lounge.com) for educational use.
```

- [ ] **Step 3: Commit**

```bash
git add tests/test_cases.md README.md
git commit -m "docs: manual test cases and README"
```

---

### Task 10: Final integration check

- [ ] **Step 1: Run full test suite**

```bash
pytest -v
```

Expected: all tests pass. If any fail, fix the failure before continuing.

- [ ] **Step 2: Smoke-test vocabulary validator against real CSV**

```bash
python3 scripts/validate_cefr_vocab.py \
  --text "The scientist investigated the neurodegenerative phenomenon." \
  --level A1
```

Expected: `scientist`, `investigated`, `neurodegenerative`, `phenomenon` flagged as `unknown` or `above_level`.

- [ ] **Step 3: Smoke-test readability validator**

```bash
python3 scripts/validate_cefr_readability.py \
  --text "The results were analysed by the team, who concluded that, because the data was insufficient, further research was required." \
  --level A1
```

Expected: violations for `sentence_length`, `passive_voice`, `clause_depth`.

- [ ] **Step 4: Verify file structure matches plan**

```bash
find . -not -path './.git/*' -not -name '.gitkeep' | sort
```

Expected paths present: `SKILL.md`, `README.md`, `requirements.txt`, `pytest.ini`, all six grammar profiles, `cefr_vocabulary.csv`, `cefr_vocabulary.sample.csv`, both validation scripts, scraper, all three test files, `test_cases.md`, both example files.

- [ ] **Step 5: Final commit**

```bash
git add -A
git status  # verify nothing unexpected is staged
git commit -m "chore: final integration check — all files present"
```
