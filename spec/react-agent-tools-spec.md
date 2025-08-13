# React Agent Tools Specification v1.0

## Executive Summary

This specification defines 8 essential tools for the LabAcc Copilot React Agent to provide comprehensive support for wet-lab biologists. The tools are designed to analyze experimental data, diagnose failures, optimize protocols, and manage laboratory information efficiently.

**Status**: Specification Complete  
**Version**: 1.0  
**Last Updated**: 2025-01-13  
**Author**: LabAcc Development Team

## Core Design Principles

1. **Natural Language Understanding**: Tools work with any language without keyword matching
2. **File-Based Intelligence**: Leverage README files and markdown for transparent reasoning
3. **Composability**: Tools can work together and share context
4. **Performance**: Response time <3 seconds for most operations
5. **Error Resilience**: Graceful degradation with helpful error messages

## Tool Inventory

### Phase 1: Core Tools (Week 1)

#### 1. analyze_data
**Purpose**: Analyze experimental data from CSV/Excel files with statistical insights

**Implementation**:
```python
@tool
def analyze_data(
    file_path: str,
    analysis_type: str = "auto",
    confidence_threshold: float = 0.95
) -> str:
    """
    Analyze experimental data from CSV/Excel files.
    
    Args:
        file_path: Path to data file
        analysis_type: Type of analysis (auto, pcr, western_blot, cell_count, etc.)
        confidence_threshold: Statistical confidence level
    
    Returns:
        Structured analysis with statistics, trends, and anomalies
    """
```

**Features**:
- Automatic data type detection
- Statistical analysis (mean, std, SEM, outliers)
- Trend detection and curve fitting
- Anomaly detection using z-scores
- Missing data handling
- Visualization recommendations

**Integration**:
- Uses `QuickFileAnalyzer` for file reading
- Pandas for data processing
- Scipy for statistical tests

**Success Metrics**:
- Response time: <2 seconds for files <10MB
- Accuracy: >95% for standard experimental data formats

---

#### 2. scan_experiments
**Purpose**: List and summarize all experiments with intelligent insights

**Implementation**:
```python
@tool
def scan_experiments(
    project_path: str = "data/alice_projects",
    include_analysis: bool = True,
    depth: str = "summary"
) -> str:
    """
    Scan project experiments and provide intelligent summaries.
    
    Args:
        project_path: Root path for experiments
        include_analysis: Include AI-generated insights
        depth: Level of detail (summary, detailed, full)
    
    Returns:
        Structured list of experiments with metadata and insights
    """
```

**Features**:
- Recursive folder scanning
- README.md content extraction
- Experiment status detection (ongoing, completed, failed)
- Pattern recognition across experiments
- Recent activity highlighting
- Success rate calculation

**Integration**:
- File system operations via pathlib
- Markdown parsing for README files
- Pattern matching for experiment types

---

#### 3. diagnose_failure
**Purpose**: Diagnose experimental failures with actionable suggestions

**Implementation**:
```python
@tool
def diagnose_failure(
    experiment_type: str,
    observed_results: str,
    expected_results: str,
    conditions: dict = None
) -> str:
    """
    Diagnose experimental failures and suggest troubleshooting steps.
    
    Args:
        experiment_type: Type of experiment (PCR, Western blot, etc.)
        observed_results: Description of what happened
        expected_results: Description of what should have happened
        conditions: Experimental conditions dictionary
    
    Returns:
        Diagnostic report with ranked troubleshooting suggestions
    """
```

**Features**:
- Pattern matching against common failure modes
- Condition validation against optimal ranges
- Ranked troubleshooting suggestions
- Literature-backed recommendations
- Historical failure analysis
- Confidence scoring for each diagnosis

**Common Failure Patterns**:
```python
PCR_FAILURES = {
    "no_bands": [
        "Check primer design and Tm",
        "Verify template quality (260/280 ratio)",
        "Optimize annealing temperature (gradient PCR)",
        "Check polymerase activity and buffer",
        "Verify cycling conditions"
    ],
    "multiple_bands": [
        "Increase annealing temperature",
        "Optimize primer concentration",
        "Add DMSO for GC-rich templates",
        "Use hot-start polymerase",
        "Redesign primers for specificity"
    ],
    "smearing": [
        "Reduce template concentration",
        "Decrease cycle number",
        "Optimize Mg2+ concentration",
        "Check for DNA degradation",
        "Use fresh dNTPs"
    ]
}
```

---

### Phase 2: Enhanced Analysis (Week 2)

#### 4. optimize_protocol
**Purpose**: Generate protocol optimizations based on experimental results

**Implementation**:
```python
@tool
def optimize_protocol(
    protocol_type: str,
    current_conditions: dict,
    results_summary: str,
    optimization_goal: str = "improve_yield"
) -> str:
    """
    Generate protocol optimization suggestions.
    
    Args:
        protocol_type: Type of protocol
        current_conditions: Current experimental conditions
        results_summary: Summary of current results
        optimization_goal: What to optimize for
    
    Returns:
        Optimization plan with specific parameter adjustments
    """
```

**Features**:
- Parameter optimization matrices
- DOE (Design of Experiments) suggestions
- Cost-benefit analysis
- Time optimization
- Success probability estimation

---

#### 5. search_literature
**Purpose**: Search scientific literature using Tavily API

**Implementation**:
```python
@tool
async def search_literature(
    query: str,
    focus: str = "methods",
    max_results: int = 5
) -> str:
    """
    Search scientific literature for relevant information.
    
    Args:
        query: Search query
        focus: Focus area (methods, troubleshooting, reviews)
        max_results: Number of results to return
    
    Returns:
        Formatted literature findings with relevance scores
    """
```

**Features**:
- Tavily API integration
- PubMed search augmentation
- Protocol database search
- Relevance ranking
- Citation formatting
- Key findings extraction

**Integration**:
- Uses existing `deep_research` module
- Caches results for 24 hours
- Cost tracking ($0.01-0.03 per query)

---

#### 6. analyze_images
**Purpose**: Analyze laboratory images (gels, microscopy, plots)

**Implementation**:
```python
@tool
async def analyze_images(
    image_path: str,
    image_type: str = "auto",
    quantify: bool = False
) -> str:
    """
    Analyze laboratory images with AI vision.
    
    Args:
        image_path: Path to image file
        image_type: Type of image (gel, microscopy, plot, etc.)
        quantify: Whether to perform quantification
    
    Returns:
        Image analysis with observations and measurements
    """
```

**Features**:
- Image type detection
- Band intensity quantification (gels)
- Cell counting (microscopy)
- Plot data extraction
- Quality assessment
- Artifact detection

**Supported Image Types**:
- Agarose/PAGE gels
- Western blots
- Microscopy (brightfield, fluorescence)
- Flow cytometry plots
- Growth curves
- Standard curves

---

### Phase 3: Advanced Features (Week 3)

#### 7. manage_files
**Purpose**: Organize and annotate experimental files

**Implementation**:
```python
@tool
def manage_files(
    action: str,
    source_path: str,
    destination_path: str = None,
    metadata: dict = None
) -> str:
    """
    Manage experimental files with intelligent organization.
    
    Args:
        action: Action to perform (organize, rename, annotate, archive)
        source_path: Source file/folder path
        destination_path: Destination path (if applicable)
        metadata: Metadata to add/update
    
    Returns:
        Confirmation of file operations performed
    """
```

**Features**:
- Smart file organization by experiment type
- Standardized naming conventions
- Metadata annotation in .labacc files
- Version control integration
- Backup creation
- Bulk operations support

---

#### 8. generate_report
**Purpose**: Create comprehensive experiment reports

**Implementation**:
```python
@tool
def generate_report(
    experiment_path: str,
    report_type: str = "summary",
    include_visuals: bool = True,
    format: str = "markdown"
) -> str:
    """
    Generate comprehensive experiment reports.
    
    Args:
        experiment_path: Path to experiment folder
        report_type: Type of report (summary, detailed, publication)
        include_visuals: Include charts and visualizations
        format: Output format (markdown, html, pdf)
    
    Returns:
        Generated report content or path to saved report
    """
```

**Features**:
- Automatic data aggregation
- Statistical summary generation
- Method section writing
- Results interpretation
- Figure generation
- Citation management

---

## Implementation Plan

### Development Phases

#### Phase 1: Core Tools (Week 1)
- [ ] Implement analyze_data with pandas integration
- [ ] Create scan_experiments with folder traversal
- [ ] Build diagnose_failure with pattern matching
- [ ] Write comprehensive unit tests
- [ ] Integration testing with sample data

#### Phase 2: Enhanced Analysis (Week 2)
- [ ] Implement optimize_protocol with DOE
- [ ] Integrate search_literature with Tavily
- [ ] Build analyze_images with vision capabilities
- [ ] Performance optimization
- [ ] End-to-end testing

#### Phase 3: Advanced Features (Week 3)
- [ ] Implement manage_files with metadata
- [ ] Create generate_report with templates
- [ ] Cross-tool integration testing
- [ ] Documentation and examples
- [ ] User acceptance testing

### Testing Strategy

#### Unit Tests
```python
# tests/test_react_tools.py
import pytest
from src.agents.react_agent_tools import *

def test_analyze_data_csv():
    """Test CSV data analysis"""
    result = analyze_data("tests/data/pcr_results.csv")
    assert "mean" in result
    assert "outliers" in result

def test_diagnose_failure_pcr():
    """Test PCR failure diagnosis"""
    result = diagnose_failure(
        experiment_type="PCR",
        observed_results="no bands",
        expected_results="single band at 500bp"
    )
    assert "primer" in result.lower()
    assert "temperature" in result.lower()
```

#### Integration Tests
```python
def test_tool_chain():
    """Test tools working together"""
    # Scan experiments
    experiments = scan_experiments()
    
    # Analyze first experiment
    first_exp = extract_first_experiment(experiments)
    analysis = analyze_data(f"{first_exp}/data.csv")
    
    # Diagnose if issues found
    if "anomaly" in analysis:
        diagnosis = diagnose_failure("PCR", analysis)
        assert diagnosis is not None
```

#### Performance Tests
```python
def test_response_time():
    """Ensure <3 second response time"""
    import time
    
    start = time.time()
    result = analyze_data("tests/data/large_dataset.csv")
    elapsed = time.time() - start
    
    assert elapsed < 3.0, f"Tool took {elapsed}s, exceeds 3s limit"
```

### Test Data Structure
```
tests/
├── data/
│   ├── pcr_results.csv          # Sample PCR data
│   ├── western_blot.xlsx        # Western blot quantification
│   ├── cell_counts.csv          # Cell counting data
│   ├── gel_image.jpg           # Agarose gel image
│   ├── microscopy.tif          # Microscopy image
│   └── corrupted.csv           # Malformed data for error testing
├── fixtures/
│   ├── experiment_folders/     # Mock experiment structure
│   └── expected_outputs/       # Expected analysis results
└── test_*.py                   # Test files
```

## Error Handling

### Error Categories
1. **Input Errors**: Invalid parameters, missing files
2. **Data Errors**: Corrupted data, unsupported formats
3. **Processing Errors**: Analysis failures, timeout
4. **External Errors**: API failures, network issues

### Error Response Format
```python
{
    "status": "error",
    "error_type": "DataError",
    "message": "Unable to parse CSV file",
    "suggestion": "Check file format and encoding",
    "fallback": "Try manual analysis with analyze_text tool"
}
```

## Success Metrics

### Performance Metrics
- **Response Time**: <3s for 95% of requests
- **Availability**: 99.9% uptime during development
- **Memory Usage**: <500MB per tool invocation
- **Concurrent Requests**: Support 10 simultaneous users

### Quality Metrics
- **Accuracy**: >90% for failure diagnosis
- **Relevance**: >80% for literature search
- **User Satisfaction**: >4/5 rating from beta testers
- **Bug Rate**: <1 critical bug per 1000 invocations

### Business Metrics
- **Time Saved**: >30% reduction in debugging time
- **Success Rate**: >60% improvement in experiment success
- **Adoption**: >50% of users using tools daily within 1 month
- **ROI**: 10x return on development investment

## Security Considerations

### Data Protection
- Validate all file paths to prevent directory traversal
- Sanitize user inputs before processing
- Implement rate limiting for API calls
- No execution of arbitrary code
- Secure handling of API keys

### Privacy
- No upload of experimental data to external services
- Local processing whenever possible
- Anonymization of data in logs
- User consent for any external API calls

## Future Enhancements

### Version 2.0 Features
- Machine learning models for pattern recognition
- Real-time experiment monitoring
- Collaborative features for lab teams
- Mobile app integration
- Voice interface for hands-free operation

### Version 3.0 Vision
- Predictive experiment planning
- Automated protocol generation
- Integration with lab equipment
- AR guidance for procedures
- Global knowledge base integration

## Appendix A: Tool Docstring Template

```python
@tool
def tool_name(required_param: str, optional_param: str = "default") -> str:
    """
    Brief description of what the tool does.
    
    This tool helps with [specific use case]. It analyzes [input type]
    and provides [output type]. Best used when [scenario].
    
    Args:
        required_param: Description of required parameter
        optional_param: Description of optional parameter (default: value)
    
    Returns:
        Description of return value format and content
    
    Examples:
        >>> tool_name("input_value")
        "Expected output format"
    
    Note:
        Any special considerations or limitations
    """
```

## Appendix B: Common Experimental Protocols

### PCR Optimization Matrix
```python
PCR_OPTIMIZATION = {
    "annealing_temp": {"range": [50, 72], "step": 2},
    "mg_concentration": {"range": [1.0, 4.0], "step": 0.5},
    "primer_concentration": {"range": [0.1, 1.0], "step": 0.2},
    "template_amount": {"range": [1, 100], "step": "log"},
    "extension_time": {"formula": "1min per kb"},
    "cycle_number": {"range": [25, 35], "step": 2}
}
```

### Western Blot Troubleshooting
```python
WESTERN_BLOT_ISSUES = {
    "no_signal": {
        "causes": ["Low protein", "Antibody issue", "Transfer problem"],
        "solutions": ["Increase loading", "Optimize antibody", "Check transfer"]
    },
    "high_background": {
        "causes": ["Blocking insufficient", "Antibody concentration"],
        "solutions": ["Increase blocking time", "Dilute antibody more"]
    }
}
```

## Document History

- **v1.0** (2025-01-13): Initial specification created
- Comprehensive tool definitions for 8 essential tools
- Three-phase implementation plan
- Testing and validation strategies
- Performance and quality metrics

---

**Next Steps**:
1. Review and approve specification
2. Set up development environment
3. Begin Phase 1 implementation
4. Create test data and fixtures
5. Implement CI/CD pipeline

**Contact**: LabAcc Development Team  
**Repository**: /src/agents/react_agent_tools.py