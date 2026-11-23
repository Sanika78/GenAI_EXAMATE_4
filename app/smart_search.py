
import json
import re
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "records.json"


def load_records():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    if isinstance(data, dict):
        data = data.get("records", [])

    return data


def search_records(query, limit=10):
    records = load_records()

    if not query.strip() or not records:
        return []

    # Give exact article-number matches priority.
    article_match = re.search(
        r"\barticle\s+(\d+[a-z]?)\b",
        query,
        re.IGNORECASE
    )

    exact_results = []

    if article_match:
        requested_article = article_match.group(1).lower()

        for record in records:
            article_no = str(record.get("article_no", "")).lower()

            if article_no == requested_article:
                result = record.copy()
                result["similarity_score"] = 1.0
                exact_results.append(result)

    # Keep TF-IDF search for normal questions.
    documents = [
        f"{record.get('article_no', '')} "
        f"{record.get('title', '')} "
        f"{record.get('part', '')} "
        f"{record.get('text', '')}"
        for record in records
    ]

    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(documents)

    query_vector = vectorizer.transform([query])
    scores = cosine_similarity(query_vector, matrix).flatten()

    ranked_indices = scores.argsort()[::-1]

    results = exact_results.copy()
    exact_ids = {
        str(record.get("article_no", "")).lower()
        for record in exact_results
    }

    for index in ranked_indices:
        if scores[index] <= 0:
            continue

        record = records[index].copy()

        if str(record.get("article_no", "")).lower() in exact_ids:
            continue

        record["similarity_score"] = round(float(scores[index]), 4)
        results.append(record)

        if len(results) >= limit:
            break

    return results[:limit]
