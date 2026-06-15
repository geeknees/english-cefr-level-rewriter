# ABOUTME: Tests for CEFR vocabulary level validator
require "set"
require "tempfile"
require_relative "../skills/english-cefr-level-rewriter/scripts/validate_cefr_vocab"

RSpec.describe "validate_cefr_vocab" do
  let(:mini_csv) do
    path = Tempfile.new(["vocab", ".csv"])
    path.write("word,cefr_level,pos\napple,A1,noun\nbank,A2,noun\nacquire,C1,verb\nrun,A1,verb\n")
    path.close
    path.path
  end

  after { File.unlink(mini_csv) if File.exist?(mini_csv) }

  describe "load_vocab" do
    it "loads words with their CEFR levels" do
      vocab = load_vocab(mini_csv)
      expect(vocab["apple"]).to eq("A1")
      expect(vocab["bank"]).to eq("A2")
      expect(vocab["acquire"]).to eq("C1")
    end
  end

  describe "above_level?" do
    it "returns true when word level is higher than target" do
      expect(above_level?("B2", "A1")).to be true
    end

    it "returns false when word level is lower than target" do
      expect(above_level?("A1", "B2")).to be false
    end

    it "returns false when levels are equal" do
      expect(above_level?("A1", "A1")).to be false
    end
  end

  describe "tokenise" do
    it "strips punctuation" do
      expect(tokenise("Hello, world!")).to eq(%w[hello world])
    end

    it "lowercases all tokens" do
      expect(tokenise("The Cat")).to eq(%w[the cat])
    end
  end

  describe "lemmatise" do
    it "strips -ed suffix" do
      expect(lemmatise("walked")).to eq("walk")
    end

    it "strips -s suffix" do
      expect(lemmatise("cats")).to eq("cat")
    end

    it "strips -ing suffix" do
      expect(lemmatise("walking")).to eq("walk")
    end

    it "leaves short words unchanged" do
      expect(lemmatise("is")).to eq("is")
    end
  end

  describe "validate" do
    let(:vocab) { load_vocab(mini_csv) }

    it "does not flag words at or below target level" do
      results = validate("I eat an apple.", "A2", vocab)
      expect(results.map { |r| r[:word] }).not_to include("apple")
    end

    it "flags words above target level as above_level" do
      results = validate("I want to acquire skills.", "A1", vocab)
      statuses = results.each_with_object({}) { |r, h| h[r[:word]] = r[:status] }
      expect(statuses["acquire"]).to eq("above_level")
    end

    it "flags unknown words" do
      results = validate("The scientist discovered a new element.", "B1", vocab)
      statuses = results.each_with_object({}) { |r, h| h[r[:word]] = r[:status] }
      expect(statuses["scientist"]).to eq("unknown")
    end

    it "deduplicates repeated tokens" do
      results = validate("apple apple apple", "B1", vocab)
      expect(results).to be_empty
    end

    it "accepts lemmatised forms within level" do
      results = validate("She runs fast.", "A2", vocab)
      expect(results.map { |r| r[:word] }).not_to include("runs")
    end
  end
end
