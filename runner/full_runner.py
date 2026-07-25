from shared import ask_model, print_section, load_memory, auto_memory_update, save_pattern, search_rag
patterns_memory = load_memory("patterns.md")
failed_memory = load_memory("failed_hypotheses.md")

question = input("\nAsk Discovery AI (FULL MODE): ").strip()
rag_context = search_rag(question, top_k=2)
print("\nRAG RESULT:")
print(rag_context)
print("--------------")

global_memory = load_memory("global_memory.md")
judge_memory = load_memory("judge_memory.md")

scholar = ask_model("Scholar", f"""
Question:
{question}

<RAG_CONTEXT>
{rag_context}
</RAG_CONTEXT>

STRICT OUTPUT FORMAT:
Known View: <1 line>
Key Evidence: <1 line>
Uncertainty: <1 line>

Rules:
- Maximum 3 lines.
- No paragraphs.
- No extra sections.
""", options={"num_predict":80})

breaker = ask_model("Breaker", f"""
Question:
{question}

Scholar Output:
{scholar}

STRICT OUTPUT FORMAT:
Assumption: <1 line>
Weak Point: <1 line>
Severity: Low / Medium / High / Critical

Rules:
- Maximum 3 lines.
- No paragraphs.
- No extra sections.
""")

builder = ask_model("Builder", f"""
<Question>
{question}
</Question>

<Scholar>
{scholar}
</Scholar>

<Failed Hypotheses>
{failed_memory}
</Failed Hypotheses>

Avoid repeating failed ideas.
Prefer novel but plausible hypotheses.

Return ONLY:
Hypothesis: ...
Mechanism: ...
Potential: .../100
""")

pattern = ask_model("Pattern", f"""
<Question>
{question}
</Question>

<Builder>
{builder}
</Builder>

<Previous Patterns>
{patterns_memory}
</Previous Patterns>

Find reusable hidden structures.

Return ONLY:
Pattern: ...
Hidden Structure: ...
Strength: .../100
""")

reasoner = ask_model("Reasoner", f"""
Question:
{question}

Scholar Output:
{scholar}

Breaker Output:
{breaker}

Builder Output:
{builder}

Pattern Output:
{pattern}

Follow internal rules only.

Return ONLY:

Reasoning: ...
Main Flaw: ...
Confidence: .../100
""")

judge = ask_model("Judge", f"""
Global Memory:
{global_memory}

Judge Memory:
{judge_memory}

Question:
{question}

Scholar:
{scholar}

Breaker:
{breaker}

Builder:
{builder}

Pattern:
{pattern}

Reasoner:
{reasoner}

STRICT OUTPUT FORMAT:
Verdict: <2 lines max>
Best Explanation: <1 line>
Confidence: <number>/100

Rules:
- Maximum 4 lines.
- No ranking.
- No score table.
- No extra sections.
""")

print_section("SCHOLAR", scholar)
print_section("BREAKER", breaker)
print_section("BUILDER", builder)
print_section("PATTERN", pattern)
save_pattern(question, pattern)
print("Pattern memory updated.")
print_section("REASONER", reasoner)
print_section("FINAL JUDGE", judge)
auto_memory_update(question, judge)