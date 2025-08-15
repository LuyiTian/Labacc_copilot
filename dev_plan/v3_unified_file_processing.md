# V3.0: Unified File Processing & Memory System

**Version**: 3.0  
**Date**: 2025-08-15  
**Status**: Planning Complete  
**Author**: Claude (with human guidance)

## Executive Summary

Version 3.0 introduces a unified file processing system that seamlessly integrates file conversion, management, and memory updates. The key innovation is separating backend infrastructure (automatic conversion) from agent capabilities (analysis and understanding), creating a clean architecture where each component has clear responsibilities.

## Core Design Principles

1. **Separation of Concerns**: Backend handles conversion, Agent handles analysis
2. **Transparent Conversion**: Files are automatically converted on upload
3. **Single Source of Truth**: File registry tracks all conversions and metadata
4. **Natural Interaction**: Agent works with content, not file formats
5. **Complete Audit Trail**: Every file operation is tracked and versioned

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      User Layer                             │
│                  (File Upload via UI)                       │
├─────────────────────────────────────────────────────────────┤
│                   Backend Layer                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  1. File Reception                                  │   │
│  │  2. Automatic Conversion (PDF/Office → Markdown)    │   │
│  │  3. Registry Update                                 │   │
│  │  4. Agent Notification                              │   │
│  └─────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                    Agent Layer                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  1. Read converted content (via read_file tool)     │   │
│  │  2. Analyze and understand                          │   │
│  │  3. Ask contextual questions                        │   │
│  │  4. Update memory with insights                     │   │
│  └─────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                    Storage Layer                            │
│              (.labacc/converted/, originals/)               │
└─────────────────────────────────────────────────────────────┘
```

## File Storage Structure

```
data/alice_projects/
└── exp_XXX_[name]/
    ├── .labacc/                    # Hidden system folder
    │   ├── file_registry.json      # Complete file tracking
    │   ├── converted/               # Markdown versions
    │   │   ├── protocol.md         # From protocol.pdf
    │   │   ├── results.md          # From results.xlsx
    │   │   └── slides.md           # From presentation.pptx
    │   └── archive/                # Version history
    │       └── [timestamp]/        # Previous versions
    ├── originals/                  # Untouched uploaded files
    │   ├── protocol.pdf
    │   ├── results.xlsx
    │   └── presentation.pptx
    ├── data/                       # User-organized data
    ├── analysis/                   # Analysis outputs
    └── README.md                   # Experiment memory
```

## Component Specifications

### 1. Backend File Conversion Pipeline

**Location**: `src/api/file_conversion.py`

```python
class FileConversionPipeline:
    """Automatic file conversion on upload."""
    
    async def process_upload(self, file: UploadFile, experiment_id: str):
        # 1. Save original
        original_path = await self.save_original(file, experiment_id)
        
        # 2. Convert if needed
        if self.needs_conversion(file.filename):
            converted_path = await self.convert_file(original_path, experiment_id)
        else:
            converted_path = original_path
        
        # 3. Update registry
        await self.update_registry(experiment_id, {
            "filename": file.filename,
            "original": original_path,
            "converted": converted_path,
            "timestamp": datetime.now(),
            "status": "ready"
        })
        
        # 4. Notify agent
        await self.notify_agent(experiment_id, file.filename)
```

**Conversion Methods**:
- **PDF Files**: Use MinerU with pipeline backend (auto-detect GPU)
- **Office Files**: Use MarkItDown (fast, CPU-only)
- **Text Files**: No conversion needed
- **Images**: Store as-is, analyze with vision tools

### 2. File Registry System

**Location**: `.labacc/file_registry.json`

```json
{
  "version": "3.0",
  "experiment_id": "exp_001_pcr_optimization",
  "files": {
    "protocol.pdf": {
      "original": {
        "path": "originals/protocol.pdf",
        "size": 245632,
        "hash": "sha256:abc123..."
      },
      "converted": {
        "path": ".labacc/converted/protocol.md",
        "size": 18432,
        "method": "MinerU",
        "timestamp": "2025-08-15T10:00:05Z"
      },
      "metadata": {
        "upload_time": "2025-08-15T10:00:00Z",
        "analyzed": true,
        "summary": "PCR protocol with touchdown cycling",
        "user_context": "Modified for difficult templates"
      }
    }
  }
}
```

### 3. Agent Tool Updates

**Modified Tools**:

```python
@tool
def read_file(file_path: str) -> str:
    """Read file contents, using converted version if available.
    
    Smart routing:
    - If file_path is a PDF/Office doc, returns markdown version
    - If file_path is text/CSV, returns original
    - Handles both original and converted paths transparently
    """
    registry = load_file_registry(get_experiment_from_path(file_path))
    
    # Check if this is a tracked file
    for filename, info in registry['files'].items():
        if file_path in [info['original']['path'], info['converted']['path']]:
            # Return the best version (converted if available)
            if info['converted']['path'] and os.path.exists(info['converted']['path']):
                return read(info['converted']['path'])
            return read(info['original']['path'])
    
    # Fallback to direct read
    return read(file_path)
```

**Removed Tools** (now internal functions):
- `convert_office_to_markdown` - Automatic on upload
- `convert_pdf_to_markdown` - Automatic on upload

**Unchanged Tools**:
- All other existing tools remain the same
- Agent focuses on analysis, not conversion

### 4. Proactive Analysis Workflow

**Enhanced with Conversion**:

1. **Upload Trigger**: User uploads files (max 3)
2. **Backend Processing**:
   - Save originals
   - Convert to markdown
   - Update registry
3. **Agent Notification**: "New files uploaded: protocol.pdf, results.xlsx"
4. **Agent Analysis**:
   - Reads converted content via `read_file`
   - Analyzes using existing tools
5. **Context Gathering**:
   - Agent asks natural questions
   - User provides experimental context
6. **Memory Update**:
   - Combines file info + analysis + context
   - Updates README with complete picture

## Implementation Phases

### Phase 1: Backend Infrastructure (Week 1)
- [ ] Implement `FileConversionPipeline` class
- [ ] Set up MarkItDown for Office files
- [ ] Set up MinerU for PDF files
- [ ] Create file registry system

### Phase 2: Storage Management (Week 1)
- [ ] Implement `.labacc/` folder structure
- [ ] Create registry update functions
- [ ] Add versioning/archive support
- [ ] Implement cleanup policies

### Phase 3: Agent Integration (Week 2)
- [ ] Update `read_file` tool with smart routing
- [ ] Remove conversion tools from agent
- [ ] Update agent prompts for new workflow
- [ ] Test transparent file reading

### Phase 4: Proactive Analysis (Week 2)
- [ ] Implement upload notification system
- [ ] Update WebSocket for real-time updates
- [ ] Enhance context gathering flow
- [ ] Integrate with memory system

### Phase 5: Testing & Refinement (Week 3)
- [ ] Test various file formats
- [ ] Handle edge cases (corrupted files, etc.)
- [ ] Performance optimization
- [ ] Documentation updates

## Success Metrics

1. **Conversion Success Rate**: >95% for standard formats
2. **Processing Speed**: <5 seconds for typical files
3. **Agent Transparency**: Agent never needs to call conversion
4. **Memory Quality**: All file context captured in README
5. **User Experience**: Seamless upload → analysis flow

## Risk Mitigation

### Technical Risks
- **Conversion Failures**: Fallback to original with user notification
- **Large Files**: Implement size limits and chunking
- **GPU Availability**: MinerU falls back to CPU automatically

### Architectural Risks
- **Complexity**: Keep clean separation between layers
- **Debugging**: Comprehensive logging at each step
- **Rollback**: Archive system allows recovery

## Migration Path

### From v2.x to v3.0
1. **Existing Files**: Run batch conversion on first access
2. **Registry Creation**: Build from filesystem scan
3. **Backward Compatibility**: Agent tools work with old paths

## Long-term Vision

### v3.1 Enhancements
- Batch file processing
- Background re-conversion with better models
- Cross-experiment file similarity detection

### v3.2 Advanced Features
- Custom conversion pipelines per file type
- Streaming conversion for large files
- Real-time collaborative editing of converted content

## Conclusion

Version 3.0 creates a robust, scalable file processing system that cleanly separates infrastructure concerns from agent intelligence. By handling conversion automatically at upload time, we free the agent to focus on what it does best: understanding and analyzing scientific content.

The unified architecture ensures:
- **Simplicity**: Agent doesn't deal with file formats
- **Reliability**: Consistent conversion pipeline
- **Traceability**: Complete audit trail
- **Flexibility**: Easy to add new formats

This design positions LabAcc Copilot as a sophisticated laboratory data management system while maintaining the simplicity that makes it accessible to researchers.

---

**Approval Status**: Ready for Implementation  
**Next Steps**: Begin Phase 1 implementation  
**Questions**: Review with team before starting