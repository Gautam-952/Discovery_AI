"""
Novelty Filter & Redundancy Prevention Engine for Discovery_AI.
Guards against circular exploration by computing embedding cosine distances 
against memory/discoveries.md and memory/failed_hypotheses.md.
"""

import re
from pathlib import Path
from typing import Dict, Any, List
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent


def extract_entries_from_file(file_path: Path) -> List[str]:
    """Splits markdown log files into distinct hypothesis entries."""
    if not file_path.exists():
        return []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return []

    # Split on markdown H2 or H3 headers
    entries = [e.strip() for e in re.split(r"\n#{2,3}\s+", content) if len(e.strip()) > 30]
    return entries


def get_embedding(text: str) -> np.ndarray:
    """Fetches an embedding vector using the local Ollama instance."""
    try:
        import ollama
        response = ollama.embeddings(model="llama3:8b", prompt=text[:2000])
        vec = np.array(response["embedding"], dtype=np.float32)
        return vec
    except Exception as e:
        # Fallback to chromadb default embedding function if ollama call fails
        try:
            from chromadb.utils import embedding_functions
            fn = embedding_functions.DefaultEmbeddingFunction()
            emb = fn([text[:1000]])[0]
            return np.array(emb, dtype=np.float32)
        except Exception:
            return None


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Calculates cosine similarity between two 1D vectors."""
    if a is None or b is None:
        return 0.0
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def check_hypothesis_novelty(
    candidate_hypothesis: str,
    threshold: float = 0.85
) -> Dict[str, Any]:
    """
    Compares candidate hypothesis against all prior discoveries and failures.
    Returns whether it is novel or redundant.
    """
    discoveries_path = BASE_DIR / "memory" / "discoveries.md"
    failed_path = BASE_DIR / "memory" / "failed_hypotheses.md"

    historical_entries = (
        extract_entries_from_file(discoveries_path) + 
        extract_entries_from_file(failed_path)
    )

    # If memory is empty, everything is novel
    if not historical_entries:
        return {
            "is_novel": True,
            "max_similarity": 0.0,
            "matched_snippet": None,
            "reason": "Memory archive is empty; hypothesis is novel."
        }

    candidate_vec = get_embedding(candidate_hypothesis)
    if candidate_vec is None:
        # Safe bypass if embedding engine is momentarily offline
        return {
            "is_novel": True,
            "max_similarity": 0.0,
            "matched_snippet": None,
            "reason": "Embedding engine bypassed; proceed."
        }

    max_sim = 0.0
    matched_entry = None

    for entry in historical_entries:
        entry_vec = get_embedding(entry)
        sim = cosine_similarity(candidate_vec, entry_vec)
        if sim > max_sim:
            max_sim = sim
            matched_entry = entry[:250]

    is_novel = max_sim < threshold

    return {
        "is_novel": is_novel,
        "max_similarity": round(max_sim, 3),
        "threshold": threshold,
        "matched_snippet": matched_entry,
        "reason": (
            "Hypothesis is sufficiently novel."
            if is_novel
            else f"Redundancy detected: Cosine similarity {max_sim:.3f} >= threshold {threshold}."
        )
    }


if __name__ == "__main__":
    # Test execution
    sample = "Entanglement entropy scaling across traversable wormhole horizons."
    res = check_hypothesis_novelty(sample)
    print("Novelty Filter Result:", res)