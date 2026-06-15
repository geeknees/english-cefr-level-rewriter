# ABOUTME: Downloads and merges CEFR-J + Octanove vocabulary CSVs into cefr_vocabulary.csv
# License of source data: CC BY-SA 4.0 — https://github.com/openlanguageprofiles/olp-en-cefrj
import csv, io, os, urllib.request

SOURCES = [
    "https://raw.githubusercontent.com/openlanguageprofiles/olp-en-cefrj/master/cefrj-vocabulary-profile-1.5.csv",
    "https://raw.githubusercontent.com/openlanguageprofiles/olp-en-cefrj/master/octanove-vocabulary-profile-c1c2-1.0.csv",
]
ORDER = {"A1": 0, "A2": 1, "B1": 2, "B2": 3, "C1": 4, "C2": 5}
VALID_LEVELS = set(ORDER)
OUT = os.path.join(os.path.dirname(__file__), "..", "resources", "vocabulary", "cefr_vocabulary.csv")

def fetch(url):
    with urllib.request.urlopen(url) as r:
        return r.read().decode("utf-8")

rows = []
for url in SOURCES:
    print(f"Fetching {url} …")
    for row in csv.DictReader(io.StringIO(fetch(url))):
        word = row.get("headword", "").strip().lower()
        level = row.get("CEFR", "").strip()
        pos = row.get("pos", "").strip()
        if pos == "vern":
            pos = "verb"
        if word and level in VALID_LEVELS and pos:
            rows.append((word, level, pos))

best = {}
for word, level, pos in rows:
    key = (word, pos)
    if key not in best or ORDER[level] < ORDER[best[key][1]]:
        best[key] = (word, level, pos)

final = sorted(best.values(), key=lambda r: (ORDER[r[1]], r[0]))

with open(OUT, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["word", "cefr_level", "pos"])
    for word, level, pos in final:
        writer.writerow([word, level, pos])

print(f"Written {len(final)} entries to {os.path.normpath(OUT)}")
