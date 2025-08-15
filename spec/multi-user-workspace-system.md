# LabAcc Copilot Project-Based Multi-User System

**Version**: 3.0  
**Date**: 2025-08-15  
**Focus**: Project-Centric + Agent-Friendly Design  

## Core Principle

**Project-based multi-user system where users work within selected projects using relative paths.**

Simple flow:
1. **User logs in** → See list of accessible projects
2. **Select project** → Agent operates entirely within that project folder  
3. **All paths relative** → No complex path resolution needed

## Table of Contents

1. [The Real Problem](#the-real-problem)
2. [Project-Centric Solution](#project-centric-solution)
3. [Agent Design](#agent-design)
4. [Implementation Plan](#implementation-plan)

## The Real Problem

### **Current Issues**

1. **One global `data/` folder, everyone sees everything**  
2. **CRITICAL BUG: Path resolution failure causing file upload errors**
3. **No private projects, controlled sharing, or simple collaboration**

### **Critical Bug Analysis** (August 2025)

**Symptom**: PDF uploaded to `/bob_projects/exp_002_optimization/` but ended up in `/data/exp_002_optimization/` (wrong location)

**Root Cause**: `src/api/file_routes.py:195-197` path reconstruction bug:
```python
# BROKEN CODE (FIXED 2025-08-15):
originals_dir = Path(project_root) / experiment_id / "originals"  
# Creates: data/exp_002_optimization/originals/
# Should be: data/bob_projects/exp_002_optimization/originals/

# FIXED CODE:
originals_dir = dest_dir / "originals"  # ✅ Use validated destination
```

**Deeper Architecture Problems**:
- ❌ **5-layer path interpretation chaos**: Frontend → API validation → Upload logic → Agent tools → Memory system
- ❌ **No single source of truth**: Each component guesses path meanings differently  
- ❌ **Brittle context extraction**: System extracts experiment context by parsing path strings
- ❌ **Path reconstruction anti-pattern**: Rebuilding paths from fragments instead of preserving validated paths

### **Real Lab Scenario**:
```
Mike: "I want my PCR experiments private, but share the successful protocol with Lisa"
Lisa: "I need to access lab protocols, work on my cancer study, and collaborate with Mike"  
Sarah (PI): "I need oversight of all lab projects and manage permissions"
Bug Report: "My PDF uploads go to wrong folders and create mysterious exp_unknown directories"
```

## Project-Centric Solution

**Key Insight**: Session-based project isolation eliminates ALL path resolution complexity by providing a single source of truth.

### **How This Fixes Current Bugs**

**Before (Broken):**
```python
# 5-layer path interpretation chaos:
Frontend: "/bob_projects/exp_002_optimization/" 
   ↓ API strips leading "/"
API: "bob_projects/exp_002_optimization/"
   ↓ validate_path() resolves against project_root
Validated: "data/bob_projects/exp_002_optimization/"
   ↓ Upload logic extracts experiment_id
Extract: "exp_002_optimization" 
   ↓ Path reconstruction (BUG!)
Result: "data/exp_002_optimization/" ❌ WRONG LOCATION
```

**After (Clean):**
```python  
# Single session-based resolution:
Session: project_path = "/external/lab_data/projects/project_bob_lung_cancer/"
Tool Call: upload_file("protocol.pdf", "experiments/")
Resolution: project_path / "experiments/" = "/external/lab_data/projects/project_bob_lung_cancer/experiments/"
Result: ✅ ALWAYS CORRECT, NO GUESSING
```

### 1. Project Storage (Outside Codebase)
```
/external/lab_data/projects/
├── project_001_mike_pcr/          (owned by mike, private)
├── project_002_lisa_cancer/       (owned by lisa, private)
├── project_003_shared_protocols/  (owned by sarah, shared with all)
├── project_004_collaboration/     (owned by mike, shared with lisa)
└── project_005_teaching/          (owned by sarah, shared with students)
```

### 2. Simple Permission Model
```
Project Owner:  Full control (read/write/delete/share)
Shared User:    Contributor access (read/write, cannot delete/share)  
Admin:          God mode (can access/manage any project)
```

### 3. Session-Based Project Selection
```
Login Flow:
1. User enters username/password
2. System shows list of accessible projects:
   - "My Projects" (owned by user)
   - "Shared with Me" (collaborative projects)
   - "Lab Resources" (admin-shared projects)
3. User selects project → Agent works entirely within that project
4. All agent operations use relative paths within selected project
```

## Agent Design

### Session Context (Simple)
```python
# User session after project selection
session_context = {
    "user_id": "mike",
    "role": "postdoc",
    "selected_project": "project_001_mike_pcr",
    "project_path": "/external/lab_data/projects/project_001_mike_pcr/",
    "permission": "owner"  # owner/shared/admin
}

# Agent call with project-scoped context
response = await handle_message(
    message="List my experiments", 
    session_context=session_context
)
```

### Agent Tools (Relative Paths Only)
```python
@tool
async def list_folder_contents(folder_path: str = ".") -> str:
    """List files/folders in current project (relative paths only)"""
    
    # All paths are relative to selected project - no permission logic needed!
    project_root = get_current_project_path()  # From session context
    full_path = project_root / folder_path
    
    if not full_path.exists():
        return f"Folder not found: {folder_path}"
    
    return list_directory_contents(full_path)

@tool
async def read_file(file_path: str) -> str:
    """Read file in current project (relative path only)"""
    
    project_root = get_current_project_path()
    full_path = project_root / file_path
    
    if not full_path.exists():
        return f"File not found: {file_path}"
    
    return read_file_contents(full_path)

@tool  
async def share_project_with_user(username: str) -> str:
    """Share current project with another user"""
    
    session = get_current_session()
    
    # System-level permission check
    if session.permission != "owner":
        return "Only project owners can share projects"
    
    try:
        add_project_collaborator(session.selected_project, username)
        return f"Shared project with {username}"
    except UserNotFound:
        return f"User {username} not found"
    except PermissionError as e:
        return f"Cannot share project: {str(e)}"
```

### System-Level Project Management
```python
# This happens OUTSIDE the agent - in the API layer
class ProjectManager:
    def get_user_projects(self, user_id: str) -> List[Project]:
        """Get list of projects user can access"""
        owned = self.get_owned_projects(user_id)
        shared = self.get_shared_projects(user_id)
        admin = self.get_admin_projects(user_id) if is_admin(user_id) else []
        return owned + shared + admin
    
    def select_project(self, user_id: str, project_id: str) -> SessionContext:
        """Set user's active project after permission check"""
        if not self.can_access_project(user_id, project_id):
            raise PermissionError(f"User cannot access project {project_id}")
        
        return SessionContext(
            user_id=user_id,
            selected_project=project_id,
            project_path=self.get_project_path(project_id),
            permission=self.get_user_permission(user_id, project_id)
        )

def get_current_project_path() -> Path:
    """Get current project path from session context"""
    session = get_current_session()
    return Path(session.project_path)
```

## Implementation Plan

### Step 1: Project-Based Storage System
**Files to create:**
- `src/projects/project_manager.py` - Project creation, sharing, permissions
- `src/projects/storage.py` - External storage path management

**Changes:**
```python
# project_manager.py 
class ProjectManager:
    def __init__(self, storage_root: str = "/external/lab_data/projects/"):
        self.storage_root = Path(storage_root)
        
    def create_project(self, user_id: str, project_name: str) -> str:
        """Create new private project for user"""
        project_id = f"project_{uuid.uuid4().hex[:8]}_{project_name}"
        project_path = self.storage_root / project_id
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Set ownership
        self.set_project_owner(project_id, user_id)
        return project_id
        
    def share_project(self, project_id: str, owner_id: str, shared_with: str):
        """Share project with another user"""
        if not self.is_project_owner(project_id, owner_id):
            raise PermissionError("Only owners can share projects")
        self.add_project_collaborator(project_id, shared_with)
```

### Step 2: Session-Based Project Selection
**Files to modify:**
- `src/api/react_bridge.py` - Add project selection to session management

**Changes:**
```python
# react_bridge.py - Session with project context
@router.post("/api/select_project")
async def select_project(project_id: str, user: User = Depends(get_current_user)):
    # System checks if user can access project
    if not project_manager.can_access_project(user.id, project_id):
        raise HTTPException(403, "Access denied to project")
    
    # Set session context
    session = get_user_session(user.id)
    session.selected_project = project_id
    session.project_path = project_manager.get_project_path(project_id)
    session.permission = project_manager.get_user_permission(user.id, project_id)
    
    return {"status": "project_selected", "project": project_id}
```

### Step 3: Agent Tools (Relative Paths Only)
**Files to modify:**
- `src/agents/react_agent.py` - Simplify all tools to use relative paths

**Changes:**
```python
# react_agent.py - Super simple relative path tools
@tool
async def list_folder_contents(folder_path: str = ".") -> str:
    """List contents of folder in current project"""
    session = get_current_session()
    project_root = Path(session.project_path)
    full_path = project_root / folder_path
    
    # No permission checks needed - user already in allowed project
    return list_directory_contents(full_path)

# All other tools follow same pattern - just relative paths
```

### Step 4: Simple Admin & Project Management UI
**Files to create:**
- `src/api/project_routes.py` - Project management endpoints
- `frontend/src/components/ProjectSelector.jsx` - Project selection UI
- `frontend/src/components/AdminPanel.jsx` - User/project admin interface

**Features:**
```python
# project_routes.py
@router.get("/api/projects")
async def get_user_projects(user: User = Depends(get_current_user)):
    """Get list of projects user can access"""
    projects = project_manager.get_user_projects(user.id)
    return {"projects": projects}

@router.post("/api/projects/create")  
async def create_project(name: str, user: User = Depends(get_current_user)):
    """Create new project"""
    project_id = project_manager.create_project(user.id, name)
    return {"project_id": project_id}

@router.post("/api/projects/{project_id}/share")
async def share_project(project_id: str, username: str, user: User = Depends(get_current_user)):
    """Share project with another user"""
    project_manager.share_project(project_id, user.id, username)
    return {"status": "shared"}
```

### What Changes vs What Stays

## **🔒 CRITICAL SECURITY PRINCIPLE:**
**Projects are isolated at the system level. Agent works with relative paths only within selected project.**

**Major Changes:**
- ✅ Add project-based storage outside codebase
- ✅ Add authentication with project selection
- ✅ Modify all tools to use relative paths only  
- ✅ Add project sharing and management system
- ❌ Remove global `data/` folder assumption

**Stays The Same:**
- ✅ LangGraph React agent architecture (even simpler now!)
- ✅ File conversion system (just within selected project)
- ✅ Memory management (just per-project memory files)
- ✅ Frontend chat interface (just add project selector)
- ✅ Tool system (simplified - no complex path logic needed)

### Implementation Complexity: **Very Simple**

**Core Architecture:**
```
Login → Project Selection → Agent Tools (Relative Paths Only)
            ↓
    /external/lab_data/projects/selected_project/
                       ↑
              Agent operates here only
```

**Core changes needed:**
1. **✅ FIXED: Immediate path bug** - `src/api/file_routes.py` line 196 (Fixed 2025-08-15)
2. **Project storage**: External folder management (0.5 day)
3. **Authentication & project selection**: Login + project picker (1 day)  
4. **Agent simplification**: Relative paths only (0.5 day) - **HUGE win: ~50 lines → ~5 lines per tool**
5. **Project management UI**: Create/share projects (1 day)

**Total effort: ~3 days** for project-based multi-user system.

### **Path Resolution Migration Strategy**

**Current Complex System** (to be replaced):
```python
# src/api/file_routes.py - Complex path reconstruction
relative_path = str(dest_dir.relative_to(project_root))
path_parts = relative_path.split('/')
for part in path_parts:
    if part.startswith('exp_'):  # Brittle experiment detection
        experiment_id = part
        break
originals_dir = Path(project_root) / experiment_id / "originals"  # BUG: reconstruction fails
```

**New Simple System** (after refactoring):
```python  
# src/projects/session.py - Bulletproof session-based resolution
class ProjectSession:
    def resolve_path(self, relative_path: str) -> Path:
        return self.project_path / relative_path  # Always works
        
# Tools become trivial:
@tool
async def upload_file(filename: str, destination: str = ".") -> str:
    session = get_current_session()
    upload_path = session.resolve_path(destination)
    # No experiment ID extraction, no path reconstruction, no guessing!
```

**Migration Benefits**:
- **Eliminates**: ~500 lines of complex path resolution logic
- **Prevents**: All path-related bugs (yours + future ones)  
- **Simplifies**: Agent tools from ~50 lines to ~5 lines each
- **Adds**: Multi-user support as a bonus

### Benefits of Project-Centric Approach

✅ **Simpler Agent**: No complex path resolution, just relative paths  
✅ **Better Security**: Complete project isolation at filesystem level  
✅ **Cleaner UX**: User selects project once, works within it naturally  
✅ **Easier Collaboration**: Share entire project, not individual files  
✅ **Admin Friendly**: Clear project ownership and sharing model  
✅ **Storage Flexible**: Projects stored outside codebase, easy backup/archive

**Key insight**: Session-based project selection eliminates all the complexity of multi-workspace path resolution. Agent just works with simple relative paths like `"./experiments/data.csv"`.

---

*Simple, agent-friendly multi-user design focused on workspace boundaries rather than complex permissions.*