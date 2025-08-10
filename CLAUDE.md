# LabAcc Copilot - Wet-Lab Biology Assistant

AI-powered assistant for wet-lab biologists to analyze experimental data, diagnose issues, and suggest optimizations.

## Architecture

### Agent System (LangGraph)
```
Planner → Retriever → Analyst → Critic → Writer
```

### Core Features
- **Multi-modal Analysis**: CSV/XLSX tables and experimental images (gel, plots)
- **File-based Memory**: README files as structured context (no vector DB needed)
- **Deep Research**: Integrated Tavily web search for literature
- **Decision Cards**: Structured recommendations with evidence citations

## File-Based Memory System

Instead of RAG/embeddings, uses README files for context:

```
data/
├── experiments/
│   └── exp_001_pcr_optimization/
│       ├── README.md        # Experiment context
│       ├── data.csv         # Raw data
│       └── images/          # Gel images, plots
├── ref/                     # Protocols, literature
└── history/                 # Previous decisions
```

Each experiment folder contains a README with: objective, methods, results, issues, next steps.

## DecisionCard Schema

```python
class DecisionCard(BaseModel):
    project_id: str
    experiment_id: str
    experiment_type: str  # PCR, gel, cell culture, etc.
    summary: str
    key_findings: List[Finding]  # with evidence citations
    proposed_changes: List[Change]  # max 3 per round
    next_design: Optional[ExperimentDesign]
    confidence_score: float
    references: List[str]  # file paths or URLs
```

## Development with uv

```bash
# All Python operations use uv:
uv run python <script.py>
uv run chainlit run src/ui/app.py
uv run pytest tests/
uv run ruff check src/
```

## Key Implementation Files

- `src/components/llm.py` - LLM configuration (follows autocell pattern)
- `src/config/keys.py` - Tavily API key management
- `src/graph/` - LangGraph agent implementation
- `src/tools/deep_research/` - Web search integration
- `src/models/decision_card.py` - Pydantic models

## Important Guidelines

1. **API Keys**: Read directly from environment variables (no .env files)
2. **LLM Selection**: Use role-based model assignments in `llm.py`
3. **Memory**: Prioritize file-based README context over vector search
4. **Changes**: Limit to 2-3 proposed changes per DecisionCard
5. **Testing**: Always run tests with `uv run pytest`

## Deep Research Tool

```python
from src.tools.deep_research import run_deep_research
result = run_deep_research("PCR optimization for GC-rich templates", max_loops=3)
```

Reports saved to `data/history/` with citations.

## Security Notes

- No hardcoded API keys
- Validate all file uploads
- Sanitize paths to prevent traversal
- Log all decision generations

## Testing

```bash
uv run pytest tests/ -v        # Run all tests
uv run pytest tests/test_llm.py  # Specific test
```

Tests use mocked API keys via fixtures in `conftest.py`.