from shared import ask_model, print_section, load_memory, auto_memory_update, search_rag

question = input("\nAsk Discovery AI (FAST MODE): ").strip()
rag_context = search_rag(question, top_k=2)
print("\nRAG RESULT:")
print(rag_context)
print("--------------")

global_memory = load_memory("global_memory.md")
judge_memory = load_memory("judge_memory.md")

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

reasoner = ask_model("Reasoner", f"""
<Question>
{question}
</Question>

<Scholar>
{scholar}
</Scholar>

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

<Question>
{question}
</Question>

<Scholar>
{scholar}
</Scholar>

<Reasoner>
{reasoner}
</Reasoner>

Return ONLY:
Verdict: ...
Best Explanation: ...
Confidence: .../100
""")

print_section("SCHOLAR", scholar)
print_section("REASONER", reasoner)
print_section("FINAL JUDGE", judge)

auto_memory_update(question, judge)
print("\nMemory updated.")