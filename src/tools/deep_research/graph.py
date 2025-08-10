import os

from langchain_core.messages import AIMessage
from langgraph.types import Send
from langgraph.graph import StateGraph
from langgraph.graph import START, END
from langchain_core.runnables import RunnableConfig
from .tools_and_schemas import SearchQueryList, Reflection, search_with_tavily
import re
from .state import (
    OverallState,
    QueryGenerationState,
    ReflectionState,
    WebSearchState,
)
from .prompts import (
    get_current_date,
    query_writer_instructions,
    web_searcher_instructions,
    reflection_instructions,
    answer_instructions,
)
from .utils import get_citations, get_research_topic, insert_citation_markers

from src.components.llm import LLM_QUERY_WRITER, LLM_TRIAGE, LLM_SMALL
from typing import Tuple
from .config import MAX_RESEARCH_LOOPS, FAN_OUT_QUERIES, SEARCH_RESULTS_PER_QUERY
from rich import print


# Nodes
def generate_query(state: OverallState) -> QueryGenerationState:
    """LangGraph node that generates search queries based on the User's question.

    Use query writer LLM to create an optimized search queries for web research based on
    the User's question.

    Args:
        state: Current graph state containing the User's question
        config: Configuration for the runnable, including LLM provider settings

    Returns:
        Dictionary with state update, including search_query key containing the generated queries
    """

    # check for custom initial search query count
    if state.get("initial_search_query_count") is None:
        state["initial_search_query_count"] = FAN_OUT_QUERIES

    structured_llm = LLM_QUERY_WRITER.with_structured_output(SearchQueryList)

    # Format the prompt
    current_date = get_current_date()
    formatted_prompt = query_writer_instructions.format(
        current_date=current_date,
        research_topic=get_research_topic(state["messages"]),
        number_queries=state["initial_search_query_count"],
        # language_mode=state.get("language_mode", "query_in_english"),
    )
    # Generate the search queries
    result = structured_llm.invoke(formatted_prompt)
    if state.get("verbose", False):
        # print(f"[bold green]Formatted prompt:[/bold green]\n\t{formatted_prompt}")
        print(f"[bold orange]Search queries:[/bold orange]\n\t{result}")
    return {
        "search_query": result.query,
        "verbose": state.get("verbose", False),
        "response_language": result.response_language,
        "language_mode": state.get("language_mode", "english"),
    }


def continue_to_web_research(state: QueryGenerationState):
    """LangGraph node that sends the search queries to the web research node.

    This is used to spawn n number of web research nodes, one for each search query.
    """
    return [
        Send(
            "web_research",
            {
                "search_query": search_query,
                "id": int(idx),
                "verbose": state.get("verbose", False),
                "response_language": state.get("response_language", "English"),
            },
        )
        for idx, search_query in enumerate(state["search_query"])
    ]


def web_research(state: WebSearchState) -> OverallState:
    """LangGraph node that performs web research using Tavily Search API.

    Args:
        state: Current graph state containing the search query and research loop count

    Returns:
        Dictionary with state update, including sources_gathered, research_loop_count, and web_research_results
    """
    if state.get("verbose", False):
        print(
            f"[bold blue]Web Query:[/bold blue]\n\t{state['search_query']}"
        )
    # do the search using Tavily Search API
    tavily_response = search_with_tavily(
        state["search_query"], count=SEARCH_RESULTS_PER_QUERY
    )

    web_search_prompt = web_searcher_instructions.format(
        current_date=get_current_date(),
        research_topic=state["search_query"],
        search_results=tavily_response,
        response_language=state.get("response_language", "English"),
    )

    # send this to the LLM TRIAGE
    if state.get("verbose", False):
        print(f"[bold blue]Reading Tavily[/bold blue]")
    llm_response = LLM_SMALL.invoke(web_search_prompt)
    content = llm_response.content
    if not content:
        raise ValueError(
            "LLM response does not contain any content. Please check the LLM response format."
        )
    # Initialize sources_gathered as an empty list
    sources_gathered = []
    markdown_citation_regex = r"\[([^\]]+)\]\((https?://[^\)]+)\)"
    markdown_citations = [
        (match.group(1), match.group(2))
        for match in re.finditer(markdown_citation_regex, content)
    ]
    sources_gathered = [
        # all the urls used in the llm response, just the url
        {
            "label": label.strip(),
            "value": url.strip(),
            "start_index": content.find(f"[{label}]({url})"),
            "end_index": content.find(f"[{label}]({url})") + len(f"[{label}]({url})"),
        }
        for label, url in markdown_citations
    ]
    # If no sources were gathered, raise an error
    if not sources_gathered:
        sources_gathered = []
        # raise ValueError("No sources were gathered from the LLM response. Please check the LLM response format.")

    result = {
        "sources_gathered": sources_gathered,
        "search_query": [state["search_query"]],
        "web_research_result": [content],
    }
    # If verbose mode is enabled, add the verbose flag to the result
    # if state.get("verbose", False):
    #     print(f"[bold blue]Sources gathered:[/bold blue]\n\t{sources_gathered}")
    #     print(f"[bold blue]Web research result:[/bold blue]\n\t{content}")
    return result


def reflection(state: OverallState) -> ReflectionState:
    """LangGraph node that identifies knowledge gaps and generates potential follow-up queries.

    Analyzes the current summary to identify areas for further research and generates
    potential follow-up queries. Uses structured output to extract
    the follow-up query in JSON format.

    Args:
        state: Current graph state containing the running summary and research topic
        config: Configuration for the runnable, including LLM provider settings

    Returns:
        Dictionary with state update, including search_query key containing the generated follow-up query
    """
    print(f"[bold red]Reflection started[/bold red]")
    # Increment the research loop count and get the reasoning model
    state["research_loop_count"] = state.get("research_loop_count", 0) + 1
    reasoning_model = LLM_TRIAGE

    # Format the prompt
    current_date = get_current_date()
    formatted_prompt = reflection_instructions.format(
        current_date=current_date,
        research_topic=get_research_topic(state["messages"]),
        summaries="\n\n---\n\n".join(state["web_research_result"]),
    )
    # init Reasoning Model
    # add a few retries
    counter = 0
    while counter < 3:
        try:
            # Invoke the LLM with structured output
            result = reasoning_model.with_structured_output(Reflection).invoke(
                formatted_prompt
            )
            break  # Exit loop if successful
        except Exception as e:
            print(f"[bold red]Error during LLM invocation:[/bold red] {e}")
            counter += 1
            if counter >= 3:
                raise ValueError("Failed to invoke LLM after 3 attempts.")
    if not result.is_sufficient:
        print(
            f"[bold orange]Knowledge gap identified:[/bold orange]\n{result.knowledge_gap}\nFollow-up queries: {result.follow_up_queries}\n[bold orange]Useful expansion:[/bold orange]\n{result.useful_expansion}"
        )
    else:
        print(f"[bold green]Sufficient[/bold green]\n{result.knowledge_gap}")
    return {
        "is_sufficient": result.is_sufficient,
        "knowledge_gap": result.knowledge_gap,
        "useful_expansion": result.useful_expansion,
        "follow_up_queries": result.follow_up_queries,
        "research_loop_count": state["research_loop_count"],
        "number_of_ran_queries": len(state["search_query"]),
    }


def evaluate_research(
    state: ReflectionState,
) -> OverallState:
    """LangGraph routing function that determines the next step in the research flow.

    Controls the research loop by deciding whether to continue gathering information
    or to finalize the summary based on the configured maximum number of research loops.

    Args:
        state: Current graph state containing the research loop count

    Returns:
        String literal indicating the next node to visit ("web_research" or "finalize_summary")
    """
    max_research_loops = (
        state.get("max_research_loops")
        if state.get("max_research_loops") is not None
        else MAX_RESEARCH_LOOPS
    )
    if state["is_sufficient"] or state["research_loop_count"] >= max_research_loops:
        return "finalize_answer"
    else:
        return [
            Send(
                "web_research",
                {
                    "search_query": follow_up_query,
                    "id": state["number_of_ran_queries"] + int(idx),
                },
            )
            for idx, follow_up_query in enumerate(state["follow_up_queries"])
        ]


def finalize_answer(state: OverallState):
    """LangGraph node that finalizes the research summary.

    Prepares the final output by deduplicating and formatting sources, then
    combining them with the running summary to create a well-structured
    research report with proper citations.

    Args:
        state: Current graph state containing the running summary and sources gathered

    Returns:
        Dictionary with state update, including running_summary key containing the formatted final summary with sources
    """
    print(f"[bold green]Finalizing answer[/bold green]")
    reasoning_model = LLM_TRIAGE

    # Format the prompt
    current_date = get_current_date()
    formatted_prompt = answer_instructions.format(
        current_date=current_date,
        research_topic=get_research_topic(state["messages"]),
        summaries="\n---\n\n".join(state["web_research_result"]),
        response_language=state.get("response_language", "English"),
    )

    result = reasoning_model.invoke(formatted_prompt)

    # Replace the short urls with the original urls and add all used urls to the sources_gathered
    # unique_sources = []
    # for source in state["sources_gathered"]:
    #     if source["value"] in result.content:
    #         unique_sources.append(source)
    
    # write the final message to a proper markdown
    title, markdown_content = harvest_markdown(result.content)
    # decide output directory
    base_dir = state.get("output_dir") or "deep_research/generated_reports"
    os.makedirs(base_dir, exist_ok=True)
    saved_path = os.path.join(base_dir, f"DeepResearch_{title}.md")
    with open(saved_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    print(f"[bold green]Final Answer Saved at {saved_path}.[/bold green]")
    return {
        "messages": [AIMessage(content=result.content)],
        "saved_path": saved_path,
    }

def harvest_markdown(response: str) -> Tuple[str, str]:
    """Extract the markdown content that is wrapped in a code block, and also recognize the title string for saving files."""
    # Use regex to find the markdown content wrapped in code blocks
    match = re.search(r"```markdown\n(.*?)\n```", response, re.DOTALL)
    if match:
        markdown_content = match.group(1).strip()
        # Extract the title from the first line of the markdown content
        title_match = re.search(r"^#\s*(.*)", markdown_content, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else "Untitled"
        return title, markdown_content
    else:
        raise ValueError("No markdown content found in the response.")


# # Create our Agent Graph
builder = StateGraph(OverallState)

# # Define the nodes we will cycle between
builder.add_node("generate_query", generate_query)
builder.add_node("web_research", web_research)
builder.add_node("reflection", reflection)
builder.add_node("finalize_answer", finalize_answer)

# # Set the entrypoint as `generate_query`
# # This means that this node is the first one called
builder.add_edge(START, "generate_query")
# # Add conditional edge to continue with search queries in a parallel branch
builder.add_conditional_edges(
    "generate_query", continue_to_web_research, ["web_research"]
)
# # Reflect on the web research
builder.add_edge("web_research", "reflection")
# # Evaluate the research
builder.add_conditional_edges(
    "reflection", evaluate_research, ["web_research", "finalize_answer"]
)
# # Finalize the answer
builder.add_edge("finalize_answer", END)

deep_research_graph = builder.compile(name="deep_research_graph")
