import os
from pathlib import Path
from pypdf import PdfReader
import chromadb
from sentence_transformers import SentenceTransformer

BASE_DIR = Path("D:/Discovery_AI")
PAPERS_DIR = BASE_DIR / "vault" / "papers"
NOTES_DIR = BASE_DIR / "vault" / "notes"
DB_DIR = str(BASE_DIR / "rag" / "db")

# Load embedding model
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# Chroma DB
client = chromadb.PersistentClient(path=DB_DIR)
collection = client.get_or_create_collection("discovery_memory")


def read_pdf(path):
    text = ""
    reader = PdfReader(path)
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text


def read_txt(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def chunk_text(text, chunk_size=500):
    chunks = []
    words = text.split()

    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)

    return chunks


def index_file(path):
    print(f"Indexing: {path}")

    if path.suffix.lower() == ".pdf":
        text = read_pdf(path)
    elif path.suffix.lower() in [".txt", ".md"]:
        text = read_txt(path)
    else:
        return

    chunks = chunk_text(text)

    for i, chunk in enumerate(chunks):
        embedding = embed_model.encode(chunk).tolist()

        collection.add(
            ids=[f"{path.name}_{i}"],
            embeddings=[embedding],
            documents=[chunk],
            metadatas=[{"source": path.name}]
        )


def main():
    for folder in [PAPERS_DIR, NOTES_DIR]:
        for file in folder.rglob("*"):
            if file.is_file():
                index_file(file)

    print("RAG indexing complete.")


if __name__ == "__main__":
    main()