import requests
from pathlib import Path
from pypdf import PdfReader

OLLAMA_URL = "http://localhost:11434/api/generate"

BASE_DIR = Path("D:/Discovery_AI")
PAPERS_DIR = BASE_DIR / "vault" / "papers"
NOTES_DIR = BASE_DIR / "vault" / "notes"

NOTES_DIR.mkdir(parents=True, exist_ok=True)


def read_pdf(path):
    text = ""
    reader = PdfReader(path)

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text


def chunk_text(text, chunk_size=8000):
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i + chunk_size])
    return chunks


def ask_model(prompt):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "hermes3:8b",
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": 700,
                "temperature": 0.2
            }
        },
        timeout=None
    )

    response.raise_for_status()
    return response.json()["response"].strip()


def summarize_chunk(chunk, idx):
    prompt = f"""
You are a research assistant.

Summarize this chunk of a physics paper.

Chunk {idx}

Text:
{chunk}

Return:
- Main ideas
- Important claims
- Equations / concepts
- Open questions
"""
    return ask_model(prompt)


def summarize_paper(pdf_path):
    text = read_pdf(pdf_path)

    if len(text) == 0:
        print(f"Could not extract text from {pdf_path.name}")
        return

    chunks = chunk_text(text)

    chunk_summaries = []

    for i, chunk in enumerate(chunks):
        print(f"Summarizing chunk {i+1}/{len(chunks)}...")
        summary = summarize_chunk(chunk, i + 1)
        chunk_summaries.append(summary)

    combined = "\n\n".join(chunk_summaries)

    final_prompt = f"""
You are Scholar AI.

Combine all chunk summaries into one final research note for Discovery AI.

Chunk Summaries:
{combined}

Return in markdown:

# {pdf_path.stem}

## Main Topic
...

## Core Claims
- ...

## Important Concepts
- ...

## Assumptions
- ...

## Open Questions
- ...

## Useful For Discovery AI
...
"""

    final_summary = ask_model(final_prompt)

    output_path = NOTES_DIR / f"{pdf_path.stem}.md"
    output_path.write_text(final_summary, encoding="utf-8")

    print(f"Saved summary: {output_path}")


def main():
    pdfs = list(PAPERS_DIR.rglob("*.pdf"))

    if not pdfs:
        print("No PDFs found.")
        return

    for pdf in pdfs:
        print(f"\nProcessing: {pdf.name}")
        summarize_paper(pdf)

    print("\nAll summaries complete.")


if __name__ == "__main__":
    main()