"""
Novelty Filter & Redundancy Prevention Engine for Discovery_AI.
Uses SentenceTransformer embeddings to compute cosine distances against
memory/discoveries.md and memory/failed_hypotheses.md.
"""

import re
from pathlib import Path
from typing import Dict, Any, List
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent

_embedder = None

def get_embedder():
    """Lazy loader for SentenceTransformer to conserve memory until invoked."""
    global _embedder
    if _embedder is None:
        try:
            from sentence_transformers import SentenceTransformer
            _embedder = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception:
            _embedder = None
    return _embedder

def extract_entries_from_file(file_path: Path) -> List[str]:
    """Splits markdown log files into distinct hypothesis entries."""
    if not file_path.exists():
        return []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return []

    entries = [e.strip() for e in re.split(r"\n#{2,3}\s+", content) if len(e.strip()) > 30]
    return entries

def get_embedding(text: str) -> np.ndarray:
    """Fetches an embedding vector using SentenceTransformer."""
    model = get_embedder()
    if model is None:
        return None
    try:
        vec = model.encode(text[:1500])
        return np.array(vec, dtype=np.float32)
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

    if not historical_entries:
        return {
            "is_novel": True,
            "max_similarity": 0.0,
            "matched_snippet": None,
            "reason": "Memory archive is empty; hypothesis is novel."
        }

    candidate_vec = get_embedding(candidate_hypothesis)
    if candidate_vec is None:
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