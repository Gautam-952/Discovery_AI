"""
Academic LaTeX Paper Generator for Discovery_AI.
Extracts confirmed discoveries and synthesizes formal LaTeX manuscripts.
"""

import sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from runner.shared import query_model, read_memory

DRAFTS_DIR = BASE_DIR / "vault" / "drafts"
DRAFTS_DIR.mkdir(parents=True, exist_ok=True)

LATEX_PROMPT_TEMPLATE = """
You are Scholar AI and Director AI drafting an academic manuscript for Discovery_AI.

Context of Discovery:
Title / Topic: {topic}
Hypothesis & Mathematical Formulation:
{hypothesis}

Judge Review & Grounding:
{review}

Task:
Generate a complete, rigorous, standalone LaTeX document (article class) detailing this discovery.
Do not output Markdown backticks or chat commentary—output ONLY valid, compileable LaTeX code.

Required LaTeX Structure:
\\documentclass[11pt,a4paper]{{article}}
\\usepackage{{amsmath,amssymb,amsfonts}}
\\usepackage{{geometry}}
\\usepackage{{hyperref}}
\\geometry{{margin=1in}}

\\title{{{topic}}}
\\author{{Discovery AI Autonomous Engine}}
\\date{{{date}}}

\\begin{{document}}
\\maketitle

\\begin{{abstract}}
...
\\end{{abstract}}

\\section{{Introduction and Theoretical Motivation}}
...

\\section{{Mathematical Model and Core Mechanism}}
... (Include explicit equations, boundary limits, and tensor relations)

\\section{{Falsifiability and Empirical Kill Conditions}}
... (Explicit observational signatures and refutation bounds)

\\section{{Adversarial Analysis and Addressed Critiques}}
... (Counter-arguments addressed during testing)

\\section{{Conclusion and Open Questions}}
...

\\begin{{thebibliography}}{{99}}
...
\\end{{thebibliography}}

\\end{{document}}
"""

def extract_latest_discovery() -> dict:
    """Reads the most recent discovery from memory/discoveries.md."""
    discoveries_path = BASE_DIR / "memory" / "discoveries.md"
    content = read_memory(str(discoveries_path))
    
    if not content or content.strip() == "None logged yet.":
        return None

    # Simple section parser based on '### ' headers
    sections = [s.strip() for s in content.split("### ") if s.strip()]
    if not sections:
        return None

    latest_section = sections[-1]
    lines = latest_section.split("\n")
    topic = lines[0].strip()
    body = "\n".join(lines[1:]).strip()

    return {
        "topic": topic,
        "content": body
    }

def clean_latex_output(raw_text: str) -> str:
    """Strips possible markdown code fence wrappers from model output."""
    cleaned = raw_text.strip()
    if cleaned.startswith("```latex"):
        cleaned = cleaned[8:]
    elif cleaned.startswith("```tex"):
        cleaned = cleaned[6:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return cleaned.strip()

def draft_manuscript(topic: str = None, hypothesis_text: str = None, review_text: str = None) -> Path:
    """Synthesizes an academic LaTeX paper and saves it to vault/drafts/."""
    if not topic or not hypothesis_text:
        latest = extract_latest_discovery()
        if not latest:
            print("[!] No discoveries found in memory/discoveries.md to draft.")
            return None
        topic = latest["topic"]
        hypothesis_text = latest["content"]
        review_text = review_text or "Confirmed by Judge AI."

    today_str = datetime.now().strftime("%B %d, %Y")
    
    prompt = LATEX_PROMPT_TEMPLATE.format(
        topic=topic,
        hypothesis=hypothesis_text,
        review=review_text,
        date=today_str
    )

    print(f"[*] Drafting formal LaTeX preprint for: '{topic}'...")
    raw_latex = query_model("scholar_ai", prompt)
    clean_latex = clean_latex_output(raw_latex)

    # Sanitize filename
    safe_title = "".join(c if c.isalnum() else "_" for c in topic)[:50].strip("_")
    output_path = DRAFTS_DIR / f"{safe_title}.tex"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(clean_latex)

    print(f"[+] Manuscript drafted successfully: {output_path}")
    return output_path

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Draft an academic LaTeX manuscript from a discovery.")
    parser.add_argument("--topic", type=str, default=None, help="Discovery topic title")
    args = parser.parse_args()

    draft_manuscript(topic=args.topic)