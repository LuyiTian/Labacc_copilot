"""
Project management API routes for multi-user system
"""

from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Form, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import uuid
import json
from pathlib import Path
from datetime import datetime
import zipfile
import shutil

from src.projects.session import session_manager
from src.projects.project_manager import project_manager
from src.projects.auth import auth_manager
from src.projects.temp_manager import get_temp_project_manager
from src.api.file_conversion import FileConversionPipeline

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/projects", tags=["projects"])
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """Get current user from auth token"""
    try:
        user_info = auth_manager.verify_token(credentials.credentials)
        if not user_info:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        return user_info
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

def get_optional_user(request: Request) -> Optional[Dict]:
    """Get user from auth token if present, otherwise return None"""
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            return auth_manager.verify_token(token)
        except:
            return None
    return None

class ProjectInfo(BaseModel):
    project_id: str
    name: str
    permission: str

class ProjectListResponse(BaseModel):
    projects: List[ProjectInfo]
    current_session: str

class SelectProjectRequest(BaseModel):
    project_id: str

class NewProjectRequest(BaseModel):
    name: str
    hypothesis: str
    planned_experiments: List[str] = []
    expected_outcomes: Optional[str] = None

@router.get("/list", response_model=ProjectListResponse)
async def list_projects(request: Request) -> ProjectListResponse:
    """Get list of projects accessible to the current user"""
    
    # Get user from auth token
    user_info = get_optional_user(request)
    if not user_info:
        # Require authentication for project listing
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = user_info["user_id"]
    
    # Create or get session ID
    session_id = request.headers.get("X-Session-ID")
    if not session_id:
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        # Create session with real user ID
        session_manager.create_session(session_id, user_id)
    else:
        # Ensure existing session is still valid, recreate if needed
        session_info = session_manager.get_session_info(session_id)
        if not session_info:
            session_manager.create_session(session_id, user_id)
    
    # Get projects from real project manager
    user_projects = project_manager.get_user_projects(user_id)
    
    return ProjectListResponse(
        projects=[
            ProjectInfo(
                project_id=project.project_id,
                name=project.name,
                permission=project_manager.get_user_permission(user_id, project.project_id)
            )
            for project in user_projects
        ],
        current_session=session_id
    )

@router.post("/select")
async def select_project(request: SelectProjectRequest, http_request: Request) -> Dict[str, Any]:
    """Select a project for the current session"""
    
    # Get session ID
    session_id = http_request.headers.get("X-Session-ID")
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID required in X-Session-ID header")
    
    # Select the project
    project_session = session_manager.select_project(session_id, request.project_id)
    
    if not project_session:
        raise HTTPException(status_code=403, detail=f"Cannot access project {request.project_id}")
    
    return {
        "status": "success",
        "selected_project": project_session.selected_project,
        "permission": project_session.permission,
        "project_path": str(project_session.project_path)
    }

@router.get("/current")
async def get_current_project(request: Request) -> Dict[str, Any]:
    """Get currently selected project information"""
    
    session_id = request.headers.get("X-Session-ID")
    if not session_id:
        return {"project_selected": False, "session_id": None}
    
    session_info = session_manager.get_session_info(session_id)
    if not session_info:
        return {"project_selected": False, "session_id": session_id}
    
    return {
        "project_selected": session_info["project_selected"],
        "session_id": session_id,
        "selected_project": session_info.get("selected_project"),
        "permission": session_info.get("permission"),
        "user_id": session_info.get("user_id")
    }

@router.post("/create-demo")
async def create_demo_project(request: Request) -> Dict[str, Any]:
    """Create a demo project for testing"""
    
    # Get user from auth token
    user_info = get_optional_user(request)
    if not user_info:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = user_info["user_id"]
    session_id = request.headers.get("X-Session-ID", f"session_{uuid.uuid4().hex[:8]}")
    
    # Ensure session exists with real user ID
    if not session_manager.get_session_info(session_id):
        session_manager.create_session(session_id, user_id)
    
    # Create demo project for the actual user
    from src.projects.project_manager import Project
    project_id = f"demo_project_{uuid.uuid4().hex[:6]}"
    project = Project(
        project_id=project_id,
        name="Demo Project",
        owner_id=user_id,
        description="Demo project for testing"
    )
    project_manager.projects[project_id] = project
    project_manager._save_projects()
    
    # Create project directory
    base_path = Path("data") / f"{user_id}_projects" / project_id
    base_path.mkdir(parents=True, exist_ok=True)
    (base_path / ".labacc").mkdir(exist_ok=True)
    (base_path / "README.md").write_text(f"# Demo Project\n\nCreated for user {user_id}")
    
    logger.info(f"Created demo project: {project_id} for user {user_id}")
    
    return {
        "status": "success",
        "project_id": project_id,
        "message": "Demo project created successfully",
        "session_id": session_id
    }

@router.post("/create-new")
async def create_new_project(request_data: NewProjectRequest, request: Request) -> Dict[str, Any]:
    """Create a new hypothesis-driven research project"""
    
    session_id = request.headers.get("X-Session-ID")
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID required")
    
    # Get session info
    session_info = session_manager.get_session_info(session_id)
    if not session_info:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    user_id = session_info.get("user_id", "temp_user")
    
    # Create project directory structure
    project_id = f"project_{request_data.name.lower().replace(' ', '_')}_{uuid.uuid4().hex[:6]}"
    base_path = Path("data") / f"{user_id}_projects" / project_id
    
    try:
        # Create directories
        base_path.mkdir(parents=True, exist_ok=True)
        (base_path / ".labacc").mkdir(exist_ok=True)
        (base_path / "experiments").mkdir(exist_ok=True)
        
        # Create README.md with hypothesis
        readme_content = f"""# {request_data.name}

## Research Question
{request_data.hypothesis}

## Hypothesis
{request_data.hypothesis}

## Planned Experiments
"""
        if request_data.planned_experiments:
            for exp in request_data.planned_experiments:
                readme_content += f"- {exp}\n"
                # Create empty experiment folder
                (base_path / "experiments" / exp).mkdir(exist_ok=True)
        else:
            readme_content += "- To be determined\n"
        
        if request_data.expected_outcomes:
            readme_content += f"\n## Expected Outcomes\n{request_data.expected_outcomes}\n"
        
        readme_content += f"\n---\nCreated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        
        (base_path / "README.md").write_text(readme_content)
        
        # Create project config
        config = {
            "project_id": project_id,
            "name": request_data.name,
            "created_at": datetime.now().isoformat(),
            "creation_mode": "hypothesis_driven",
            "status": "planning",
            "owner": user_id
        }
        (base_path / ".labacc" / "project_config.json").write_text(json.dumps(config, indent=2))
        
        # Register project with project_manager
        from src.projects.project_manager import Project
        project = Project(
            project_id=project_id,
            name=request_data.name,
            owner_id=user_id,
            description=request_data.hypothesis
        )
        project_manager.projects[project_id] = project
        project_manager._save_projects()
        
        logger.info(f"Created new project: {project_id} for user {user_id}")
        
        return {
            "status": "success",
            "project_id": project_id,
            "message": f"Project '{request_data.name}' created successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to create project: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create project: {str(e)}")

@router.post("/import-data")
async def import_existing_data(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    files: List[UploadFile] = File(...),
    request: Request = None
) -> Dict[str, Any]:
    """Import existing experimental data as a new project"""
    
    session_id = request.headers.get("X-Session-ID")
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID required")
    
    # Get session info
    session_info = session_manager.get_session_info(session_id)
    if not session_info:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    user_id = session_info.get("user_id", "temp_user")
    
    # Create project directory
    project_id = f"project_{name.lower().replace(' ', '_')}_{uuid.uuid4().hex[:6]}"
    base_path = Path("data") / f"{user_id}_projects" / project_id
    
    try:
        # Create directories
        base_path.mkdir(parents=True, exist_ok=True)
        (base_path / ".labacc").mkdir(exist_ok=True)
        experiments_path = base_path / "experiments"
        experiments_path.mkdir(exist_ok=True)
        
        # Initialize conversion pipeline
        conversion_pipeline = FileConversionPipeline(str(base_path.parent))
        
        # Process uploaded files
        file_structure = {}
        files_to_convert = []  # Track files that need conversion
        
        for file in files:
            content = await file.read()
            
            # Handle ZIP files
            if file.filename.endswith('.zip'):
                import io
                with zipfile.ZipFile(io.BytesIO(content)) as zf:
                    # Extract maintaining structure
                    for zip_info in zf.filelist:
                        if not zip_info.is_dir():
                            # Get the path components
                            path_parts = zip_info.filename.split('/')
                            
                            # Create directory structure
                            if len(path_parts) > 1:
                                dir_path = experiments_path / '/'.join(path_parts[:-1])
                                dir_path.mkdir(parents=True, exist_ok=True)
                            
                            # Extract file
                            file_path = experiments_path / zip_info.filename
                            file_path.write_bytes(zf.read(zip_info))
                            
                            # Track structure
                            exp_name = path_parts[0] if len(path_parts) > 1 else "imported_files"
                            if exp_name not in file_structure:
                                file_structure[exp_name] = {"files": [], "converted": []}
                            
                            filename = path_parts[-1]
                            file_structure[exp_name]["files"].append(filename)
                            
                            # Check if needs conversion
                            if conversion_pipeline.needs_conversion(filename):
                                files_to_convert.append({
                                    "path": file_path,
                                    "exp_name": exp_name,
                                    "filename": filename
                                })
            else:
                # Regular file - put in imported_files folder
                imported_path = experiments_path / "imported_files"
                imported_path.mkdir(exist_ok=True)
                file_path = imported_path / file.filename
                file_path.write_bytes(content)
                
                if "imported_files" not in file_structure:
                    file_structure["imported_files"] = {"files": [], "converted": []}
                file_structure["imported_files"]["files"].append(file.filename)
                
                # Check if needs conversion
                if conversion_pipeline.needs_conversion(file.filename):
                    files_to_convert.append({
                        "path": file_path,
                        "exp_name": "imported_files",
                        "filename": file.filename
                    })
        
        # Convert PDF/DOCX/PPTX files to Markdown
        conversion_results = []
        for file_info in files_to_convert:
            try:
                logger.info(f"Converting {file_info['filename']} to Markdown...")
                
                # Determine experiment folder for conversion
                exp_folder = experiments_path / file_info['exp_name']
                
                # Process the file through conversion pipeline
                result = await conversion_pipeline.process_upload(
                    file_info['path'],
                    file_info['exp_name']
                )
                
                if result['conversion_status'] == 'success':
                    file_structure[file_info['exp_name']]["converted"].append({
                        "original": file_info['filename'],
                        "markdown": result.get('analysis_path', 'converted.md')
                    })
                    conversion_results.append(f"✅ {file_info['filename']}")
                else:
                    conversion_results.append(f"⚠️ {file_info['filename']} (conversion failed)")
                    
            except Exception as e:
                logger.error(f"Failed to convert {file_info['filename']}: {e}")
                conversion_results.append(f"❌ {file_info['filename']} (error)")
        
        # Generate README from discovered structure
        readme_content = f"""# {name}

{description if description else 'Imported experimental data project'}

## Project Structure (Auto-discovered)
"""
        for exp_name, exp_data in file_structure.items():
            readme_content += f"\n### Experiment: {exp_name}\n"
            readme_content += f"- Files: {len(exp_data['files'])} items\n"
            
            # List original files
            files_list = exp_data['files']
            if len(files_list) <= 5:
                for f in files_list:
                    readme_content += f"  - {f}\n"
            else:
                for f in files_list[:3]:
                    readme_content += f"  - {f}\n"
                readme_content += f"  - ... and {len(files_list) - 3} more files\n"
            
            # List converted files if any
            if exp_data.get('converted'):
                readme_content += f"\n- **Converted Documents:** {len(exp_data['converted'])} files\n"
                for conv in exp_data['converted']:
                    readme_content += f"  - {conv['original']} → Markdown\n"
        
        readme_content += f"\n---\nImported: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        
        (base_path / "README.md").write_text(readme_content)
        
        # Create project config
        config = {
            "project_id": project_id,
            "name": name,
            "created_at": datetime.now().isoformat(),
            "creation_mode": "data_driven",
            "status": "analyzing",
            "owner": user_id,
            "imported_structure": file_structure
        }
        (base_path / ".labacc" / "project_config.json").write_text(json.dumps(config, indent=2))
        
        # TODO: Trigger background analysis of imported data
        # This would normally trigger the agent to analyze the imported files
        
        # Create file registry for tracking conversions
        registry = {
            "version": "3.0",
            "project_id": project_id,
            "created_at": datetime.now().isoformat(),
            "files": {}
        }
        
        for exp_name, exp_data in file_structure.items():
            for filename in exp_data['files']:
                registry["files"][filename] = {
                    "experiment": exp_name,
                    "upload_time": datetime.now().isoformat(),
                    "needs_conversion": conversion_pipeline.needs_conversion(filename)
                }
            
            # Add conversion info
            for conv in exp_data.get('converted', []):
                if conv['original'] in registry["files"]:
                    registry["files"][conv['original']]["conversion"] = {
                        "status": "success",
                        "markdown_path": conv['markdown'],
                        "timestamp": datetime.now().isoformat()
                    }
        
        (base_path / ".labacc" / "file_registry.json").write_text(json.dumps(registry, indent=2))
        
        # Generate README for each experiment folder that doesn't have one
        for exp_name in file_structure.keys():
            exp_path = experiments_path / exp_name
            exp_readme = exp_path / "README.md"
            
            if not exp_readme.exists():
                exp_readme_content = f"""# Experiment: {exp_name}

## Overview
This experiment folder was imported on {datetime.now().strftime('%Y-%m-%d')}.

## Files
"""
                for filename in file_structure[exp_name]['files']:
                    exp_readme_content += f"- {filename}\n"
                
                if file_structure[exp_name].get('converted'):
                    exp_readme_content += f"\n## Converted Documents\n"
                    for conv in file_structure[exp_name]['converted']:
                        exp_readme_content += f"- {conv['original']} (converted to Markdown)\n"
                
                exp_readme_content += f"\n## Notes\n_Add your experimental notes here_\n"
                
                exp_readme.write_text(exp_readme_content)
        
        # Register project with project_manager
        from src.projects.project_manager import Project
        project = Project(
            project_id=project_id,
            name=name,
            owner_id=user_id,
            description=description or f"Imported data project: {name}"
        )
        project_manager.projects[project_id] = project
        project_manager._save_projects()
        
        logger.info(f"Imported project: {project_id} with {len(files)} files, {len(conversion_results)} conversions")
        
        # Calculate total files imported
        total_files = sum(len(exp_data['files']) for exp_data in file_structure.values())
        
        return {
            "status": "success",
            "project_id": project_id,
            "message": f"Project '{name}' imported successfully",
            "files_imported": total_files,
            "conversions": conversion_results if conversion_results else None
        }
        
    except Exception as e:
        logger.error(f"Failed to import project: {e}")
        # Clean up partial project if it exists
        if base_path.exists():
            shutil.rmtree(base_path)
        raise HTTPException(status_code=500, detail=f"Failed to import project: {str(e)}")

@router.get("/debug/sessions")
async def debug_sessions() -> Dict[str, Any]:
    """Debug endpoint to see active sessions"""
    return {
        "active_sessions": session_manager.list_active_sessions()
    }