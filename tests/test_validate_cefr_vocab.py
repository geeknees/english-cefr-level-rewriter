# ABOUTME: Tests for CEFR vocabulary level validator
import csv
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "english-cefr-level-rewriter" / "scripts"))

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
    assert results == []


def test_validate_lemmatised_form_accepted(mini_csv):
    vocab = load_vocab(mini_csv)
    # "runs" → lemmatised "run" → A1, target A2 → ok
    results = validate("She runs fast.", "A2", vocab)
    words_flagged = [r["word"] for r in results]
    assert "runs" not in words_flagged
