from __future__ import annotations

from typing import Iterable

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph

from .state import GraphState
from .nodes import (
    node_planner,
    node_retriever,
    node_analyst,
    node_critic,
    node_writer,
)


def build_graph():
    """Compile the LangGraph application with a memory checkpointer."""
    graph = StateGraph(GraphState)

    graph.add_node("planner", node_planner)
    graph.add_node("retriever", node_retriever)
    graph.add_node("analyst", node_analyst)
    graph.add_node("critic", node_critic)
    graph.add_node("writer", node_writer)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "retriever")
    graph.add_edge("retriever", "analyst")
    graph.add_edge("analyst", "critic")
    graph.add_edge("critic", "writer")
    graph.set_finish_point("writer")

    checkpointer = MemorySaver()
    app = graph.compile(checkpointer=checkpointer)
    return app


