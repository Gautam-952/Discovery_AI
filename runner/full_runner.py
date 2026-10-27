import sys
import argparse
from pathlib import Path

# Ensure paths resolve properly
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from runner.shared import (
    ask_model,
    print_section,
    load_memory,
    auto_memory_update,
    save_pattern,
    search_rag,
    evaluate_verdict,
    run_math_verification_pipeline
)
from runner.paper_drafter import draft_manuscript

# --- CLI / Topic Parameter Handling ---
parser = argparse.ArgumentParser(description="Full Runner Pipeline for Discovery_AI")
parser.add_argument("--topic", type=str, default=None, help="Research topic or hypothesis to evaluate")
args = parser.parse_args()

if args.topic:
    question = args.topic.strip()
else:
    question = input("\nAsk Discovery AI (FULL MODE): ").strip()

patterns_memory = load_memory("patterns.md")
failed_memory = load_memory("failed_hypotheses.md")
global_memory = load_memory("global_memory.md")
judge_memory = load_memory("judge_memory.md")

rag_context = search_rag(question, top_k=2)
print("\nRAG RESULT:")
print(rag_context)
print("--------------")

# --- Step 1: Scholar AI ---
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
""", options={"num_predict": 80})

# --- Step 2: Breaker AI ---
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

# --- Step 3: Builder AI ---
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

# --- Step 4: Symbolic Math Audit (SymPy) ---
print("[*] Running symbolic math verification on Builder hypothesis...")
math_audit = run_math_verification_pipeline(builder)

# --- Step 5: Pattern AI ---
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

# --- Step 6: Reasoner AI ---
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

# --- Step 7: Judge AI (Quantitative Evaluation) ---
judge_prompt = f"""
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

=== SYMBOLIC MATH ENGINE AUDIT (SymPy) ===
{math_audit.get('summary_for_judge', 'No equations audited.')}

Score the hypothesis across all 4 pillars and return strictly valid JSON matching your rubric:
"""

judge = ask_model("Judge", judge_prompt)

# --- Display Terminal Logs ---
print_section("SCHOLAR", scholar)
print_section("BREAKER", breaker)
print_section("BUILDER", builder)
print_section("MATH AUDIT", math_audit.get("summary_for_judge", "N/A"))
print_section("PATTERN", pattern)
save_pattern(question, pattern)
print("Pattern memory updated.")
print_section("REASONER", reasoner)
print_section("FINAL JUDGE", judge)

# --- Step 8: Parse Verdict & Trigger Actions ---
verdict_result = evaluate_verdict(judge)
print("\n" + "=" * 50)
print(f"[*] Quantitative Scorecard:")
print(f"    - Verdict: {verdict_result['verdict']}")
print(f"    - Total Score: {verdict_result.get('total_score', 0.0)}")
print(f"    - Subscores: {verdict_result.get('subscores', {})}")
print(f"    - Critical Flaw / Status: {verdict_result.get('critical_flaw', 'None')}")
print("=" * 50 + "\n")

if verdict_result["verdict"] == "ACCEPTED":
    print("[+] Discovery passed all hurdles! Logging to discoveries and drafting LaTeX preprint...")
    
    # 1. Update discoveries memory
    discovery_entry = (
        f"\n### {question}\n"
        f"**Hypothesis:**\n{builder}\n\n"
        f"**Scorecard:** {verdict_result['total_score']} | Subscores: {verdict_result.get('subscores', {})}\n"
        f"**Summary:** {verdict_result.get('summary', '')}\n"
    )
    discoveries_path = BASE_DIR / "memory" / "discoveries.md"
    with open(discoveries_path, "a", encoding="utf-8") as f:
        f.write(discovery_entry)

    # 2. Compile LaTeX manuscript
    draft_manuscript(
        topic=question,
        hypothesis_text=builder,
        review_text=f"Total Score: {verdict_result['total_score']}\n{verdict_result.get('summary', '')}"
    )
else:
    # Auto-log rejected ideas to avoid cyclic exploration
    auto_memory_update(question, judge)