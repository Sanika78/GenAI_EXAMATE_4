
import re

from app.rag import ask_with_rag
from app.tools import locate_article


def run_agent(question: str, top_k: int = 4):
    # Validate input
    if not question or not question.strip():
        return {
            "answer": "Please enter a valid question.",
            "tool_used": None,
            "confidence": "low",
            "sources": []
        }

    question = question.strip()

    # Detect article number
    match = re.search(
        r"\b(?:article|art\.?)\s*(\d+[A-Z]{0,2})\b",
        question,
        re.IGNORECASE
    )

    # Select article lookup tool
    if match:
        article_no = match.group(1).upper()
        result = locate_article(article_no)

        if result["found"]:
            answer = (
                f"Article {article_no} belongs to "
                f"{result['part']} - {result['part_name']}. "
                f"Article range: {result['article_range']}."
            )
        else:
            answer = result["message"]

        return {
            "answer": answer,
            "tool_used": "locate_article",
            "confidence": "medium" if result["found"] else "low",
            "details": result,
            "sources": []
        }

    # Select RAG tool for conceptual questions
    result = ask_with_rag(question, top_k=top_k)

    return {
        "answer": result["answer"],
        "tool_used": "ask_with_rag",
        "confidence": result["confidence"],
        "follow_up": result["follow_up"],
        "sources": result["sources"]
    }
