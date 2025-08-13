"""
LangChain Tool wrappers for deep_research so ReAct-style agents can call it.
"""


from langchain_core.tools import tool

from .api import run_deep_research


@tool("deep_research", return_direct=False)
def deep_research_tool(
    query: str,
    initial_search_query_count: int = 10,
    max_research_loops: int = 5,
    response_language: str | None = None,
    output_dir: str | None = None,
) -> str:
    """Conduct deep literature/web research and return a markdown report.

    Args:
        query: Research question or topic.
        initial_search_query_count: Number of initial search queries to generate.
        max_research_loops: Maximum number of research reflection loops.
        response_language: Optional target language for the response.

    Returns:
        Markdown string containing the research report with citations.
    """
    result = run_deep_research(
        query,
        initial_search_query_count=initial_search_query_count,
        max_research_loops=max_research_loops,
        verbose=True,
        response_language=response_language,
        output_dir=output_dir,
    )
    return result.get("final_text", "")


