"""
Memory Tools for React Agent
Tools that interact with the README memory system
"""

import os
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path

from langchain_core.tools import tool

from src.memory.readme_memory import MemoryManager, ExperimentMemory
from src.components.llm import get_llm_instance
from langchain_core.messages import HumanMessage

# Initialize memory manager
memory_manager = MemoryManager()

# ============= Memory Tools =============

@tool
async def read_memory(
    experiment_id: str,
    section: Optional[str] = None
) -> str:
    """
    Read experiment memory from README file.
    
    Args:
        experiment_id: Experiment folder name (e.g., 'exp_001_pcr_optimization')
        section: Optional section to read ('overview', 'results', 'files', 'insights', etc.)
                If None, returns the full README content
    
    Returns:
        The requested memory content as formatted text
    """
    try:
        memory = memory_manager.read_memory(experiment_id)
        
        if memory is None:
            return f"No README memory found for experiment '{experiment_id}'. The experiment may not exist or lacks a README.md file."
        
        # If specific section requested
        if section:
            section_lower = section.lower()
            
            if section_lower == "overview":
                if memory.overview:
                    return f"**Overview for {experiment_id}:**\n" + \
                           f"Motivation: {memory.overview.get('motivation', 'Not specified')}\n" + \
                           f"Key Question: {memory.overview.get('key_question', 'Not specified')}\n" + \
                           f"Hypothesis: {memory.overview.get('hypothesis', 'Not specified')}"
                return "No overview section found"
            
            elif section_lower == "files":
                if memory.files:
                    files_str = f"**Files in {experiment_id}:**\n"
                    for file in memory.files:
                        files_str += f"- {file.get('name', 'Unknown')} ({file.get('type', 'Unknown')}): {file.get('summary', 'No summary')}\n"
                    return files_str
                return "No files documented"
            
            elif section_lower == "results":
                if memory.results:
                    results_str = f"**Results for {experiment_id}:**\n"
                    if memory.results.get('key_findings'):
                        results_str += "Key Findings:\n"
                        for finding in memory.results['key_findings']:
                            results_str += f"- {finding}\n"
                    if memory.results.get('statistics'):
                        results_str += "\nStatistics:\n"
                        for key, value in memory.results['statistics'].items():
                            results_str += f"- {key}: {value}\n"
                    return results_str
                return "No results documented"
            
            elif section_lower == "insights":
                if memory.insights:
                    insights_str = f"**Insights for {experiment_id}:**\n"
                    for insight in memory.insights:
                        insights_str += f"- [{insight.get('timestamp', 'Unknown time')}] {insight.get('insight', '')}\n"
                    return insights_str
                return "No insights documented"
            
            elif section_lower == "methods":
                if memory.methods:
                    return f"**Methods for {experiment_id}:**\n{memory.methods}"
                return "No methods documented"
            
            elif section_lower == "parameters":
                if memory.parameters:
                    params_str = f"**Parameters for {experiment_id}:**\n"
                    for param_type, params in memory.parameters.items():
                        if params:
                            params_str += f"\n{param_type.title()} Variables:\n"
                            for key, value in params.items():
                                params_str += f"- {key}: {value}\n"
                    return params_str
                return "No parameters documented"
            
            else:
                return f"Unknown section '{section}'. Available sections: overview, files, results, insights, methods, parameters"
        
        # Return full content
        return f"**Full README for {experiment_id}:**\n\n{memory.raw_content}"
    
    except Exception as e:
        return f"Error reading memory: {str(e)}"


@tool
async def write_memory(
    experiment_id: str,
    section: str,
    content: str,
    preserve_rest: bool = True
) -> str:
    """
    Update a section of the experiment README memory.
    
    Args:
        experiment_id: Experiment folder name
        section: Section to update ('overview', 'results', 'files', 'insights', 'notes', etc.)
        content: New content for the section (can be text or JSON string for structured data)
        preserve_rest: If True, preserves other sections (default: True)
    
    Returns:
        Confirmation of the update
    """
    try:
        # Parse content if it's JSON
        try:
            parsed_content = json.loads(content)
        except:
            parsed_content = content
        
        # Update the section
        success = memory_manager.update_section(experiment_id, section, parsed_content)
        
        if success:
            return f"Successfully updated {section} section in {experiment_id} README memory"
        else:
            return f"Failed to update {section} section in {experiment_id}"
    
    except Exception as e:
        return f"Error writing memory: {str(e)}"


@tool
async def search_memories(
    query: str,
    scope: str = "all"
) -> str:
    """
    Search across all experiment README memories.
    
    Args:
        query: Search query text
        scope: Search scope ('all', 'recent', 'active')
    
    Returns:
        Search results with matching experiments and context
    """
    try:
        results = memory_manager.search_memories(query, scope)
        
        if not results:
            return f"No experiments found matching '{query}'"
        
        output = f"Found {len(results)} experiments matching '{query}':\n\n"
        
        for result in results[:5]:  # Limit to first 5 results
            output += f"**{result['experiment_id']}:**\n"
            for match in result.get('matches', []):
                output += f"  - {match}\n"
            output += "\n"
        
        if len(results) > 5:
            output += f"\n...and {len(results) - 5} more experiments"
        
        return output
    
    except Exception as e:
        return f"Error searching memories: {str(e)}"


@tool
async def append_insight(
    experiment_id: str,
    insight: str,
    source: str = "agent"
) -> str:
    """
    Add a new insight to the experiment README.
    
    Args:
        experiment_id: Experiment folder name
        insight: The insight text to add
        source: Source of the insight ('agent', 'user', 'analysis')
    
    Returns:
        Confirmation of the insight addition
    """
    try:
        # Read current memory
        memory = memory_manager.read_memory(experiment_id)
        
        if memory is None:
            return f"Cannot add insight: experiment '{experiment_id}' not found"
        
        # Create insight entry
        new_insight = {
            'timestamp': datetime.now().isoformat(),
            'insight': f"[{source}] {insight}"
        }
        
        # Append to insights
        memory.insights.append(new_insight)
        
        # Add to change log
        memory.change_log.append({
            'timestamp': datetime.now().isoformat(),
            'change': f"Added insight from {source}"
        })
        
        # Write back
        success = memory_manager.write_memory(memory)
        
        if success:
            return f"Added insight to {experiment_id}: {insight}"
        else:
            return f"Failed to add insight to {experiment_id}"
    
    except Exception as e:
        return f"Error adding insight: {str(e)}"


@tool
async def update_file_registry(
    experiment_id: str,
    file_name: str,
    file_type: str,
    file_size: str,
    summary: str
) -> str:
    """
    Add or update a file entry in the experiment README.
    
    Args:
        experiment_id: Experiment folder name
        file_name: Name of the file
        file_type: Type of file ('data', 'image', 'document', etc.)
        file_size: Size of the file
        summary: Brief description of the file content
    
    Returns:
        Confirmation of the file registry update
    """
    try:
        # Read current memory
        memory = memory_manager.read_memory(experiment_id)
        
        if memory is None:
            # Create new experiment if doesn't exist
            memory_manager.create_experiment_readme(experiment_id)
            memory = memory_manager.read_memory(experiment_id)
        
        # Check if file already exists
        existing_file = None
        for i, file in enumerate(memory.files):
            if file.get('name') == file_name:
                existing_file = i
                break
        
        # Create file entry
        file_entry = {
            'name': file_name,
            'type': file_type,
            'size': file_size,
            'summary': summary,
            'added': datetime.now().isoformat()
        }
        
        # Update or append
        if existing_file is not None:
            memory.files[existing_file] = file_entry
            action = "Updated"
        else:
            memory.files.append(file_entry)
            action = "Added"
        
        # Add to change log
        memory.change_log.append({
            'timestamp': datetime.now().isoformat(),
            'change': f"{action} file entry: {file_name}"
        })
        
        # Write back
        success = memory_manager.write_memory(memory)
        
        if success:
            return f"{action} file '{file_name}' in {experiment_id} registry"
        else:
            return f"Failed to update file registry for {experiment_id}"
    
    except Exception as e:
        return f"Error updating file registry: {str(e)}"


@tool
async def compare_experiments(
    experiment_ids: str,
    aspect: str = "all"
) -> str:
    """
    Compare multiple experiments based on their README memories.
    
    Args:
        experiment_ids: Comma-separated list of experiment IDs
        aspect: What to compare ('results', 'methods', 'parameters', 'all')
    
    Returns:
        Comparative analysis of the experiments
    """
    try:
        exp_list = [e.strip() for e in experiment_ids.split(',')]
        
        if len(exp_list) < 2:
            return "Please provide at least 2 experiment IDs to compare (comma-separated)"
        
        # Read all experiment memories
        memories = {}
        for exp_id in exp_list:
            memory = memory_manager.read_memory(exp_id)
            if memory:
                memories[exp_id] = memory
        
        if len(memories) < 2:
            return f"Could not read enough experiments. Found: {list(memories.keys())}"
        
        # Build comparison
        comparison = f"**Comparing {len(memories)} experiments:**\n\n"
        
        # Compare based on aspect
        if aspect in ["all", "results"]:
            comparison += "**Results Comparison:**\n"
            for exp_id, memory in memories.items():
                comparison += f"\n{exp_id}:\n"
                if memory.results.get('key_findings'):
                    for finding in memory.results['key_findings'][:2]:
                        comparison += f"  - {finding}\n"
                else:
                    comparison += "  - No results documented\n"
        
        if aspect in ["all", "methods"]:
            comparison += "\n**Methods Comparison:**\n"
            for exp_id, memory in memories.items():
                comparison += f"\n{exp_id}:\n"
                if memory.methods:
                    # First 200 chars of methods
                    comparison += f"  {memory.methods[:200]}...\n"
                else:
                    comparison += "  - No methods documented\n"
        
        if aspect in ["all", "parameters"]:
            comparison += "\n**Parameters Comparison:**\n"
            for exp_id, memory in memories.items():
                comparison += f"\n{exp_id}:\n"
                if memory.parameters:
                    for param_type, params in memory.parameters.items():
                        if params:
                            comparison += f"  {param_type}: {', '.join(params.keys())}\n"
                else:
                    comparison += "  - No parameters documented\n"
        
        # Use LLM to generate insights
        llm = get_llm_instance()
        prompt = f"""Based on this experiment comparison, identify patterns and key differences:

{comparison}

Provide 2-3 key insights about what makes experiments successful or different."""
        
        response = llm.invoke([HumanMessage(content=prompt)])
        comparison += f"\n**Insights from comparison:**\n{response.content}"
        
        return comparison
    
    except Exception as e:
        return f"Error comparing experiments: {str(e)}"


@tool
async def create_experiment(
    experiment_name: str,
    motivation: str = "",
    key_question: str = ""
) -> str:
    """
    Create a new experiment with initial README memory.
    
    Args:
        experiment_name: Name for the experiment (will be converted to exp_XXX format)
        motivation: Why this experiment is being conducted
        key_question: The main research question
    
    Returns:
        Confirmation of experiment creation
    """
    try:
        # Generate experiment ID
        name_clean = experiment_name.lower().replace(' ', '_')
        name_clean = ''.join(c for c in name_clean if c.isalnum() or c == '_')
        
        # Find next available number
        existing = [d.name for d in Path(memory_manager.project_root).iterdir() 
                   if d.is_dir() and d.name.startswith("exp_")]
        
        if existing:
            numbers = []
            for exp in existing:
                try:
                    num = int(exp.split('_')[1])
                    numbers.append(num)
                except:
                    pass
            next_num = max(numbers) + 1 if numbers else 1
        else:
            next_num = 1
        
        experiment_id = f"exp_{next_num:03d}_{name_clean}"
        
        # Create the experiment
        success = memory_manager.create_experiment_readme(experiment_id, experiment_name)
        
        if success and (motivation or key_question):
            # Update with provided information
            memory = memory_manager.read_memory(experiment_id)
            if motivation:
                memory.overview['motivation'] = motivation
            if key_question:
                memory.overview['key_question'] = key_question
            memory_manager.write_memory(memory)
        
        if success:
            return f"Created new experiment '{experiment_id}' with initial README memory"
        else:
            return f"Failed to create experiment '{experiment_id}'"
    
    except Exception as e:
        return f"Error creating experiment: {str(e)}"


@tool
async def get_project_insights() -> str:
    """
    Get cross-experiment insights from all README memories.
    
    Returns:
        Summary of patterns and learnings across all experiments
    """
    try:
        # Get all experiments
        exp_dirs = [d for d in Path(memory_manager.project_root).iterdir() 
                   if d.is_dir() and d.name.startswith("exp_")]
        
        if not exp_dirs:
            return "No experiments found in project"
        
        # Collect insights from all experiments
        all_insights = []
        successful_experiments = []
        failed_experiments = []
        
        for exp_dir in exp_dirs:
            memory = memory_manager.read_memory(exp_dir.name)
            if memory:
                # Collect insights
                for insight in memory.insights:
                    all_insights.append(f"{exp_dir.name}: {insight.get('insight', '')}")
                
                # Track status
                if memory.status == "completed":
                    successful_experiments.append(exp_dir.name)
                elif memory.status == "failed":
                    failed_experiments.append(exp_dir.name)
        
        # Build summary
        summary = f"**Project Insights Summary:**\n\n"
        summary += f"Total experiments: {len(exp_dirs)}\n"
        summary += f"Successful: {len(successful_experiments)}\n"
        summary += f"Failed: {len(failed_experiments)}\n\n"
        
        if all_insights:
            summary += "**Recent Insights:**\n"
            for insight in all_insights[-5:]:  # Last 5 insights
                summary += f"- {insight}\n"
        
        # Use LLM to find patterns
        if len(all_insights) > 3:
            llm = get_llm_instance()
            prompt = f"""Analyze these experimental insights and identify 2-3 key patterns or learnings:

{chr(10).join(all_insights[:10])}

What patterns emerge? What works consistently?"""
            
            response = llm.invoke([HumanMessage(content=prompt)])
            summary += f"\n**Patterns Identified:**\n{response.content}"
        
        return summary
    
    except Exception as e:
        return f"Error getting project insights: {str(e)}"