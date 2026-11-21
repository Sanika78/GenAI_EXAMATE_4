# SamvidhanSathi – AI-Powered Constitution of India Assistant

**Technologies:** Python, FastAPI, Streamlit, LangChain/LangGraph, ChromaDB, Sentence Transformers, Groq, Google Gemini, Docker, GitHub Actions

- Developed an AI-powered Constitution of India assistant using **FastAPI, Streamlit, and Retrieval-Augmented Generation (RAG)** to provide contextual answers with source references.
- Implemented **semantic search using Sentence Transformers and ChromaDB**, along with LangGraph-based agent workflows, LLM integration, response caching, and token usage monitoring.
- Deployed the REST API on **Render** and configured **GitHub Actions CI** for automated Pytest, Ruff, and Docker build checks; recorded a **98.7% lower response latency** on a repeated cached request during local testing.