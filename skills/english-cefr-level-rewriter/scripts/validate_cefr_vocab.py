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
