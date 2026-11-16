
from app.vectorstore import semantic_search
from app.llm import ask_llm


def ask_with_rag(question: str, top_k: int = 4):

    # 1. Validate question
    if not question.strip():
        return {
            "answer": "I don't know.",
            "confidence": "low",
            "follow_up": "Please ask a question about the Constitution.",
            "sources": []
        }

    # 2. Retrieve relevant chunks from ChromaDB
    chunks = semantic_search(question, limit=top_k)

    # 3. If no relevant chunks are found
    if not chunks:
        return {
            "answer": "I don't know.",
            "confidence": "low",
            "follow_up": "Try asking another question about the Constitution.",
            "sources": []
        }

    # 4. Prepare context from retrieved chunks
    context_parts = []
    sources = []

    for chunk in chunks:
        context_parts.append(
            f"""
            Article: {chunk.get('article_no')}
            Title: {chunk.get('title')}
            Page: {chunk.get('page')}
            Content: {chunk.get('text')}
            """
        )

        source = {
            "article_no": chunk.get("article_no"),
            "title": chunk.get("title"),
            "source": chunk.get("source"),
            "page": chunk.get("page")
        }

        if source not in sources:
            sources.append(source)

    context = "\n\n".join(context_parts)

    # 5. Build a grounded prompt
    rag_question = f"""
    Answer the following question using ONLY the provided context.

    Rules:
    - Do not use outside knowledge.
    - Do not invent constitutional articles or facts.
    - If the context does not contain enough information,
      answer exactly: I don't know.
    - Give a clear and simple answer.

    Retrieved Context:
    {context}

    User Question:
    {question}
    """

    # 6. Generate answer using the configured LLM
    response = ask_llm(rag_question)

    # 7. Return answer with citations
    return {
        "answer": response.get("answer", "I don't know."),
        "confidence": response.get("confidence", "low"),
        "follow_up": response.get("follow_up", ""),
        "sources": sources
    }
