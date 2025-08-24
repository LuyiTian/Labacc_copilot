"""
Memory tools for the React agent.
LLM-based extraction for multi-language support - NO pattern matching!
"""

from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from typing import Optional
from pathlib import Path
import json
import logging
from datetime import datetime

from src.memory.memory import SimpleMemory
from src.components.llm import get_llm_instance

logger = logging.getLogger(__name__)

# Module-level storage for initialization
_memory_manager = None
_llm_instance = None


def init_memory_tools(project_root: str = "data/alice_projects", llm=None):
    """Initialize memory tools with project root and LLM instance."""
    global _memory_manager, _llm_instance
    from src.memory.memory import SimpleMemoryManager
    _memory_manager = SimpleMemoryManager(project_root)
    _llm_instance = llm or get_llm_instance()
    logger.info(f"Initialized memory tools with root: {project_root}")


@tool
async def get_experiment_info(experiment_id: str, what_info: str) -> str:
    """Get specific information from an experiment's README using LLM extraction.
    Works in ANY language - no pattern matching!
    
    Args:
        experiment_id: The experiment folder name (e.g., 'exp_001_pcr')
        what_info: Natural language description of what info you need
    
    Returns:
        Extracted information from the README
    """
    if not _memory_manager:
        return "Memory system not initialized"
    
    memory = _memory_manager.read_memory(experiment_id)
    if not memory:
        return f"No README found for {experiment_id}"
    
    # Use LLM to extract the requested information
    prompt = f"""From this experiment README, extract: {what_info}

README content:
{memory.raw_content}

Provide only the requested information, be concise."""
    
    response = _llm_instance.invoke([HumanMessage(content=prompt)])
    return response.content

# Alias for backward compatibility
read_memory = get_experiment_info


@tool
async def update_experiment_readme(experiment_id: str, updates: str) -> str:
    """Update an experiment's README with new information.
    The LLM will figure out how to integrate the updates naturally.
    
    Args:
        experiment_id: The experiment folder name
        updates: What information to add/update in natural language
    
    Returns:
        Confirmation message
    """
    if not _memory_manager:
        return "Memory system not initialized"
    
    # CRITICAL FIX: Must await async function!
    result = await _memory_manager.update_memory(experiment_id, updates, _llm_instance)
    return result

# Alias for backward compatibility  
append_insight = update_experiment_readme


@tool
def list_all_experiments() -> str:
    """List all experiments in the project with their current status.
    Simple directory listing - no complex parsing.
    
    Returns:
        List of experiments with basic info
    """
    if not _memory_manager:
        return "Memory system not initialized"
    
    experiments = _memory_manager.list_experiments()
    if not experiments:
        return "No experiments found"
    
    result = "Experiments in this project:\n"
    for exp in experiments:
        result += f"- {exp['name']}: {exp['status']}\n"
    
    return result

# Alias for backward compatibility
scan_project = list_all_experiments


@tool
async def search_experiments(search_query: str) -> str:
    """Search across all experiments using semantic search.
    The LLM understands the query in ANY language.
    
    Args:
        search_query: What to search for (any language)
    
    Returns:
        Relevant experiments and information
    """
    if not _memory_manager or not _llm_instance:
        return "Memory system not initialized"
    
    experiments = _memory_manager.list_experiments()
    if not experiments:
        return "No experiments to search"
    
    # Collect all README contents
    all_readmes = []
    for exp in experiments:
        memory = _memory_manager.read_memory(exp['name'])
        if memory:
            all_readmes.append({
                'name': exp['name'],
                'content': memory.raw_content[:1000]  # First 1000 chars
            })
    
    if not all_readmes:
        return "No experiment READMEs found"
    
    # Use LLM to search
    prompt = f"""Search query: {search_query}

Experiments:
"""
    for exp in all_readmes:
        prompt += f"\n{exp['name']}:\n{exp['content']}\n---\n"
    
    prompt += f"\nFind experiments relevant to the search query and explain why they match."
    
    response = _llm_instance.invoke([HumanMessage(content=prompt)])
    return response.content


@tool  
async def get_experiment_summary(experiment_id: str) -> str:
    """Generate a concise summary of an experiment.
    
    Args:
        experiment_id: The experiment folder name
    
    Returns:
        AI-generated summary
    """
    if not _memory_manager or not _llm_instance:
        return "Memory system not initialized"
    
    memory = _memory_manager.read_memory(experiment_id)
    if not memory:
        return f"No README found for {experiment_id}"
    
    prompt = f"""Provide a brief 2-3 sentence summary of this experiment:
{memory.raw_content[:2000]}"""
    
    response = _llm_instance.invoke([HumanMessage(content=prompt)])
    return response.content


@tool
async def update_file_registry(
    experiment_id: str,
    file_name: str, 
    file_type: str,
    file_size: str,
    summary: str
) -> str:
    """Update the file registry in experiment README.
    
    Args:
        experiment_id: Experiment folder name
        file_name: Name of the file
        file_type: Type of file (Data/Image/Document/etc)
        file_size: Size of the file
        summary: Brief description of the file
    """
    update_text = f"""
Add this file to the file registry:
- File: {file_name}
- Type: {file_type}
- Size: {file_size}
- Summary: {summary}
"""
    
    return await update_experiment_readme(experiment_id, update_text)


@tool
async def create_experiment(
    experiment_name: str,
    motivation: str,
    key_question: str
) -> str:
    """Create a new experiment with initial README.
    
    Args:
        experiment_name: Name for the experiment
        motivation: Why this experiment
        key_question: Main research question
    """
    from src.projects.session import get_current_session
    
    try:
        session = get_current_session()
        if not session:
            return "No active session. Please select a project first."
        
        # Create experiment folder under experiments/ directory
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        exp_folder_name = f"{timestamp}_{experiment_name.lower().replace(' ', '_')}"
        exp_path = session.resolve_path(f"experiments/{exp_folder_name}")
        exp_path.mkdir(parents=True, exist_ok=True)
        
        # Create initial README
        readme_content = f"""# Experiment: {experiment_name}

## Overview
**Created**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Status**: Active
**Motivation**: {motivation}
**Key Question**: {key_question}

## Methods
To be documented...

## Results
No results yet.

## Files
No files uploaded yet.

## Issues & Troubleshooting
None reported.

## Next Steps
1. Set up experimental protocol
2. Begin data collection
"""
        
        readme_path = exp_path / "README.md"
        readme_path.write_text(readme_content)
        
        return f"Created experiment: {exp_folder}"
        
    except Exception as e:
        logger.error(f"Failed to create experiment: {e}")
        return f"Error creating experiment: {str(e)}"


@tool
async def get_project_insights() -> str:
    """Get insights across all experiments in the project.
    
    Returns:
        Cross-experiment patterns and learnings
    """
    if not _memory_manager or not _llm_instance:
        return "Memory system not initialized"
    
    experiments = _memory_manager.list_experiments()
    if not experiments:
        return "No experiments found"
    
    # Collect successful patterns
    all_insights = []
    for exp in experiments[:5]:  # Limit to 5 for performance
        memory = _memory_manager.read_memory(exp['name'])
        if memory and len(memory.raw_content) > 100:
            all_insights.append(f"{exp['name']}: {memory.raw_content[:500]}")
    
    if not all_insights:
        return "No experiment data available for insights"
    
    prompt = f"""Based on these experiments, identify:
1. Common successful approaches
2. Recurring issues and solutions
3. Best practices emerging

Experiments:
{chr(10).join(all_insights)}

Provide actionable insights for future experiments."""
    
    response = _llm_instance.invoke([HumanMessage(content=prompt)])
    return response.content