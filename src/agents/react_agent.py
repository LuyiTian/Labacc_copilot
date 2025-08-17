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
from datetime import datetime
import asyncio
import logging
import aiohttp
import json

from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from src.components.llm import get_llm_instance
from src.components.file_analyzer import QuickFileAnalyzer

# Setup logger early
logger = logging.getLogger(__name__)

# Import memory functions
from src.memory.memory_tools import (
    read_memory,
    append_insight,
    scan_project,
    get_experiment_summary,
    update_file_registry,
    get_project_insights,
    create_experiment
)

# Import session management for bulletproof path resolution
from src.projects.session import get_current_session, require_session

# Setup logging configuration
try:
    from src.config.logging_config import setup_logging, log_conversation
    setup_logging()
except ImportError:
    # Fallback if logging config not available
    pass

# ============= Tool Call Notification System =============

async def notify_tool_call(session_id: str, tool_name: str, status: str, args: dict = None):
    """Send tool call notification to WebSocket via HTTP endpoint"""
    try:
        async with aiohttp.ClientSession() as session:
            url = "http://localhost:8002/api/tool-update"
            data = {
                "session_id": session_id,
                "tool_name": tool_name,
                "status": status,
                "args": args or {}
            }
            async with session.post(url, json=data) as response:
                if response.status != 200:
                    logger.warning(f"Failed to send tool update: {response.status}")
    except Exception as e:
        logger.debug(f"Could not send tool update: {e}")
        # Don't fail if notification fails - it's not critical

# ============= Analysis Tools (with automatic memory updates) =============

@tool
async def analyze_image(image_path: str, experiment_context: str = "") -> str:
    """Analyze an experimental image using vision AI to understand its content.
    
    Use this tool when users ask about images or when you need to understand
    visual data like plots, microscopy images, gel electrophoresis, etc.
    
    Args:
        image_path: Path to the image file relative to project root
        experiment_context: Optional context about the experiment
    
    Returns:
        Detailed analysis of the image content and scientific relevance
    """
    try:
        # Get current session for path resolution
        session = require_session()
        full_path = session.resolve_path(image_path)
        
        if not full_path.exists():
            return f"Image not found: {image_path}"
        
        # Check if it's an image file
        image_extensions = {'.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp', '.gif', '.webp'}
        if full_path.suffix.lower() not in image_extensions:
            return f"Not an image file: {image_path} (supported: {', '.join(image_extensions)})"
        
        # Use the image analyzer
        from src.components.image_analyzer import analyze_lab_image
        
        # Extract experiment ID from path if possible
        experiment_id = None
        path_parts = Path(image_path).parts
        for part in path_parts:
            if part.startswith("exp_"):
                experiment_id = part
                break
        
        # Analyze the image
        result = await analyze_lab_image(
            image_path=str(full_path),
            context=experiment_context,
            experiment_id=experiment_id
        )
        
        if not result.success:
            return f"Failed to analyze image: {result.error_message}"
        
        # Format the response
        response = f"""Image Analysis for {result.file_name}:

**Content**: {result.content_description}

**Experimental Relevance**: {result.experimental_context if result.experimental_context else 'General laboratory image'}

**Image Details**:
- Size: {result.image_size[0]}×{result.image_size[1]} pixels
- Format: {result.format}
"""
        
        if result.key_features:
            response += "\n**Key Observations**:\n"
            for feature in result.key_features:
                response += f"- {feature}\n"
        
        if result.suggested_tags:
            response += f"\n**Tags**: {', '.join(result.suggested_tags)}"
        
        return response
        
    except RuntimeError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        logger.error(f"Error analyzing image: {e}")
        return f"Error analyzing image: {str(e)}"

@tool
async def scan_project() -> str:
    """Scan the entire project to get an overview of all experiments, folders, and main data.
    
    Use this tool first when user asks about the project structure or wants a general overview.
    Returns a comprehensive summary of the project contents and organization.
    """
    try:
        # Get current session - bulletproof path resolution!
        session = require_session()
        project_path = session.project_path
        
        if not project_path.exists():
            return f"Project folder not found: {session.selected_project}"
        
        # Find all experiment folders and other directories
        experiments = []
        other_folders = []
        
        for item in sorted(project_path.rglob("*")):
            if item.is_dir():
                relative_path = item.relative_to(project_path)
                if item.name.startswith("exp_"):
                    # Try to read status from README
                    status = "No README"
                    try:
                        readme_path = item / "README.md"
                        if readme_path.exists():
                            with open(readme_path, 'r') as f:
                                first_lines = f.read(500)
                                status = "Active" if "Active" in first_lines else "Has README"
                    except:
                        pass
                    experiments.append(f"📂 {relative_path}: {status}")
                elif len(relative_path.parts) == 1:  # Top-level folders only
                    file_count = len(list(item.iterdir())) if item.exists() else 0
                    other_folders.append(f"📁 {relative_path}/ ({file_count} items)")
        
        result = f"=== PROJECT: {session.selected_project} ===\n"
        result += f"Permission: {session.permission}\n\n"
        
        if other_folders:
            result += "Main folders:\n" + "\n".join(other_folders[:10]) + "\n\n"
        
        if experiments:
            result += f"Experiments ({len(experiments)} found):\n" + "\n".join(experiments[:15])
            if len(experiments) > 15:
                result += f"\n... and {len(experiments) - 15} more experiments"
        else:
            result += "No experiment folders found (folders starting with 'exp_')"
        
        return result
        
    except RuntimeError as e:
        return f"Error: {str(e)}"


@tool  
async def list_folder_contents(folder_path: str = ".") -> str:
    """List files and subfolders in a specified folder within the current project.
    
    Use this to explore directory contents and find specific files or experiments.
    
    Args:
        folder_path: Path relative to project root (e.g., 'experiments' or 'experiments/exp_001').
                    Use "." for project root directory.
    """
    try:
        # Bulletproof session-based path resolution - NO MORE CHAOS!
        session = require_session()
        full_path = session.resolve_path(folder_path)
        
        if not full_path.exists():
            return f"Folder not found: {folder_path}"
        
        if not full_path.is_dir():
            return f"Not a folder: {folder_path}"
        
        # List contents
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
        
    except RuntimeError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        logger.error(f"Error listing folder: {e}")
        return f"Error listing folder: {str(e)}"


@tool
async def read_file(file_path: str) -> str:
    """Read file contents within current project.
    Automatically uses converted version if available.
    
    Args:
        file_path: Path to file relative to project root (e.g., 'experiments/exp_001/README.md')
    
    Returns:
        File contents as string
    """
    try:
        # Bulletproof session-based path resolution!
        session = require_session()
        full_path = session.resolve_path(file_path)
        
        # Smart check for converted markdown files
        # If user asks for a PDF in originals/, check if .md exists in experiment root
        if full_path.suffix.lower() == '.pdf' and 'originals' in str(full_path):
            # Look for converted .md file in experiment root
            path_parts = Path(file_path).parts
            if len(path_parts) >= 1 and path_parts[0].startswith('exp_'):
                experiment_id = path_parts[0]
                exp_root = session.resolve_path(experiment_id)
                md_path = exp_root / f"{full_path.stem}.md"
                
                if md_path.exists():
                    logger.info(f"Found converted markdown: {md_path}")
                    with open(md_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    return f"# {full_path.name} (Converted to Markdown)\n\n{content}"
        
        # Fall back to original file
        if not full_path.exists():
            return f"File not found: {file_path}"
        
        if not full_path.is_file():
            return f"Not a file: {file_path}"
        
        # Check if it's a binary file
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return f"# Content of {full_path.name}\n\n{content}"
        except UnicodeDecodeError:
            # Binary file - check if conversion failed
            return f"Binary file: {full_path.name} ({full_path.stat().st_size} bytes)\nNote: File conversion may have failed. Try re-uploading or use analyze_data tool."
        
    except RuntimeError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        return f"Error reading file: {str(e)}"


@tool
async def analyze_data(file_path: str) -> str:
    """Analyze experimental data file within current project.
    
    Args:
        file_path: Path to the data file relative to project root
    """
    try:
        # Bulletproof session-based path resolution!
        session = require_session()
        full_path = session.resolve_path(file_path)
        
        if not full_path.exists():
            return f"File not found: {file_path}"
        
        # Use file analyzer
        llm = get_llm_instance()
        analyzer = QuickFileAnalyzer(llm)
        
        # Analyze file
        analysis = await analyzer.analyze_file(str(full_path))
        
        # TODO: Context-aware summarizer needs to be adapted for new project structure
        # For now, use basic analysis
        
        result = f"File Analysis for {analysis.file_name}:\n"
        result += f"- Type: {analysis.file_type}\n"
        result += f"- Size: {analysis.size_bytes} bytes\n"
        result += f"- Summary: {analysis.content_summary}\n"
        result += f"- Project: {session.selected_project}\n"
        
        if analysis.data_points:
            result += f"- Data points: {analysis.data_points}\n"
        
        logger.debug(f"Analyzed file: {analysis.file_name} in project {session.selected_project}")
        
        return result
        
    except RuntimeError as e:
        return f"Error: {str(e)}"
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
    
    # Initialize memory tools with LLM
    from src.memory.memory_tools import init_memory_tools
    # Get project root from session if available
    try:
        session = get_current_session()
        project_root = session.get_project_root() if session else "data/alice_projects"
    except:
        project_root = "data/alice_projects"
    
    init_memory_tools(project_root=project_root, llm=llm)
    logger.info(f"Initialized memory tools for {project_root}")
    
    # Use original tools without wrapping to avoid async/sync issues
    tools = [
        scan_project,
        list_folder_contents,
        read_file,
        analyze_data,
        analyze_image,  # Vision AI for images
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
    current_folder: Optional[str] = None,  # Deprecated - kept for compatibility
    selected_files: Optional[List[str]] = None  # Deprecated - kept for compatibility
) -> str:
    """Handle a user message with session-based project context."""
    
    try:
        # Get session context - this is the single source of truth!
        session = get_current_session()
        
        if not session:
            return "Error: No project selected. Please select a project first."
        
        # Session-based context injection - much simpler!
        context_parts = []
        
        # Add project context
        context_parts.append(f"Working in project: {session.selected_project}")
        
        # Add recent uploads context if any
        if hasattr(session, 'recent_uploads') and session.recent_uploads:
            context_parts.append("\n=== Recently Uploaded Files ===")
            for upload in session.recent_uploads[-3:]:  # Show last 3 uploads
                context_parts.append(f"• {upload['file']} in {upload['experiment']} ({upload['timestamp'][:10]})")
                if upload.get('converted'):
                    context_parts.append(f"  (Converted to Markdown for analysis)")
        
        # TODO: Load experiment-specific context if needed
        # This will need to be adapted for the new project structure
        
        # Build enriched message with README context and explicit tool guidance
        readme_context = ""
        try:
            readme_path = session.resolve_path("README.md")
            if readme_path.exists():
                with open(readme_path, 'r', encoding='utf-8') as f:
                    readme_content = f.read()
                    readme_context = f"\n\n[PROJECT README CONTEXT]\n{readme_content}\n"
        except Exception as e:
            logger.debug(f"Could not load README.md: {e}")
        
        system_hint = f"""

[SYSTEM CONTEXT]
You are working within project: {session.selected_project}
All file paths are relative to the project root.{readme_context}
"""
        
        if context_parts:
            enriched_message = message + "\n\n" + "\n".join(context_parts) + system_hint
        else:
            enriched_message = message
        
        # Create agent
        agent = create_memory_agent()
        
        # Track tool calls and response
        tool_calls_made = []
        unique_tools = set()
        final_response = ""
        all_messages = []
        last_ai_message = None
        
        # Stream events for real-time tool visibility
        async for event in agent.astream_events(
            {"messages": [HumanMessage(content=enriched_message)]},
            config={"recursion_limit": 50},
            version="v1"  # Try v1 for better compatibility
        ):
            event_type = event.get("event", "")
            
            # Handle tool start events
            if event_type == "on_tool_start":
                tool_name = event.get("name", "unknown")
                tool_input = event.get("data", {}).get("input", {})
                
                # Send "starting" notification immediately
                logger.info(f"Tool {tool_name} starting execution for session {session_id}")
                await notify_tool_call(session_id, tool_name, "starting", tool_input)
                
                # Track for logging
                if tool_name not in unique_tools:
                    unique_tools.add(tool_name)
                    if isinstance(tool_input, dict):
                        args_str = ', '.join(f"{k}={v}" for k, v in tool_input.items())
                    else:
                        args_str = str(tool_input)
                    tool_calls_made.append(f"{tool_name}({args_str})")
            
            # Handle tool end events
            elif event_type == "on_tool_end":
                tool_name = event.get("name", "unknown")
                logger.info(f"Tool {tool_name} completed for session {session_id}")
                await notify_tool_call(session_id, tool_name, "completed", {})
            
            # Handle chat model events - this is where the actual response comes from
            elif event_type == "on_chat_model_end":
                # Extract the AI message from chat model output
                output = event.get("data", {}).get("output", None)
                if output:
                    # The output could be a message directly
                    if isinstance(output, AIMessage):
                        last_ai_message = output
                        if output.content:
                            final_response = output.content
                            logger.debug(f"Got AI response from chat model: {len(final_response)} chars")
                    # Or it could be in a different format
                    elif hasattr(output, "content"):
                        final_response = output.content
                        logger.debug(f"Got content from output: {len(final_response)} chars")
            
            # Handle chain events
            elif event_type == "on_chain_end":
                # Try to extract final result from chain output
                output = event.get("data", {}).get("output", {})
                if isinstance(output, dict) and "messages" in output:
                    all_messages = output["messages"]
                    # Get the last AI message
                    for msg in reversed(all_messages):
                        if isinstance(msg, AIMessage) and msg.content:
                            # Use this as response if we don't have one yet or if it's longer
                            if not final_response or len(msg.content) > len(final_response):
                                final_response = msg.content
                                logger.debug(f"Got response from chain end: {len(final_response)} chars")
                            break
        
        # Use the final response
        response = final_response
        
        # Check if response is empty or truncated
        if not response or response.strip() in ["", "...", "…"]:
            logger.warning("Empty or truncated response from agent")
            # Try to find a previous non-empty response from all_messages
            for prev_msg in reversed(all_messages[:-1] if all_messages else []):
                if isinstance(prev_msg, AIMessage) and prev_msg.content:
                    response = prev_msg.content
                    break
            else:
                # If still no response, provide a helpful error message
                if tool_calls_made:
                    response = f"I encountered an issue processing your request. The tools were called but didn't return expected results. Tool calls attempted: {', '.join(tool_calls_made[:3])}. Please try rephrasing your question or check if the files/folders exist."
                else:
                    response = "I encountered an issue processing your request. Please try rephrasing your question."
        
        # Check if user is responding to file upload questions and update memory
        if session and hasattr(session, 'pending_questions') and session.pending_questions:
            # Check if the user's message seems to be providing context about uploaded files
            # This is more flexible than assuming only the next message is relevant
            message_lower = message.lower()
            is_providing_context = any([
                # User is explaining something
                any(word in message_lower for word in ['是', 'is', 'was', 'are', 'for', '用于', '用来', '为了']),
                # User is answering a what/why/how question
                any(word in message_lower for word in ['because', '因为', 'since', '由于']),
                # Message is longer than typical commands (likely explanatory)
                len(message) > 50
            ])
            
            if is_providing_context:
                # Process ALL pending questions since user might be providing batch context
                for exp_id, question_info in list(session.pending_questions.items()):
                    if question_info.get('asked'):
                        logger.info(f"Capturing user context for {question_info['file']} in {exp_id}")
                        
                        # Prepare comprehensive memory update
                        memory_update = f"""
## File Upload: {question_info['file']} ({datetime.now().strftime('%Y-%m-%d %H:%M')})

### Uploaded File (Actual Information Only)
- **Name:** {question_info['file']}
- **Location:** {question_info.get('path', 'N/A')}
- **Experiment:** {exp_id}

### File Analysis
{question_info.get('initial_analysis', 'No initial analysis available')}

### User-Provided Context
{message}

### Discussion
{response[:500] if response else 'No response captured'}

Note: All information above is based on actual file content and user-provided context only.
---
"""
                        
                        # Update experiment README
                        try:
                            from src.memory.memory_tools import update_experiment_readme
                            
                            # Ensure we're updating the correct experiment
                            update_result = await update_experiment_readme.ainvoke({
                                "experiment_id": exp_id,
                                "updates": memory_update
                            })
                            logger.info(f"✅ Memory successfully updated for {exp_id}: {update_result[:100]}")
                            
                            # Mark as processed but keep for reference (don't delete immediately)
                            session.pending_questions[exp_id]['processed'] = True
                            session.pending_questions[exp_id]['processed_at'] = datetime.now().isoformat()
                            
                        except Exception as e:
                            logger.error(f"❌ Failed to update memory for {exp_id}: {e}")
                            import traceback
                            traceback.print_exc()
                
                # Clean up old processed questions (older than 1 hour)
                now = datetime.now()
                for exp_id in list(session.pending_questions.keys()):
                    q_info = session.pending_questions[exp_id]
                    if q_info.get('processed'):
                        processed_time = datetime.fromisoformat(q_info.get('processed_at', now.isoformat()))
                        if (now - processed_time).seconds > 3600:  # 1 hour
                            del session.pending_questions[exp_id]
                            logger.info(f"Cleaned up old processed question for {exp_id}")
        
        # Enhanced conversation logging with tool calls
        try:
            if tool_calls_made:
                logger.info(f"Tools used: {', '.join(tool_calls_made)}")
            log_conversation(message, response, session_id)
        except:
            pass  # Don't fail if logging fails
        
        # Debug log
        logger.info(f"[Session: {session_id}]")
        logger.info(f"User: {message[:100]}...")
        logger.info(f"Agent: {response[:200]}...")
        
        return response
        
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        error_msg = f"Error: {str(e)}"
        
        # Log error conversation
        try:
            log_conversation(message, error_msg, session_id)
        except:
            pass
        
        return error_msg


async def handle_message_with_trajectory(
    message: str, 
    session_id: str = "default",
    current_folder: Optional[str] = None,
    selected_files: Optional[List[str]] = None
) -> tuple[str, list]:
    """
    Handle a user message and return both response and execution trajectory.
    
    This is an enhanced version of handle_message that captures the full
    execution trajectory for evaluation purposes.
    
    Returns:
        tuple: (response_string, execution_messages_list)
    """
    
    try:
        # AUTOMATIC CONTEXT INJECTION (same as handle_message)
        context_parts = []
        
        # 1. Load experiment context automatically if in experiment folder
        if current_folder and current_folder.startswith("exp_"):
            try:
                # Read README automatically (not as a tool!)
                readme_content = await read_memory.ainvoke({
                    "experiment_id": current_folder
                })
                
                # Just dump the full README content - no parsing needed
                rich_context = f"""
=== FULL README CONTENT FOR {current_folder.upper()} ===
This is the complete README.md content from folder {current_folder}:
{readme_content}
=== END OF README CONTENT ===
"""
                context_parts.append(rich_context)
            except:
                pass
        
        # 2. Add context about current folder and files
        if current_folder:
            context_parts.append(f"User is currently in folder: {current_folder}")
        
        if selected_files:
            # Build full paths for clarity
            if current_folder:
                file_paths = [f"{current_folder}/{f}" for f in selected_files]
            else:
                file_paths = selected_files
            context_parts.append(f"User has selected these files: {', '.join(file_paths)}")
        
        # 3. Build final message with smart instructions based on available context
        system_hint = ""
        if current_folder and current_folder.startswith("exp_") and context_parts and "CURRENT EXPERIMENT CONTEXT" in str(context_parts):
            system_hint = f"""
[SYSTEM INSTRUCTIONS]
The complete README.md content for {current_folder} is provided above. DO NOT call any tools to read it again:
- DO NOT use analyze_data to read README.md - the full content is already in this prompt
- DO NOT use list_folder_contents to check folder contents - you have the README information
- The README contains all experiment details: overview, methods, results, issues, next steps
- Answer questions directly from the README content provided above
- Only call tools if you need information NOT in the README above
Current folder: {current_folder}
Selected files: {selected_files if selected_files else 'None'}
"""
        elif current_folder and selected_files:
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
        
        # Track tool calls, response, and execution messages
        tool_calls_made = []
        unique_tools = set()
        final_response = ""
        all_messages = []
        last_ai_message = None
        execution_trajectory = []  # This will store the full trajectory
        
        # Import message types for trajectory
        from langchain_core.messages import ToolMessage, FunctionMessage, SystemMessage
        
        # Add initial human message to trajectory
        initial_human_msg = HumanMessage(content=enriched_message)
        execution_trajectory.append(initial_human_msg)
        
        # Stream events for real-time tool visibility and trajectory capture
        async for event in agent.astream_events(
            {"messages": [initial_human_msg]},
            config={"recursion_limit": 50},
            version="v1"
        ):
            event_type = event.get("event", "")
            
            # Capture messages from events for trajectory
            if "messages" in event.get("data", {}):
                event_messages = event["data"]["messages"]
                if isinstance(event_messages, list):
                    for msg in event_messages:
                        if msg not in execution_trajectory:  # Avoid duplicates
                            execution_trajectory.append(msg)
            
            # Handle tool start events
            if event_type == "on_tool_start":
                tool_name = event.get("name", "unknown")
                tool_input = event.get("data", {}).get("input", {})
                
                # Send "starting" notification immediately
                logger.info(f"Tool {tool_name} starting execution for session {session_id}")
                await notify_tool_call(session_id, tool_name, "starting", tool_input)
                
                # Track for logging
                if tool_name not in unique_tools:
                    unique_tools.add(tool_name)
                    if isinstance(tool_input, dict):
                        args_str = ', '.join(f"{k}={v}" for k, v in tool_input.items())
                    else:
                        args_str = str(tool_input)
                    tool_calls_made.append(f"{tool_name}({args_str})")
            
            # Handle tool end events
            elif event_type == "on_tool_end":
                tool_name = event.get("name", "unknown")
                tool_output = event.get("data", {}).get("output", "")
                
                logger.info(f"Tool {tool_name} completed for session {session_id}")
                await notify_tool_call(session_id, tool_name, "completed", {})
                
                # Create a ToolMessage for trajectory
                tool_msg = ToolMessage(
                    content=str(tool_output),
                    tool_call_id=f"{tool_name}_{len(execution_trajectory)}",
                    name=tool_name
                )
                execution_trajectory.append(tool_msg)
            
            # Handle chat model events
            elif event_type == "on_chat_model_end":
                output = event.get("data", {}).get("output", {})
                if output:
                    # Store all messages from this event
                    if hasattr(output, "generations"):
                        for gen in output.generations:
                            if hasattr(gen, "message"):
                                all_messages.append(gen.message)
                                if isinstance(gen.message, AIMessage):
                                    execution_trajectory.append(gen.message)
                                    last_ai_message = gen.message
                                    if gen.message.content:
                                        final_response = gen.message.content
                    elif isinstance(output, AIMessage):
                        all_messages.append(output)
                        execution_trajectory.append(output)
                        last_ai_message = output
                        if output.content:
                            final_response = output.content
                    elif hasattr(output, "content"):
                        final_response = output.content
            
            # Handle chain events
            elif event_type == "on_chain_end":
                output = event.get("data", {}).get("output", {})
                if isinstance(output, dict) and "messages" in output:
                    chain_messages = output["messages"]
                    all_messages = chain_messages
                    # Add any new messages to trajectory
                    for msg in chain_messages:
                        if msg not in execution_trajectory:
                            execution_trajectory.append(msg)
                    # Get the last AI message
                    for msg in reversed(chain_messages):
                        if isinstance(msg, AIMessage) and msg.content:
                            if not final_response or len(msg.content) > len(final_response):
                                final_response = msg.content
                            break
        
        # Use the final response
        response = final_response
        
        # Check if response is empty or truncated
        if not response or response.strip() in ["", "...", "…"]:
            logger.warning("Empty or truncated response from agent")
            # Try to find a previous non-empty response from execution_trajectory
            for prev_msg in reversed(execution_trajectory):
                if isinstance(prev_msg, AIMessage) and prev_msg.content:
                    response = prev_msg.content
                    break
            else:
                # If still no response, provide a helpful error message
                if tool_calls_made:
                    response = f"I encountered an issue processing your request. The tools were called but didn't return expected results. Tool calls attempted: {', '.join(tool_calls_made[:3])}. Please try rephrasing your question or check if the files/folders exist."
                else:
                    response = "I encountered an issue processing your request. Please try rephrasing your question."
        
        # Background memory update (same as handle_message)
        if current_folder and current_folder.startswith("exp_"):
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
            
            asyncio.create_task(update_memory_from_conversation())
            logger.debug(f"Triggered background memory analysis")
        
        # Enhanced conversation logging with tool calls
        try:
            if tool_calls_made:
                logger.info(f"Tools used: {', '.join(tool_calls_made)}")
            log_conversation(message, response, session_id)
        except:
            pass
        
        # Debug log
        logger.info(f"[Session: {session_id}]")
        logger.info(f"User: {message[:100]}...")
        logger.info(f"Agent: {response[:200]}...")
        logger.info(f"Trajectory: {len(execution_trajectory)} messages captured")
        
        return response, execution_trajectory
        
    except Exception as e:
        logger.error(f"Error handling message with trajectory: {e}")
        error_msg = f"Error: {str(e)}"
        
        # Return error with minimal trajectory
        error_trajectory = [
            HumanMessage(content=message),
            AIMessage(content=error_msg)
        ]
        
        try:
            log_conversation(message, error_msg, session_id)
        except:
            pass
        
        return error_msg, error_trajectory


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