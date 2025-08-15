# LabAcc Copilot

AI laboratory assistant for experimental data analysis and optimization with automatic document conversion.

## 🚀 Quick Start

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup
git clone <repo-url>
cd Labacc_copilot
uv sync

# Optional: Install MinerU for advanced PDF conversion (recommended)
uv pip install magic-pdf[full] --extra-index-url https://myhloli.github.io/wheels/

cd frontend && npm install && cd ..

# Set API keys
export TAVILY_API_KEY="your-key"
export OPENROUTER_API_KEY="your-key"

# Start
./start-dev.sh
# Open http://localhost:5173
```

## 💡 Features

- **Automatic Document Conversion**: PDFs and Office files convert to Markdown on upload
- **Multi-language Support**: Works in English, Chinese, Spanish, etc.
- **Memory System**: Each experiment has persistent README memory
- **Real-time Tool Visibility**: See which tools are running live
- **Literature Search**: Integrated Tavily API for research papers
- **Smart Context**: Pre-loads relevant data to reduce tool calls
- **Proactive Analysis**: Automatically analyzes uploaded files and asks contextual questions

## 📝 Example Usage

```
"列出我的实验"               → Lists all experiments
"Analyze exp_001 data"      → Analyzes specific experiment
"Read protocol.pdf"         → Reads PDF content (auto-converted to Markdown)
"PCR optimization tips"     → Provides optimization suggestions
"Research CRISPR methods"   → Searches scientific literature
"创建新实验文件夹"            → Creates new experiment folder
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

| Format | Extensions | Conversion Tool | Quality |
|--------|------------|----------------|---------|
| **PDF** | .pdf | MinerU/MarkItDown | Excellent with MinerU |
| **Word** | .docx, .doc | MarkItDown | Excellent |
| **PowerPoint** | .pptx, .ppt | MarkItDown | Good |
| **Excel** | .xlsx, .xls | MarkItDown | Good (tables preserved) |
| **HTML** | .html, .htm | MarkItDown | Excellent |
| **OpenOffice** | .odt, .odp, .ods | MarkItDown | Good |
| **Rich Text** | .rtf | MarkItDown | Good |

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

### Optional: Enhanced PDF Conversion

For better PDF conversion quality (especially for complex scientific PDFs with formulas):

```bash
# Install MinerU with GPU support (CUDA)
uv pip install magic-pdf[full] --extra-index-url https://myhloli.github.io/wheels/

# Or for Apple Silicon (MPS)
uv pip install magic-pdf[full-mps] --extra-index-url https://myhloli.github.io/wheels/
```

## 🔧 Troubleshooting

- **Port already in use**: Kill existing processes or use different ports
- **API key errors**: Ensure environment variables are set correctly
- **Frontend not loading**: Check if backend is running on port 8002
- **Tool not found**: Restart the backend after code changes
- **PDF conversion fails**: Install MinerU or files will use basic conversion
- **Large files slow**: Conversion happens on first upload, subsequent reads are fast

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

**Version**: 3.0.0  
**Last Updated**: 2025-08-15  
**Status**: Unified file processing with automatic document conversion operational