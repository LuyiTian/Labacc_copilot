from __future__ import annotations

import os
import shutil
from dataclasses import dataclass


@dataclass
class FileInfo:
    path: str
    size_bytes: int
    mtime: float
    is_dir: bool


def _normalize_root(root: str) -> str:
    root_abs = os.path.abspath(root)
    return root_abs


def _ensure_within_root(root: str, target_path: str) -> str:
    root_abs = _normalize_root(root)
    resolved = os.path.abspath(target_path)
    if not resolved.startswith(root_abs + os.sep) and resolved != root_abs:
        raise PermissionError("Path traversal outside project root is not allowed")
    return resolved


def list_dir(root: str, rel_path: str = ".") -> list[FileInfo]:
    base = _ensure_within_root(root, os.path.join(root, rel_path))
    entries: list[FileInfo] = []
    with os.scandir(base) as it:
        for entry in it:
            if entry.name.startswith("."):
                continue
            stat = entry.stat()
            entries.append(
                FileInfo(
                    path=os.path.relpath(entry.path, root),
                    size_bytes=stat.st_size,
                    mtime=stat.st_mtime,
                    is_dir=entry.is_dir(),
                )
            )
    entries.sort(key=lambda e: (not e.is_dir, e.path.lower()))
    return entries


def read_file(root: str, rel_path: str) -> bytes:
    path = _ensure_within_root(root, os.path.join(root, rel_path))
    with open(path, "rb") as f:
        return f.read()


def write_file(root: str, rel_path: str, data: bytes, overwrite: bool = True) -> None:
    path = _ensure_within_root(root, os.path.join(root, rel_path))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not overwrite and os.path.exists(path):
        raise FileExistsError(f"File already exists: {rel_path}")
    with open(path, "wb") as f:
        f.write(data)


def delete_path(root: str, rel_path: str) -> None:
    path = _ensure_within_root(root, os.path.join(root, rel_path))
    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.exists(path):
        os.remove(path)


def move_path(root: str, src_rel: str, dst_rel: str, overwrite: bool = False) -> None:
    src = _ensure_within_root(root, os.path.join(root, src_rel))
    dst = _ensure_within_root(root, os.path.join(root, dst_rel))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.exists(dst) and not overwrite:
        raise FileExistsError(f"Destination exists: {dst_rel}")
    shutil.move(src, dst)



