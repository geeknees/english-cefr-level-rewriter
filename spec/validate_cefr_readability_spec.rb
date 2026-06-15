# ABOUTME: Tests for CEFR grammar/readability validator
require_relative "../skills/english-cefr-level-rewriter/scripts/validate_cefr_readability"

RSpec.describe "validate_cefr_readability" do
  describe "split_sentences" do
    it "splits on sentence-ending punctuation" do
      expect(split_sentences("Hello world. How are you?").size).to eq(2)
    end

    it "returns a single sentence as an array of one" do
      expect(split_sentences("One sentence.")).to eq(["One sentence."])
    end
  end

  describe "count_words" do
    it "counts words correctly" do
      expect(count_words("The cat sat on the mat.")).to eq(6)
    end
  end

  describe "count_subordinate_clauses" do
    it "detects 'that'" do
      expect(count_subordinate_clauses("I think that you are right.")).to eq(1)
    end

    it "returns 0 for a simple sentence" do
      expect(count_subordinate_clauses("She runs fast.")).to eq(0)
    end

    it "counts multiple subordinators" do
      expect(count_subordinate_clauses("I know that she said that he left.")).to eq(2)
    end
  end

  describe "has_passive?" do
    it "detects past passive" do
      expect(has_passive?("The book was written by her.")).to be true
    end

    it "returns false for active voice" do
      expect(has_passive?("She wrote the book.")).to be false
    end

    it "detects present passive" do
      expect(has_passive?("The report is reviewed every week.")).to be true
    end
  end

  describe "PROFILES" do
    it "allows 'can' at A1" do
      expect(PROFILES["A1"][:allowed_modals]).to include("can")
    end

    it "does not allow 'must' at A1" do
      expect(PROFILES["A1"][:allowed_modals]).not_to include("must")
    end

    it "allows 'must' at B1" do
      expect(PROFILES["B1"][:allowed_modals]).to include("must")
    end

    it "has no modal restriction at C1" do
      expect(PROFILES["C1"][:allowed_modals]).to be_nil
    end
  end

  describe "check_modals" do
    it "returns empty when modal is allowed" do
      expect(check_modals("You can do it.", PROFILES["A1"][:allowed_modals])).to be_empty
    end

    it "returns disallowed modal" do
      result = check_modals("You must do it.", PROFILES["A1"][:allowed_modals])
      expect(result).to include("must")
    end
  end

  describe "validate_readability" do
    it "flags sentences exceeding word count limit at A1" do
      text = "This is a really very long sentence that goes well beyond the A1 word count limit."
      rules = validate_readability(text, "A1").map { |v| v[:rule] }
      expect(rules).to include("sentence_length")
    end

    it "flags passive voice at A1" do
      rules = validate_readability("The cake was eaten by the boy.", "A1").map { |v| v[:rule] }
      expect(rules).to include("passive_voice")
    end

    it "allows passive voice at B1" do
      rules = validate_readability("The cake was eaten by the boy.", "B1").map { |v| v[:rule] }
      expect(rules).not_to include("passive_voice")
    end

    it "flags excessive subordinate clauses at A1" do
      rules = validate_readability("I think that she said that he left.", "A1").map { |v| v[:rule] }
      expect(rules).to include("clause_depth")
    end

    it "flags disallowed modal at A1" do
      rules = validate_readability("You must leave now.", "A1").map { |v| v[:rule] }
      expect(rules).to include("modal_verb")
    end

    it "passes a clean A1 sentence" do
      expect(validate_readability("I can swim. She is here.", "A1")).to be_empty
    end
  end
end
