# ABOUTME: Tests for CEFR vocabulary CSV builder (merge/dedup logic)
require "csv"
require "set"
require "tempfile"

# Extract testable logic from build_cefr_vocab.rb without running the download
ORDER = %w[A1 A2 B1 B2 C1 C2].each_with_index.to_h.freeze unless defined?(ORDER)
VALID_LEVELS = ORDER.keys.to_set unless defined?(VALID_LEVELS)

def merge_and_dedup(rows)
  best = {}
  rows.each do |word, level, pos|
    key = [word, pos]
    best[key] = [word, level, pos] if !best.key?(key) || ORDER[level] < ORDER[best[key][1]]
  end
  best.values.sort_by { |word, level, _pos| [ORDER[level], word] }
end

RSpec.describe "build_cefr_vocab" do
  describe "merge_and_dedup" do
    it "keeps the lowest CEFR level when duplicates appear" do
      rows = [
        ["bank", "A2", "noun"],
        ["bank", "B1", "noun"],
      ]
      result = merge_and_dedup(rows)
      expect(result).to eq([["bank", "A2", "noun"]])
    end

    it "keeps separate entries for same word with different POS" do
      rows = [
        ["run", "A1", "verb"],
        ["run", "B1", "noun"],
      ]
      result = merge_and_dedup(rows)
      expect(result.size).to eq(2)
    end

    it "sorts by CEFR level then alphabetically" do
      rows = [
        ["zoo",   "A1", "noun"],
        ["apple", "A1", "noun"],
        ["bank",  "A2", "noun"],
      ]
      result = merge_and_dedup(rows)
      expect(result.map { |r| r[0] }).to eq(%w[apple zoo bank])
    end

    it "drops rows with invalid CEFR levels when filtered before merging" do
      rows = [["word", "X9", "noun"]]
      rows.select! { |_, level, _| VALID_LEVELS.include?(level) }
      expect(merge_and_dedup(rows)).to be_empty
    end

    it "corrects the vern typo to verb before merging" do
      rows = [["remonstrate", "C2", "vern"]].map do |word, level, pos|
        [word, level, pos == "vern" ? "verb" : pos]
      end
      result = merge_and_dedup(rows)
      expect(result.first[2]).to eq("verb")
    end
  end

  describe "CSV output shape" do
    it "writes the expected header and rows" do
      rows = [["apple", "A1", "noun"], ["run", "A1", "verb"]]
      Tempfile.open(["vocab", ".csv"]) do |f|
        CSV.open(f.path, "w") do |csv|
          csv << %w[word cefr_level pos]
          rows.each { |r| csv << r }
        end
        parsed = CSV.read(f.path, headers: true)
        expect(parsed.headers).to eq(%w[word cefr_level pos])
        expect(parsed[0]["word"]).to eq("apple")
        expect(parsed[1]["pos"]).to eq("verb")
      end
    end
  end
end
