# ABOUTME: Tests for CEFR grammar/readability validator
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "english-cefr-level-rewriter" / "scripts"))

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
