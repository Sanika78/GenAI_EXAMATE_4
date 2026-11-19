from pathlib import Path
import json
from app.vectorstore import semantic_search
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from app.llm import ask_llm
from app.smart_search import search_records
from app.rag import ask_with_rag
from app.graph import run_graph


# -------------------------------
# FastAPI Application
# -------------------------------

app = FastAPI(
    title="SamvidhanSathi API",
    description="Constitution of India - Smart Search and AI Assistant API",
    version="1.0.0"
)


# -------------------------------
# Request Models
# -------------------------------

class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1)


class ChatRequest(BaseModel):
    question: str
    prompt_version: int = 1

class AskRequest(BaseModel):
    question: str
    top_k: int = 4


class AgentRequest(BaseModel):
    question: str = ""
    thread_id: str = Field(..., min_length=1)
    approved: bool | None = None

    
# -------------------------------
# Data File Path
# -------------------------------

DATA_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "records.json"
)


# -------------------------------
# Load Constitution Records
# -------------------------------

def load_records():

    if not DATA_FILE.exists():
        raise HTTPException(
            status_code=500,
            detail="Constitution records file not found."
        )

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, dict):
            data = data.get("records", [])

        return data

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Invalid JSON format in records.json"
        )


# -------------------------------
# Health Check API
# -------------------------------

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "project": "SamvidhanSathi"
    }


# -------------------------------
# Get All Records
# -------------------------------

@app.get("/records")
def get_records(
    limit: int = Query(default=10, ge=1, le=1000)
):

    records = load_records()

    return {
        "total": len(records),
        "returned": min(limit, len(records)),
        "records": records[:limit]
    }


# -------------------------------
# Get Record by Article Number
# -------------------------------

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


# -------------------------------
# Smart Search API
# -------------------------------

@app.get("/search")
def search(
    q: str = Query(..., min_length=1)
):

    if not q.strip():
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty"
        )

    results = search_records(q)

    return {
        "query": q,
        "total_results": len(results),
        "results": results
    }


# -------------------------------
# Constitution Question API
# -------------------------------

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

@app.get("/search/semantic")
def semantic_search_api(q: str = Query(..., min_length=1)):
    question = q.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty"
        )

    try:
        results = semantic_search(question, limit=5)

        return {
            "query": question,
            "total_results": len(results),
            "results": results
        }

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Semantic search is currently unavailable."
        )
# -------------------------------
# AI Chat API with Prompt Versioning
# -------------------------------

@app.post("/chat")
def chat(request: ChatRequest):

    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    if request.prompt_version not in [1, 2]:
        raise HTTPException(
            status_code=400,
            detail="prompt_version must be 1 or 2"
        )

    try:
        result = ask_llm(
            request.question,
            request.prompt_version
        )
        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        print("LLM ERROR:", repr(e))
        raise HTTPException(
            status_code=503,
            detail="LLM provider failed. Check the server terminal."
        )

@app.post("/ask")
def ask_endpoint(request: AskRequest):

    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    try:
        return ask_with_rag(
            request.question,
            top_k=request.top_k
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"RAG error: {str(e)}"
        )



    # -------------------------------
# Agent API
# -------------------------------

@app.post("/agent")
def agent_endpoint(request: AgentRequest):

    try:
        result = run_graph(
            question=request.question,
            thread_id=request.thread_id,
            approved=request.approved
        )

        if "__interrupt__" in result:
            return {
                "status": "approval_required",
                "thread_id": request.thread_id,
                "approval_request": result["__interrupt__"][0].value
            }

        return {
            "status": "completed",
            "thread_id": request.thread_id,
            "result": result.get("result")
        }

    except Exception as e:
        print("AGENT ERROR:", repr(e))
        raise HTTPException(
            status_code=500,
            detail="Agent execution failed."
        )


        