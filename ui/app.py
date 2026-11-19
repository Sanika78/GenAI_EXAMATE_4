import os
import streamlit as st
import requests
import json
import csv
import uuid
from pathlib import Path
from datetime import datetime

# ---------------- CONFIGURATION ----------------

st.set_page_config(
    page_title="SamvidhanSathi",
    page_icon="⚖️",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = BASE_DIR / "data" / "records.json"
FEEDBACK_FILE = BASE_DIR / "ui" / "feedback.csv"

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

# ---------------- LOAD DATA ----------------

@st.cache_data
def load_records():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


records = load_records()


# ---------------- SESSION STATE ----------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_agent" not in st.session_state:
    st.session_state.pending_agent = None


# ---------------- HELPER FUNCTIONS ----------------

def save_feedback(question, answer, feedback):
    file_exists = FEEDBACK_FILE.exists()

    with open(FEEDBACK_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "timestamp",
                "question",
                "answer",
                "feedback"
            ])

        writer.writerow([
            datetime.now().isoformat(),
            question,
            answer,
            feedback
        ])


def get_answer(data):
    if isinstance(data, dict):
        return (
            data.get("answer")
            or data.get("result")
            or data.get("message")
            or str(data)
        )
    return str(data)


def show_sources(sources):
    if not sources:
        st.caption("No source citations were returned.")
        return

    with st.expander("📚 View source citations"):
        if isinstance(sources, list):
            for source in sources:
                if isinstance(source, dict):
                    article = source.get("article_no", "")
                    title = source.get("title", "")
                    text = source.get("text", "")
                    st.markdown(f"**Article {article} – {title}**")
                    if text:
                        st.caption(text[:500])
                else:
                    st.write(source)
        else:
            st.write(sources)


def ask_backend(question, endpoint):
    try:
        if endpoint == "ask":
            response = requests.post(
                f"{API_URL}/ask",
                json={"question": question, "top_k": 4},
                timeout=90
            )
        else:
            thread_id = str(uuid.uuid4())

            response = requests.post(
                f"{API_URL}/agent",
                json={
                    "question": question,
                    "thread_id": thread_id
                },
                timeout=90
            )

            data = response.json()

            # Handle LangGraph human approval
            if data.get("status") == "approval_required":
                st.session_state.pending_agent = {
                    "thread_id": thread_id,
                    "question": question
                }
                return {
                    "answer": "This request requires tool approval.",
                    "sources": [],
                    "approval_required": True
                }

            response.raise_for_status()
            return data

        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as error:
        return {
            "answer": f"Unable to connect to the API: {error}",
            "sources": []
        }


# ---------------- HEADER ----------------

st.title("⚖️ SamvidhanSathi")
st.caption("Your AI-powered Constitution of India assistant")

st.markdown(
    "Ask questions about the Indian Constitution, "
    "explore Articles, and understand constitutional provisions."
)

chat_tab, article_tab = st.tabs([
    "💬 Chat Assistant",
    "📖 Article Card"
])


# ---------------- CHAT ASSISTANT ----------------

with chat_tab:

    st.subheader("Ask SamvidhanSathi")

    endpoint = st.radio(
        "Choose assistant mode",
        ["ask", "agent"],
        format_func=lambda x: "RAG Assistant (/ask)" if x == "ask"
        else "Agent Assistant (/agent)",
        horizontal=True
    )

    # Display conversation history
    for index, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message["role"] == "assistant":
                show_sources(message.get("sources", []))

                st.caption("Was this answer helpful?")
                col1, col2 = st.columns(2)

                with col1:
                    if st.button("👍", key=f"up_{index}"):
                        save_feedback(
                            message.get("question", ""),
                            message["content"],
                            "positive"
                        )
                        st.toast("Positive feedback saved!")

                with col2:
                    if st.button("👎", key=f"down_{index}"):
                        save_feedback(
                            message.get("question", ""),
                            message["content"],
                            "negative"
                        )
                        st.toast("Negative feedback saved!")

    # Approval workflow
    if st.session_state.pending_agent:
        st.warning("The agent is waiting for your approval.")

        if st.button("Approve tool execution"):
            pending = st.session_state.pending_agent

            try:
                response = requests.post(
                    f"{API_URL}/agent",
                    json={
                        "question": pending["question"],
                        "thread_id": pending["thread_id"],
                        "approved": True
                    },
                    timeout=90
                )
                response.raise_for_status()
                result = response.json()

                answer = get_answer(result)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": result.get("sources", []),
                    "question": pending["question"]
                })

                st.session_state.pending_agent = None
                st.rerun()

            except requests.exceptions.RequestException as error:
                st.error(f"Approval request failed: {error}")

    prompt = st.chat_input("Ask a question about the Constitution...")

    if prompt:
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        with st.spinner("SamvidhanSathi is thinking..."):
            result = ask_backend(prompt, endpoint)

        answer = get_answer(result)

        if result.get("approval_required"):
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "sources": [],
                "question": prompt
            })
        else:
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "sources": result.get("sources", []),
                "question": prompt
            })

        st.rerun()


# ---------------- ARTICLE CARD ----------------

with article_tab:

    st.subheader("Explore a Constitutional Article")

    article_options = {
        f"Article {record.get('article_no')} – {record.get('title', 'Untitled')}":
        record
        for record in records
    }

    selected_label = st.selectbox(
        "Select an Article",
        list(article_options.keys())
    )

    selected = article_options[selected_label]

    st.markdown(f"### Article {selected.get('article_no')}")
    st.markdown(f"**{selected.get('title', '')}**")

    left, right = st.columns(2)

    with left:
        st.markdown("#### 📜 Original Constitutional Text")
        st.info(selected.get("text", "Original text unavailable."))

        st.caption(
            f"Part: {selected.get('part', 'Not specified')} | "
            f"Source page: {selected.get('source_page', 'Not specified')}"
        )

    with right:
        st.markdown("#### 💡 Plain-English Explanation")

        if st.button("Generate simple explanation"):
            question = (
                f"Explain Article {selected.get('article_no')} "
                f"in simple English for a student. "
                f"Explain its meaning and give a simple example."
            )

            with st.spinner("Generating explanation..."):
                result = ask_backend(question, "ask")

            st.session_state.article_explanation = get_answer(result)

        if "article_explanation" in st.session_state:
            st.success(st.session_state.article_explanation)
        else:
            st.write(
                "Click the button above to understand this Article "
                "in simple English."
            )

    # Amendment footnotes
    st.markdown("---")
    st.markdown("#### 🏷️ Amendment History")

    amendments = selected.get("amended_by", [])

    if amendments:
        if isinstance(amendments, str):
            amendments = [amendments]

        for index, amendment in enumerate(amendments, start=1):
            st.markdown(
                f"**[{index}] Amendment Act:** {amendment}"
            )
    else:
        st.caption(
            "No amendment details are available in the current dataset "
            "for this Article."
        )


# ---------------- FOOTER ----------------

st.markdown("---")
st.caption("SamvidhanSathi | Constitution of India AI Assistant")
