# ABOUTME: Validates English text grammar complexity against a CEFR level using heuristic rules
require "optparse"

CEFR_ORDER = %w[A1 A2 B1 B2 C1 C2].freeze unless defined?(CEFR_ORDER)

PROFILES = {
  "A1" => {
    max_words_per_sentence: 10,
    max_clause_depth:       0,
    passive_allowed:        false,
    allowed_modals:         %w[can can't cannot].to_set,
  },
  "A2" => {
    max_words_per_sentence: 15,
    max_clause_depth:       1,
    passive_allowed:        false,
    allowed_modals:         %w[can can't cannot could will won't would].to_set,
  },
  "B1" => {
    max_words_per_sentence: 20,
    max_clause_depth:       1,
    passive_allowed:        true,
    allowed_modals:         %w[can can't cannot could will won't would must should may might shall].to_set,
  },
  "B2" => {
    max_words_per_sentence: 25,
    max_clause_depth:       2,
    passive_allowed:        true,
    allowed_modals:         %w[can can't cannot could will won't would must should may might shall need ought].to_set,
  },
  "C1" => { max_words_per_sentence: 35,  max_clause_depth: 3,   passive_allowed: true, allowed_modals: nil },
  "C2" => { max_words_per_sentence: 999, max_clause_depth: 999, passive_allowed: true, allowed_modals: nil },
}.freeze

SUBORDINATORS = /\b(that|which|who|whom|whose|when|where|while|because|although|since|unless|until|if|though|so that|in order that)\b/i
PASSIVE       = /\b(am|is|are|was|were|be|been|being)\s+(\w+ed|\w+en)\b/i
ALL_MODALS    = %w[can could will would must should may might shall need ought can't cannot won't].freeze

def split_sentences(text)
  text.strip.split(/(?<=[.!?])\s+/).map(&:strip).reject(&:empty?)
end

def count_words(sentence)
  sentence.scan(/\b\w+\b/).size
end

def count_subordinate_clauses(sentence)
  sentence.scan(SUBORDINATORS).size
end

def has_passive?(sentence)
  PASSIVE.match?(sentence)
end

def check_modals(sentence, allowed)
  return [] if allowed.nil?
  pattern = /\b(#{ALL_MODALS.map { |m| Regexp.escape(m) }.join("|")})\b/i
  sentence.scan(pattern).flatten.reject { |m| allowed.include?(m.downcase) }
end

def validate_readability(text, target_level)
  profile    = PROFILES[target_level.upcase]
  violations = []
  split_sentences(text).each do |sentence|
    snippet = sentence[0, 80]
    wc = count_words(sentence)
    if wc > profile[:max_words_per_sentence]
      violations << { sentence: snippet, rule: "sentence_length",
                      detail: "#{wc} words (max #{profile[:max_words_per_sentence]})" }
    end
    depth = count_subordinate_clauses(sentence)
    if depth > profile[:max_clause_depth]
      violations << { sentence: snippet, rule: "clause_depth",
                      detail: "#{depth} subordinate clause(s) (max #{profile[:max_clause_depth]})" }
    end
    if !profile[:passive_allowed] && has_passive?(sentence)
      violations << { sentence: snippet, rule: "passive_voice",
                      detail: "passive construction not allowed at this level" }
    end
    check_modals(sentence, profile[:allowed_modals]).each do |modal|
      violations << { sentence: snippet, rule: "modal_verb",
                      detail: "'#{modal}' not in allowed modal inventory for #{target_level.upcase}" }
    end
  end
  violations
end

def print_violations(violations)
  if violations.empty?
    puts "No violations found."
    return
  end
  violations.each do |v|
    puts "[#{v[:rule]}] #{v[:detail]}"
    puts "  → #{v[:sentence]}"
  end
end

if __FILE__ == $0
  options = {}
  OptionParser.new do |opts|
    opts.banner = "Usage: validate_cefr_readability.rb --text TEXT --level LEVEL"
    opts.on("--text TEXT",  "Text to validate")                { |v| options[:text]  = v }
    opts.on("--level LEVEL", CEFR_ORDER, "Target CEFR level") { |v| options[:level] = v }
  end.parse!

  abort("--text is required")  unless options[:text]
  abort("--level is required") unless options[:level]

  violations = validate_readability(options[:text], options[:level])
  print_violations(violations)
  exit(violations.empty? ? 0 : 1)
end
