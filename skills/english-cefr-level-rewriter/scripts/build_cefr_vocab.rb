# ABOUTME: Downloads and merges CEFR-J + Octanove vocabulary CSVs into cefr_vocabulary.csv
# License of source data: CC BY-SA 4.0 — https://github.com/openlanguageprofiles/olp-en-cefrj
require "csv"
require "net/http"
require "uri"

SOURCES = [
  "https://raw.githubusercontent.com/openlanguageprofiles/olp-en-cefrj/master/cefrj-vocabulary-profile-1.5.csv",
  "https://raw.githubusercontent.com/openlanguageprofiles/olp-en-cefrj/master/octanove-vocabulary-profile-c1c2-1.0.csv",
].freeze

ORDER = %w[A1 A2 B1 B2 C1 C2].each_with_index.to_h.freeze
VALID_LEVELS = ORDER.keys.to_set
OUT = File.expand_path("../resources/vocabulary/cefr_vocabulary.csv", __dir__)

def fetch(url)
  uri = URI.parse(url)
  Net::HTTP.get(uri)
end

rows = []
SOURCES.each do |url|
  puts "Fetching #{url} …"
  CSV.parse(fetch(url), headers: true) do |row|
    word  = row["headword"].to_s.strip.downcase
    level = row["CEFR"].to_s.strip
    pos   = row["pos"].to_s.strip
    pos   = "verb" if pos == "vern"
    next unless word != "" && VALID_LEVELS.include?(level) && pos != ""
    rows << [word, level, pos]
  end
end

best = {}
rows.each do |word, level, pos|
  key = [word, pos]
  best[key] = [word, level, pos] if !best.key?(key) || ORDER[level] < ORDER[best[key][1]]
end

final = best.values.sort_by { |word, level, _pos| [ORDER[level], word] }

CSV.open(OUT, "w") do |csv|
  csv << %w[word cefr_level pos]
  final.each { |row| csv << row }
end

puts "Written #{final.size} entries to #{OUT}"
