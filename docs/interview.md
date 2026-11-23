# SamvidhanSathi – Interview Preparation

## 1. 60-Second Project Pitch

SamvidhanSathi is an AI-powered assistant that helps users understand the Constitution of India through simple, conversational questions.

The problem I wanted to solve was that constitutional documents are lengthy and legal language can be difficult for ordinary users to understand.

I built the application using Python, FastAPI, Streamlit, and Retrieval-Augmented Generation. The system retrieves relevant constitutional content, uses ChromaDB and Sentence Transformers for semantic retrieval, and sends the retrieved context to an LLM through Groq to generate a grounded answer.

I also implemented source references, confidence levels, prompt-based grounding, response caching, and API endpoints. The backend is deployed on Render and the frontend on Streamlit Community Cloud.

My main focus was to make answers useful while reducing unsupported or fabricated information. This project helped me understand document processing, embeddings, vector search, API development, LLM integration, and deployment.

## 2. Ten Likely Interview Questions and Answers

### Q1. What is SamvidhanSathi?

SamvidhanSathi is an AI-powered Constitution of India assistant. Users can ask questions in natural language and receive simplified answers based on retrieved constitutional content, along with source references.

### Q2. Why did you choose this project?

The Constitution contains important information, but its legal language and length can make it difficult to understand. I wanted to build a tool that makes this information easier to access and understand.

### Q3. Explain the architecture of your project.

The application has two main components:

- **Frontend:** Streamlit provides the interactive chat interface.
- **Backend:** FastAPI exposes endpoints for questions and document retrieval.

When a user asks a question, the backend retrieves relevant content using the retrieval pipeline. The retrieved context is passed to the LLM, which generates an answer. The API returns the answer, confidence, follow-up question, and sources to the frontend.

### Q4. What is RAG, and why did you use it?

RAG stands for Retrieval-Augmented Generation.

It combines two steps:

1. Retrieval: Find relevant information from the document collection.
2. Generation: Give that information to an LLM to generate an answer.

I used RAG because I wanted the assistant to answer using constitutional content rather than relying only on the LLM's pre-trained knowledge.

### Q5. What is the role of ChromaDB and Sentence Transformers?

Sentence Transformers convert text into numerical embeddings that represent semantic meaning.

ChromaDB stores and searches these embeddings. When a user asks a question, the question is converted into an embedding and compared with stored document embeddings to retrieve relevant content.

### Q6. What was the hardest technical problem?

One of the hardest problems was parsing a large legal PDF into clean, article-level chunks.

Legal documents are not structured like ordinary text. Article numbers can contain suffixes, such as 21A and 243ZH. Some articles are omitted or repealed. Clauses can contain nested numbering such as (1)(a)(i), and amendment footnotes must remain connected to the correct clause.

A simple split based on line breaks or article numbers can corrupt the document structure.

I approached this by treating article identification, text cleaning, clause boundaries, page references, and amendment notes as separate parsing concerns. I also focused on preserving metadata so retrieved content could be traced back to its source.

The key lesson was that retrieval quality depends heavily on the quality of document preprocessing. If the source text is split incorrectly, even a good embedding model can retrieve incomplete or misleading context.

### Q7. How do you reduce hallucinations?

I use a grounding prompt that instructs the LLM to answer from the retrieved context, avoid inventing constitutional facts, and respond with "I don't know" when the context is insufficient.

I also return source metadata with the answer so users can identify the supporting constitutional record.

### Q8. Why did you use FastAPI?

FastAPI makes it easy to build REST APIs using Python. It provides request validation through Pydantic, automatic Swagger documentation, and a convenient way to expose endpoints such as `/health`, `/records`, `/search`, and `/ask`.

### Q9. What challenges did you face during deployment?

I deployed the backend on Render and the frontend separately on Streamlit Community Cloud.

One challenge was configuring the frontend to call the deployed backend instead of the local `127.0.0.1` address. I also encountered temporary Gemini availability errors. I configured the application to use Groq as the active LLM provider and verified the deployed `/ask` endpoint through Swagger.

This taught me the importance of environment variables, cloud logs, API testing, and separating frontend and backend deployments.

### Q10. What would you improve in the future?

I would improve the system in these areas:

- Strengthen article-level PDF parsing and validation.
- Expand and verify the constitutional document corpus.
- Improve retrieval using hybrid search and reranking.
- Add multilingual question support.
- Add more evaluation datasets and automated answer-quality tests.
- Improve monitoring, latency tracking, and deployment reliability.

## 3. Hardest-Problem Interview Story

**Topic: Parsing a large legal PDF into reliable article-level chunks**

**Situation:** The Constitution is a long legal document with complex formatting, nested clauses, amendment notes, and article numbering.

**Task:** I needed to convert the PDF into structured records so the retrieval system could return the correct article and its supporting text.

**Action:** I focused on identifying article boundaries, preserving suffix-based article numbers, cleaning wrapped lines, maintaining nested clause structure, retaining amendment notes, and keeping source-page metadata. I treated omitted or repealed provisions carefully rather than assuming every article number represented an active provision.

**Result:** This work highlighted how important preprocessing is in a RAG system. Clean, correctly structured chunks make retrieval more accurate and make it easier to trace generated answers back to source material.

**Strong closing line:** "I learned that building a reliable RAG application is not just about choosing an LLM. The quality of the source data, parsing, chunking, and retrieval is equally important."

## 4. Demo Rehearsal Checklist

### Rehearsal 1 – Technical walkthrough

- [ ] Open the deployed Streamlit application.
- [ ] Ask: "What is Article 21 of the Indian Constitution?"
- [ ] Explain the answer and its source reference.
- [ ] Ask a second question about Fundamental Rights.
- [ ] Show the FastAPI Swagger documentation.
- [ ] Explain the `/ask` request and response.
- [ ] Explain the RAG pipeline and deployment architecture.

### Rehearsal 2 – Interview-style walkthrough

- [ ] Introduce the problem and project in 60 seconds.
- [ ] Demonstrate one question from the frontend.
- [ ] Explain retrieval, embeddings, ChromaDB, and Groq.
- [ ] Explain the hardest PDF parsing challenge.
- [ ] Explain one deployment issue and how it was fixed.
- [ ] Mention limitations and future improvements.

## 5. Final Verification

- [ ] All open items in `PROGRESS.md` are resolved or explicitly documented.
- [ ] README contains the correct frontend and backend URLs.
- [ ] API health endpoint responds successfully.
- [ ] `/ask` returns an answer with source metadata.
- [ ] Frontend successfully communicates with the deployed backend.
- [ ] Tests and lint checks pass.
- [ ] Both demo rehearsals are completed.
- [ ] Final Git tag is created and pushed.


