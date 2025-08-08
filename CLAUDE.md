# LabAcc Copilot - Wet-Lab Biology Assistant

## Project Overview

LabAcc Copilot is an AI-powered assistant designed specifically for wet-lab biologists to analyze experimental data, diagnose issues, and suggest optimizations. Unlike coding copilots, this system focuses on biological experiment troubleshooting, data interpretation, and experimental design recommendations.

## Critical Analysis of Initial Plan

### Strengths
- **Solid Architecture**: LangGraph-based agent system with clear separation of concerns
- **Multi-modal Capabilities**: Handles both tabular data and experimental images  
- **Persistent Memory**: SQLite-based conversation persistence and long-term learning
- **Structured Output**: Pydantic models ensure consistent, actionable recommendations
- **Proven Frameworks**: Leverages mature LangChain ecosystem

### Areas for Improvement
- **Rigidity**: Fixed DecisionCard structure may not fit all experiment types
- **Error Handling**: Missing robust validation and fallback mechanisms
- **Security**: No mention of input sanitization or file handling security
- **Scalability**: No discussion of performance or multi-user considerations
- **Configuration**: Hard-coded assumptions about data organization
- **Observability**: Missing logging, monitoring, and debugging capabilities

## Architecture

### Core Components

#### 1. Agent System (LangGraph)
```
Planner → Retriever → Analyst → Critic → Writer
     ↓                    ↓         ↓        ↓
  Planning         Knowledge    Analysis   Decision
   State           Retrieval   & QC       Generation
```

#### 2. Data Processing Pipeline
- **Input Validation**: Sanitize and validate all file inputs
- **Multi-modal Processing**: Handle CSV/XLSX tables and PNG/JPEG images
- **Knowledge Retrieval**: File-based memory system using README files for project and experiment context
- **Output Generation**: Structured recommendations with evidence citations

#### 3. Memory Management
- **Short-term**: Conversation state within LangGraph
- **Long-term**: Persistent storage of decisions and session summaries
- **File-based Memory**: README-driven context retrieval system

## File-Based Memory System

### Overview
Instead of vector embeddings and complex RAG systems, LabAcc Copilot uses a simplified file-based memory approach centered around README files that serve as structured memory and context for different levels of the project hierarchy.

### Memory Hierarchy
```
labacc_copilot/
├── README.md                    # Main project memory (like CLAUDE.md)
├── data/
│   ├── experiments/
│   │   ├── exp_001_pcr_optimization/
│   │   │   ├── README.md        # Experiment summary & context
│   │   │   ├── data.csv         # Raw experimental data
│   │   │   └── images/          # Experimental images
│   │   └── exp_002_gel_analysis/
│   │       ├── README.md        # Experiment summary & context
│   │       └── gel_images/
│   ├── ref/
│   │   ├── README.md            # Reference documents index
│   │   ├── protocols/           # Standard protocols
│   │   └── literature/          # Research papers
│   └── history/
│       ├── README.md            # Decision history index
│       └── decisions/           # Previous DecisionCards
```

### README File Structure

#### Main Project README.md
```markdown
# Project: [Project Name]
**Status**: Active | Planning | Completed | On Hold
**Started**: YYYY-MM-DD
**Last Updated**: YYYY-MM-DD

## Project Overview
Brief description of the overall project goals and context.

## Current Focus
What we're currently working on and immediate next steps.

## Key Findings
- Major discoveries or insights from experiments
- Patterns observed across multiple experiments

## Active Experiments
- [exp_001_pcr_optimization](./data/experiments/exp_001_pcr_optimization/): Status and brief summary
- [exp_002_gel_analysis](./data/experiments/exp_002_gel_analysis/): Status and brief summary

## Resources & References
- Links to key protocols, papers, or external resources
- Contact information for collaborators

## Notes
Any additional context or observations.
```

#### Experiment README.md Template
```markdown
# Experiment: [Experiment Name]
**ID**: exp_XXX_[descriptive_name]
**Status**: Planning | In Progress | Completed | Failed
**Date Started**: YYYY-MM-DD
**Date Completed**: YYYY-MM-DD (if applicable)

## Objective
Clear statement of what this experiment aims to achieve.

## Hypothesis
What we expect to happen and why.

## Methods
- Protocol used
- Key parameters and conditions
- Sample information

## Results Summary
- Key observations
- Data files: [data.csv](./data.csv), [images/](./images/)
- Success metrics and outcomes

## Issues Encountered
- Problems faced during execution
- Deviations from planned protocol
- Technical difficulties

## Analysis & Interpretation
- What the results mean
- How they relate to the hypothesis
- Statistical analysis summary

## Next Steps
- Follow-up experiments suggested
- Parameters to optimize
- Additional controls needed

## Decision History
- Links to DecisionCards generated for this experiment
- Previous AI assistant recommendations and their outcomes
```

### Memory Retrieval Process

#### Context Assembly
When a user asks a question, the system:

1. **Main Context**: Always includes the main project README.md
2. **Experiment Context**: If question relates to specific experiments, includes relevant experiment README files
3. **Reference Context**: Includes reference README and relevant protocol/literature summaries
4. **History Context**: Includes decision history README and recent DecisionCards if relevant

#### File Selection Logic
```python
def get_relevant_context(user_query: str, project_path: str) -> List[str]:
    context_files = []
    
    # Always include main project memory
    context_files.append(f"{project_path}/README.md")
    
    # Include experiment context if query mentions experiments
    if mentions_experiments(user_query):
        exp_readmes = find_relevant_experiment_readmes(user_query, project_path)
        context_files.extend(exp_readmes[:5])  # Limit to top 5 most relevant
    
    # Include reference context if needed
    if needs_reference_info(user_query):
        context_files.append(f"{project_path}/data/ref/README.md")
    
    # Include decision history if troubleshooting
    if is_troubleshooting_query(user_query):
        context_files.append(f"{project_path}/data/history/README.md")
    
    return context_files
```

### Deep Research Integration

The integrated [deep_research tool](./src/tools/deep_research/) provides web-based literature search capabilities:

#### Features
- **Multi-query Search**: Generates optimized search queries from user questions
- **Iterative Refinement**: Uses reflection to identify knowledge gaps and search deeper
- **Source Citation**: All external findings include proper citations and URLs
- **Report Generation**: Creates structured markdown reports saved to `data/history/`

#### Integration Points
- **Retriever Agent**: Can invoke deep_research when local context is insufficient
- **Citation Tracking**: External sources are properly attributed in DecisionCards
- **Knowledge Updates**: Research findings can be incorporated into project README files

### Advantages of File-Based Memory

#### Simplicity
- No vector database setup or maintenance
- Human-readable and editable memory
- Easy to version control with git
- Transparent knowledge organization

#### Maintainability  
- Users can directly edit and update context
- Clear provenance of information
- Simple backup and recovery
- Cross-platform compatibility

#### Performance
- Fast file system access
- No embedding computation overhead
- Minimal memory usage
- Predictable response times

#### Collaboration
- Team members can contribute to README files
- Clear documentation of experimental progress
- Shared understanding through structured summaries
- Easy knowledge transfer

## Implementation Guidelines

### Project Structure
```
labacc_copilot/
├── src/
│   ├── agents/          # LangGraph agent implementations
│   ├── models/          # Pydantic data models
│   ├── processors/      # Data processing utilities
│   ├── memory/          # File-based memory and context management
│   ├── ui/             # Chainlit/Gradio interface
│   └── utils/          # Common utilities
├── data/
│   ├── ref/            # Reference documents
│   └── history/        # Decision history
├── config/             # Configuration files
├── tests/              # Test suite
└── docs/              # Documentation
```

### Key Technologies
- **Framework**: LangChain + LangGraph for agent orchestration
- **UI**: Chainlit (primary) or Gradio (fallback) for chat interface
- **Persistence**: SQLite for checkpointing and conversation history
- **Vision**: Provider-agnostic multimodal LLM integration
- **Memory System**: README-based file memory for project context and experiment summaries

### Data Models

#### Enhanced DecisionCard
```python
from typing import Optional, Union, List, Literal
from pydantic import BaseModel, Field, validator

class Evidence(BaseModel):
    source: str  # file path or URL
    excerpt: Optional[str] = None
    confidence: Literal["low", "medium", "high"]

class Finding(BaseModel):
    statement: str
    evidence: List[Evidence]
    category: Literal["observation", "hypothesis", "conclusion"]

class Change(BaseModel):
    factor: str
    current_value: Union[str, float, None]
    proposed_value: Union[str, float]
    rationale: str
    risk_level: Literal["low", "medium", "high"]
    expected_outcome: str
    validation_method: Optional[str] = None

class ExperimentDesign(BaseModel):
    design_type: Literal["screening", "optimization", "validation", "troubleshoot"]
    factors: dict[str, Union[List[str], List[float]]]
    controls: List[str]
    sample_size: int
    methodology_notes: str

class DecisionCard(BaseModel):
    id: str = Field(..., description="Unique identifier")
    timestamp: str
    project_id: str
    experiment_id: str
    experiment_type: str  # e.g., "PCR", "gel electrophoresis", "cell culture"
    
    # Analysis results
    summary: str
    key_findings: List[Finding]
    proposed_changes: List[Change] = Field(max_items=3)  # Enforce change budget
    next_design: Optional[ExperimentDesign] = None
    
    # Metadata
    confidence_score: float = Field(ge=0.0, le=1.0)
    references: List[str]
    tags: List[str] = []
    
    @validator('proposed_changes')
    def validate_change_budget(cls, v):
        if len(v) > 3:
            raise ValueError("Maximum 3 changes per decision card")
        return v
```

### Security Considerations

#### File Handling
- **Input Validation**: Validate file types, sizes, and content before processing
- **Sandboxing**: Process uploaded files in isolated environments
- **Path Traversal**: Prevent directory traversal attacks in file paths
- **Content Scanning**: Basic malware scanning for uploaded files

#### Data Privacy
- **Local Processing**: Keep sensitive experimental data on-premises
- **Access Control**: Implement user authentication and project-based permissions
- **Audit Logging**: Log all file accesses and decision generations
- **Data Retention**: Configurable retention policies for experimental data

### Configuration Management

#### Environment Configuration
```yaml
# config/settings.yaml
app:
  name: "LabAcc Copilot"
  version: "0.1.0"
  environment: "development"

llm:
  provider: "openai"  # openai, anthropic, google
  model: "gpt-4o"
  temperature: 0.1
  max_tokens: 4000

memory:
  main_readme: "README.md"          # Main project memory file
  experiments_dir: "data/experiments"  # Directory containing experiment folders
  reference_dir: "data/ref"         # Reference documents directory
  history_dir: "data/history"       # Decision history directory
  max_context_files: 10             # Maximum README files to include in context

ui:
  interface: "chainlit"  # chainlit, gradio
  host: "0.0.0.0"
  port: 8000
  upload_max_size: "10MB"

storage:
  database_url: "sqlite:///data/copilot.db"
  documents_path: "data/ref"
  experiments_path: "data/experiments"
  history_path: "data/history"

deep_research:
  enabled: true
  max_loops: 3
  search_queries_per_round: 3
  tavily_results_per_query: 10

security:
  allowed_file_types: [".csv", ".xlsx", ".png", ".jpg", ".jpeg", ".pdf", ".md", ".txt"]
  max_file_size: 10485760  # 10MB
  scan_uploads: true
```

### Testing Strategy

#### Unit Tests
- Individual agent functionality
- Data model validation
- File processing utilities
- Security input validation

#### Integration Tests
- Multi-agent workflows
- RAG retrieval accuracy
- Multimodal processing pipeline
- UI interaction flows

#### Acceptance Tests
```python
# Test scenarios based on initial plan
def test_multimodal_analysis():
    """Test image analysis with gel electrophoresis image"""
    # Upload gel image -> expect lane analysis

def test_conversation_persistence():
    """Test multi-turn conversation with memory"""
    # 10-message dialogue -> restart -> verify context

def test_decision_card_generation():
    """Test structured output generation"""
    # Provide experimental data -> expect valid DecisionCard

def test_change_budget_enforcement():
    """Test maximum 2-3 changes per recommendation"""
    # Verify system doesn't recommend too many changes

def test_citation_accuracy():
    """Test proper citation of evidence sources"""
    # Verify all claims link to source files or URLs
```

### Development Workflow

#### Setup Commands
```bash
# Install dependencies
pip install -e .
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v --cov=src/

# Start development server
chainlit run src/ui/app.py --port 8000

# Lint and format
ruff check src/ tests/
ruff format src/ tests/
mypy src/
```

#### Pre-commit Hooks
- Code formatting (ruff)
- Type checking (mypy)
- Security scanning (bandit)
- Test execution (pytest)

### Deployment Considerations

#### Local Development
- Docker Compose for consistent environment
- Volume mounts for data persistence
- Hot reloading for development

#### Production Deployment
- Container orchestration (Docker/k8s)
- External database (PostgreSQL)
- Load balancing for multiple users
- Backup and recovery procedures
- Monitoring and alerting

### Error Handling & Observability

#### Logging Strategy
```python
import logging
import structlog

# Structured logging with context
logger = structlog.get_logger()

# Log experimental data processing
logger.info("Processing experiment data", 
           project_id=project_id, 
           experiment_id=exp_id,
           file_count=len(files))

# Log agent decisions
logger.info("Generated decision card",
           decision_id=card.id,
           confidence=card.confidence_score,
           changes_count=len(card.proposed_changes))
```

#### Error Recovery
- Graceful degradation when external services fail
- Fallback to simpler analysis when multimodal fails
- User-friendly error messages with actionable guidance
- Automatic retry mechanisms with exponential backoff

### Extensibility

#### Plugin Architecture
- Custom experiment type analyzers
- Additional data format support
- Integration with lab equipment APIs
- Custom decision card templates

#### API Design
```python
# Agent interface for extensibility
class AnalysisAgent(ABC):
    @abstractmethod
    def analyze(self, experiment_data: ExperimentData) -> AnalysisResult:
        pass
    
    @abstractmethod
    def get_supported_types(self) -> List[str]:
        pass

# Register new analyzers
agent_registry.register("western_blot", WesternBlotAnalyzer())
agent_registry.register("qpcr", QPCRAnalyzer())
```

## Success Metrics

### Technical Metrics
- **Response Time**: <5 seconds for typical analysis
- **Accuracy**: >80% user satisfaction with recommendations
- **Uptime**: 99% availability for production deployments
- **Memory Usage**: Conversation history retrieval <2 seconds

### User Experience Metrics
- **Adoption**: Regular use by target biologists
- **Retention**: Multi-session usage patterns
- **Effectiveness**: Measurable improvement in experiment success rates
- **Satisfaction**: Positive feedback on recommendation quality

## Migration from Initial Plan

### Phase 1: Core Implementation
1. Basic agent system with simplified DecisionCard
2. File processing for common formats (CSV, PNG)
3. Simple Chainlit UI with file upload
4. SQLite persistence for conversations

### Phase 2: Enhanced Capabilities
1. Multimodal image analysis
2. RAG system with reranking
3. External research tool integration
4. Advanced experiment design suggestions

### Phase 3: Production Readiness
1. Security hardening and access control
2. Performance optimization and scaling
3. Comprehensive testing and monitoring
4. Documentation and deployment automation

## Getting Started

1. **Clone and Setup**
   ```bash
   git clone <repo>
   cd labacc_copilot
   pip install -e .
   ```

2. **Configure Environment**
   ```bash
   cp config/settings.example.yaml config/settings.yaml
   # Edit config/settings.yaml with your API keys and preferences
   ```

3. **Initialize Data Directories**
   ```bash
   mkdir -p data/{ref,history}
   # Add reference documents to data/ref/
   ```

4. **Start Development Server**
   ```bash
   chainlit run src/ui/app.py
   ```

5. **Run Tests**
   ```bash
   pytest tests/ -v
   ```

This specification provides a robust foundation for building a production-ready wet-lab biology copilot while addressing the gaps in the initial plan.