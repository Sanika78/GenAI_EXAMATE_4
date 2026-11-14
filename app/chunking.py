
import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "records.json"


def load_documents():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    if isinstance(data, dict):
        data = data.get("records", [])

    return data


def chunk_documents(chunk_size=500, overlap=80):
    documents = load_documents()
    chunks = []

    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("Use chunk_size > overlap >= 0")

    for index, doc in enumerate(documents):
        text = re.sub(r"\s+", " ", doc.get("text", "")).strip()

        if not text:
            continue

        title = doc.get("title") or "Untitled"
        source = doc.get("source") or "Constitution of India"
        page = doc.get("source_page", doc.get("page", "Unknown"))
        article_no = doc.get("article_no", "Unknown")

        start = 0
        chunk_number = 0

        while start < len(text):
            end = min(start + chunk_size, len(text))

            # Try to end at a sentence boundary
            if end < len(text):
                boundary = text.rfind(". ", start, end)
                if boundary > start + chunk_size // 2:
                    end = boundary + 1

            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append({
                    "id": f"record_{index}_chunk_{chunk_number}",
                    "text": chunk_text,
                    "title": str(title),
                    "source": str(source),
                    "page": str(page),
                    "article_no": str(article_no)
                })

            if end >= len(text):
                break

            chunk_number += 1
            start = max(start + 1, end - overlap)

    return chunks


if __name__ == "__main__":
    result = chunk_documents()

    print("Total chunks:", len(result))
    print("Sample chunks:")

    for chunk in result[:5]:
        print(chunk)
