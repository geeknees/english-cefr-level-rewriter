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
    r"\b(am|is|are|was|were|be|been|being)\s+(\w+ed|\w+en)\b", re.IGNORECASE
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
