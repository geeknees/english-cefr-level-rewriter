# ABOUTME: Validates English text vocabulary against a CEFR level using cefr_vocabulary.csv
require "csv"
require "optparse"

CEFR_ORDER = %w[A1 A2 B1 B2 C1 C2].freeze unless defined?(CEFR_ORDER)
DEFAULT_CSV = File.expand_path("../resources/vocabulary/cefr_vocabulary.csv", __dir__)

def load_vocab(csv_path)
  vocab = {}
  CSV.foreach(csv_path, headers: true) do |row|
    word = row["word"].to_s.downcase
    vocab[word] ||= row["cefr_level"].to_s.upcase
  end
  vocab
end

def above_level?(word_level, target_level)
  return false unless CEFR_ORDER.include?(word_level) && CEFR_ORDER.include?(target_level)
  CEFR_ORDER.index(word_level) > CEFR_ORDER.index(target_level)
end

def tokenise(text)
  text.scan(/[a-zA-Z']+/).map(&:downcase)
end

def lemmatise(word)
  %w[ing ed s].each do |suffix|
    return word[0..-(suffix.length + 1)] if word.end_with?(suffix) && word.length > suffix.length + 2
  end
  word
end

def validate(text, target_level, vocab)
  target  = target_level.upcase
  results = []
  seen    = Set.new
  tokenise(text).each do |token|
    next if seen.include?(token)
    seen.add(token)
    found_level = vocab[token] || vocab[lemmatise(token)]
    status = if found_level.nil?
      "unknown"
    elsif above_level?(found_level, target)
      "above_level"
    else
      next
    end
    results << { word: token, found_level: found_level || "—", target_level: target, status: status }
  end
  results
end

def print_table(results)
  if results.empty?
    puts "No violations found."
    return
  end
  puts format("%-20s %-12s %-12s %s", "word", "found_level", "target_level", "status")
  puts "-" * 56
  results.each do |r|
    puts format("%-20s %-12s %-12s %s", r[:word], r[:found_level], r[:target_level], r[:status])
  end
end

if __FILE__ == $0
  require "set"
  options = { vocab: DEFAULT_CSV }
  OptionParser.new do |opts|
    opts.banner = "Usage: validate_cefr_vocab.rb --text TEXT --level LEVEL [--vocab PATH]"
    opts.on("--text TEXT",  "Text to validate")                   { |v| options[:text]  = v }
    opts.on("--level LEVEL", CEFR_ORDER, "Target CEFR level")    { |v| options[:level] = v }
    opts.on("--vocab PATH", "Path to vocabulary CSV")             { |v| options[:vocab] = v }
  end.parse!

  abort("--text is required")  unless options[:text]
  abort("--level is required") unless options[:level]

  vocab   = load_vocab(options[:vocab])
  results = validate(options[:text], options[:level], vocab)
  print_table(results)
  exit(results.empty? ? 0 : 1)
end
