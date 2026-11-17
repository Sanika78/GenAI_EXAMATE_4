
import re
from typing import TypedDict, Any

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

from app.tools import locate_article


MAX_QUESTION_LENGTH = 1000

ALLOWED_TOOLS = {
    "locate_article",
    "ask_with_rag"
}
class AgentState(TypedDict, total=False):
    question: str
    tool: str
    approved: bool
    result: dict[str, Any]
    history: list[dict[str, str]]

def validate_input(state: AgentState):
    question = state.get("question", "")

    if not isinstance(question, str) or not question.strip():
        return {
            "error": "Question cannot be empty."
        }

    if len(question) > MAX_QUESTION_LENGTH:
        return {
            "error": "Question is too long. Maximum 1000 characters allowed."
        }

    return {"error": ""}



def validation_node(state: AgentState):
    result = validate_input(state)

    if result["error"]:
        return {
            "result": {
                "answer": result["error"],
                "tool_used": None,
                "confidence": "low"
            }
        }

    return {}


def route_after_validation(state: AgentState):
    if state.get("result"):
        return "end"

    return "select_tool"

def select_tool(state: AgentState):
    question = state["question"]

    match = re.search(
        r"\b(?:article|art\.?)\s*(\d+[A-Z]{0,2})\b",
        question,
        re.IGNORECASE
    )

    if match:
        return {"tool": "locate_article"}

    return {"tool": "ask_with_rag"}




def approval_node(state: AgentState):
    if state.get("tool") not in ALLOWED_TOOLS:
        return {
            "approved": False,
            "result": {
                "answer": "Tool is not allowed.",
                "tool_used": state.get("tool")
            }
        }
    decision = interrupt({
        "message": "Approve execution of the selected tool?",
        "selected_tool": state["tool"],
        "question": state["question"]
    })

    approved = (
        decision.get("approved", False)
        if isinstance(decision, dict)
        else bool(decision)
    )

    return {"approved": approved}


def execute_tool(state: AgentState):
    if state.get("tool") not in ALLOWED_TOOLS:
        return {
            "result": {
                "answer": "Tool execution blocked.",
                "tool_used": state.get("tool")
            }
        }
    question = state["question"]

    if state["tool"] == "locate_article":
        match = re.search(
            r"\b(?:article|art\.?)\s*(\d+[A-Z]{0,2})\b",
            question,
            re.IGNORECASE
        )

        article_no = match.group(1).upper()
        result = locate_article(article_no)

        if result["found"]:
            answer = (
                f"Article {article_no} belongs to "
                f"{result['part']} - {result['part_name']}."
            )
        else:
            answer = result["message"]

        return {
            "result": {
                "answer": answer,
                "tool_used": "locate_article",
                "details": result
            }
        }

    # Include recent conversation when answering follow-up questions
    history = state.get("history", [])

    if history:
        previous_context = "\n".join(
            f"User: {item['question']}\nAssistant: {item['answer']}"
            for item in history[-5:]
        )

        contextual_question = (
            f"Previous conversation:\n{previous_context}\n\n"
            f"Current question: {question}"
        )
    else:
        contextual_question = question

    from app.rag import ask_with_rag

    result = ask_with_rag(contextual_question)

    return {
        "result": {
            **result,
            "tool_used": "ask_with_rag"
        }
    }


def save_history(state: AgentState):
    history = list(state.get("history", []))
    result = state["result"]

    history.append({
        "question": state["question"],
        "answer": result.get("answer", "")
    })

    return {"history": history[-10:]}


def rejected_node(state: AgentState):
    return {
        "result": {
            "answer": "Tool execution was rejected by the user.",
            "tool_used": state["tool"],
            "approved": False
        }
    }


def route_after_approval(state: AgentState):
    if state.get("approved"):
        return "execute_tool"

    return "rejected"


workflow = StateGraph(AgentState)

workflow.add_node("validation", validation_node)
workflow.add_node("select_tool", select_tool)
workflow.add_node("approval", approval_node)
workflow.add_node("execute_tool", execute_tool)
workflow.add_node("save_history", save_history)
workflow.add_node("rejected", rejected_node)

workflow.add_edge(START, "validation")

workflow.add_conditional_edges(
    "validation",
    route_after_validation,
    {
        "select_tool": "select_tool",
        "end": END
    }
)

workflow.add_edge("select_tool", "approval")

workflow.add_conditional_edges(
    "approval",
    route_after_approval,
    {
        "execute_tool": "execute_tool",
        "rejected": "rejected"
    }
)

workflow.add_edge("execute_tool", "save_history")
workflow.add_edge("save_history", END)
workflow.add_edge("rejected", END)

memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)



def run_graph(question: str, thread_id: str, approved=None):
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    if approved is None:
        return graph.invoke(
            {"question": question},
            config=config
        )

    return graph.invoke(
        Command(resume={"approved": approved}),
        config=config
    )
