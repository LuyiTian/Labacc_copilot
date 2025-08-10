"""
Programmatic API for the deep research graph.

Provides a simple function for agents/workflows to invoke deep research
and get back a final markdown report string (and raw AI message content).
"""

from typing import Any, Dict, Optional

from langchain_core.messages import HumanMessage

from .graph import deep_research_graph


def run_deep_research(
    query: str,
    *,
    initial_search_query_count: int = 10,
    max_research_loops: int = 5,
    verbose: bool = True,
    response_language: Optional[str] = None,
    output_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Execute the deep research workflow and return the final result.

    Args:
        query: Research question/topic.
        initial_search_query_count: Number of initial queries to fan out.
        max_research_loops: Maximum reflection/search loops.
        verbose: Whether to log progress.
        response_language: Force response language; if None, model decides.

    Returns:
        Dict with keys:
            - messages: List of messages from the graph, last one contains final content
            - final_text: Raw text content from the final AI message
    """

    state: Dict[str, Any] = {
        "messages": [HumanMessage(content=query)],
        "initial_search_query_count": int(initial_search_query_count),
        "max_research_loops": int(max_research_loops),
        "verbose": bool(verbose),
    }
    if response_language:
        state["response_language"] = response_language
    if output_dir:
        state["output_dir"] = output_dir

    result = deep_research_graph.invoke(state)
    messages = result.get("messages", [])
    final_text = messages[-1].content if messages else ""

    return {
        "messages": messages,
        "final_text": final_text,
        "saved_path": result.get("saved_path"),
    }


