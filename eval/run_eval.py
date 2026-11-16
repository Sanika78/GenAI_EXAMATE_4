
import json
import chromadb

from pathlib import Path
from app.chunking import chunk_documents
from app.embed import generate_embeddings

BASE_DIR = Path(__file__).resolve().parent.parent
EVAL_FILE = BASE_DIR / "eval" / "eval_set.json"

with open(EVAL_FILE, "r", encoding="utf-8") as file:
    eval_questions = json.load(file)


def evaluate_config(chunk_size, overlap, top_k):
    print(f"\nTesting: chunk_size={chunk_size}, top_k={top_k}")

    chunks = chunk_documents(
        chunk_size=chunk_size,
        overlap=overlap
    )

    if not chunks:
        raise ValueError("No chunks found. Check data/records.json.")

    client = chromadb.Client()
    collection = client.create_collection(
        name=f"eval_{chunk_size}_{top_k}"
    )

    texts = [chunk["text"] for chunk in chunks]
    embeddings = generate_embeddings(texts)

    collection.add(
        ids=[chunk["id"] for chunk in chunks],
        documents=texts,
        embeddings=embeddings,
        metadatas=[
            {
                "article_no": str(chunk["article_no"]),
                "title": chunk["title"],
                "source": chunk["source"],
                "page": int(chunk["page"])
            }
            for chunk in chunks
        ]
    )

    correct = 0
    total = 0

    for item in eval_questions:
        expected = str(item["expected_article"])

        if expected == "UNKNOWN":
            continue

        total += 1
        query_embedding = generate_embeddings(
            [item["question"]]
        )[0]

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, collection.count())
        )

        retrieved_articles = [
            metadata["article_no"]
            for metadata in results["metadatas"][0]
        ]

        is_correct = expected in retrieved_articles

        if is_correct:
            correct += 1

        print(
            f"Q{item['id']}: "
            f"{'PASS' if is_correct else 'FAIL'} "
            f"| Expected: {expected} "
            f"| Retrieved: {retrieved_articles}"
        )

    accuracy = (correct / total * 100) if total else 0

    print(f"Accuracy: {correct}/{total} = {accuracy:.2f}%")

    return {
        "chunk_size": chunk_size,
        "overlap": overlap,
        "top_k": top_k,
        "correct": correct,
        "total": total,
        "accuracy": round(accuracy, 2)
    }


if __name__ == "__main__":
    results = []

    results.append(evaluate_config(500, 80, 3))
    results.append(evaluate_config(800, 80, 5))

    print("\n========== FINAL COMPARISON ==========")

    for result in results:
        print(result)

    winner = max(results, key=lambda item: item["accuracy"])

    print("\nWinning configuration:")
    print(winner)
