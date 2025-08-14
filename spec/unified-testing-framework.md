# LabAcc Copilot - Unified Testing Framework

**Status**: Implementation Ready  
**Date**: 2025-01-14  
**Version**: v1.0  
**Philosophy**: Two distinct testing systems for two different purposes

---

## Executive Summary

A **unified testing framework** that clearly separates two fundamentally different types of testing:

1. **Unit Tests** - Fast, isolated, deterministic tests for code correctness
2. **Agent-Driven Evaluation** - LLM-as-judge evaluation for complex behavior assessment

**Key Principle**: These are **different systems** that serve **different purposes** and should **never be mixed**.

---

## 🎯 Framework Architecture

```
LabAcc Copilot Testing Framework
├── Unit Tests (pytest)               │ Agent-Driven Evaluation
│   ├── Fast (<1s per test)           │   ├── Slow (5-30s per scenario)
│   ├── Deterministic outputs         │   ├── Subjective outputs  
│   ├── Error detection               │   ├── Quality assessment
│   ├── Isolated components           │   ├── End-to-end workflows
│   └── Assert statements             │   └── LLM-as-judge scoring
│                                     │
├── Run: uv run pytest               │ Run: python run_evaluation.py
└── Reports: Pass/Fail counts         └── Reports: Quality scores
```

---

## 📊 Test Type Classification

### Current Tests Analysis

| Test File | Type | Purpose | Framework | Keep/Move |
|-----------|------|---------|-----------|-----------|
| `test_config.py` | **Unit** | API key validation | pytest | ✅ Keep as Unit |
| `test_llm.py` | **Unit** | LLM instance creation | pytest | ✅ Keep as Unit |
| `test_deep_research.py` | **Integration** | Tool functionality | pytest | ✅ Keep as Unit |
| `test_memory_system.py` | **Mixed** | Memory operations | pytest | 🔄 Split |
| `test_multi_round_conversations.py` | **Agent** | Conversation quality | Agent-Eval | 🔄 Move |
| `agent_evaluation/*` | **Agent** | Behavior assessment | Agent-Eval | ✅ Keep as Agent |

---

## 🧪 Unit Testing Framework

### Purpose
- Test **individual functions** and **isolated components**
- Verify **code correctness** and **error handling**
- Fast feedback during development
- Clear pass/fail based on **expected outputs**

### What Gets Unit Tested
```python
# ✅ Unit Test Examples
def test_readme_memory_read():
    """Test README file reading functionality"""
    memory = ReadmeMemory("test_path")
    content = memory.read_memory()
    assert content.startswith("# Experiment")

def test_file_analyzer_csv():
    """Test CSV file analysis"""
    analyzer = FileAnalyzer()
    result = analyzer.analyze_csv("test.csv")
    assert "columns" in result
    assert "rows" in result

def test_llm_config_creation():
    """Test LLM configuration"""
    llm = get_llm_instance("test-model")
    assert llm is not None
    assert hasattr(llm, "invoke")
```

### Directory Structure
```
tests/unit/
├── test_memory/
│   ├── test_readme_memory.py      # README operations
│   ├── test_auto_updater.py       # File upload processing
│   └── test_context_manager.py    # Context management
├── test_tools/
│   ├── test_file_analyzer.py      # File analysis functions
│   ├── test_deep_research.py      # Research tool functionality
│   └── test_summarizer.py         # Text summarization
├── test_api/
│   ├── test_file_routes.py        # API endpoints
│   └── test_bridge.py             # React agent bridge
├── test_config/
│   ├── test_keys.py               # API key management
│   └── test_llm.py                # LLM configuration
└── conftest.py                    # Unit test fixtures
```

### Unit Test Characteristics
- **Fast**: <1 second per test
- **Isolated**: Mock external dependencies
- **Deterministic**: Same input → same output
- **Simple assertions**: `assert`, `assertEqual`, clear pass/fail
- **No LLM calls**: Mock or skip LLM interactions
- **Focused**: One function/component per test

---

## 🤖 Agent-Driven Evaluation Framework

### Purpose
- Evaluate **complex agent behavior** and **conversation quality**
- Assess **subjective qualities**: relevance, helpfulness, reasoning
- Test **end-to-end workflows** and **multi-turn conversations**
- Use **LLM-as-judge** for nuanced evaluation

### What Gets Agent Evaluation
```python
# ✅ Agent Evaluation Examples
scenario = ConversationScenario(
    name="memory_user_correction",
    description="User corrects agent analysis",
    turns=[
        ("Analyze this data", "analyze_data"),
        ("我不同意，是因为载入量问题", "should acknowledge correction"),
        ("那怎么解决？", "should provide solution based on correction")
    ]
)
# Evaluated by LLM judge for: correctness, helpfulness, context retention
```

### Directory Structure
```
tests/agent_evaluation/
├── scenarios/
│   ├── conversation_scenarios.py  # Multi-turn conversations
│   ├── memory_scenarios.py        # Memory system behavior
│   ├── tool_selection_scenarios.py # Tool usage evaluation
│   └── multilingual_scenarios.py  # Language handling
├── evaluators/
│   ├── conversation_evaluator.py  # Multi-turn evaluation
│   ├── memory_evaluator.py        # Memory system evaluation
│   └── comprehensive_evaluator.py # Combined evaluation
├── runners/
│   ├── scenario_runner.py         # Execute scenarios
│   └── evaluation_runner.py       # Run evaluations
└── reports/
    ├── conversation_reports.py    # Reporting system
    └── summary_generator.py       # Summary generation
```

### Agent Evaluation Characteristics
- **Slow**: 5-30 seconds per scenario
- **Subjective**: Quality assessment, not just correctness
- **End-to-end**: Full agent workflows
- **LLM-judged**: LLM evaluates response quality
- **Contextual**: Multi-turn, complex scenarios
- **Scored**: 1-10 ratings with detailed feedback

---

## 🚀 Unified Commands

### Unit Tests
```bash
# Run all unit tests (fast)
uv run pytest tests/unit/ -v

# Run specific component tests
uv run pytest tests/unit/test_memory/ -v
uv run pytest tests/unit/test_tools/ -v

# Run with coverage
uv run pytest tests/unit/ --cov=src --cov-report=html

# Quick development loop
uv run pytest tests/unit/ -x --lf  # Stop on first failure, last failed
```

### Agent-Driven Evaluation
```bash
# Run agent evaluation (slow, comprehensive)
python run_evaluation.py --quick     # 3 minutes, core scenarios
python run_evaluation.py --standard  # 8 minutes, comprehensive
python run_evaluation.py --full      # 15 minutes, all scenarios

# Specific evaluation categories
python run_evaluation.py --memory    # Memory system evaluation
python run_evaluation.py --conversation # Multi-turn conversations
python run_evaluation.py --tools     # Tool selection evaluation
```

### Development Workflow
```bash
# 1. During development - run unit tests frequently
uv run pytest tests/unit/ -x  # Fast feedback

# 2. Before commit - run both
uv run pytest tests/unit/          # Ensure code correctness
python run_evaluation.py --quick   # Ensure behavior quality

# 3. Before release - comprehensive evaluation
python run_evaluation.py --full    # Full behavior assessment
```

---

## 📁 Implementation Plan

### Phase 1: Restructure Existing Tests (Week 1)

#### 1.1 Create Unit Test Structure
```bash
mkdir -p tests/unit/{test_memory,test_tools,test_api,test_config}
```

#### 1.2 Move Pure Unit Tests
- `test_config.py` → `tests/unit/test_config/`
- `test_llm.py` → `tests/unit/test_config/`
- `test_deep_research.py` → `tests/unit/test_tools/`

#### 1.3 Extract Unit Tests from Mixed Files
- Extract unit-testable parts from `test_memory_system.py`
- Move conversation tests to agent evaluation

### Phase 2: Clean Agent Evaluation (Week 2)

#### 2.1 Consolidate Agent Tests
- Move `test_multi_round_conversations.py` to agent evaluation
- Organize by scenario type, not test type
- Remove unit-test style assertions from agent tests

#### 2.2 Improve Agent Evaluation
- Enhance LLM-as-judge evaluation criteria
- Add more realistic conversation scenarios
- Improve scoring and reporting

### Phase 3: Unified Interface (Week 3)

#### 3.1 Update Command Interface
- `run_evaluation.py` - Only agent evaluation
- `pytest` - Only unit tests
- Update documentation and README

#### 3.2 CI/CD Integration
- Unit tests run on every commit
- Agent evaluation runs on PR merge
- Different failure handling for each type

---

## 🎯 Success Criteria

### Unit Tests
- ✅ All tests run in <30 seconds total
- ✅ 100% deterministic (no flaky tests)
- ✅ Clear pass/fail (no subjective evaluation)
- ✅ >90% code coverage for core components
- ✅ No external API calls (mocked)

### Agent Evaluation
- ✅ Comprehensive behavior assessment
- ✅ Multi-turn conversation evaluation
- ✅ Memory system validation
- ✅ Tool selection assessment
- ✅ Multilingual capability testing
- ✅ Quality scores with actionable feedback

### Framework Clarity
- ✅ Clear separation of concerns
- ✅ No mixing of unit and agent tests
- ✅ Different commands for different purposes
- ✅ Different success criteria
- ✅ Different reporting formats

---

## 📋 Test Migration Guide

### For Existing Tests

#### Unit Test Checklist
- [ ] Test runs in <1 second
- [ ] No LLM API calls (mock instead)
- [ ] Single component/function focus
- [ ] Clear input/output relationship
- [ ] Deterministic results

#### Agent Evaluation Checklist
- [ ] Tests end-to-end behavior
- [ ] Evaluates subjective qualities
- [ ] Uses realistic scenarios
- [ ] Allows LLM API calls
- [ ] Evaluated by LLM judge

### Migration Examples

#### ❌ Bad: Mixed Test
```python
def test_memory_system_integration():
    # This mixes unit testing and behavior evaluation
    memory = ReadmeMemory("test")
    response = await handle_message("analyze this")  # LLM call
    assert "analysis" in response  # Simple keyword matching
```

#### ✅ Good: Separate Tests
```python
# Unit Test
def test_readme_memory_operations():
    memory = ReadmeMemory("test") 
    memory.write_memory("test content", "section")
    content = memory.read_memory()
    assert "test content" in content

# Agent Evaluation
scenario = {
    "user_query": "Analyze my experiment data",
    "context": "user uploaded CSV file",
    "evaluation_criteria": "Uses appropriate tools, provides relevant insights"
}
```

---

## 🔧 Technical Implementation

### conftest.py Updates
```python
# tests/unit/conftest.py - For unit tests
@pytest.fixture
def mock_llm():
    """Mock LLM for unit tests - no real API calls"""
    return MockLLM()

@pytest.fixture  
def temp_memory_dir():
    """Isolated temporary directory for memory tests"""
    return create_temp_dir()

# tests/agent_evaluation/conftest.py - For agent evaluation
@pytest.fixture
def real_bob_projects():
    """Real bob_projects data for agent evaluation"""
    return restore_bob_projects_from_backup()
```

### New Unit Test Examples
```python
# tests/unit/test_memory/test_readme_memory.py
def test_readme_creation():
    memory = ReadmeMemory("test_path") 
    assert memory.readme_path.name == "README.md"

def test_memory_section_write():
    memory = ReadmeMemory(tmp_path)
    memory.write_memory("test content", "Test Section")
    content = memory.read_memory()
    assert "## Test Section" in content
    assert "test content" in content

def test_insight_appending():
    memory = ReadmeMemory(tmp_path)
    memory.append_insight("First insight")
    memory.append_insight("Second insight") 
    content = memory.read_memory()
    assert "First insight" in content
    assert "Second insight" in content
```

---

## 📈 Reporting & Metrics

### Unit Test Reports
```
=================== Unit Test Results ===================
tests/unit/test_memory/test_readme_memory.py::test_readme_creation PASSED
tests/unit/test_tools/test_file_analyzer.py::test_csv_analysis PASSED
tests/unit/test_config/test_llm.py::test_llm_creation PASSED

==================== 47 passed in 12.3s ====================
Coverage: 89% (target: >90%)
```

### Agent Evaluation Reports
```
🤖 Agent Evaluation Results
========================================
Memory System Evaluation:      8.7/10 ✅
Multi-turn Conversations:      8.3/10 ✅  
Tool Selection Logic:          8.9/10 ✅
Multilingual Support:          8.1/10 ✅

Overall Agent Quality:          8.5/10 ✅
Pass Rate:                      94% (47/50)
```

---

## 🎉 Benefits of Unified Framework

1. **Clear Purpose Separation**
   - Unit tests catch bugs quickly
   - Agent evaluation assesses quality

2. **Appropriate Tools for Each Job**
   - pytest for deterministic testing
   - LLM-as-judge for subjective evaluation

3. **Better Developer Experience**
   - Fast unit tests during development
   - Comprehensive evaluation before release

4. **Maintainable Test Suite**
   - No confusion about test types
   - Clear expectations for each test

5. **Scalable Testing Strategy**
   - Easy to add new unit tests
   - Easy to add new evaluation scenarios

---

**Document Status**: Ready for Implementation  
**Next Steps**: Phase 1 implementation - restructure existing tests  
**Timeline**: 3 weeks to complete unified framework