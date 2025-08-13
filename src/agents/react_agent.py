"""
Simplified React Agent for LabAcc Copilot using LangGraph
Ultra-simple implementation following LangGraph best practices
"""

import os
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import asyncio

from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from src.components.llm import get_llm_instance


# ============= Simple Tool Definitions =============

@tool
def scan_project() -> str:
    """Scan all experiments in the project. Lists experiment folders with details."""
    project_root = "data/alice_projects"
    
    if not os.path.exists(project_root):
        return "No experiments found. Project folder doesn't exist yet."
    
    experiments = []
    for folder in sorted(os.listdir(project_root)):
        if os.path.isdir(os.path.join(project_root, folder)) and folder.startswith("exp_"):
            experiments.append(folder)
    
    if not experiments:
        return "No experiments found."
    
    return f"Found {len(experiments)} experiments: " + ", ".join(experiments)


@tool
def analyze_experiment(folder_name: str) -> str:
    """Analyze a specific experiment folder.
    
    Args:
        folder_name: Name of experiment folder like 'exp_001_pcr'
    """
    project_root = "data/alice_projects"
    folder_path = os.path.join(project_root, folder_name)
    
    if not os.path.exists(folder_path):
        return f"Folder '{folder_name}' not found."
    
    files = os.listdir(folder_path)
    response = f"Analysis of {folder_name}: Found {len(files)} files. "
    
    if "pcr" in folder_name.lower():
        response += "PCR experiment detected. Check annealing temp and primer concentration."
    
    return response


@tool  
def research_literature(query: str) -> str:
    """Search scientific literature.
    
    Args:
        query: Research topic or question
    """
    return f"Literature search for '{query}': Would search PubMed, protocols.io, etc. Deep research available via Tavily API."


@tool
def optimize_protocol(experiment_type: str, issue: str = "") -> str:
    """Get optimization suggestions.
    
    Args:
        experiment_type: Type like 'PCR', 'Western blot'
        issue: Current problem (optional)
    """
    suggestions = f"Optimizing {experiment_type}. "
    
    if "pcr" in experiment_type.lower():
        suggestions += "Try: gradient PCR, add DMSO for GC-rich, check Mg2+ concentration."
    
    if issue:
        suggestions += f" For '{issue}': check reagents, verify template quality."
    
    return suggestions


# ============= Create Agent =============

def create_simple_agent():
    """Create a simple React agent."""
    
    # Get LLM - using GPT-OSS 120B via OpenRouter
    llm = get_llm_instance("openrouter-gpt-oss-120b")
    
    # Tools
    tools = [
        scan_project,
        analyze_experiment,
        research_literature,
        optimize_protocol
    ]
    
    # Create agent - simple, no extra parameters
    agent = create_react_agent(llm, tools)
    
    return agent


# ============= Message Handler =============

async def handle_message(message: str, session_id: str = "default") -> str:
    """Handle a user message."""
    
    try:
        # Create agent
        agent = create_simple_agent()
        
        # Invoke with message
        result = agent.invoke({
            "messages": [HumanMessage(content=message)]
        })
        
        # Extract response
        if result and "messages" in result:
            # Get last AI message
            for msg in reversed(result["messages"]):
                if isinstance(msg, AIMessage):
                    return msg.content
        
        return "No response generated."
        
    except Exception as e:
        return f"Error: {str(e)}"


# ============= Test Function =============

async def test():
    """Test the agent."""
    queries = [
        "Hello",
        "Scan my experiments",
        "Help optimize PCR"
    ]
    
    for q in queries:
        print(f"Q: {q}")
        response = await handle_message(q)
        print(f"A: {response}\n")


if __name__ == "__main__":
    asyncio.run(test())