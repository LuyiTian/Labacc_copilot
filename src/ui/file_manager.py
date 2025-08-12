"""Visual file manager component for Chainlit UI"""

import os
from pathlib import Path
from typing import List, Dict, Any
import chainlit as cl


def get_file_tree(root_path: str, current_path: str = "") -> List[Dict[str, Any]]:
    """Generate file tree structure for display"""
    full_path = os.path.join(root_path, current_path) if current_path else root_path
    
    items = []
    try:
        for entry in sorted(os.listdir(full_path)):
            entry_path = os.path.join(full_path, entry)
            rel_path = os.path.join(current_path, entry) if current_path else entry
            
            if os.path.isdir(entry_path):
                items.append({
                    "name": entry,
                    "path": rel_path,
                    "type": "folder",
                    "icon": "📁"
                })
            else:
                # Determine file icon based on extension
                ext = Path(entry).suffix.lower()
                icon = get_file_icon(ext)
                items.append({
                    "name": entry,
                    "path": rel_path,
                    "type": "file",
                    "icon": icon,
                    "size": os.path.getsize(entry_path)
                })
    except PermissionError:
        pass
    
    return items


def get_file_icon(extension: str) -> str:
    """Return appropriate icon for file type"""
    icons = {
        ".csv": "📊",
        ".xlsx": "📊",
        ".xls": "📊",
        ".txt": "📄",
        ".md": "📝",
        ".pdf": "📕",
        ".png": "🖼️",
        ".jpg": "🖼️",
        ".jpeg": "🖼️",
        ".gif": "🖼️",
        ".py": "🐍",
        ".ipynb": "📓",
        ".json": "📋",
        ".yaml": "📋",
        ".yml": "📋",
        ".log": "📜",
    }
    return icons.get(extension, "📄")


def format_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f}TB"


async def render_file_manager(root_path: str, current_path: str = "") -> List[cl.Action]:
    """Render file manager as action buttons for sidebar"""
    items = get_file_tree(root_path, current_path)
    actions = []
    
    # Add parent directory navigation if not at root
    if current_path:
        parent_path = os.path.dirname(current_path)
        actions.append(
            cl.Action(
                name="folder_browse",
                label="🔙 Back",
                payload={"path": parent_path}
            )
        )
    
    # Add folders first
    for item in items:
        if item["type"] == "folder":
            actions.append(
                cl.Action(
                    name="folder_browse",
                    label=f"{item['icon']} {item['name']}/",
                    payload={"path": item['path']}
                )
            )
    
    # Then add files
    for item in items:
        if item["type"] == "file":
            size_str = format_size(item.get('size', 0))
            actions.append(
                cl.Action(
                    name="file_preview",
                    label=f"{item['icon']} {item['name']} ({size_str})",
                    payload={"path": item['path']}
                )
            )
    
    return actions


async def handle_file_action(action: str, path: str, root_path: str) -> str:
    """Handle file operations from UI"""
    full_path = os.path.join(root_path, path)
    
    if action == "preview":
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read(1000)  # Read first 1000 chars
                if len(content) == 1000:
                    content += "\n... (truncated)"
                return f"**{path}**\n```\n{content}\n```"
        except UnicodeDecodeError:
            return f"**{path}** (binary file)"
        except Exception as e:
            return f"Error reading {path}: {e}"
    
    elif action == "delete":
        try:
            if os.path.isdir(full_path):
                import shutil
                shutil.rmtree(full_path)
            else:
                os.remove(full_path)
            return f"✅ Deleted: {path}"
        except Exception as e:
            return f"❌ Error deleting {path}: {e}"
    
    return f"Unknown action: {action}"