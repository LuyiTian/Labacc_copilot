# Project and Experiment Renaming Support Specification

**Version**: 1.0  
**Date**: 2025-01-20  
**Status**: 🚧 TODO - Not Yet Implemented  
**Priority**: Medium  
**Philosophy**: Scientists rename things as understanding evolves - the system should support this

## Problem Statement

Scientists frequently need to rename projects and experiments as their understanding evolves:
- Initial name: "exp_001" → Final name: "PCR_optimization_62C"
- Project evolves: "test_project" → "CRISPR_knockout_study"
- Better organization: "Jan15_data" → "2025_01_15_Western_blot"

Currently, the LabAcc Copilot system **does not support renaming** without breaking functionality.

## Current Limitations

### 1. No Project Renaming
- No API endpoint exists for renaming projects
- Project ID is used as folder name (`project_crispr_study_a3f2d1`)
- Changing folder name breaks all references

### 2. Broken Experiment Renaming
While folders can be moved/renamed via `/api/files/move`, this breaks:
- **Memory system**: Looks for README at old path
- **File registry**: Contains hardcoded paths to converted files
- **Agent tools**: Reference experiments by folder name
- **Session context**: May have cached paths

### 3. Tight Coupling Issues
```python
# Current problematic patterns:
readme_path = project_root / experiment_id / "README.md"  # experiment_id IS the folder name
registry["files"]["protocol.pdf"]["experiment"] = "exp_001"  # Hardcoded folder name
```

## Proposed Solution

### Architecture Change: Stable IDs vs Display Names

Separate internal IDs from user-visible names:

```json
// .labacc/experiment_metadata.json
{
  "id": "exp_a3f2d1c8",           // Stable, never changes
  "display_name": "PCR at 62°C",   // User-friendly, can change
  "folder_name": "PCR_62C_final",  // Physical folder, can change
  "created": "2025-01-20",
  "renamed_from": ["exp_001", "PCR_test"],  // History
  "last_renamed": "2025-01-21"
}
```

### New API Endpoints

#### 1. Rename Project
```python
@router.put("/api/projects/{project_id}/rename")
async def rename_project(
    project_id: str,
    new_name: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Rename a project (display name only, not folder)
    
    Steps:
    1. Verify user has owner/admin permission
    2. Update project metadata display name
    3. Update README.md title
    4. Log the change
    5. Return success
    """
```

#### 2. Rename Experiment
```python
@router.put("/api/experiments/{experiment_id}/rename")
async def rename_experiment(
    experiment_id: str,
    new_name: str,
    update_folder: bool = False,  # Whether to rename physical folder
    session_id: str = Header(None)
):
    """
    Rename an experiment with cascade updates
    
    Steps:
    1. Load experiment metadata
    2. If update_folder:
       - Rename physical folder
       - Update all paths in file_registry.json
    3. Update display name in metadata
    4. Update README.md title
    5. Notify memory system of change
    6. Clear any cached paths in session
    7. Return new paths
    """
```

### File Registry Update Logic

```python
def update_registry_after_rename(
    registry_path: Path,
    old_experiment: str,
    new_experiment: str
):
    """Update all paths in registry after experiment rename"""
    registry = json.loads(registry_path.read_text())
    
    for file_id, file_info in registry["files"].items():
        # Update experiment reference
        if file_info.get("experiment") == old_experiment:
            file_info["experiment"] = new_experiment
        
        # Update conversion paths
        if "conversion" in file_info:
            old_path = file_info["conversion"]["markdown_path"]
            new_path = old_path.replace(f"/{old_experiment}/", f"/{new_experiment}/")
            file_info["conversion"]["markdown_path"] = new_path
    
    registry_path.write_text(json.dumps(registry, indent=2))
```

### Memory System Adaptation

```python
class SimpleMemoryManager:
    def load_memory(self, experiment_id: str) -> SimpleMemory:
        """Load memory using stable ID, not folder name"""
        # First, resolve actual folder from metadata
        metadata_path = self.project_root / ".labacc" / "experiments.json"
        experiments = json.loads(metadata_path.read_text())
        
        exp_info = experiments.get(experiment_id)
        if not exp_info:
            # Fallback: assume experiment_id is folder name (backwards compat)
            folder_name = experiment_id
        else:
            folder_name = exp_info["folder_name"]
        
        readme_path = self.project_root / folder_name / "README.md"
        # ... rest of loading logic
```

### Frontend UI Changes

```jsx
// Add rename button in file manager
function ExperimentItem({ experiment }) {
  const [isRenaming, setIsRenaming] = useState(false);
  const [newName, setNewName] = useState(experiment.display_name);
  
  const handleRename = async () => {
    await fetch(`/api/experiments/${experiment.id}/rename`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`
      },
      body: JSON.stringify({
        new_name: newName,
        update_folder: true  // User choice
      })
    });
    
    // Refresh file list
    await loadFiles();
  };
  
  return (
    <div className="experiment-item">
      {isRenaming ? (
        <input 
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
          onBlur={handleRename}
        />
      ) : (
        <span onClick={() => setIsRenaming(true)}>
          {experiment.display_name}
        </span>
      )}
    </div>
  );
}
```

## Migration Path

### Phase 1: Metadata Introduction (Non-breaking)
1. Add `.labacc/experiments.json` to track metadata
2. Update tools to check metadata first, fall back to folder names
3. No breaking changes for existing projects

### Phase 2: Rename API
1. Implement rename endpoints
2. Add UI rename functionality  
3. Update file registry on renames

### Phase 3: Full Stable IDs
1. Generate UUIDs for all experiments
2. Update all tools to use stable IDs
3. Migrate existing projects

## Testing Requirements

1. **Rename project** → Verify all sessions still work
2. **Rename experiment** → Verify:
   - Memory system finds new README
   - File registry paths updated
   - Converted files still accessible
   - Agent tools work with new name
3. **Rename with active session** → Session updates properly
4. **Rename shared project** → Other users see update
5. **Rename history** → Can see previous names

## Backwards Compatibility

- Existing projects without metadata continue to work
- Folder names used as IDs when metadata missing
- Gradual migration path for old projects

## Security Considerations

- Only project owner or admin can rename
- Validate new names (no path traversal)
- Log all renames for audit trail
- Preserve rename history

## Success Metrics

- Users can rename without breaking functionality
- No data loss during rename operations
- Memory and registry stay consistent
- Clear rename history for traceability

## Implementation Priority

**Medium Priority** - Important for usability but not blocking core functionality

**Estimated Effort**: 2-3 days
- 1 day: Backend API and cascade logic
- 1 day: Frontend UI and testing
- 0.5 day: Documentation and migration guide

## Notes

This aligns with the Linus Torvalds philosophy - scientists need to rename things as they learn more about their experiments. Fighting this natural workflow is bad design. The system should adapt to how scientists actually work, not force them into rigid naming schemes.

---
**Status**: Awaiting implementation  
**Last Updated**: 2025-01-20  
**Author**: LabAcc Development Team