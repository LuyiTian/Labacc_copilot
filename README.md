# LabAcc Copilot

AI laboratory assistant for experimental data analysis and optimization with automatic document conversion.

## 🚀 Quick Start

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup
git clone <repo-url>
cd Labacc_copilot

# Create Python 3.12 environment (required for MinerU v2)
uv python install 3.12
uv venv .venv --python 3.12
uv sync

# Install frontend dependencies
cd frontend && npm install && cd ..

# Set API keys
export TAVILY_API_KEY="your-key"
export OPENROUTER_API_KEY="your-key"

# For MinerU models (use modelscope in China/Asia)
export MINERU_MODEL_SOURCE=modelscope  # or huggingface (default)

# Start
./start-dev.sh
# Open http://localhost:5173
```

## 🎯 What You Can Do

### Project Management
- **Create new project** - Start from hypothesis or import existing data
- **Import experiments** - Upload ZIP files with automatic PDF/Office conversion
- **Browse experiments** - Navigate your project structure visually

### File Operations  
- **Upload any document** - PDFs, Word, PowerPoint auto-convert to readable format
- **Read files** - "Show me protocol.pdf" or "读取实验记录"
- **Select multiple files** - Ctrl+click to analyze together

### Data Analysis
- **Analyze experiments** - "What went wrong with exp_001?"
- **Compare results** - "Compare all PCR experiments"
- **Diagnose issues** - "Why did my cells die?"
- **Get optimization tips** - "How to improve RNA extraction yield?"

### Research & Learning
- **Search literature** - "Find recent CRISPR papers"
- **Get protocols** - "Standard Western blot protocol"
- **Ask questions** - Works in any language!

### Memory & Insights
- **Track learnings** - Agent remembers your experimental insights
- **Update notes** - "Add note: 62°C worked best for PCR"
- **Get summaries** - "Summarize this week's experiments"

## 📝 Example Commands

```
"列出我的实验"               → Lists all experiments
"Analyze exp_001 data"      → Analyzes specific experiment
"Read protocol.pdf"         → Reads PDF content (auto-converted to Markdown)
"PCR optimization tips"     → Provides optimization suggestions
"Research CRISPR methods"   → Searches scientific literature
"创建新实验文件夹"            → Creates new experiment folder
```

## 🚀 Project Creation System (v3.3) ✨ NEW

### Two Ways to Create Projects:

#### 1. Start New Research (Hypothesis-Driven)
- Click "➕ Create Project" → "🧪 Start New Research"
- Enter your research question/hypothesis
- List planned experiments (auto-creates folders)
- System creates project structure with README

#### 2. Import Existing Data (Data-Driven)
- Click "➕ Create Project" → "📁 Import Existing Data"
- Drag & drop folders or ZIP files
- **Automatic conversion**: All PDFs, DOCX, PPTX → Markdown
- **README generation**: Main project + each experiment folder
- **Preserves structure**: Your original folder organization maintained
- Shows conversion results: ✅ success, ⚠️ failed

### Import Example:
```
Upload: experiment_data.zip containing:
├── Jan15_PCR/
│   ├── protocol.docx
│   └── results.pdf
└── Jan22_sequencing/
    └── analysis.pptx

Result: All documents converted, READMEs created, ready for AI analysis!
```

## 📄 Document Processing Workflow (v3.0)

### How File Upload Works:

1. **Upload**: Drop any file (PDF, Word, PowerPoint, Excel) via the web interface
2. **Auto-Conversion**: System automatically converts to Markdown in background
3. **Smart Storage**: 
   - Original files → `exp_XXX/originals/`
   - Converted files → `exp_XXX/.labacc/converted/`
   - Registry tracking → `exp_XXX/.labacc/file_registry.json`
4. **Proactive Analysis**: Agent analyzes content and asks contextual questions
5. **Memory Update**: Your responses are saved to experiment README

### Supported File Formats:

| Format | Extensions | Conversion Tool | Quality | Speed |
|--------|------------|----------------|---------|-------|
| **PDF** | .pdf | MinerU v2 → MarkItDown | Excellent (OCR, formulas) | 2-3s |
| **Word** | .docx, .doc | MarkItDown | Excellent | 1s |
| **PowerPoint** | .pptx, .ppt | MarkItDown | Good | 1-2s |
| **Excel** | .xlsx, .xls | MarkItDown | Good (tables preserved) | 1s |
| **HTML** | .html, .htm | MarkItDown | Excellent | <1s |
| **OpenOffice** | .odt, .odp, .ods | MarkItDown | Good | 1-2s |
| **Rich Text** | .rtf | MarkItDown | Good | 1s |
| **Markdown** | .md | No conversion needed | Original | 0s |
| **Text/Code** | .txt, .py, .json, etc. | No conversion needed | Original | 0s |

**Conversion Flow**: 
- System tries MinerU v2 first for PDFs (if installed)
- Falls back to MarkItDown if MinerU fails or isn't installed
- All conversions happen automatically on upload
- Converted files are cached for instant subsequent access

### Example Workflow:

```bash
# 1. Upload a PDF protocol
Upload: "pcr_protocol.pdf" → Converts to Markdown automatically

# 2. Agent proactively analyzes
Agent: "I see this is a PCR protocol for gene amplification. The annealing 
        temperature is 58°C for 30 seconds. What gene are you targeting?"

# 3. You provide context
You: "It's for amplifying the p53 gene exon 7, expected size 750bp"

# 4. Memory updates automatically
README.md updated with file info and your context

# 5. Later, you can ask
You: "Read the PCR protocol"
Agent: [Shows converted Markdown content with full formatting]
```

## ⚙️ Configuration

```bash
export TAVILY_API_KEY="tvly-..."     # Literature search
export OPENROUTER_API_KEY="sk-..."   # LLM provider
```

### Optional: Enhanced PDF Conversion with MinerU v2

For superior PDF conversion quality (especially for complex scientific PDFs with formulas, tables, and OCR):

```bash
# Install MinerU v2 (includes magic-pdf)
uv pip install "mineru[all]"

# First run will download ~500MB of models
# Test MinerU installation:
uv run mineru -p "your_pdf.pdf" -o /tmp/test --output-type md

# If you encounter model download issues, set:
export MINERU_MODEL_SOURCE=modelscope  # Use modelscope mirror (faster in Asia)
# or
export MINERU_MODEL_SOURCE=huggingface  # Default source
```

**Note**: MinerU requires Python 3.12. If you have Python 3.13+, create a 3.12 environment as shown in Quick Start.

## 🔧 Troubleshooting

- **Port already in use**: Kill existing processes or use different ports
- **API key errors**: Ensure environment variables are set correctly
- **Frontend not loading**: Check if backend is running on port 8002
- **Tool not found**: Restart the backend after code changes
- **PDF conversion fails**: Install MinerU v2 or files will use MarkItDown fallback
- **Large files slow**: Conversion happens on first upload, subsequent reads are fast
- **MinerU model download fails**: Set `export MINERU_MODEL_SOURCE=modelscope` for mirror
- **Python 3.13 build errors**: Use Python 3.12 as shown in Quick Start (required for MinerU v2)
- **"outlines-core" Rust error**: Install with Python 3.12, not 3.13+

## 📚 Documentation

- `STATUS.md` - Current system status and changelog
- `CLAUDE.md` - Development guidelines (for developers)
- `/spec/` - Technical specifications
- `/dev_plan/` - Development roadmap

## 📄 License

MIT License - See LICENSE file for details

## 🔒 Security & Privacy

- All data stored locally in `data/alice_projects/`
- No automatic cloud uploads
- API keys stored as environment variables
- File path validation to prevent traversal
- Human-readable file-based memory (no black box embeddings)

## 🤝 Contributing

See [CLAUDE.md](CLAUDE.md) for development guidelines and architecture decisions.

## 📝 License

[License information]

## 🔗 Resources

- **Documentation**: See `/dev_plan/` for detailed plans
- **Status**: Check `STATUS.md` for current capabilities
- **Vision**: Read `dev_plan/v2_copilot_vision.md` for roadmap

---

## 🎯 Adding New Features (Super Easy!)

With v2.1's simplified architecture, adding new features is trivial:

```python
# 1. Open src/agents/react_agent.py
# 2. Add your tool:
from langchain_core.tools import tool

@tool
def your_new_tool(param: str) -> str:
    """Tool description - LLM reads this to know when to use it."""
    # Implementation
    return "Result"

# 3. Add to tools list
tools = [...existing_tools, your_new_tool]

# 4. That's it! The agent will use it when appropriate
```

---

**Version**: 3.0.1  
**Last Updated**: 2025-08-15  
**Status**: Unified file processing with MinerU v2 integration complete