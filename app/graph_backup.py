import re
from typing import TypedDict, Any

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

from app.tools import locate_article


class AgentState(TypedDict, total=False):
    question: str
    tool: str
    approved: bool
    result: dict[str, Any]


# Node 1: Decide which tool to use
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


# Node 2: Ask for human approval
def approval_node(state: AgentState):
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


# Node 3: Execute the selected tool
def execute_tool(state: AgentState):
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

    from app.rag import ask_with_rag

    result = ask_with_rag(question)

    return {
        "result": {
            **result,
            "tool_used": "ask_with_rag"
        }
    }


# Node 4: Handle rejected approval
def rejected_node(state: AgentState):
    return {
        "result": {
            "answer": "Tool execution was rejected by the user.",
            "tool_used": state["tool"],
            "approved": False
        }
    }


# Decide what happens after approval
def route_after_approval(state: AgentState):
    if state.get("approved"):
        return "execute_tool"

    return "rejected"


# Build the LangGraph workflow
workflow = StateGraph(AgentState)

workflow.add_node("select_tool", select_tool)
workflow.add_node("approval", approval_node)
workflow.add_node("execute_tool", execute_tool)
workflow.add_node("rejected", rejected_node)

workflow.add_edge(START, "select_tool")
workflow.add_edge("select_tool", "approval")

workflow.add_conditional_edges(
    "approval",
    route_after_approval,
    {
        "execute_tool": "execute_tool",
        "rejected": "rejected"
    }
)

workflow.add_edge("execute_tool", END)
workflow.add_edge("rejected", END)


# Add conversation memory
memory = MemorySaver()

graph = workflow.compile(checkpointer=memory)


# Function to run or resume the graph
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
