from pathlib import Path
import json

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from app.smart_search import search_records

app = FastAPI(
    title="SamvidhanSathi API",
    description="Constitution of India - Smart Search API",
    version="1.0.0"
)

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "records.json"


def load_records():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    if isinstance(data, dict):
        data = data.get("records", [])

    return data


class QuestionRequest(BaseModel):
    question: str


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "project": "SamvidhanSathi"
    }


@app.get("/records")
def get_records(limit: int = Query(default=10, ge=1, le=1000)):
    records = load_records()

    return {
        "total": len(records),
        "returned": min(limit, len(records)),
        "records": records[:limit]
    }


@app.get("/records/{id}")
def get_record(id: str):
    records = load_records()

    for record in records:
        if str(record.get("article_no")) == id:
            return record

    raise HTTPException(
        status_code=404,
        detail=f"Article {id} not found"
    )


@app.get("/search")
def search(q: str = Query(..., min_length=1)):
    results = search_records(q)

    return {
        "query": q,
        "total_results": len(results),
        "results": results
    }


@app.post("/questions")
def ask_question(request: QuestionRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    results = search_records(question, limit=5)

    return {
        "question": question,
        "message": (
            "Relevant Constitution records found."
            if results else
            "No relevant records found."
        ),
        "results": results
    }
