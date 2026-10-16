"""
Shared utilities, memory operations, SymPy validation hooks,
and model inference interfaces for Discovery_AI.
Configured for Hermes inference via OpenAI-compatible endpoint.
"""

import os
import re
import json
from pathlib import Path
from openai import OpenAI

BASE_DIR = Path(__file__).resolve().parent.parent

# Connect to local Hermes vLLM server
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="hermes-local"
)

HERMES_MODEL_ID = "NousResearch/Hermes-3-Llama-3.1-8B"

# --- Memory and File Utilities ---

def read_memory(file_path: str) -> str:
    path = Path(file_path)
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""

def load_memory(filename: str) -> str:
    return read_memory(str(BASE_DIR / "memory" / filename))

def update_memory(file_path: str, content: str):
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(content)

def save_pattern(topic: str, pattern_content: str):
    entry = f"\n### Pattern: {topic}\n{pattern_content}\n"
    update_memory(str(BASE_DIR / "memory" / "patterns.md"), entry)

def auto_memory_update(topic: str, failure_log: str):
    entry = f"\n### Rejected: {topic}\n{failure_log}\n"
    update_memory(str(BASE_DIR / "memory" / "failed_hypotheses.md"), entry)

def print_section(title: str, body: str):
    print("\n" + "=" * 50)
    print(f"[{title}]")
    print("=" * 50)
    print(body)

# --- Brain Persona Loader ---

def load_brain_prompt(agent_name: str) -> str:
    """Loads system instructions from brains/<agent>_brain.md."""
    clean_name = agent_name.lower().replace(" ", "_")
    if not clean_name.endswith("_ai"):
        clean_name += "_ai"
    
    brain_file = BASE_DIR / "brains" / f"{clean_name.replace('_ai', '')}_brain.md"
    if brain_file.exists():
        with open(brain_file, "r", encoding="utf-8") as f:
            return f.read()
    return "You are an expert theoretical physics researcher."

# --- Hermes Inference Interface ---

def ask_model(agent_name: str, prompt: str, options: dict = None) -> str:
    """Queries Hermes serving endpoint using the persona brain as system instructions."""
    system_instruction = load_brain_prompt(agent_name)
    max_tokens = 600
    if options and "num_predict" in options:
        max_tokens = options["num_predict"]

    try:
        response = client.chat.completions.create(
            model=HERMES_MODEL_ID,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[!] Inference error querying {agent_name}: {e}")
        return ""

def query_model(agent_name: str, prompt: str) -> str:
    return ask_model(agent_name, prompt)

# --- RAG Stub / Interface ---

def search_rag(query: str, top_k: int = 2) -> str:
    """Queries ChromaDB vector collection if initialized."""
    try:
        import chromadb
        client_chroma = chromadb.PersistentClient(path=str(BASE_DIR / "rag" / "db"))
        collection = client_chroma.get_collection("physics_corpus")
        results = collection.query(query_texts=[query], n_results=top_k)
        docs = results.get("documents", [[]])[0]
        return "\n---\n".join(docs) if docs else "No RAG context found."
    except Exception:
        return "RAG database uninitialized or empty."

# --- Math Extraction & SymPy Audit Hooks ---

def extract_equations_from_hypothesis(hypothesis_text: str) -> list:
    equations = []
    display_matches = re.findall(r"\$\$(.*?)\$\$", hypothesis_text, re.DOTALL)
    for m in display_matches:
        cleaned = m.strip().replace("\\", "")
        if cleaned:
            equations.append(cleaned)
    line_matches = re.findall(r"(?:ds\^2|g_\{.*?\}|T_\{.*?\}|H\s*=)\s*=\s*([^,\n\.]+)", hypothesis_text)
    for m in line_matches:
        cleaned = m.strip().replace("$", "").replace("\\", "")
        if cleaned:
            equations.append(cleaned)
    return list(set(equations))

def run_math_verification_pipeline(hypothesis_text: str) -> dict:
    from runner.math_verifier import verify_hypothesis_equations, check_asymptotic_flatness
    
    extracted_eqs = extract_equations_from_hypothesis(hypothesis_text)
    if not extracted_eqs:
        return {
            "has_equations": False,
            "summary_for_judge": "No parseable symbolic formulas found; relying on theoretical description."
        }

    verification_results = verify_hypothesis_equations(extracted_eqs)
    flatness_checks = []
    for eq in extracted_eqs:
        if "M/r" in eq or "r" in eq:
            flatness_checks.append(check_asymptotic_flatness(eq, radial_var_str="r"))

    formatted_logs = [
        f"- Eq: `{res.get('equation')}` | Valid Syntax: {res.get('valid_syntax')} | Eval: {res.get('simplified', res.get('error'))}"
        for res in verification_results
    ]
    for fc in flatness_checks:
        formatted_logs.append(f"- Asymptotic Limit: {fc.get('status')} ({fc.get('message', '')})")

    return {
        "has_equations": True,
        "results": verification_results,
        "summary_for_judge": "\n".join(formatted_logs)
    }

# --- Quantitative Verdict Evaluator ---

def evaluate_verdict(raw_judge_output: str) -> dict:
    """Parses JSON scorecard and enforces the 4-pillar cutoff."""
    cleaned = raw_judge_output.strip()
    if "```json" in cleaned:
        cleaned = cleaned.split("```json")[1].split("```")[0].strip()
    elif "```" in cleaned:
        cleaned = cleaned.split("```")[1].split("```")[0].strip()

    try:
        data = json.loads(cleaned)
    except Exception:
        return {
            "verdict": "REJECTED",
            "total_score": 0.0,
            "subscores": {},
            "summary": "Malformed or non-JSON output from Judge AI."
        }

    subscores = {
        "falsifiability": float(data.get("falsifiability_score", 0.0)),
        "math_consistency": float(data.get("math_consistency_score", 0.0)),
        "novelty": float(data.get("novelty_score", 0.0)),
        "grounding": float(data.get("grounding_score", 0.0))
    }

    # Recalculate weighted score
    recomputed_score = (
        0.35 * subscores["falsifiability"] +
        0.25 * subscores["math_consistency"] +
        0.25 * subscores["novelty"] +
        0.15 * subscores["grounding"]
    )

    is_accepted = recomputed_score >= 0.80 and all(v >= 0.60 for v in subscores.values())

    return {
        "verdict": "ACCEPTED" if is_accepted else "REJECTED",
        "total_score": round(recomputed_score, 3),
        "subscores": subscores,
        "critical_flaw": data.get("critical_flaw", "None stated"),
        "summary": data.get("verdict_summary", "")
    }