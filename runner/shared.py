import re
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

DEFAULT_OPTIONS = {
    "num_predict": 120,
    "temperature": 0.25,
    "top_p": 0.75,
    "repeat_penalty": 1.2,
}

def load_memory(filename):
    path = MEMORY_DIR / filename
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""

def save_memory(filename, content, append=True):
    path = MEMORY_DIR / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if append else "w"
    with open(path, mode, encoding="utf-8") as f:
        f.write(content.strip())
        f.write("\n\n")

def ask_model(role, prompt, options=None):
    model = MODELS[role]
    final_options = DEFAULT_OPTIONS.copy()
    if options:
        final_options.update(options)

    print(f"\nRunning {role}...")
    start = time.time()

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": final_options,
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

def update_session_memory(question, final_verdict):
    content = f"""
Current Question:
{question}

Latest Verdict:
{final_verdict}

------------------------
"""
    save_memory("session_memory.md", content, append=False)

def save_discovery(question, verdict, confidence):
    content = f"""
Question:
{question}

Discovery:
{verdict}

Confidence:
{confidence}/100

------------------------
"""
    save_memory("discoveries.md", content, append=True)

def save_failed_hypothesis(question, reason):
    content = f"""
Question:
{question}

Failure:
{reason}

------------------------
"""
    save_memory("failed_hypotheses.md", content, append=True)

def extract_confidence(text):
    match = re.search(r"(\d+)\s*/\s*100", text)
    if match:
        return int(match.group(1))
    return None

def auto_memory_update(question, judge_output):
    confidence = extract_confidence(judge_output)

    update_session_memory(question, judge_output)

    if confidence is None:
        return

    text = judge_output.lower()

    novelty_words = [
        "may", "possible", "hypothesis", "emerge",
        "pattern", "lead", "could", "unexplained"
    ]

    # Failed / weak ideas
    if confidence <= 40:
        save_failed_hypothesis(question, judge_output)

    # Promising discovery lead
    elif confidence >= 70 and any(word in text for word in novelty_words):
        save_discovery(question, judge_output, confidence)

    # Normal strong answer: only session memory, not discovery
    else:
        return
def save_pattern(question, pattern_output):
    content = f"""
Question:
{question}

Pattern:
{pattern_output}

------------------------
"""
    save_memory("patterns.md", content, append=True)

def search_rag(query, top_k=3):
    try:
        import chromadb
        from sentence_transformers import SentenceTransformer

        db_dir = str(BASE_DIR / "rag" / "db")
        embed_model = SentenceTransformer("all-MiniLM-L6-v2")

        client = chromadb.PersistentClient(path=db_dir)
        collection = client.get_or_create_collection("discovery_memory")

        query_embedding = embed_model.encode(query).tolist()

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]

        chunks = []
        for doc, meta in zip(documents, metadatas):
            source = meta.get("source", "unknown")
            chunks.append(f"Source: {source}\n{doc}")

        return "\n\n---\n\n".join(chunks)

    except Exception as e:
        return f"RAG unavailable: {e}"