from __future__ import annotations

from typing import List, Optional, TypedDict, Any
from typing_extensions import Annotated

from langgraph.graph import add_messages

from langchain_core.messages import AnyMessage


class GraphState(TypedDict, total=False):
    """State carried through the LangGraph workflow.

    Fields:
    - messages: Conversation history as LangChain messages
    - project_root: Optional project root path for file operations
    - attachments: Optional list of file paths attached by the user for this turn
    - plan: Optional short plan text produced by the planner
    - retrieved_context: Optional list of retrieved text snippets
    - analysis_notes: Optional analysis notes from the analyst
    - critique: Optional brief critique from the critic
    - response: Final response text to send back to the user
    """

    messages: Annotated[List[AnyMessage], add_messages]
    project_root: Optional[str]
    attachments: Optional[List[str]]
    plan: Optional[str]
    retrieved_context: Optional[List[str]]
    analysis_notes: Optional[str]
    critique: Optional[str]
    response: Optional[str]


