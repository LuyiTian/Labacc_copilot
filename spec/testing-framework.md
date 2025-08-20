# LabAcc Copilot - Testing Framework

**Status**: Active Implementation  
**Date**: 2025-01-20  
**Version**: v3.4.0  
**Philosophy**: Test what matters, keep it simple, no overengineering

---

## Executive Summary

LabAcc Copilot uses a **three-tier testing strategy** that covers code correctness, system integration, and agent behavior:

1. **Unit Tests** - Fast, deterministic tests for individual functions (pytest)
2. **Integration Tests** - Workflow testing with mocked dependencies
3. **Agent Evaluation** - LLM-as-judge for behavior quality assessment

Additionally, the **multi-user system** adds authentication, session, and permission testing.

---

## 🏗️ Current Testing Architecture

```
LabAcc Testing System v3.4.0
├── Unit Tests (pytest)              
│   ├── tests/unit/                  
│   ├── Fast (<1s per test)          
│   ├── Mocked dependencies          
│   └── Deterministic results        
│                                     
├── Integration Tests                 
│   ├── tests/integration/           
│   ├── Complete workflows           
│   ├── Mock LLMs & sessions         
│   └── File upload → analysis       
│                                     
├── Agent Evaluation (LLM-as-judge)  
│   ├── tests/agent_evaluation/      
│   ├── Response + trajectory eval   
│   ├── Multi-turn conversations     
│   └── Comprehensive scoring        
│                                     
└── Multi-User Tests                 
    ├── Authentication & sessions     
    ├── Project management           
    ├── Permission control           
    └── API endpoint testing         
```

---

## 📊 Test Categories & Current Implementation

### 1. Unit Tests (`tests/unit/`)
**Purpose**: Test individual functions and components in isolation

**Current Files**:
- `test_config/test_config.py` - Configuration and API keys
- `test_config/test_llm.py` - LLM instance creation
- `test_file_registry.py` - File registry operations
- `test_tools/test_deep_research.py` - Research tool functions
- `test_tools/test_file_analyzer.py` - File analysis functions

**Characteristics**:
- ✅ Fast execution (<1s per test)
- ✅ Uses pytest framework
- ✅ Mocks external dependencies
- ✅ Clear pass/fail assertions
- ✅ No LLM API calls

**Run Command**:
```bash
uv run pytest tests/unit/ -v
```

### 2. Integration Tests (`tests/integration/`)
**Purpose**: Test complete workflows and system integration

**Current Files**:
- `test_upload_workflow.py` - File upload → conversion → analysis
- `test_memory_update.py` - Memory system updates with file uploads

**Characteristics**:
- ✅ Tests end-to-end workflows
- ✅ Uses mock sessions and LLMs
- ✅ Verifies multi-step processes
- ✅ Tests file conversion pipeline
- ✅ Checks registry updates

**Run Command**:
```bash
uv run python tests/integration/test_upload_workflow.py
```

### 3. Agent Evaluation (`tests/agent_evaluation/`)
**Purpose**: Evaluate agent behavior quality using LLM-as-judge

**Current Files**:
- `comprehensive_evaluator.py` - Combined response + trajectory evaluation
- `evaluator_agent.py` - Response quality evaluation
- `trajectory_evaluator.py` - Execution path evaluation
- `conversation_scenarios.py` - Multi-turn test cases
- `multiuser_test_cases.py` - Multi-user specific scenarios
- `run_evaluation.py` - Main evaluation CLI

**Evaluation Metrics**:
```python
{
    # Response Quality (60% weight)
    'accuracy': 1-10,
    'relevance': 1-10,
    'completeness': 1-10,
    'language_understanding': 1-10,
    
    # Trajectory Quality (40% weight)
    'tool_selection': 1-10,
    'reasoning_quality': 1-10,
    'error_recovery': 1-10,
    'efficiency': 1-10
}
```

**Run Command**:
```bash
# Quick evaluation (3 min)
python -m tests.agent_evaluation.run_evaluation --quick

# Full evaluation (15 min)
python -m tests.agent_evaluation.run_evaluation --full

# Multi-user focused
python -m tests.agent_evaluation.run_evaluation --categories project_isolation,session_management
```

### 4. Multi-User System Tests
**Purpose**: Test authentication, sessions, and project management

**Current Files**:
- `test_api_simple.py` - Basic API testing with real users
- `test_admin_functionality.py` - Admin panel and user management
- `test_session_management.py` - Session creation and isolation
- `validate_multiuser_system.py` - Multi-user system validation

**Test Users**:
- `admin/admin123` - Admin role
- `alice/alice123` - Regular user
- `bob/bob123` - Regular user

**Coverage**:
- ✅ Authentication with real users
- ✅ Token generation and verification
- ✅ Project creation and selection
- ✅ Session isolation between users
- ✅ Admin permissions
- ✅ Project sharing

**Run Command**:
```bash
# All multi-user tests
python tests/run_multiuser_tests.py

# Quick critical tests
python tests/run_multiuser_tests.py --quick

# Specific category
python tests/run_multiuser_tests.py -c "Multi-User Tests"
```

### 5. Memory System Tests
**Purpose**: Test the simplified memory system

**Current Files**:
- `test_simple_memory.py` - SimpleMemory with LLM extraction

**Features Tested**:
- ✅ Multi-language support (English, Chinese, Japanese)
- ✅ LLM-based information extraction
- ✅ README updates without templates
- ✅ No pattern matching

**Run Command**:
```bash
uv run python tests/test_simple_memory.py
```

### 6. File Conversion Tests
**Purpose**: Test document conversion pipeline

**Current Files**:
- `test_file_conversion_unit.py` - Unit tests for conversion
- `test_file_conversion_integration.py` - Integration tests

**Coverage**:
- ✅ PDF conversion with MinerU
- ✅ Office document conversion
- ✅ Registry tracking
- ✅ Fallback mechanisms

---

## 🚀 Test Runners

### 1. Unit Test Runner (pytest)
```bash
# All unit tests
uv run pytest tests/unit/

# With coverage
uv run pytest tests/unit/ --cov=src

# Specific component
uv run pytest tests/unit/test_config/
```

### 2. Agent Evaluation Runner
```bash
# Main evaluation CLI
python -m tests.agent_evaluation.run_evaluation [options]

Options:
  --compatibility    # Run legacy format tests
  --native          # Run multi-user tests only
  --categories      # Specific test categories
  --max-parallel    # Parallel execution (default: 3)
  --evaluator-model # LLM for evaluation
  --output-dir      # Results directory
```

### 3. Multi-User Test Runner
```bash
# Comprehensive runner
python tests/run_multiuser_tests.py [options]

Options:
  -v, --verbose     # Detailed output
  -c, --category    # Specific category
  -q, --quick       # Critical tests only
  -r, --report      # Save detailed report
```

---

## 📈 Test Metrics & Reporting

### Report Formats

**Unit Tests** (pytest output):
```
tests/unit/test_config/test_config.py::test_tavily_api_key PASSED
tests/unit/test_tools/test_file_analyzer.py::test_csv_analysis PASSED
==================== 47 passed in 12.3s ====================
```

**Agent Evaluation** (JSON reports):
```json
{
  "total_tests": 50,
  "passed_tests": 47,
  "overall_pass_rate": 0.94,
  "category_scores": {
    "memory_system": 8.7,
    "conversations": 8.3,
    "tool_selection": 8.9
  },
  "average_response_time": 2.3
}
```

**Multi-User Tests** (Summary output):
```
📊 Test Results Summary
================================
✅ API Tests: 5/5 passed
✅ Multi-User Tests: 6/6 passed
✅ Session Tests: 6/6 passed
⏱️ Duration: 45.2 seconds
```

### Test Data Locations
- **Reports**: `tests/reports/`
- **Test Data**: `data/bob_projects/` (backed up in `bob_projects_backup_*/`)
- **Temp Files**: Created in temp directories, auto-cleaned

---

## 🎯 Testing Philosophy

Following the project's Linus Torvalds-inspired approach:

1. **Keep it simple** - No overengineered test frameworks
2. **Test real workflows** - Focus on what users actually do
3. **Fast feedback** - Unit tests run in seconds
4. **Clear results** - Obvious pass/fail, no ambiguity
5. **Single source of truth** - This document reflects reality

### What We Test
- ✅ Code correctness (unit tests)
- ✅ System integration (workflows)
- ✅ Agent behavior quality (LLM evaluation)
- ✅ Multi-user functionality (auth, sessions)
- ✅ Memory system (multi-language)
- ✅ File conversions (PDF, Office)

### What We Don't Test (Yet)
- ❌ Performance under load
- ❌ Browser-based E2E tests
- ❌ Security/injection attacks
- ❌ Cost optimization
- ❌ Bio-safety validation

---

## 🔧 Development Workflow

### During Development
```bash
# Run unit tests frequently
uv run pytest tests/unit/ -x --lf  # Stop on failure, run last failed

# Test specific component
uv run pytest tests/unit/test_memory/ -v
```

### Before Commit
```bash
# 1. Unit tests
uv run pytest tests/unit/

# 2. Critical multi-user tests
python tests/run_multiuser_tests.py --quick

# 3. Quick agent evaluation
python -m tests.agent_evaluation.run_evaluation --quick
```

### Before Release
```bash
# Full test suite
python tests/run_multiuser_tests.py
python -m tests.agent_evaluation.run_evaluation --full
```

---

## 🐛 Common Test Issues & Solutions

### Issue: Tests fail with missing API keys
**Solution**: Set environment variables
```bash
export TAVILY_API_KEY="your-key"
export SILICONFLOW_API_KEY="your-key"
```

### Issue: Agent evaluation takes too long
**Solution**: Use quick mode or reduce parallel execution
```bash
python -m tests.agent_evaluation.run_evaluation --quick --max-parallel 1
```

### Issue: Multi-user tests fail with auth errors
**Solution**: Ensure backend is running
```bash
# Start backend first
uv run uvicorn src.api.app:app --port 8002
# Then run tests
python tests/test_api_simple.py
```

### Issue: File conversion tests fail
**Solution**: Check MinerU installation
```bash
# Requires Python 3.12 environment
python --version  # Should be 3.12+
```

---

## 📝 Adding New Tests

### Adding Unit Tests
1. Create file in appropriate `tests/unit/` subdirectory
2. Use pytest conventions (`test_*.py`, `def test_*()`)
3. Mock external dependencies
4. Keep tests fast (<1s)

### Adding Integration Tests
1. Create file in `tests/integration/`
2. Use TestSession for temp environments
3. Mock LLMs and sessions as needed
4. Test complete workflows

### Adding Agent Evaluation Scenarios
1. Add to `conversation_scenarios.py` or create new scenario file
2. Define test cases with expected outcomes
3. Include evaluation criteria
4. Use MultiUserTestCase for multi-user scenarios

### Adding Multi-User Tests
1. Update test files for new auth/session features
2. Use real users (alice, bob, admin)
3. Test with httpx AsyncClient
4. Verify permissions and isolation

---

## 📊 Current Test Coverage

**As of v3.4.0**:
- Unit Tests: ~30 test files
- Integration Tests: 2 main workflows
- Agent Evaluation: 50+ scenarios
- Multi-User Tests: 15+ test cases
- Total Test Files: ~50

**Recent Changes**:
- ✅ Added multi-user authentication tests
- ✅ Added session management tests
- ✅ Added admin functionality tests
- ✅ Removed outdated memory parser tests
- ✅ Consolidated file conversion tests

---

## 🔄 Continuous Improvement

### Weekly
- Review test failures
- Add regression tests for bugs
- Update test data from real usage

### Monthly
- Expand test scenarios
- Improve evaluation criteria
- Update this documentation

### Quarterly
- Major test refactoring if needed
- Performance testing review
- Security testing assessment

---

**Document Status**: Current and Accurate  
**Supersedes**: unified-testing-framework.md, practical-testing-framework.md  
**Next Update**: When test architecture changes significantly