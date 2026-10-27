from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer

BASE_DIR = Path("D:/Discovery_AI")
DB_DIR = str(BASE_DIR / "rag" / "db")

embed_model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path=DB_DIR)
collection = client.get_or_create_collection("discovery_memory")


def search_rag(query, top_k=3):
    query_embedding = embed_model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    output = []

    for doc, meta in zip(documents, metadatas):
        source = meta.get("source", "unknown")
        output.append(f"Source: {source}\nText: {doc}")

    return "\n\n---\n\n".join(output)


if __name__ == "__main__":
    question = input("Search RAG: ")
    print(search_rag(question))