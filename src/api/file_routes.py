"""File management API routes for LabAcc Copilot

This module provides REST API endpoints for file operations,
designed to work with the React frontend file manager.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

import aiofiles
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Create API router
router = APIRouter(prefix="/api/files", tags=["files"])


# Request/Response models
class FileInfo(BaseModel):
    """File information model"""
    name: str
    path: str
    is_dir: bool
    size: int
    modified: str
    created: str
    thumbnail_url: str | None = None


class ListFilesResponse(BaseModel):
    """Response for listing files"""
    files: list[FileInfo]
    current_path: str
    parent_path: str | None


class CreateFolderRequest(BaseModel):
    """Request to create a new folder"""
    path: str
    folder_name: str


class MoveFilesRequest(BaseModel):
    """Request to move files"""
    source_paths: list[str]
    destination_path: str


class DeleteFilesRequest(BaseModel):
    """Request to delete files"""
    paths: list[str]


# Security utilities
def validate_path(path: str, project_root: str) -> Path:
    """Validate and sanitize file paths to prevent directory traversal"""
    # Remove null bytes and normalize
    clean_path = path.replace('\x00', '').strip()

    # Resolve to absolute path
    if clean_path.startswith('/'):
        clean_path = clean_path[1:]

    full_path = Path(project_root) / clean_path
    resolved_path = full_path.resolve()

    # Ensure path is within project root
    if not str(resolved_path).startswith(str(Path(project_root).resolve())):
        raise HTTPException(status_code=403, detail="Access denied: Path outside project root")

    return resolved_path


def get_project_root() -> str:
    """Get the project root directory from environment or default"""
    default_root = os.path.join(os.getcwd(), "data", "alice_projects")
    return os.environ.get("LABACC_PROJECT_ROOT", default_root)


# File operation endpoints
@router.get("/list", response_model=ListFilesResponse)
async def list_files(
    path: str = "/",
    project_root: str = Depends(get_project_root)
) -> ListFilesResponse:
    """List files and directories in the specified path"""
    try:
        # Validate path
        dir_path = validate_path(path, project_root)

        if not dir_path.exists():
            raise HTTPException(status_code=404, detail="Path not found")

        if not dir_path.is_dir():
            raise HTTPException(status_code=400, detail="Path is not a directory")

        # List files
        files = []
        for item in sorted(dir_path.iterdir()):
            try:
                stat = item.stat()
                relative_path = str(item.relative_to(project_root))

                file_info = FileInfo(
                    name=item.name,
                    path=relative_path,
                    is_dir=item.is_dir(),
                    size=stat.st_size if not item.is_dir() else 0,
                    modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    created=datetime.fromtimestamp(stat.st_ctime).isoformat(),
                )

                # Add thumbnail URL for images
                if item.is_file() and item.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif']:
                    file_info.thumbnail_url = f"/api/files/thumbnail/{relative_path}"

                files.append(file_info)
            except (PermissionError, OSError):
                continue

        # Get parent path
        parent_path = None
        if path != "/" and path != "":
            parent_path = str(Path(path).parent)
            if parent_path == ".":
                parent_path = "/"

        return ListFilesResponse(
            files=files,
            current_path=path,
            parent_path=parent_path
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")


@router.post("/upload")
async def upload_files(
    files: list[UploadFile] = File(...),
    path: str = Form("/"),
    project_root: str = Depends(get_project_root)
) -> dict[str, Any]:
    """Upload one or more files to the specified path"""
    try:
        # Validate destination path
        dest_dir = validate_path(path, project_root)

        if not dest_dir.exists():
            dest_dir.mkdir(parents=True, exist_ok=True)

        if not dest_dir.is_dir():
            raise HTTPException(status_code=400, detail="Destination is not a directory")

        uploaded_files = []

        for file in files:
            # Sanitize filename
            filename = Path(file.filename).name
            file_path = dest_dir / filename

            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)

            uploaded_files.append({
                "name": filename,
                "path": str(file_path.relative_to(project_root)),
                "size": len(content)
            })

        return {
            "success": True,
            "uploaded_count": len(uploaded_files),
            "files": uploaded_files
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload files: {str(e)}")


@router.post("/folder")
async def create_folder(
    request: CreateFolderRequest,
    project_root: str = Depends(get_project_root)
) -> dict[str, Any]:
    """Create a new folder"""
    try:
        # Validate parent path
        parent_dir = validate_path(request.path, project_root)

        if not parent_dir.exists():
            raise HTTPException(status_code=404, detail="Parent directory not found")

        if not parent_dir.is_dir():
            raise HTTPException(status_code=400, detail="Parent path is not a directory")

        # Create new folder
        folder_name = Path(request.folder_name).name  # Sanitize folder name
        new_folder = parent_dir / folder_name

        if new_folder.exists():
            raise HTTPException(status_code=409, detail="Folder already exists")

        new_folder.mkdir(parents=True, exist_ok=True)

        return {
            "success": True,
            "folder_path": str(new_folder.relative_to(project_root))
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create folder: {str(e)}")


@router.delete("")
async def delete_files(
    request: DeleteFilesRequest,
    project_root: str = Depends(get_project_root)
) -> dict[str, Any]:
    """Delete files or folders"""
    try:
        deleted_count = 0
        errors = []

        for path_str in request.paths:
            try:
                file_path = validate_path(path_str, project_root)

                if not file_path.exists():
                    errors.append(f"{path_str}: Not found")
                    continue

                if file_path.is_dir():
                    shutil.rmtree(file_path)
                else:
                    file_path.unlink()

                deleted_count += 1

            except Exception as e:
                errors.append(f"{path_str}: {str(e)}")

        return {
            "success": deleted_count > 0,
            "deleted_count": deleted_count,
            "errors": errors if errors else None
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete files: {str(e)}")


@router.put("/move")
async def move_files(
    request: MoveFilesRequest,
    project_root: str = Depends(get_project_root)
) -> dict[str, Any]:
    """Move or rename files"""
    try:
        # Validate destination
        dest_dir = validate_path(request.destination_path, project_root)

        if not dest_dir.exists():
            dest_dir.mkdir(parents=True, exist_ok=True)

        if not dest_dir.is_dir():
            raise HTTPException(status_code=400, detail="Destination is not a directory")

        moved_files = []
        errors = []

        for source_path_str in request.source_paths:
            try:
                source_path = validate_path(source_path_str, project_root)

                if not source_path.exists():
                    errors.append(f"{source_path_str}: Not found")
                    continue

                # Move file
                dest_path = dest_dir / source_path.name
                shutil.move(str(source_path), str(dest_path))

                moved_files.append({
                    "source": source_path_str,
                    "destination": str(dest_path.relative_to(project_root))
                })

            except Exception as e:
                errors.append(f"{source_path_str}: {str(e)}")

        return {
            "success": len(moved_files) > 0,
            "moved_count": len(moved_files),
            "files": moved_files,
            "errors": errors if errors else None
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to move files: {str(e)}")


@router.get("/download/{file_path:path}")
async def download_file(
    file_path: str,
    project_root: str = Depends(get_project_root)
) -> FileResponse:
    """Download a file"""
    try:
        # Validate path
        file = validate_path(file_path, project_root)

        if not file.exists():
            raise HTTPException(status_code=404, detail="File not found")

        if not file.is_file():
            raise HTTPException(status_code=400, detail="Path is not a file")

        return FileResponse(
            path=str(file),
            filename=file.name,
            media_type='application/octet-stream'
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download file: {str(e)}")


@router.get("/metadata/{file_path:path}")
async def get_file_metadata(
    file_path: str,
    project_root: str = Depends(get_project_root)
) -> dict[str, Any]:
    """Get detailed metadata for a file"""
    try:
        # Validate path
        file = validate_path(file_path, project_root)

        if not file.exists():
            raise HTTPException(status_code=404, detail="File not found")

        stat = file.stat()

        metadata = {
            "name": file.name,
            "path": str(file.relative_to(project_root)),
            "is_dir": file.is_dir(),
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "extension": file.suffix if file.is_file() else None,
            "mime_type": None,  # TODO: Implement mime type detection
        }

        # Add file-specific metadata
        if file.is_file():
            if file.suffix.lower() in ['.csv', '.tsv']:
                # For CSV files, could add row/column count
                metadata["file_type"] = "data"
            elif file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif']:
                metadata["file_type"] = "image"
            elif file.suffix.lower() in ['.txt', '.md', '.log']:
                metadata["file_type"] = "text"
            else:
                metadata["file_type"] = "unknown"

        return metadata

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metadata: {str(e)}")
