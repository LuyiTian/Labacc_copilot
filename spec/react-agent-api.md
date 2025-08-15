# React Agent API Specification v2.1

## Executive Summary

This specification documents the simplified React Agent API architecture implemented in LabAcc Copilot v2.1, using LangGraph's React agent pattern with tools.

## 1. Architecture Overview

### Current Implementation (v2.1)
```
User → React Frontend → FastAPI → LangGraph React Agent → Tools → Response
```

### Key Components
- **React Frontend**: localhost:5173 (unchanged)
- **FastAPI Backend**: localhost:8002
- **React Agent**: Single LangGraph agent with tools
- **Tools**: Simple @tool decorated functions

## 2. API Endpoints

### 2.1 Chat Endpoints

#### Initialize Session
```http
POST /api/chat/init
Content-Type: application/json

{
  "currentFolder": string | null,
  "selectedFiles": string[]
}

Response:
{
  "sessionId": string,
  "status": "initialized"
}
```

#### Send Message
```http
POST /api/chat/message
Content-Type: application/json

{
  "sessionId": string,
  "message": string,
  "currentFolder": string | null,
  "selectedFiles": string[]
}

Response:
{
  "response": string,
  "author": "Assistant",
  "sessionId": string
}
```

#### Update Context
```http
POST /api/chat/context
Content-Type: application/json

{
  "sessionId": string,
  "currentFolder": string | null,
  "selectedFiles": string[]
}

Response:
{
  "status": "context_updated"
}
```

### 2.2 File Management Endpoints (unchanged)

#### List Files
```http
GET /api/files/list?path=/

Response:
{
  "files": [
    {
      "name": string,
      "type": "file" | "folder",
      "path": string,
      "size": number
    }
  ]
}
```

#### Upload Files
```http
POST /api/files/upload
Content-Type: multipart/form-data

FormData:
- files: File[]
- path: string

Response:
{
  "uploaded": string[],
  "failed": string[]
}
```

## 3. React Agent Implementation

### 3.1 Agent Structure
```python
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

# Define tools
@tool
def scan_project() -> str:
    """Scan all experiments in the project."""
    # Implementation
    return "Found experiments: ..."

@tool
def analyze_experiment(folder_name: str) -> str:
    """Analyze a specific experiment folder."""
    # Implementation
    return f"Analysis of {folder_name}: ..."

# Create agent
agent = create_react_agent(llm, [scan_project, analyze_experiment, ...])
```

### 3.2 Message Processing
```python
async def handle_message(message: str, session_id: str) -> str:
    """Process user message through React agent."""
    
    # Create agent
    agent = create_simple_agent()
    
    # Invoke with message
    result = agent.invoke({
        "messages": [HumanMessage(content=message)]
    })
    
    # Extract response
    for msg in reversed(result["messages"]):
        if isinstance(msg, AIMessage):
            return msg.content
    
    return "No response generated."
```

## 4. Available Tools

### 4.1 Core Analysis Tools

#### scan_project
```python
@tool
def scan_project() -> str:
    """Scan all experiments in the project and show their current status."""
```

#### list_folder_contents
```python
@tool
def list_folder_contents(folder_path: str) -> str:
    """List files and subfolders in a specified folder.
    Args:
        folder_path: Path to the folder (e.g., 'exp_001_pcr' or full path)
    """
```

#### analyze_data
```python
@tool
def analyze_data(file_path: str) -> str:
    """Analyze experimental data file with context awareness.
    Args:
        file_path: Path to the data file (relative or absolute)
    """
```

#### diagnose_issue
```python
@tool
def diagnose_issue(problem: str) -> str:
    """Diagnose experimental issues using scientific reasoning.
    Args:
        problem: Description of the problem
    """
```

#### suggest_optimization
```python
@tool
def suggest_optimization(aspect: str) -> str:
    """Suggest optimizations based on successful patterns.
    Args:
        aspect: What to optimize (e.g., 'PCR conditions', 'yield', 'purity')
    """
```

#### run_deep_research
```python
@tool
def run_deep_research(query: str) -> str:
    """Search scientific literature and web for relevant information.
    Args:
        query: Research query
    """
```

#### create_new_experiment
```python
@tool
def create_new_experiment(name: str, motivation: str, key_question: str) -> str:
    """Create a new experiment with initial README memory.
    Args:
        name: Experiment name
        motivation: Why this experiment
        key_question: Main research question
    """
```

### 4.2 File Reading Tools (NEW)

#### read_file
```python
@tool
def read_file(file_path: str) -> str:
    """Read file contents, automatically using converted version if available.
    
    This tool transparently handles both original and converted files.
    For PDFs, Office docs, it returns the markdown-converted content.
    For text files, CSVs, it returns the original content.
    
    Args:
        file_path: Path to the file (original or converted)
    
    Returns:
        File contents as string (markdown for converted docs, raw for text)
    
    Note: Conversion happens automatically on upload - this tool just reads.
    """
```

### 4.3 Figure Analysis Tool (NEW)

#### analyze_figure_with_context
```python
@tool
def analyze_figure_with_context(
    image_path: str,
    context: str,
    experiment_id: Optional[str] = None
) -> str:
    """Analyze a scientific figure (gel, microscopy, plot) with contextual information.
    
    This tool understands the figure in the context of the experiment,
    using both visual analysis and text context to provide meaningful insights.
    
    Args:
        image_path: Path to the image file (png, jpg, tiff, etc.)
        context: Related text context about this figure (e.g., "Western blot 
                 for protein X under conditions Y", "Gel showing PCR products 
                 from samples 1-6", "Microscopy of cells treated with drug Z")
        experiment_id: Optional experiment ID for additional context from README
    
    Returns:
        Detailed analysis including:
        - Visual interpretation (bands, signals, morphology)
        - Quality assessment (exposure, artifacts, controls)
        - Quantitative insights if applicable
        - Suggestions for improvement
        - Comparison with expected results based on context
    
    Example:
        analyze_figure_with_context(
            "exp_001/western_blot.png",
            "Western blot of HEK293 cells transfected with GFP-tagged protein, 
             expected size 75kDa, loading control GAPDH at 37kDa",
            "exp_001_protein_expression"
        )
    """
```

### 4.4 Enhanced Data Analysis Tools (NEW)

#### analyze_excel_data
```python
@tool
def analyze_excel_data(
    file_path: str,
    sheet_name: Optional[str] = None,
    analysis_type: Literal["summary", "statistics", "trends", "quality"] = "summary"
) -> str:
    """Specialized analysis for Excel experimental data.
    
    Args:
        file_path: Path to Excel file
        sheet_name: Specific sheet to analyze (None for all sheets)
        analysis_type: Type of analysis to perform
            - summary: Overview of data structure and content
            - statistics: Descriptive statistics, outliers, distributions
            - trends: Time series, dose-response, correlations
            - quality: Data quality checks, missing values, anomalies
    
    Returns:
        Analysis results with visualizations and insights
    """
```

#### compare_datasets
```python
@tool
def compare_datasets(
    file_paths: List[str],
    comparison_type: Literal["replicates", "conditions", "time_series"] = "replicates"
) -> str:
    """Compare multiple experimental datasets for consistency and differences.
    
    Args:
        file_paths: List of data files to compare
        comparison_type: How to compare the datasets
            - replicates: Check reproducibility between replicates
            - conditions: Compare different experimental conditions
            - time_series: Analyze temporal changes
    
    Returns:
        Comparison results with statistical tests and visualizations
    """
```

## 5. Adding New Capabilities

### 5.1 Simple Tool Addition
```python
# 1. Define the tool
@tool
def new_capability(param: str) -> str:
    """Description for LLM to understand when to use this tool."""
    # Implementation
    return "Result"

# 2. Add to tools list
tools = [
    scan_project,
    analyze_experiment,
    new_capability,  # Just add here!
    ...
]

# 3. That's it! The agent will automatically use it when appropriate
```

## 6. Key Improvements in v2.1

### Simplifications
- **No orchestrators**: Single React agent handles everything
- **No intent detection**: LLM naturally understands intent
- **No keyword matching**: Works in any language
- **No complex routing**: Agent selects tools automatically

### Benefits
- **70% less code** than v2.0
- **Easier to maintain** and extend
- **Natural language** understanding
- **Multi-language** support out of the box

## 7. Testing

### Quick Test
```bash
# Start backend
uv run uvicorn src.api.app:app --port 8002 --reload

# Test with curl
curl -X POST http://localhost:8002/api/chat/init -H "Content-Type: application/json" -d '{}'

# Send message
curl -X POST http://localhost:8002/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{"sessionId": "...", "message": "Scan my experiments"}'
```

### Direct Agent Test
```bash
uv run python src/agents/react_agent.py
```

## 8. Performance Characteristics

- **Response Time**: 2-3 seconds for most queries
- **Deep Research**: 10-30 seconds (Tavily API)
- **Concurrent Sessions**: Supported
- **Memory**: Conversation history per session

## 9. Error Handling

The system gracefully handles:
- Invalid session IDs
- Tool execution failures
- LLM timeouts
- File operation errors

All errors return structured responses with helpful messages.

## 10. Backend File Processing (NOT Agent Tools)

### 10.1 Internal Conversion Functions

These functions run automatically on file upload and are NOT exposed as agent tools:

```python
# Backend internal functions (src/api/file_conversion.py)

async def convert_office_to_markdown_internal(
    file_path: str,
    output_path: str
) -> bool:
    """Internal function for automatic Office → Markdown conversion.
    Uses MarkItDown. Called automatically on upload."""
    
async def convert_pdf_to_markdown_internal(
    file_path: str,
    output_path: str,
    method: str = "auto"
) -> bool:
    """Internal function for automatic PDF → Markdown conversion.
    Uses MinerU. Called automatically on upload."""

def update_file_registry(
    experiment_id: str,
    file_info: dict
) -> None:
    """Updates .labacc/file_registry.json with conversion info."""
```

### 10.2 File Conversion Setup

#### MarkItDown Installation
```bash
pip install 'markitdown[all]'  # Or selective: [docx,pptx,xlsx,pdf]
```

#### MinerU Installation
```bash
# Basic installation (CPU/GPU auto-detect)
pip install mineru[core]

# With SGLang acceleration (recommended for GPU)
pip install mineru[all]
```

### 10.3 Conversion Flow

1. **User uploads file** → Backend receives
2. **Backend converts** → Stores in `.labacc/converted/`
3. **Backend updates registry** → Tracks both paths
4. **Agent notified** → "New file uploaded: protocol.pdf"
5. **Agent reads** → Uses `read_file` tool, gets markdown version

### 10.4 Tool Implementation Guidelines

1. **read_file**: Reads converted version if exists, else original
2. **analyze_figure_with_context**: Combine vision API with context
3. **analyze_excel_data**: Deep analysis beyond conversion
4. **compare_datasets**: Cross-file comparison

### 10.3 Performance Considerations

- **Office files**: MarkItDown is CPU-fast, no GPU needed
- **PDFs**: MinerU auto-detects CUDA/MPS, use pipeline backend by default
- **Images**: Consider caching analysis results
- **Large files**: Implement streaming for memory efficiency

### 10.4 License Notes

- **MarkItDown**: MIT License (permissive)
- **MinerU**: AGPL-3.0 (copyleft, review for commercial use)

## 11. Future Enhancements (v2.3)

- Background task execution
- Proactive monitoring tools
- Scheduled analysis
- Real-time notifications
- Batch file processing
- Advanced figure comparison

---

**Version**: 3.0.0  
**Status**: Unified File Processing Architecture  
**Architecture**: LangGraph React Agent with Backend Conversion Pipeline  
**Last Updated**: 2025-08-15

**Key v3.0 Changes**:
- File conversion is now automatic on upload (backend responsibility)
- Agent tools simplified - only `read_file` needed, not conversion tools
- Clear separation between backend functions and agent tools
- Transparent handling of converted content