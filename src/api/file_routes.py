"""File management API routes for LabAcc Copilot

This module provides REST API endpoints for file operations,
designed to work with the React frontend file manager.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any
import asyncio
import logging

import aiofiles
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Import memory tools for auto-updating README
from src.memory.memory_tools import update_file_registry, append_insight
from src.memory.file_summarizer import summarize_uploaded_file

# Import file conversion and registry
from src.api.file_conversion import FileConversionPipeline
from src.api.file_registry import FileRegistry

logger = logging.getLogger(__name__)

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


def get_project_root(request: Request) -> str:
    """Get the session-specific project root directory"""
    from src.projects.session import session_manager
    
    # Get session ID from header
    session_id = request.headers.get("X-Session-ID")
    if not session_id:
        raise HTTPException(status_code=401, detail="No session ID provided")
    
    # Get session context
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=403, detail="Invalid or expired session")
    
    # Return the session-specific project path
    return str(session.project_path)


# File operation endpoints
@router.get("/list", response_model=ListFilesResponse)
async def list_files(
    request: Request,
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
        
        # Initialize conversion pipeline and registry
        conversion_pipeline = FileConversionPipeline(project_root)
        file_registry = FileRegistry(project_root)

        for file in files:
            # Sanitize filename
            filename = Path(file.filename).name
            
            # Determine if this is an experiment folder
            relative_path = str(dest_dir.relative_to(project_root))
            path_parts = relative_path.split('/')
            experiment_id = None
            for part in path_parts:
                if part.startswith('exp_'):
                    experiment_id = part
                    break
            
            # Determine where to save the file
            if experiment_id and conversion_pipeline.needs_conversion(filename):
                # For convertible files in experiments, save to originals/
                # FIXED: Use dest_dir instead of reconstructing path from experiment_id
                originals_dir = dest_dir / "originals"
                originals_dir.mkdir(parents=True, exist_ok=True)
                file_path = originals_dir / filename
            else:
                # For other files, save to requested location
                file_path = dest_dir / filename

            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            file_size = len(content)
            relative_file_path = str(file_path.relative_to(project_root))

            # Process conversion if needed and in experiment
            conversion_result = None
            if experiment_id:
                conversion_result = await conversion_pipeline.process_upload(
                    file_path, 
                    experiment_id
                )
                
                # Update registry with full information
                file_registry.add_file(
                    experiment_id=experiment_id,
                    filename=filename,
                    original_path=relative_file_path,
                    converted_path=conversion_result.get("converted_path"),
                    file_size=file_size,
                    conversion_status=conversion_result.get("conversion_status", "not_needed"),
                    conversion_method=conversion_result.get("conversion_method")
                )

            uploaded_files.append({
                "name": filename,
                "path": relative_file_path,
                "size": file_size,
                "converted": conversion_result.get("converted_path") if conversion_result else None,
                "conversion_status": conversion_result.get("conversion_status") if conversion_result else "not_needed"
            })
        
        # Auto-update README if uploading to an experiment folder
        try:
            # Check if this is an experiment folder
            relative_path = str(dest_dir.relative_to(project_root))
            path_parts = relative_path.split('/')
            
            # Find experiment folder (starts with exp_)
            experiment_id = None
            for part in path_parts:
                if part.startswith('exp_'):
                    experiment_id = part
                    break
            
            if experiment_id:
                # Update README in background
                async def update_readme_background():
                    try:
                        for file_info in uploaded_files:
                            filename = file_info["name"]
                            size = file_info["size"]
                            
                            # Determine file type
                            file_ext = Path(filename).suffix.lower()
                            if file_ext in ['.csv', '.tsv', '.txt']:
                                file_type = "Data"
                            elif file_ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg']:
                                file_type = "Image"
                            elif file_ext in ['.pdf', '.doc', '.docx', '.md']:
                                file_type = "Document"
                            elif file_ext in ['.py', '.ipynb']:
                                file_type = "Code"
                            elif file_ext in ['.json', '.yaml', '.yml']:
                                file_type = "Config"
                            else:
                                file_type = "File"
                            
                            # Use LLM to generate context-aware summary
                            # Use converted file if available for better analysis
                            file_full_path = Path(project_root) / file_info["path"]
                            
                            # Check if we have a converted version
                            if file_info.get("converted"):
                                # Use converted markdown for analysis
                                analysis_path = Path(project_root) / file_info["converted"]
                                if analysis_path.exists():
                                    file_full_path = analysis_path
                                    logger.info(f"Using converted file for analysis: {analysis_path}")
                            
                            # Get intelligent summary with experiment context
                            try:
                                summary = await summarize_uploaded_file(
                                    str(file_full_path),
                                    experiment_id
                                )
                                logger.info(f"Generated LLM summary for {filename}: {summary[:50]}...")
                            except Exception as e:
                                logger.error(f"Failed to generate LLM summary: {e}")
                                # Fallback to simple summary
                                summary = f"Uploaded {file_type.lower()} file"
                            
                            # Update file registry
                            await update_file_registry.ainvoke({
                                "experiment_id": experiment_id,
                                "file_name": filename,
                                "file_type": file_type,
                                "file_size": f"{size} bytes",
                                "summary": summary
                            })
                        
                        # Add insight about new files
                        if len(uploaded_files) == 1:
                            await append_insight.ainvoke({
                                "experiment_id": experiment_id,
                                "insight": f"Added {uploaded_files[0]['name']} to experiment",
                                "source": "file_upload"
                            })
                        else:
                            await append_insight.ainvoke({
                                "experiment_id": experiment_id,
                                "insight": f"Added {len(uploaded_files)} new files to experiment",
                                "source": "file_upload"
                            })
                        
                        logger.info(f"Updated README for {experiment_id} after file upload")
                    except Exception as e:
                        logger.error(f"Failed to update README for {experiment_id}: {e}")
                
                # Run the update in background (don't wait for it)
                asyncio.create_task(update_readme_background())
                
        except Exception as e:
            # Don't fail the upload if README update fails
            logger.error(f"Error in README auto-update: {e}")

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
        
        # If creating an experiment folder, initialize README
        try:
            if folder_name.startswith('exp_'):
                from src.memory.memory_tools import create_experiment
                
                async def init_experiment_readme():
                    try:
                        # Extract experiment name from folder name
                        # exp_001_pcr_optimization -> PCR optimization
                        parts = folder_name.split('_', 2)  # Split on first 2 underscores
                        if len(parts) >= 3:
                            exp_name = parts[2].replace('_', ' ').title()
                        else:
                            exp_name = folder_name
                        
                        await create_experiment.ainvoke({
                            "experiment_name": exp_name,
                            "motivation": "Created via web interface",
                            "key_question": "To be defined"
                        })
                        logger.info(f"Initialized README for new experiment: {folder_name}")
                    except Exception as e:
                        logger.error(f"Failed to initialize README for {folder_name}: {e}")
                
                # Run in background
                asyncio.create_task(init_experiment_readme())
                
        except Exception as e:
            logger.error(f"Error initializing experiment: {e}")

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
