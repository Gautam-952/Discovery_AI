from shared import ask_model, print_section, load_memory, auto_memory_update, save_pattern, search_rag
patterns_memory = load_memory("patterns.md")
failed_memory = load_memory("failed_hypotheses.md")

def main():
    question = input("\nAsk Discovery AI (CREATIVE MODE): ").strip()
    rag_context = search_rag(question, top_k=2)
    print("\nRAG RESULT:")
    print(rag_context)
    print("--------------")

    global_memory = load_memory("global_memory.md")
    creative_memory = load_memory("creative_memory.md")

    scholar = ask_model("Scholar", f"""
<Question>
{question}
</Question>

<RAG_CONTEXT>
{rag_context}
</RAG_CONTEXT>

Return ONLY:

Known View: ...
Key Evidence: ...
Uncertainty: ...
""", options={"num_predict":80})

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

Global Memory:
{global_memory}

Creative Memory:
{creative_memory}

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

    judge = ask_model("Judge", f"""
<Question>
{question}
</Question>

Scholar:
{scholar}

Builder:
{builder}

Pattern:
{pattern}

Return ONLY:

Verdict: ...
Best Explanation: ...
Confidence: .../100
""")

    print_section("SCHOLAR", scholar)
    print_section("BUILDER", builder)
    print_section("PATTERN", pattern)
    save_pattern(question, pattern)
    print("Pattern memory updated.")
    print_section("FINAL JUDGE", judge)
    auto_memory_update(question, judge)


if __name__ == "__main__":
    main()