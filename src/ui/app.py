from __future__ import annotations

import os
from datetime import datetime
from typing import Optional, Tuple

import chainlit as cl
from langchain_core.messages import HumanMessage
from src.graph.app import build_graph
from src.graph.state import GraphState
from src.tools.files import (
    list_dir as list_dir_safe,
    read_file as read_file_safe,
    write_file as write_file_safe,
    delete_path as delete_path_safe,
    move_path as move_path_safe,
)
from src.ui.file_manager import render_file_manager, handle_file_action
from src.components.file_intent_parser import FileIntentParser, FileIntent
from src.components.smart_folder_manager import SmartFolderManager
from datetime import datetime
from src.components.file_analyzer import QuickFileAnalyzer
from src.components.llm import get_llm_instance
import re
import shutil


APP = build_graph()

# Cache LLM instance for performance
_cached_parser_llm = None

def get_parser_llm():
    """Get cached LLM instance for parsing (using smaller model for speed)"""
    global _cached_parser_llm
    if _cached_parser_llm is None:
        _cached_parser_llm = get_llm_instance("siliconflow-qwen-8b")  # Use 8B model for 30x faster parsing
    return _cached_parser_llm


def _get_username() -> str:
    # Chainlit deployments behind reverse proxy can pass REMOTE_USER
    return os.environ.get("REMOTE_USER") or os.environ.get("USER") or "anonymous"


@cl.on_chat_start
async def on_chat_start():
    username = _get_username()
    session_id = cl.user_session.get("id")
    thread_id = f"{username}:{session_id}"
    cl.user_session.set("thread_id", thread_id)
    
    # Get project root
    project_root = os.environ.get("LABACC_PROJECT_ROOT", os.getcwd())
    cl.user_session.set("project_root", project_root)
    
    # Initialize current browsing folder as None
    cl.user_session.set("current_folder", None)
    
    # Render file manager actions
    file_actions = await render_file_manager(project_root)
    await cl.Message(
        content=f"Welcome to LabAcc Copilot!\n🔬 Project: {os.path.basename(project_root)}",
        actions=file_actions
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    thread_id: str = cl.user_session.get("thread_id")
    project_root: Optional[str] = os.environ.get("LABACC_PROJECT_ROOT", os.getcwd())

    attachments = []
    attachment_names = {}  # Map UUID path to original name
    for elem in message.elements or []:
        if hasattr(elem, "path") and elem.path:
            attachments.append(elem.path)
            # Store original filename - try multiple attributes
            if hasattr(elem, "name") and elem.name:
                attachment_names[elem.path] = elem.name
            elif hasattr(elem, "display") and elem.display:
                attachment_names[elem.path] = elem.display
            elif hasattr(elem, "content") and isinstance(elem.content, str):
                # Sometimes the filename is in content
                attachment_names[elem.path] = elem.content

    content = (message.content or "").strip()
    
    # Check for natural language file management requests
    if attachments and content and not content.startswith("/"):
        # Use simple pattern matching for common cases (fast)
        is_file_request = any(keyword in content.lower() for keyword in [
            'save', 'upload', 'store', 'put', 'file', 'folder', 
            '保存', '上传', '文件夹'  # Chinese keywords
        ])
        
        if is_file_request:
            # Get current folder context
            current_folder = cl.user_session.get("current_folder")
            print(f"DEBUG: Retrieved current_folder from session: {current_folder}")
            
            # Handle files AND pass to agents for additional instructions
            await _handle_natural_language_files(message, content, attachments, project_root, current_folder, attachment_names, thread_id)
            return
    
    # Slash commands for simple file management
    if content.startswith("/"):
        reply = await _handle_command(content, project_root, attachments)
        await cl.Message(content=reply).send()
        return

    # Default: pass to LangGraph agent system
    state: GraphState = {
        "messages": [HumanMessage(content=message.content)],
        "project_root": project_root,
        "attachments": attachments,
    }
    result = await cl.make_async(APP.invoke)(state, config={"configurable": {"thread_id": thread_id}})
    await cl.Message(content=result.get("response", "(no response)"), author="Analyst").send()


async def _handle_natural_language_files(
    message: cl.Message,
    content: str,
    attachments: list[str],
    project_root: str,
    current_folder: Optional[str] = None,
    attachment_names: dict = None,
    thread_id: str = None
) -> None:
    """Handle AI-powered natural language file management requests"""
    if attachment_names is None:
        attachment_names = {}
    try:
        # Initialize components with cached LLM for performance
        llm = get_parser_llm()  # Use cached 8B model
        parser = FileIntentParser(llm)
        folder_manager = SmartFolderManager(project_root)
        analyzer = QuickFileAnalyzer(llm)
        
        # Show processing message
        processing_msg = await cl.Message(content="🤖 Processing your request...").send()
        
        # Simple approach: Default to current folder if browsing, otherwise create new
        if current_folder:
            # User is browsing a folder - use it by default
            folder_suggestion = "current_folder"
            print(f"Using current browsing folder: {current_folder}")
        else:
            # No folder context - create a new one with sensible defaults
            folder_suggestion = f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            print(f"No current folder, creating new: {folder_suggestion}")
        
        # Create simple intent (skip complex LLM parsing for now)
        intent = FileIntent(
            operation_type="save",
            experiment_type=None,
            date_context=datetime.now().strftime("%Y-%m-%d"),
            folder_suggestion=folder_suggestion,
            analysis_request=False,
            files_description=content,
            confidence_score=1.0,
            raw_message=content,
            detected_language="auto"
        )
        
        # Create smart folder  
        folder_name, folder_path = await folder_manager.create_experiment_folder(intent, True, current_folder)
        print(f"Using folder: {folder_name}")
        
        # Save files to the folder
        saved_files = []
        for attachment in attachments:
            # Use original filename if available, otherwise use UUID name
            original_name = attachment_names.get(attachment)
            if original_name:
                file_name = original_name
                print(f"Using original filename: {file_name}")
            else:
                file_name = os.path.basename(attachment)
                print(f"No original name found, using: {file_name}")
            
            # Handle filename conflicts
            dest_path = os.path.join(folder_path, file_name)
            if os.path.exists(dest_path):
                # Add timestamp to make it unique
                name_parts = file_name.rsplit('.', 1)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                if len(name_parts) == 2:
                    file_name = f"{name_parts[0]}_{timestamp}.{name_parts[1]}"
                else:
                    file_name = f"{file_name}_{timestamp}"
                dest_path = os.path.join(folder_path, file_name)
            
            # Copy file
            with open(attachment, 'rb') as src, open(dest_path, 'wb') as dst:
                dst.write(src.read())
            saved_files.append(dest_path)
        
        # Quick analysis of files
        analyses = await analyzer.analyze_multiple_files(saved_files)
        analysis_summary = analyzer.generate_summary_report(analyses)
        
        # Generate response
        confidence_indicator = "✅" if intent.confidence_score > 0.7 else "⚠️"
        
        response_parts = [
            f"{confidence_indicator} **Files organized successfully!**",
            f"📁 Created folder: `{folder_name}`",
            f"💾 Saved {len(saved_files)} files",
            "",
            analysis_summary
        ]
        
        # Add actions for further analysis
        actions = []
        
        if intent.analysis_request or intent.operation_type == "analyze":
            actions.extend([
                cl.Action(
                    name="deep_analysis",
                    label="🔬 Run Deep Analysis",
                    payload={"folder": folder_name, "type": "deep"}
                ),
                cl.Action(
                    name="compare_experiments",
                    label="📊 Compare with Previous",
                    payload={"folder": folder_name, "type": "compare"}
                )
            ])
        
        # Always offer file browser for the new folder
        actions.append(
            cl.Action(
                name="folder_browse",
                label=f"📂 Browse {folder_name}",
                payload={"path": folder_name}
            )
        )
        
        # Update message content
        processing_msg.content = "\n".join(response_parts)
        processing_msg.actions = actions
        await processing_msg.update()
        
        # Pass to agents for additional instructions (e.g., "update readme")
        # Check if there are additional instructions beyond just saving files
        additional_instructions = any(keyword in content.lower() for keyword in [
            'update', 'modify', 'analyze', 'create', 'generate', 'compare', 
            'readme', 'report', 'chart', 'summary', 'document'
        ])
        
        if additional_instructions and thread_id:
            # Pass the full request to agents with context about saved files
            agent_msg = await cl.Message(content="🤖 Processing additional instructions...").send()
            
            state: GraphState = {
                "messages": [HumanMessage(content=f"Files have been saved to {folder_name}. User request: {content}")],
                "project_root": project_root,
                "attachments": saved_files,  # Pass the saved file paths
            }
            
            result = await cl.make_async(APP.invoke)(state, config={"configurable": {"thread_id": thread_id}})
            agent_msg.content = result.get("response", "Additional instructions completed")
            await agent_msg.update()
        
    except Exception as e:
        await cl.Message(content=f"❌ Error processing files: {str(e)}").send()


async def _handle_command(content: str, project_root: str, attachments: list[str]) -> str:
    try:
        if content.startswith("/pwd"):
            return f"Project root: {project_root}"

        if content.startswith("/ls"):
            _, rel = _split_once(content, default=".")
            entries = list_dir_safe(project_root, rel)
            lines = [f"{'[D]' if e.is_dir else '[F]'} {e.path} ({e.size_bytes}B)" for e in entries]
            return "\n".join(lines) or "(empty)"

        if content.startswith("/cat"):
            _, rel = _split_once(content)
            data = read_file_safe(project_root, rel)
            try:
                text = data.decode("utf-8")
            except UnicodeDecodeError:
                # Binary preview: show first 64 bytes as hex
                head = data[:64]
                text = "<binary> " + head.hex(" ")
            if len(text) > 4000:
                text = text[:4000] + "\n... (truncated)"
            return f"```\n{text}\n```"

        if content.startswith("/rm"):
            _, rel = _split_once(content)
            delete_path_safe(project_root, rel)
            return f"Deleted: {rel}"

        if content.startswith("/mv"):
            parts = content.split(maxsplit=2)
            if len(parts) < 3:
                return "Usage: /mv <src_rel> <dst_rel>"
            _, src_rel, dst_rel = parts
            move_path_safe(project_root, src_rel, dst_rel)
            return f"Moved: {src_rel} -> {dst_rel}"

        if content.startswith("/save"):
            # Save uploaded attachments into a destination directory under project root
            _, dest_dir = _split_once(content, default=".")
            if not attachments:
                return "No attachments to save. Upload files then use: /save <dest_dir>"
            saved = []
            for src in attachments:
                name = os.path.basename(src)
                rel_path = os.path.join(dest_dir, name)
                with open(src, "rb") as f:
                    write_file_safe(project_root, rel_path, f.read(), overwrite=True)
                saved.append(rel_path)
            return "Saved files:\n" + "\n".join(saved)

        if content.startswith("/files"):
            # Show file browser actions
            file_actions = await render_file_manager(project_root)
            await cl.Message(
                content="📁 Browse your project files:",
                actions=file_actions
            ).send()
            return "Use buttons above to browse files"

        if content.startswith("/help"):
            return (
                "Commands:\n"
                "/pwd — show project root\n"
                "/ls [rel] — list directory\n"
                "/cat <rel> — show file contents\n"
                "/files — show file browser buttons\n"
                "/save [dest_dir] — save uploaded files to dest_dir (default .)\n"
                "/rm <rel> — delete path\n"
                "/mv <src> <dst> — move/rename\n"
            )

        return "Unknown command. Try /help"
    except Exception as e:
        return f"Error: {e}"


def _split_once(content: str, default: Optional[str] = None) -> Tuple[str, str]:
    parts = content.split(maxsplit=1)
    if len(parts) == 1:
        if default is None:
            raise ValueError("Missing argument")
        return parts[0], default
    return parts[0], parts[1]


@cl.action_callback("deep_analysis")
async def on_deep_analysis(action: cl.Action):
    """Handle deep analysis action"""
    folder_name = action.payload.get("folder", "")
    project_root = cl.user_session.get("project_root")
    
    if folder_name and project_root:
        # Show processing message
        processing_msg = await cl.Message(content=f"🔬 Running deep analysis on {folder_name}...").send()
        
        # Pass to LangGraph agent system for detailed analysis
        thread_id = cl.user_session.get("thread_id")
        folder_path = os.path.join(project_root, folder_name)
        
        # Get files in folder for analysis
        files_in_folder = []
        if os.path.exists(folder_path):
            for file_name in os.listdir(folder_path):
                if file_name != "README.md":  # Skip README
                    files_in_folder.append(os.path.join(folder_path, file_name))
        
        state: GraphState = {
            "messages": [HumanMessage(content=f"Please perform detailed analysis of the experimental data in folder {folder_name}")],
            "project_root": project_root,
            "attachments": files_in_folder,
        }
        
        result = await cl.make_async(APP.invoke)(state, config={"configurable": {"thread_id": thread_id}})
        
        processing_msg.content = result.get("response", "Analysis completed")
        await processing_msg.update()


@cl.action_callback("compare_experiments")
async def on_compare_experiments(action: cl.Action):
    """Handle experiment comparison action"""
    folder_name = action.payload.get("folder", "")
    project_root = cl.user_session.get("project_root")
    
    if folder_name and project_root:
        # Find other experiment folders for comparison
        folder_manager = SmartFolderManager(project_root)
        existing_folders = folder_manager.get_existing_folders()
        
        # Remove current folder from comparison list
        comparison_folders = [f for f in existing_folders if f != folder_name]
        
        if not comparison_folders:
            await cl.Message(content="No other experiments found for comparison.").send()
            return
        
        # Show comparison options
        comparison_actions = []
        for comp_folder in comparison_folders[-5:]:  # Show last 5 experiments
            comparison_actions.append(
                cl.Action(
                    name="run_comparison",
                    label=f"📊 Compare with {comp_folder}",
                    payload={"folder1": folder_name, "folder2": comp_folder}
                )
            )
        
        await cl.Message(
            content=f"Select experiment to compare with **{folder_name}**:",
            actions=comparison_actions
        ).send()


@cl.action_callback("run_comparison")
async def on_run_comparison(action: cl.Action):
    """Handle specific experiment comparison"""
    folder1 = action.payload.get("folder1", "")
    folder2 = action.payload.get("folder2", "")
    project_root = cl.user_session.get("project_root")
    
    if folder1 and folder2 and project_root:
        # Show processing message
        processing_msg = await cl.Message(content=f"📊 Comparing {folder1} with {folder2}...").send()
        
        # Pass to LangGraph for comparison analysis
        thread_id = cl.user_session.get("thread_id")
        
        state: GraphState = {
            "messages": [HumanMessage(content=f"Compare experimental results between {folder1} and {folder2}. Analyze differences, improvements, and suggest next steps.")],
            "project_root": project_root,
            "attachments": [],
        }
        
        result = await cl.make_async(APP.invoke)(state, config={"configurable": {"thread_id": thread_id}})
        
        processing_msg.content = result.get("response", "Comparison completed")
        await processing_msg.update()


@cl.action_callback("file_preview")
async def on_file_preview(action: cl.Action):
    """Handle file preview action"""
    file_path = action.payload.get("path", "")
    project_root = cl.user_session.get("project_root")
    
    if file_path and project_root:
        result = await handle_file_action("preview", file_path, project_root)
        await cl.Message(content=result).send()


@cl.action_callback("folder_browse") 
async def on_folder_browse(action: cl.Action):
    """Handle folder browse action"""
    folder_path = action.payload.get("path", "")
    project_root = cl.user_session.get("project_root")
    
    if project_root:
        # Store current folder in session
        cl.user_session.set("current_folder", folder_path)
        
        # Update file manager with new folder
        file_actions = await render_file_manager(project_root, folder_path)
        await cl.Message(
            content=f"📁 Browsing: {folder_path or '/'}",
            actions=file_actions
        ).send()


