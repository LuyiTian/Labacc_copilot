from __future__ import annotations

import operator
from dataclasses import dataclass, field
from typing import Annotated, TypedDict

from langgraph.graph import add_messages


class OverallState(TypedDict):
    messages: Annotated[list, add_messages]
    search_query: Annotated[list, operator.add]
    web_research_result: Annotated[list, operator.add]
    sources_gathered: Annotated[list, operator.add]
    output_dir: str
    initial_search_query_count: int
    max_research_loops: int
    research_loop_count: int
    reasoning_model: str
    verbose: bool
    response_language: str
    language_mode: str  # "english" or "mix"


class ReflectionState(TypedDict):
    knowledge_gap: str
    useful_expansion: str
    is_sufficient: bool
    follow_up_queries: Annotated[list, operator.add]
    research_loop_count: int
    number_of_ran_queries: int
    verbose: bool


class Query(TypedDict):
    query: str
    rationale: str
    response_language: str
    verbose: bool


class QueryGenerationState(TypedDict):
    search_query: list[Query]
    verbose: bool
    response_language: str
    language_mode: str


class WebSearchState(TypedDict):
    search_query: str
    id: str
    verbose: bool
    response_language: str


@dataclass(kw_only=True)
class SearchStateOutput:
    running_summary: str = field(default=None)  # Final report
