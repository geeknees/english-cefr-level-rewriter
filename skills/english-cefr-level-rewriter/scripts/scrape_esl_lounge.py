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
