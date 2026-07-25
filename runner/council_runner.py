import requests
import time
from pathlib import Path

OLLAMA_URL = "http://localhost:11434/api/generate"

BASE_DIR = Path("D:/Discovery_AI")
MEMORY_DIR = BASE_DIR / "memory"

MODELS = {
    "Scholar": "scholar_ai",
    "Breaker": "breaker_ai",
    "Builder": "builder_ai",
    "Pattern": "pattern_ai",
    "Reasoner": "reasoner_ai",
    "Judge": "judge_ai",
}

OPTIONS = {
    "num_predict": 250,
    "temperature": 0.3,
    "top_p": 0.8,
    "repeat_penalty": 1.15,
}

def load_memory(filename):
    path = MEMORY_DIR / filename
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""

def ask_model(role, model, prompt):
    print(f"\nRunning {role}...")
    start = time.time()

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": OPTIONS,
        },
        timeout=None,
    )

    response.raise_for_status()
    text = response.json()["response"].strip()

    print(f"{role} done in {round(time.time() - start, 1)}s")
    return text

def print_section(title, text):
    print("\n" + "=" * 18 + f" {title} " + "=" * 18)
    print(text)

def main():
    question = input("\nAsk Discovery Council: ").strip()

    global_memory = load_memory("global_memory.md")
    judge_memory = load_memory("judge_memory.md")

    scholar = ask_model("Scholar", MODELS["Scholar"], f"""
Question:
{question}

Task:
Give strongest accepted knowledge.
Keep concise.
""")

    breaker = ask_model("Breaker", MODELS["Breaker"], f"""
Question:
{question}

Scholar Output:
{scholar}

Task:
Find assumptions, weak points, and boundary conditions.
Keep concise.
""")

    builder = ask_model("Builder", MODELS["Builder"], f"""
Question:
{question}

Scholar Output:
{scholar}

Breaker Output:
{breaker}

Task:
Create alternative hypotheses or new explanations.
Keep concise.
""")

    pattern = ask_model("Pattern", MODELS["Pattern"], f"""
Question:
{question}

Scholar Output:
{scholar}

Breaker Output:
{breaker}

Builder Output:
{builder}

Task:
Find hidden structures, patterns, analogies, or repeated principles.
Keep concise.
""")

    reasoner = ask_model("Reasoner", MODELS["Reasoner"], f"""
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

Task:
Verify reasoning quality, hidden assumptions, evidence strength, and confidence reliability.
Keep concise.
""")

    judge = ask_model("Judge", MODELS["Judge"], f"""
Long-Term Memory:

GLOBAL MEMORY:
{global_memory}

JUDGE MEMORY:
{judge_memory}

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

Reasoner Output:
{reasoner}

Task:
Use memory plus all agent outputs.
Give final verdict and final answer.
Be balanced, concise, and decisive.
""")

    print_section("SCHOLAR", scholar)
    print_section("BREAKER", breaker)
    print_section("BUILDER", builder)
    print_section("PATTERN", pattern)
    print_section("REASONER", reasoner)
    print_section("FINAL JUDGE", judge)

if __name__ == "__main__":
    main()