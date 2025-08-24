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

## Content Analysis System (v1.2 Update)

**Added**: 2025-01-22  
**Philosophy**: Simple inline processing, no complex background jobs

### Analysis Flow for Imported Data

When user imports existing data:

1. **Upload Phase** (0-5 seconds)
   - Files uploaded to server
   - Structure preserved
   - Status: "Uploading files..."

2. **Conversion Phase** (5-30 seconds)
   - PDF/DOCX/PPTX → Markdown
   - MinerU v2 for PDFs, MarkItDown for Office
   - Status: "Converting documents..." with file names

3. **Analysis Phase** (30-60 seconds) - NEW
   - React agent analyzes converted markdown files
   - Extracts key insights per document
   - Identifies experiment type, methods, results
   - Status: "Analyzing content..." with progress

4. **README Generation** (60-65 seconds) - ENHANCED
   - Creates enriched README with actual insights
   - Not just file listings but real understanding
   - Includes experiment summaries, key findings
   - Status: "Generating project documentation..."

5. **Complete** 
   - Project ready with intelligent documentation
   - User sees summary of what was found

### Status Tracking Implementation

**Simple WebSocket messages - no new infrastructure:**

```python
# In project_routes.py during import
await notify_status(session_id, "uploading", {"progress": 20, "message": "Uploading files..."})
await notify_status(session_id, "converting", {"progress": 40, "message": f"Converting {file.name}..."})
await notify_status(session_id, "analyzing", {"progress": 60, "message": f"Analyzing {converted_file}..."})
await notify_status(session_id, "generating", {"progress": 80, "message": "Generating documentation..."})
await notify_status(session_id, "complete", {"progress": 100, "message": "Project created successfully!"})
```

**Frontend display - reuse existing components:**

```jsx
// In ProjectCreationModal.jsx
{importStatus && (
  <div className="import-status">
    <div className="progress-bar">
      <div className="progress-fill" style={{width: `${importStatus.progress}%`}} />
    </div>
    <p>{importStatus.message}</p>
  </div>
)}
```

### Content Analysis Approach

**Multi-step React agent process:**

1. **Phase 1: Structure Discovery**
   - Agent uses `list_folder_contents` to understand project structure
   - Identifies all experiment folders and file organization
   - Maps out which documents were converted

2. **Phase 2: Deep Document Analysis**
   - Agent uses `read_file` to read all converted markdown documents
   - Focuses on protocols, results, analyses, presentations
   - Extracts actual data, methods, findings (not structured parsing!)

3. **Phase 3: Comprehensive README Generation**
   - Agent writes professional scientific documentation
   - Includes: Project Overview, Research Questions, Methodology
   - Per-experiment sections with objectives, methods, results, conclusions
   - Overall findings synthesis and next steps

**Key Principles:**
- NO structured extraction or parsing
- NO keyword matching or pattern recognition  
- Agent naturally understands content in ANY language
- Agent generates README directly in natural language
- Comprehensive prompts guide agent through research process

### Enhanced README Format

**Before (current - just file listing):**
```markdown
### Experiment: Jan15_CD45_enriched
- Files: 23 items
- Converted Documents: 3 files
```

**After (with comprehensive agent analysis):**
```markdown
# T-Cell Exhaustion in Aging Study

## Project Overview

This project investigates T-cell exhaustion markers in aging populations, focusing on the differential 
expression of PD-1, TIM-3, and LAG-3 on CD8+ T cells from young (20-30 years) versus elderly (70-80 years) 
donors. The hypothesis is that aging leads to increased expression of exhaustion markers, contributing to 
immunosenescence and reduced vaccine efficacy in elderly populations.

The project employs flow cytometry, single-cell RNA sequencing, and functional assays to characterize 
exhausted T-cell populations. Initial experiments focus on establishing baseline expression patterns, 
followed by stimulation assays to assess functional capacity.

## Research Questions

1. Do elderly individuals show higher baseline expression of T-cell exhaustion markers?
2. Is there a correlation between exhaustion marker expression and cytokine production capacity?
3. Can exhausted T-cells from elderly donors be rejuvenated through checkpoint blockade?
4. What transcriptional signatures define exhausted vs functional T-cells in aging?

## Methodology

The project uses peripheral blood mononuclear cells (PBMCs) isolated via Ficoll density gradient 
centrifugation. CD8+ T cells are enriched using magnetic bead separation (Miltenyi, >95% purity required). 
Flow cytometry panels include CD3, CD8, CD45RA, CCR7 for subset identification, and PD-1, TIM-3, LAG-3, 
CTLA-4 for exhaustion markers. Functional assessments use PMA/ionomycin stimulation with intracellular 
cytokine staining for IFN-γ, TNF-α, and IL-2.

## Experiments

### Experiment: Jan15_CD45_enriched
**Objective**: Establish CD45+ cell enrichment protocol for downstream T-cell isolation
**Date**: January 15, 2025
**Status**: Completed

**Methods**:
- Ficoll-Paque PLUS density gradient (1.077 g/mL)
- Anti-CD45 MicroBeads (Miltenyi, 20 μL per 10^7 cells)
- LS columns on QuadroMACS separator
- Flow validation using CD45-APC, 7-AAD viability

**Key Results**:
- Starting material: 2.3 × 10^7 PBMCs from 10mL blood
- Post-enrichment yield: 1.8 × 10^6 CD45+ cells
- Purity: 94.3% CD45+ (flow cytometry)
- Viability: 82% (7-AAD negative)
- Recovery rate: 78% (below expected 85-90%)

**Conclusions**:
Protocol successfully enriches CD45+ cells but recovery needs optimization. Cell clumping observed, 
likely from incomplete bead removal.

**Issues/Notes**:
- Increase wash steps from 2 to 3 to reduce clumping
- Consider using CliniMACS PBS/EDTA buffer instead of plain PBS
- Some RBC contamination noted - may need additional lysis step

### Experiment: Jan22_exhaustion_panel
**Objective**: Optimize 8-color flow cytometry panel for T-cell exhaustion markers
**Date**: January 22, 2025
**Status**: In Progress

[Additional experiments would be documented similarly...]

## Overall Findings

Initial experiments establish robust cell isolation protocols with >94% purity for CD45+ enrichment. 
Preliminary flow cytometry data shows increased PD-1 expression on CD8+ T cells from elderly donors 
(mean 42.3% vs 18.7% in young, p<0.01). Technical challenges include cell clumping during magnetic 
separation and RBC contamination requiring protocol optimization.

## File Organization

- `/experiments/` - Individual experiment folders with raw data, protocols, and analyses
- Each experiment contains converted markdown documents from original protocols and results
- Flow cytometry FCS files stored in `/raw_data/` subdirectories
- Analysis scripts and figures in `/analysis/` subdirectories

## Next Steps

1. Optimize enrichment protocol to achieve >85% recovery
2. Complete titration of exhaustion marker antibodies
3. Process samples from 5 young and 5 elderly donors for pilot study
4. Submit samples for scRNA-seq library preparation

---
*This documentation was generated from imported experimental data on 2025-01-22*
```

## Future Enhancements (NOT NOW)

These are noted but NOT for immediate implementation:
- Project templates (avoid overengineering)
- Collaborative projects (adds complexity)
- Version control integration (later phase)
- Project archival (when needed)
- Multi-step wizards (unnecessary complexity)

## Implementation Status

1. ✅ Remove demo project button
2. ✅ Add Create Project button  
3. ✅ Build ProjectCreationModal component
4. ✅ Implement /api/projects/create-new
5. ✅ Implement /api/projects/import-data
6. ✅ Auto-convert PDF/DOCX/PPTX files
7. ✅ Generate README for each experiment
8. ✅ Create file registry for tracking
9. 🚧 Add AI content analysis after conversion
10. 🚧 Add real-time status tracking during import
11. 🚧 Test both creation paths in production

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