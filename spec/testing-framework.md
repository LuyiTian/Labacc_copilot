# LabAcc Copilot - Practical Testing Framework

**Status**: Updated for Early-Stage Project  
**Date**: 2025-01-23  
**Version**: v3.4.1  
**Philosophy**: Test core functionality, keep it simple, don't over-test

---

## Executive Summary

For this early-stage project, we focus on **essential testing only**:

1. **Core Function Tests** - Test file conversion, memory system, API endpoints work
2. **Basic Integration** - Test file upload → conversion → agent analysis flow
3. **Smoke Tests** - Quick tests to verify system isn't broken before commits

**What we DON'T test** (not needed for small project):
- Performance/load testing
- Security/injection attacks  
- Cost optimization
- Browser E2E testing
- Exhaustive edge cases

---

## 🏗️ Simplified Testing Structure

```
LabAcc Testing (What Actually Matters)
├── Quick Smoke Tests (2 min)              
│   ├── File upload works?
│   ├── Agent responds?
│   └── Basic auth works?
│                                     
├── Core Functionality (5 min)                 
│   ├── PDF → Markdown conversion
│   ├── Memory read/write
│   ├── Project creation
│   └── Session management
│                                     
└── Full Test Suite (10 min)
    ├── All the above
    ├── Multi-user scenarios
    └── Agent evaluation (optional)
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

### What We Actually Need to Test (Priority Order)

**Critical (Test Every Commit)**
- ✅ File upload → conversion works
- ✅ Agent can read files and respond
- ✅ Basic auth/login works
- ✅ Projects can be created

**Important (Test Before Release)**
- ✅ Memory system reads/writes READMEs
- ✅ Sessions isolate users properly
- ✅ File registry tracks conversions
- ✅ React agent tools execute

**Nice to Have (Test Weekly)**
- 🟡 Agent response quality (expensive LLM calls)
- 🟡 Multi-turn conversations
- 🟡 Edge cases in file conversion

### What We DON'T Need (Waste of Time)
- ❌ Load testing (it's a small lab tool)
- ❌ Browser automation (manual testing is fine)
- ❌ Security testing (not internet-facing)
- ❌ Cost optimization (users pay their own API keys)
- ❌ 100% code coverage (diminishing returns)

---

## 🔧 Practical Development Workflow

### During Development (Every Save)
```bash
# Just run the quick smoke test
./tests/run_tests.sh quick  # 30 seconds
```

### Before Commit (Every Push)
```bash
# Run core functionality tests
uv run python tests/test_file_conversion_unit.py  # File conversion works?
uv run python tests/test_api_simple.py            # API endpoints work?
# Total: 2-3 minutes
```

### Before Release (Weekly)
```bash
# Run everything that matters
./tests/run_tests.sh all       # All unit + integration tests
python tests/run_multiuser_tests.py  # Multi-user scenarios
# Total: 10 minutes

# Optional: Agent quality check (expensive)
# python -m tests.agent_evaluation.run_evaluation --quick
```

### What NOT to Do
```bash
# DON'T run these every time (waste of time):
# - Full agent evaluation suite (uses expensive LLM calls)
# - Exhaustive edge case testing
# - Performance benchmarking
# - Security scanning
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

## 📊 Test Cleanup Recommendations

### Tests to KEEP (Essential)
```
tests/
├── test_file_conversion_unit.py     # Core functionality
├── test_api_simple.py               # API endpoints work
├── test_session_management.py       # User isolation
├── integration/
│   └── test_upload_workflow.py      # Main user flow
└── run_tests.sh                     # Simple test runner
```

### Tests to SIMPLIFY
- **Agent evaluation** - Make it optional, not default
- **Multi-user tests** - Combine into single file
- **Unit tests** - Focus on critical paths only

### Tests to REMOVE (Overkill)
- Complex test generators
- Multiple overlapping test runners
- Exhaustive edge case scenarios
- Performance benchmarks
- Mock-heavy unit tests that test mocks not code

### New Simple Test Pattern
```python
# Simple, direct testing - no complex fixtures
def test_file_upload():
    """Test that files can be uploaded and converted"""
    # 1. Upload a PDF
    # 2. Check it converts to markdown
    # 3. Verify agent can read it
    # Done - no need for 20 edge cases
```

---

## 🔄 Testing Philosophy for Small Projects

### Core Principles
1. **Test the happy path** - If basic flow works, 90% of usage works
2. **Manual testing is OK** - For UI and edge cases
3. **Fast feedback** - Tests should run in seconds, not minutes
4. **Pragmatic coverage** - Test what breaks, not everything
5. **Delete failing tests** - If a test keeps failing and isn't critical, delete it

### When to Add Tests
- After a bug is found (regression test)
- For critical user flows (upload, convert, analyze)
- For tricky logic (path resolution, auth)

### When NOT to Add Tests
- For simple CRUD operations
- For UI interactions (test manually)
- For third-party integrations (they have their own tests)
- For "what if" scenarios that never happen

### The 80/20 Rule
- 20% of tests catch 80% of bugs
- Focus on that 20%
- Delete the rest

---

**Document Status**: Simplified for Early-Stage Project  
**Philosophy**: Practical testing for a small team, not enterprise testing  
**Remember**: Perfect test coverage is the enemy of shipping features