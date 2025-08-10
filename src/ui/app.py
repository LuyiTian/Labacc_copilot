from __future__ import annotations

import os
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
import shutil


APP = build_graph()


def _get_username() -> str:
    # Chainlit deployments behind reverse proxy can pass REMOTE_USER
    return os.environ.get("REMOTE_USER") or os.environ.get("USER") or "anonymous"


@cl.on_chat_start
async def on_chat_start():
    username = _get_username()
    session_id = cl.user_session.get("id")
    thread_id = f"{username}:{session_id}"
    cl.user_session.set("thread_id", thread_id)
    await cl.Message(content=f"Session started. thread_id={thread_id}").send()


@cl.on_message
async def on_message(message: cl.Message):
    thread_id: str = cl.user_session.get("thread_id")
    project_root: Optional[str] = os.environ.get("LABACC_PROJECT_ROOT", os.getcwd())

    attachments = []
    for elem in message.elements or []:
        if hasattr(elem, "path") and elem.path:
            attachments.append(elem.path)

    # Slash commands for simple file management
    content = (message.content or "").strip()
    if content.startswith("/"):
        reply = await _handle_command(content, project_root, attachments)
        await cl.Message(content=reply).send()
        return

    state: GraphState = {
        "messages": [HumanMessage(content=message.content)],
        "project_root": project_root,
        "attachments": attachments,
    }
    result = await cl.make_async(APP.invoke)(state, config={"configurable": {"thread_id": thread_id}})
    await cl.Message(content=result.get("response", "(no response)"), author="Analyst").send()


# Note: cl.on_event is not available in current Chainlit version
# This would be used for custom UI actions in future versions


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

        if content.startswith("/help"):
            return (
                "Commands:\n"
                "/pwd — show project root\n"
                "/ls [rel] — list directory\n"
                "/cat <rel> — show file contents\n"
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


