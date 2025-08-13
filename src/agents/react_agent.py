"""
React Agent for LabAcc Copilot - With Automatic Background Memory Management

This module implements a React agent using LangGraph that can:
1. Handle user queries with automatic context awareness
2. Automatically update README memories from conversations
3. Analyze experimental data with background memory updates
4. Search scientific literature
5. Suggest optimizations based on patterns

Memory is handled AUTOMATICALLY - no explicit memory tools needed!
"""

import os
from pathlib import Path
from typing import List, Optional
import asyncio
import logging

from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from src.components.llm import get_llm_instance
from src.components.file_analyzer import QuickFileAnalyzer

# Import memory functions for AUTOMATIC use (not as tools!)
from src.memory.memory_tools import (
    read_memory,
    append_insight,
    update_file_registry,
    get_project_insights,
    create_experiment
)

# Setup logging configuration
try:
    from src.config.logging_config import setup_logging, log_conversation
    setup_logging()
except ImportError:
    # Fallback if logging config not available
    pass

logger = logging.getLogger(__name__)

# ============= Analysis Tools (with automatic memory updates) =============

@tool
async def scan_project() -> str:
    """Scan all experiments in the project and show their current status."""
    project_root = Path("data/alice_projects")
    
    if not project_root.exists():
        return "No experiments found. Project folder doesn't exist yet."
    
    experiments = []
    experiment_details = []
    
    for folder in sorted(project_root.iterdir()):
        if folder.is_dir() and folder.name.startswith("exp_"):
            experiments.append(folder.name)
            # Try to read status from README automatically
            try:
                readme_path = folder / "README.md"
                if readme_path.exists():
                    with open(readme_path, 'r') as f:
                        first_lines = f.read(500)  # Quick read
                        status = "Active" if "Active" in first_lines else "Unknown"
                        experiment_details.append(f"- {folder.name}: {status}")
                else:
                    experiment_details.append(f"- {folder.name}: No README")
            except:
                experiment_details.append(f"- {folder.name}: Cannot read")
    
    if not experiments:
        return "No experiments found. Create a new experiment folder starting with 'exp_'"
    
    result = f"Found {len(experiments)} experiments:\n"
    result += "\n".join(experiment_details[:20])
    if len(experiment_details) > 20:
        result += f"\n... and {len(experiment_details) - 20} more"
    
    return result


@tool  
async def list_folder_contents(folder_path: str) -> str:
    """List files and subfolders in a specified folder.
    
    Args:
        folder_path: Path to the folder (e.g., 'exp_001_pcr' or full path)
    """
    try:
        # Resolve path - handle project-relative paths
        if folder_path.startswith("/"):
            # Remove leading slash for project-relative paths
            folder_path = folder_path.lstrip("/")
        
        # Check if it's in bob_projects or alice_projects
        if folder_path.startswith("bob_projects"):
            # Look in data/bob_projects
            relative_path = folder_path.replace("bob_projects/", "").replace("bob_projects", "")
            if relative_path:
                full_path = Path("data/bob_projects") / relative_path
            else:
                full_path = Path("data/bob_projects")
        elif folder_path.startswith("alice_projects"):
            # Look in data/alice_projects
            relative_path = folder_path.replace("alice_projects/", "").replace("alice_projects", "")
            if relative_path:
                full_path = Path("data/alice_projects") / relative_path
            else:
                full_path = Path("data/alice_projects")
        elif folder_path.startswith("exp_"):
            # Experiment folder - check both locations
            alice_path = Path("data/alice_projects") / folder_path
            bob_path = Path("data/bob_projects") / folder_path
            if alice_path.exists():
                full_path = alice_path
            elif bob_path.exists():
                full_path = bob_path
            else:
                full_path = alice_path  # Default to alice
        else:
            # Default to alice_projects for other paths
            full_path = Path("data/alice_projects") / folder_path
        
        if not full_path.exists():
            # Try bob_projects as fallback
            bob_path = Path("data/bob_projects") / folder_path
            if bob_path.exists():
                full_path = bob_path
            else:
                return f"Folder not found: {folder_path}"
        
        if not full_path.is_dir():
            return f"Not a folder: {folder_path}"
        
        # List contents
        contents = []
        files = []
        folders = []
        
        for item in sorted(full_path.iterdir()):
            if item.is_dir():
                folders.append(f"📁 {item.name}/")
            else:
                size = item.stat().st_size
                if size < 1024:
                    size_str = f"{size}B"
                elif size < 1024*1024:
                    size_str = f"{size/1024:.1f}KB"
                else:
                    size_str = f"{size/(1024*1024):.1f}MB"
                files.append(f"📄 {item.name} ({size_str})")
        
        result = f"Contents of {folder_path}:\n\n"
        
        if folders:
            result += "Folders:\n" + "\n".join(folders) + "\n\n"
        
        if files:
            result += "Files:\n" + "\n".join(files)
        
        if not folders and not files:
            result = f"Folder {folder_path} is empty"
        
        # If it's an experiment folder with README, add a note
        readme_path = full_path / "README.md"
        if readme_path.exists():
            result += "\n\n📝 Note: This experiment has a README.md with memory/context"
        
        return result
        
    except Exception as e:
        logger.error(f"Error listing folder: {e}")
        return f"Error listing folder: {str(e)}"


@tool
async def analyze_data(file_path: str) -> str:
    """Analyze experimental data file. Context is automatically loaded if in an experiment folder.
    
    Args:
        file_path: Path to the data file (relative or absolute)
    """
    try:
        # Use file analyzer
        llm = get_llm_instance()
        analyzer = QuickFileAnalyzer(llm)
        
        # Resolve path - handle project-relative paths like /bob_projects/README.md
        if file_path.startswith("/"):
            # Remove leading slash
            file_path = file_path.lstrip("/")
        
        # Check if it's in bob_projects or alice_projects
        if file_path.startswith("bob_projects/"):
            relative_path = file_path.replace("bob_projects/", "")
            full_path = Path("data/bob_projects") / relative_path
        elif file_path.startswith("alice_projects/"):
            relative_path = file_path.replace("alice_projects/", "")
            full_path = Path("data/alice_projects") / relative_path
        elif Path(file_path).is_absolute():
            full_path = Path(file_path)
        else:
            # Try both locations
            alice_path = Path("data/alice_projects") / file_path
            bob_path = Path("data/bob_projects") / file_path
            if alice_path.exists():
                full_path = alice_path
            elif bob_path.exists():
                full_path = bob_path
            else:
                full_path = alice_path  # Default
        
        if not full_path.exists():
            return f"File not found: {file_path}"
        
        # Analyze file
        analysis = await analyzer.analyze_file(str(full_path))
        
        # For better summaries, also use our context-aware summarizer
        from src.memory.file_summarizer import summarize_uploaded_file
        
        # Detect experiment ID for context
        experiment_id = None
        path_str = str(full_path)
        if "/exp_" in path_str:
            parts = path_str.split("/")
            for part in parts:
                if part.startswith("exp_"):
                    experiment_id = part
                    break
        
        # Get context-aware summary
        try:
            context_summary = await summarize_uploaded_file(str(full_path), experiment_id)
        except:
            context_summary = analysis.content_summary
        
        result = f"File Analysis for {analysis.file_name}:\n"
        result += f"- Type: {analysis.file_type}\n"
        result += f"- Size: {analysis.size_bytes} bytes\n"
        result += f"- Summary: {context_summary}\n"
        
        if analysis.data_points:
            result += f"- Data points: {analysis.data_points}\n"
        
        # AUTOMATIC MEMORY UPDATE - happens in background!
        async def update_memory_background():
            try:
                # Detect if this is in an experiment folder
                path_str = str(full_path)
                if "/exp_" in path_str:
                    # Extract experiment ID
                    parts = path_str.split("/")
                    for part in parts:
                        if part.startswith("exp_"):
                            experiment_id = part
                            # Update README automatically with context-aware summary
                            await update_file_registry.ainvoke({
                                "experiment_id": experiment_id,
                                "file_name": analysis.file_name,
                                "file_type": analysis.file_type,
                                "file_size": f"{analysis.size_bytes} bytes",
                                "summary": context_summary  # Use the context-aware summary
                            })
                            
                            if analysis.analysis_confidence > 0.7:
                                await append_insight.ainvoke({
                                    "experiment_id": experiment_id,
                                    "insight": f"Analyzed {analysis.file_name}: {analysis.content_summary}",
                                    "source": "analysis"
                                })
                            logger.info(f"Auto-updated README for {experiment_id}")
                            break
            except Exception as e:
                logger.error(f"Background memory update failed: {e}")
        
        # Fire and forget - don't wait
        asyncio.create_task(update_memory_background())
        
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing file: {e}")
        return f"Error analyzing file: {str(e)}"


@tool
async def diagnose_issue(problem: str) -> str:
    """Diagnose experimental issues using scientific reasoning.
    Context from current experiment is automatically included.
    
    Args:
        problem: Description of the problem
    """
    try:
        # Use LLM for diagnosis
        llm = get_llm_instance()
        
        # Get project-wide insights automatically
        insights = ""
        try:
            insights = await get_project_insights.ainvoke({})
            insights = f"\n\nRelevant patterns from other experiments:\n{insights}\n"
        except:
            pass
        
        prompt = f"""Problem reported: {problem}
{insights}
Based on scientific knowledge and any relevant patterns, diagnose the likely causes and suggest solutions.
Focus on practical, actionable advice. Reason from first principles."""
        
        response = llm.invoke([HumanMessage(content=prompt)])
        diagnosis = response.content
        
        return diagnosis
        
    except Exception as e:
        logger.error(f"Error diagnosing issue: {e}")
        return f"Error diagnosing issue: {str(e)}"


@tool
async def suggest_optimization(aspect: str) -> str:
    """Suggest optimizations based on successful patterns.
    Automatically uses context from current experiment and project insights.
    
    Args:
        aspect: What to optimize (e.g., "PCR conditions", "yield", "purity")
    """
    try:
        # Get project insights automatically
        insights = await get_project_insights.ainvoke({})
        
        # Use LLM to suggest optimizations
        llm = get_llm_instance()
        prompt = f"""Optimization requested for: {aspect}

Based on successful experiments and patterns:
{insights}

Suggest 3-5 specific optimizations that have worked well in similar cases.
Be specific with parameters and conditions."""
        
        response = llm.invoke([HumanMessage(content=prompt)])
        suggestions = response.content
        
        return suggestions
        
    except Exception as e:
        logger.error(f"Error suggesting optimizations: {e}")
        return f"Error suggesting optimizations: {str(e)}"


@tool
async def run_deep_research(query: str) -> str:
    """Search scientific literature and web for relevant information.
    
    Args:
        query: Research query
    """
    try:
        from src.tools.deep_research import run_deep_research as deep_research
        result = await deep_research(query, max_loops=1)
        return f"Research Results:\n{result}"
    except Exception as e:
        return f"Research unavailable: {str(e)}"


@tool
async def create_new_experiment(name: str, motivation: str, key_question: str) -> str:
    """Create a new experiment with initial README memory.
    
    Args:
        name: Experiment name
        motivation: Why this experiment
        key_question: Main research question
    """
    try:
        result = await create_experiment.ainvoke({
            "experiment_name": name,
            "motivation": motivation,
            "key_question": key_question
        })
        return result
    except Exception as e:
        return f"Error creating experiment: {str(e)}"


# ============= Create Agent (without explicit memory tools!) =============

def create_memory_agent():
    """Create a React agent without explicit memory tools."""
    
    # Get LLM configuration
    from src.components.llm import AGENT_MODEL_ASSIGNMENTS
    model_name = AGENT_MODEL_ASSIGNMENTS.get("react_agent", 
                                              AGENT_MODEL_ASSIGNMENTS.get("default"))
    
    llm = get_llm_instance(model_name)
    logger.info(f"React agent using model: {model_name}")
    
    # Only functional tools, no memory management tools!
    tools = [
        scan_project,
        list_folder_contents,
        analyze_data,
        diagnose_issue,
        suggest_optimization,
        run_deep_research,
        create_new_experiment
    ]
    
    # Create agent
    agent = create_react_agent(llm, tools)
    
    return agent


# ============= Message Handler with Automatic Memory =============

async def handle_message(
    message: str, 
    session_id: str = "default",
    current_folder: Optional[str] = None,
    selected_files: Optional[List[str]] = None
) -> str:
    """Handle a user message with automatic memory management."""
    
    try:
        # AUTOMATIC CONTEXT INJECTION
        context_parts = []
        
        # 1. Load experiment context automatically if in experiment folder
        if current_folder and current_folder.startswith("exp_"):
            try:
                # Read README automatically (not as a tool!)
                readme_content = await read_memory.ainvoke({
                    "experiment_id": current_folder
                })
                
                # Extract key information
                if "Overview" in readme_content:
                    context_parts.append(f"Current Experiment Context:\n{readme_content[:1000]}")
            except:
                pass
        
        # 2. Add context about current folder and files
        # NO PATTERN MATCHING - just provide context, let LLM understand
        if current_folder:
            context_parts.append(f"User is currently in folder: {current_folder}")
        
        if selected_files:
            # Build full paths for clarity
            if current_folder:
                file_paths = [f"{current_folder}/{f}" for f in selected_files]
            else:
                file_paths = selected_files
            context_parts.append(f"User has selected these files: {', '.join(file_paths)}")
        
        # 3. Build final message with automatic context and instructions
        system_hint = ""
        if current_folder and selected_files:
            system_hint = f"\n\n[System: User is looking at folder '{current_folder}' with files {selected_files} selected. When they say 'this folder' or 'this file', use list_folder_contents for folders and analyze_data for files.]"
        elif current_folder:
            system_hint = f"\n\n[System: User is looking at folder '{current_folder}'. When they ask about 'this folder', use list_folder_contents tool with folder_path='{current_folder}'.]"
        elif selected_files:
            system_hint = f"\n\n[System: User has selected files {selected_files}. When they ask about 'this file', use analyze_data tool.]"
        
        if context_parts:
            enriched_message = message + "\n\n" + "\n".join(context_parts) + system_hint
        else:
            enriched_message = message
        
        # Create agent
        agent = create_memory_agent()
        
        # Process message with higher recursion limit - USE ASYNC!
        result = await agent.ainvoke(
            {"messages": [HumanMessage(content=enriched_message)]},
            config={"recursion_limit": 50}  # Increase from default 25
        )
        
        # Extract response and log tool calls
        if result and "messages" in result:
            # Log tool interactions for debugging
            tool_calls_made = []
            for msg in result["messages"]:
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    for tool_call in msg.tool_calls:
                        tool_name = tool_call.get('name', tool_call.get('function', {}).get('name', 'unknown'))
                        tool_args = tool_call.get('arguments', tool_call.get('function', {}).get('arguments', '{}'))
                        tool_calls_made.append(f"{tool_name}({tool_args})")
                        logger.debug(f"Tool call: {tool_name} with args: {tool_args}")
            
            # Get the final response
            for msg in reversed(result["messages"]):
                if isinstance(msg, AIMessage):
                    response = msg.content
                    
                    # AUTOMATIC MEMORY EXTRACTION AND UPDATE
                    if current_folder and current_folder.startswith("exp_"):
                        # Use the smart memory updater to extract and apply updates
                        from src.memory.auto_memory_updater import auto_update_memory
                        
                        async def update_memory_from_conversation():
                            try:
                                result = await auto_update_memory(
                                    user_message=message,
                                    agent_response=response,
                                    experiment_id=current_folder
                                )
                                logger.info(f"Memory update result: {result}")
                            except Exception as e:
                                logger.error(f"Failed to auto-update memory: {e}")
                        
                        # Fire and forget - don't wait
                        asyncio.create_task(update_memory_from_conversation())
                    
                    # Enhanced conversation logging with tool calls
                    try:
                        if tool_calls_made:
                            logger.info(f"Tools used: {', '.join(tool_calls_made)}")
                        log_conversation(message, response, session_id)
                    except:
                        pass  # Don't fail if logging fails
                    
                    return response
        
        return "No response generated."
        
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        error_msg = f"Error: {str(e)}"
        
        # Log error conversation
        try:
            log_conversation(message, error_msg, session_id)
        except:
            pass
        
        return error_msg


# ============= Test Function =============

async def test():
    """Test the React agent with automatic memory."""
    
    print("Testing LabAcc Copilot React Agent (Automatic Memory)...")
    print("=" * 50)
    
    # Test queries
    queries = [
        ("Scan my experiments", None, None),
        ("Analyze data.csv", "exp_001_pcr", ["data.csv"]),
        ("What's wrong with my PCR?", "exp_001_pcr", None),
        ("How can I improve yield?", "exp_001_pcr", None),
    ]
    
    for q, folder, files in queries:
        print(f"\nQ: {q}")
        if folder:
            print(f"   (in folder: {folder})")
        response = await handle_message(q, current_folder=folder, selected_files=files)
        print(f"A: {response[:300]}...")
    
    print("\n" + "=" * 50)
    print("Memory updates happened automatically in background!")
    print("Check README files to see automatic updates.")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test())