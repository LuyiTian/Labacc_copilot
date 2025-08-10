from __future__ import annotations

from typing import Dict

from langchain_core.messages import HumanMessage, SystemMessage

from .state import GraphState
from ..components.llm import get_llm_instance, get_available_models


def _get_safe_llm():
    available = get_available_models()
    if not available:
        return None
    # Pick the first available configured model
    model_name = next(iter(available.keys()))
    try:
        return get_llm_instance(model_name)
    except Exception:
        return None


def node_planner(state: GraphState) -> GraphState:
    llm = _get_safe_llm()
    messages = state.get("messages", [])
    system = SystemMessage(
        content=(
            "You are Planner. Read the latest user goal and produce a one-"
            "sentence plan for this round. Reply with only the plan text."
        )
    )
    prompt_messages = [system] + messages[-3:]
    if llm is None:
        plan_text = "Plan unavailable (no LLM configured)."
    else:
        plan_text = llm.invoke(prompt_messages).content
    state["plan"] = plan_text
    return state


def node_retriever(state: GraphState) -> GraphState:
    # MVP stub: leave retrieved_context empty; local RAG will be added later
    state["retrieved_context"] = []
    return state


def node_analyst(state: GraphState) -> GraphState:
    llm = _get_safe_llm()
    plan = state.get("plan") or ""
    attachments = state.get("attachments") or []
    # Keep minimal: mention attachment names if present
    attach_note = f"Attachments: {', '.join([a.split('/')[-1] for a in attachments])}" if attachments else ""
    human = HumanMessage(
        content=(
            "Given the plan, draft a short analysis note (2-3 bullet points).\n"
            f"Plan: {plan}\n{attach_note}"
        )
    )
    if llm is None:
        analysis = "- No LLM configured. Set API keys to enable analysis."
    else:
        analysis = llm.invoke([human]).content
    state["analysis_notes"] = analysis
    return state


def node_critic(state: GraphState) -> GraphState:
    llm = _get_safe_llm()
    analysis = state.get("analysis_notes") or ""
    human = HumanMessage(
        content=(
            "Critique the analysis briefly in one bullet and suggest one next step."
            f"\nAnalysis: {analysis}"
        )
    )
    if llm is None:
        critique = "- Next step: configure an LLM provider (OPENAI_API_KEY, SILICONFLOW_API_KEY, etc.)."
    else:
        critique = llm.invoke([human]).content
    state["critique"] = critique
    return state


def node_writer(state: GraphState) -> GraphState:
    llm = _get_safe_llm()
    messages = state.get("messages", [])
    plan = state.get("plan") or ""
    analysis = state.get("analysis_notes") or ""
    critique = state.get("critique") or ""
    
    # For simple greetings, provide a friendly response
    last_msg = messages[-1].content if messages else ""
    if last_msg.lower().strip() in ["hi", "hello", "hey"]:
        final_text = "Hello! I'm LabAcc Copilot, your wet-lab biology assistant. I can help you analyze experimental data, troubleshoot issues, and suggest optimizations. How can I assist you today?"
        state["response"] = final_text
        return state

    human = HumanMessage(
        content=(
            "You are a helpful biology lab assistant. Write a natural, conversational response based on:\n"
            f"User question: {last_msg}\n"
            f"Analysis: {analysis}\n"
            f"Suggestion: {critique}\n\n"
            "Provide a clear, helpful response. Do not show internal planning details."
        )
    )
    if llm is None:
        final_text = (
            "LLM not configured. Set one of: OPENAI_API_KEY, SILICONFLOW_API_KEY,"
            " ANTHROPIC_API_KEY, or GOOGLE_API_KEY. Then restart the app."
        )
    else:
        final_text = llm.invoke([human]).content
    state["response"] = final_text
    return state


