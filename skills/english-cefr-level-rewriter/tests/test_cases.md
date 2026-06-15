# Manual Test Cases

12 cases, 2 per CEFR target level. Each case specifies source text, target level, mode, expected rewritten output, and key validation checks.

---

## TC-01 | Target: A1 | Mode: strict

**Source:** "The government has implemented new legislation to reduce carbon emissions."

**Expected rewrite:** "The government made a new rule. This rule helps the air stay clean."

**Key checks:**
- No words above A1 (government, rule, air, clean all A1)
- No passive voice
- Max 10 words per sentence
- "legislation" removed and concept explained
- "carbon emissions" → "the air stay clean"

---

## TC-02 | Target: A1 | Mode: balanced

**Source:** "She acquired several professional qualifications during her studies."

**Expected rewrite:** "She got many certificates (official documents) during her studies."

**Key checks:**
- "acquired" → "got" (A1 verb)
- "professional qualifications" → "certificates" with gloss
- No passive; no subordinate clauses
- Proper nouns (none here): N/A

---

## TC-03 | Target: A2 | Mode: strict

**Source:** "The renovation of the apartment was completed ahead of schedule due to efficient project management."

**Expected rewrite:** "They finished fixing the apartment early. Good planning helped them do this."

**Key checks:**
- Passive removed ("was completed" → active)
- "renovation" → "fixing"
- "efficient project management" → "Good planning"
- Each sentence ≤ 15 words

---

## TC-04 | Target: A2 | Mode: balanced

**Source:** "Despite the adverse weather conditions, the expedition reached its destination."

**Expected rewrite:** "The weather was very bad. But the group still arrived at the place they wanted to go."

**Key checks:**
- "adverse" → "very bad" (A2 phrasing)
- "expedition" → "group" (A2 noun)
- "destination" → "the place they wanted to go" (A2 explanation)
- "Despite" → "But" (A2 discourse marker)

---

## TC-05 | Target: B1 | Mode: balanced

**Source:** "The CEO announced that the company would be restructuring its operations to enhance profitability."

**Expected rewrite:** "The CEO said that the company would change how it works to make more money."

**Key checks:**
- "restructuring" → "change how it works"
- "enhance profitability" → "make more money"
- CEO kept as proper noun/abbreviation
- One subordinate clause ("that…") — within B1 limit

---

## TC-06 | Target: B1 | Mode: learning

**Source:** "Air pollution is exacerbated by industrial emissions from fossil fuel combustion."

**Expected rewrite:** "Air pollution is made worse (exacerbated) by pollution from factories. These factories burn fossil fuels (coal, oil, gas)."

**Key checks:**
- "exacerbated" kept with gloss in parentheses (learning mode)
- "industrial emissions" → "pollution from factories"
- "fossil fuels" kept with examples
- Passive ("is made worse") permitted at B1

---

## TC-07 | Target: B2 | Mode: balanced

**Source:** "The study conclusively demonstrates a causal relationship between sleep deprivation and impaired decision-making."

**Expected rewrite:** "The study clearly shows that lack of sleep causes people to make worse decisions."

**Key checks:**
- "conclusively" → "clearly" (B2 adverb)
- "demonstrates a causal relationship between" → "shows that … causes" (clearer phrasing)
- "sleep deprivation" → "lack of sleep"
- "impaired decision-making" → "make worse decisions"

---

## TC-08 | Target: B2 | Mode: strict

**Source:** "Notwithstanding the aforementioned limitations, the methodology remains robust and replicable."

**Expected rewrite:** "Although there are some limitations, the method is still strong and can be repeated."

**Key checks:**
- "Notwithstanding" → "Although"
- "aforementioned" → "some" (reference clarified in context)
- "methodology" → "method"
- "robust" → "strong"; "replicable" → "can be repeated"
- Sentence ≤ 25 words

---

## TC-09 | Target: C1 | Mode: balanced

**Source:** "The bill was unanimously rejected by the legislature after protracted negotiations failed to yield a workable compromise."

**Expected rewrite:** "The legislature unanimously rejected the bill after lengthy negotiations failed to produce a workable compromise."

**Key checks:**
- "protracted" → "lengthy" (C1-appropriate synonym)
- Passive inverted to active for clarity while remaining within C1 passive allowance
- "yield" → "produce" (clearer at C1)
- Sentence within C1 word-count limit

---

## TC-10 | Target: C1 | Mode: learning

**Source:** "The policy has inadvertently exacerbated socioeconomic disparities."

**Expected rewrite:** "The policy has inadvertently (without meaning to) exacerbated (made worse) socioeconomic (relating to income and society) disparities (differences)."

**Key checks:**
- All technical terms retained with glosses (learning mode)
- No structural changes needed — sentence is already C1-appropriate

---

## TC-11 | Target: C2 | Mode: balanced

**Source:** "He told me that you told him that she had said that the meeting was cancelled."

**Expected rewrite:** (Preserve as-is — already C2 level structure)

**Key checks:**
- Three-level embedding detected
- C2 has no clause-depth limit — no rewrite needed
- with_validation output shows "no violations"

---

## TC-12 | Target: C2 | Mode: strict | Proper noun test

**Source:** "Apple's CEO Tim Cook announced that the company had acquired a UK-based AI startup called DeepMind for an undisclosed sum."

**Expected rewrite:** "Apple's CEO Tim Cook announced that the company had bought a UK-based AI startup called DeepMind for an unknown amount of money."

**Key checks:**
- "acquired" → "bought" in strict mode
- "undisclosed" → "unknown"
- Proper nouns preserved: Apple, Tim Cook, DeepMind, UK
- No factual changes
