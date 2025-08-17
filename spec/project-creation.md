# Project Creation System Specification

**Version**: 1.1  
**Author**: LabAcc Copilot Team  
**Date**: 2025-01-16  
**Status**: ✅ FULLY IMPLEMENTED  
**Philosophy**: Simple, direct, no overengineering (Linus Torvalds approach)

## Overview

Project creation in LabAcc Copilot supports two fundamental scientific workflows:
1. **Hypothesis-Driven**: Planning experiments before execution
2. **Data-Driven**: Organizing existing experimental data

Both paths are equally valid and reflect real laboratory practices across cultures and methodologies.

## Two Creation Paths

### Path 1: Start New Research (Empty Project)

**Use Case**: Scientist has a hypothesis/idea but no data yet  
**Icon**: 🧪 (Empty beaker)  
**Workflow**:
1. User clicks "Create Project" → selects "Start New Research"
2. Simple form appears:
   - Project Name (required)
   - Research Question/Hypothesis (required, multiline)
   - Planned Experiments (optional, comma-separated list)
   - Expected Outcomes (optional, multiline)
3. System creates:
   ```
   data/{user}_projects/{project_name}/
   ├── README.md              # Auto-generated with hypothesis
   ├── .labacc/
   │   └── project_config.json
   └── experiments/          # Empty, ready for data
   ```

### Path 2: Import Existing Data

**Use Case**: Scientist has folders of existing experimental data  
**Icon**: 📁 (Folder)  
**Workflow**:
1. User clicks "Create Project" → selects "Import Existing Data"
2. Upload interface appears:
   - Drag & drop zone for folders/zip files
   - Project Name (auto-suggested from folder name)
   - Brief Description (optional)
3. System processes:
   - Accepts: Multiple folders, ZIP archives, nested structures
   - Preserves: Original folder names and structure
   - **Auto-converts**: PDF, DOCX, PPTX → Markdown
   - Generates: README.md with discovered structure
   - **Creates**: Individual README for each experiment folder
4. File conversion:
   - Detects documents needing conversion
   - Uses MinerU v2 for PDFs
   - Uses MarkItDown for Office files
   - Preserves originals, creates .md versions
   - Tracks conversions in file registry
5. Post-import:
   - Shows conversion results to user
   - Ready for immediate AI analysis
   - All documents searchable and readable

## Implementation Details

### Frontend Component: ProjectCreationModal

```jsx
// Simplified modal with two clear options
<Modal>
  <h2>Create New Project</h2>
  
  <div className="creation-options">
    <button onClick={() => setMode('new')}>
      <span className="icon">🧪</span>
      <h3>Start New Research</h3>
      <p>Plan experiments from hypothesis</p>
    </button>
    
    <button onClick={() => setMode('import')}>
      <span className="icon">📁</span>
      <h3>Import Existing Data</h3>
      <p>Organize completed experiments</p>
    </button>
  </div>
  
  {mode === 'new' && <NewResearchForm />}
  {mode === 'import' && <DataImportForm />}
</Modal>
```

### Backend API Endpoints

#### POST /api/projects/create-new
```python
@router.post("/create-new")
async def create_new_project(request: NewProjectRequest):
    """
    Creates empty project with hypothesis-driven structure
    
    Request:
    {
        "name": "CRISPR_efficiency_study",
        "hypothesis": "Guide RNA length affects...",
        "planned_experiments": ["exp1", "exp2"],
        "expected_outcomes": "We expect to see..."
    }
    """
    # Simple implementation:
    # 1. Create project folder
    # 2. Write README.md with hypothesis
    # 3. Create empty experiment folders
    # 4. Return project_id
```

#### POST /api/projects/import-data
```python
@router.post("/import-data")
async def import_existing_data(
    files: List[UploadFile],
    name: str = Form(...),
    description: str = Form(None)
):
    """
    Imports existing experimental data
    
    Accepts:
    - Multiple folders as ZIP
    - Individual files
    - Nested folder structures
    """
    # Simple implementation:
    # 1. Extract/save uploaded files
    # 2. Preserve folder structure
    # 3. Scan and catalog all files
    # 4. Generate README from structure
    # 5. Trigger background analysis
    # 6. Return project_id
```

### File Structure Examples

#### New Research Project
```
data/alice_projects/crispr_optimization/
├── README.md
│   # CRISPR Optimization Study
│   
│   ## Research Question
│   Does guide RNA length affect CRISPR efficiency?
│   
│   ## Hypothesis
│   Shorter guide RNAs (17-18nt) will show...
│   
│   ## Planned Experiments
│   - exp_001_length_17nt
│   - exp_002_length_18nt
│   - exp_003_length_20nt
│   
│   ## Expected Outcomes
│   We expect to observe...
│
├── .labacc/
│   └── project_config.json
│       {
│         "created_at": "2025-01-16",
│         "creation_mode": "hypothesis_driven",
│         "status": "planning"
│       }
│
└── experiments/
    ├── exp_001_length_17nt/  # Empty, awaiting data
    ├── exp_002_length_18nt/  # Empty, awaiting data
    └── exp_003_length_20nt/  # Empty, awaiting data
```

#### Imported Data Project (UPDATED)
```
data/bob_projects/scrnaseq_immune_study/
├── README.md                    # Main project overview
│   # ScRNAseq Immune Study
│   
│   ## Project Structure (Auto-discovered)
│   
│   ### Experiment: Jan15_CD45_enriched
│   - Files: 23 items
│   - Converted Documents: 3 files
│     - protocol.docx → Markdown
│     - results.pdf → Markdown
│     - analysis.pptx → Markdown
│   
│   ### Experiment: Jan22_control
│   - Files: 18 items
│   - Converted Documents: 2 files
│
├── .labacc/
│   ├── project_config.json
│   └── file_registry.json      # Tracks all conversions
│
└── experiments/
    ├── Jan15_CD45_enriched/
    │   ├── README.md            # Auto-generated for this experiment
    │   ├── protocol.docx        # Original preserved
    │   ├── protocol.md          # Converted for AI analysis
    │   ├── results.pdf          # Original preserved
    │   ├── results.md           # Converted for AI analysis
    │   ├── raw_data/
    │   └── processed/
    └── Jan22_control/
        ├── README.md            # Auto-generated for this experiment
        ├── summary.pdf          # Original
        ├── summary.md           # Converted
        └── data/
```

## Key Design Decisions

### 1. No Wizards or Complex Forms
- Single modal with two clear options
- Minimal required fields
- Let AI understand context, don't force structure

### 2. Preserve User's Mental Model
- Don't rename user's folders
- Keep original file organization
- Respect existing naming conventions

### 3. Background Intelligence
- Auto-analyze imported data
- Generate insights without blocking
- Ask clarifying questions naturally

### 4. Multi-Language by Design
- No keyword matching for project types
- LLM understands research questions in any language
- Support diverse scientific thinking patterns

## User Experience Flow

### Scenario 1: Planning New Research
1. Click "➕ Create Project"
2. Select "🧪 Start New Research"
3. Enter hypothesis in native language
4. Submit → Project created instantly
5. Start adding experiments as data arrives

### Scenario 2: Organizing Existing Data
1. Click "➕ Create Project"
2. Select "📁 Import Existing Data"
3. Drag folders or ZIP file
4. Submit → Files uploaded and organized
5. Agent analyzes in background
6. Receive insights and questions in chat

## Error Handling

### Simple, Clear Feedback
- "Project name already exists"
- "Upload failed - file too large (max 500MB)"
- "Invalid file format - use ZIP for folders"

### No Complex Validation
- Don't validate hypothesis format
- Don't enforce folder structures
- Don't require specific file types

## Testing Strategy

### Unit Tests
```python
def test_create_empty_project():
    """Test hypothesis-driven project creation"""
    
def test_import_zip_file():
    """Test data import from ZIP"""
    
def test_preserve_folder_structure():
    """Ensure original structure maintained"""
```

### Integration Tests
- Create project → Add experiment → Analyze
- Import data → Background analysis → Questions
- Multi-language hypothesis → Correct project setup

## Performance Targets

- Project creation: <1 second
- Data import: <5 seconds for 100MB
- Background analysis start: <2 seconds
- Initial insights: <30 seconds

## Security Considerations

- Validate file paths (prevent traversal)
- Scan uploads for malware
- Limit file sizes (500MB default)
- User isolation (separate project folders)

## Future Enhancements (NOT NOW)

These are noted but NOT for immediate implementation:
- Project templates (avoid overengineering)
- Collaborative projects (adds complexity)
- Version control integration (later phase)
- Project archival (when needed)

## Implementation Status

1. ✅ Remove demo project button
2. ✅ Add Create Project button  
3. ✅ Build ProjectCreationModal component
4. ✅ Implement /api/projects/create-new
5. ✅ Implement /api/projects/import-data
6. ✅ Auto-convert PDF/DOCX/PPTX files
7. ✅ Generate README for each experiment
8. ✅ Create file registry for tracking
9. 🚧 Add background AI analysis trigger
10. 🚧 Test both creation paths in production

## Success Metrics

- Both paths equally accessible (no bias)
- <10 seconds from intent to working
- Zero configuration required
- Works in all languages without setup

## Philosophy Reminder

**Linus Torvalds approach**:
- Don't add features you don't need today
- Make it work, make it right, make it fast
- User's workflow > Developer's architecture
- Simplicity is the ultimate sophistication

---

**Status**: Specification Complete  
**Next Step**: Implement ProjectCreationModal component