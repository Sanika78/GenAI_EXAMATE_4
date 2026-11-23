import re
from pathlib import Path
import chromadb

from app.chunking import chunk_documents
from app.embed import generate_embeddings

BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = BASE_DIR / "chroma_db"

client = chromadb.PersistentClient(path=str(CHROMA_DIR))


def get_collection():
    """Always retrieve the current collection by name."""
    return client.get_or_create_collection(name="samvidhansathi")


def index_documents():
    collection = get_collection()
    chunks = chunk_documents()

    if not chunks:
        return 0

    texts = [chunk["text"] for chunk in chunks]
    embeddings = generate_embeddings(texts)

    collection.upsert(
        ids=[chunk["id"] for chunk in chunks],
        documents=texts,
        embeddings=embeddings,
        metadatas=[
            {
                "title": chunk["title"],
                "source": chunk["source"],
                "page": chunk["page"],
                "article_no": chunk["article_no"]
            }
            for chunk in chunks
        ]
    )

    return len(chunks)




def semantic_search(query, limit=5):
    if not query.strip():
        return []

    # 1. Handle exact article-number questions directly from records.json.
    article_match = re.search(
        r"\barticle\s+(\d+[a-z]?)\b",
        query,
        re.IGNORECASE
    )

    if article_match:
        requested_article = article_match.group(1).lower()

        source_chunks = chunk_documents()

        exact_matches = [
            chunk for chunk in source_chunks
            if str(chunk.get("article_no", "")).lower() == requested_article
        ]

        if exact_matches:
            return [
                {
                    "id": chunk["id"],
                    "text": chunk["text"],
                    "title": chunk["title"],
                    "source": chunk["source"],
                    "page": chunk["page"],
                    "article_no": chunk["article_no"],
                    "distance": 0.0
                }
                for chunk in exact_matches[:limit]
            ]

    # 2. Use ChromaDB for normal semantic questions.
    collection = get_collection()

    if collection.count() == 0:
        return []

    query_embedding = generate_embeddings([query])[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(limit, collection.count())
    )

    matches = []

    if not results["ids"] or not results["ids"][0]:
        return matches

    for i, chunk_id in enumerate(results["ids"][0]):
        metadata = results["metadatas"][0][i]

        matches.append({
            "id": chunk_id,
            "text": results["documents"][0][i],
            "title": metadata.get("title"),
            "source": metadata.get("source"),
            "page": metadata.get("page"),
            "article_no": metadata.get("article_no"),
            "distance": results["distances"][0][i]
        })

    return matches


if __name__ == "__main__":
    total = index_documents()

    print("Indexed chunks:", total)
    print("Stored chunks:", get_collection().count())

    results = semantic_search(
        "What is the right to life under the Constitution?"
    )

    for result in results:
        print(result)
