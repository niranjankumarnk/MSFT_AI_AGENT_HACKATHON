# rag_agent.py

from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional
from rag_tools import upload_manual_tool, retrieve_context_tool, generate_response_tool

class MessagesState(TypedDict):
    query: Optional[str]
    file_bytes: Optional[bytes]
    filename: Optional[str]
    retrieved_chunks: Optional[List]
    answer: Optional[str]
    image_urls: Optional[List]

def create_agentic_rag_graph():
    workflow = StateGraph(MessagesState)

    @workflow.add_node
    def upload_manual(state):
        if state["file_bytes"] and state["filename"]:
            upload_manual_tool(state["file_bytes"], state["filename"])
        return state

    @workflow.add_node
    def retrieve_context(state):
        chunks = retrieve_context_tool(state["query"], state["filename"], top_k=1)
        return {**state, "retrieved_chunks": chunks}

    @workflow.add_node
    def generate_answer(state):
        answer, image_urls = generate_response_tool(state["query"], state["retrieved_chunks"])
        return {**state, "answer": answer, "image_urls": image_urls}

    workflow.set_entry_point("upload_manual")
    workflow.add_edge("upload_manual", "retrieve_context")
    workflow.add_edge("retrieve_context", "generate_answer")
    workflow.add_edge("generate_answer", END)

    return workflow.compile()
