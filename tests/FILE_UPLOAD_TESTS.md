# File Upload Test System Documentation

## Overview

Comprehensive test framework for the **file upload → conversion → analysis → memory** cycle, implemented following Linus Torvalds' philosophy: simple, direct, no overengineering.

## 🎯 What We Test

### Complete File Processing Cycle
1. **File Upload** - Files saved to correct locations
2. **Format Conversion** - PDF/Office → Markdown
3. **Context Loading** - README provides experiment context
4. **Agent Analysis** - Intelligent analysis with context
5. **Question Generation** - Follow-up questions created
6. **User Response Capture** - Answers tracked in session
7. **Memory Update** - README updated with insights

## 🏗️ Test Architecture

```
tests/
├── run_tests.sh              # Master test runner (NEW)
├── unit/                     # Fast, isolated tests
│   └── test_file_registry.py # File tracking tests
├── integration/              # Workflow tests
│   ├── test_upload_workflow.py   # Upload→conversion→analysis
│   └── test_memory_update.py     # User response→memory
├── fixtures/                 # Test data
│   ├── sample.txt           # Test document
│   └── mock_responses.json  # Predictable LLM outputs
└── utils/                    # Test utilities
    ├── mock_llm.py          # Fast, predictable LLM
    └── test_session.py      # Test environment setup
```

## 🚀 Quick Start

### Run All File Upload Tests
```bash
./tests/run_tests.sh file-upload
```

### Run Quick Smoke Test
```bash
./tests/run_tests.sh quick
```

### Run Specific Test
```bash
uv run python tests/integration/test_upload_workflow.py
```

## 📊 Test Results

### Current Status: ✅ ALL PASSING
```
============================================================
📊 TEST SUMMARY
============================================================
   Passed: 3/3

🎉 ALL TESTS PASSED!
```

## 🧪 Test Details

### 1. Upload → Conversion → Analysis Test
**File**: `tests/integration/test_upload_workflow.py`

**Tests**:
- File upload and storage in `originals/`
- Conversion detection for PDFs/Office files
- File registry updates
- Agent analysis with README context
- Follow-up question generation
- Session state tracking

**Key Assertions**:
```python
assert registry_path.exists()              # Registry created
assert "protocol.txt" in registry['files'] # File tracked
assert "Summary" in analysis_response      # Analysis quality
assert "?" in analysis_response           # Questions generated
assert session.pending_questions          # Questions tracked
```

### 2. Memory Update Test
**File**: `tests/integration/test_memory_update.py`

**Tests**:
- Initial memory state
- Question tracking in session
- User response processing
- Memory update with context
- Question clearance after update
- Memory persistence

**Key Assertions**:
```python
assert len(updated_content) > len(initial_content)  # Memory grew
assert "File Upload Analysis" in updated_content    # Section added
assert experiment_id not in session.pending_questions # Cleared
```

### 3. File Registry Test
**File**: `tests/unit/test_file_registry.py`

**Tests**:
- Registry creation with correct structure
- Registry updates and persistence
- File tracking with conversion status

## 🔧 Test Utilities

### Mock LLM
**Purpose**: Fast, predictable responses without API calls

**Benefits**:
- Tests run in seconds (no API latency)
- Predictable outputs (same every time)
- Zero cost (no token usage)
- Easy edge case testing

**Usage**:
```python
from tests.utils.mock_llm import MockLLM, patch_llm_for_tests

# In test
mock_llm, original = patch_llm_for_tests()
# ... run test ...
unpatch_llm(original)
```

### Test Session Manager
**Purpose**: Isolated test environments

**Features**:
- Temporary directories for test data
- Automatic cleanup after tests
- Mock experiment setup
- Session state management

**Usage**:
```python
from tests.utils.test_session import TestSession

test_session = TestSession(use_temp_dir=True)
project_root, experiment_id, session_id = test_session.setup()
# ... run test ...
test_session.cleanup()
```

## 🎯 Design Philosophy

Following Linus Torvalds' approach:

### Simple is Better
- No complex test frameworks
- Direct Python scripts
- Clear pass/fail results

### Fast Feedback
- Mock LLM for speed
- Small test data
- Parallel execution

### Real Scenarios
- Test actual user workflows
- Use realistic data
- Cover edge cases

### No Overengineering
- Just enough testing
- Focus on critical paths
- Maintainable code

## 🔍 Debugging Tests

### Verbose Output
```bash
uv run python -v tests/integration/test_upload_workflow.py
```

### Check Test Environment
```bash
ls -la /tmp/labacc_test_*
```

### Run Individual Test Functions
```python
# In Python
import asyncio
from tests.integration.test_upload_workflow import test_pdf_conversion
asyncio.run(test_pdf_conversion())
```

## 📈 Future Improvements

### TODO Tests
- [ ] Corrupted file handling
- [ ] Large file uploads (>10MB)
- [ ] Concurrent upload testing
- [ ] WebSocket notification tests
- [ ] UI state management tests
- [ ] Network error recovery

### Performance Goals
- All tests < 30 seconds
- Individual test < 5 seconds
- Mock responses < 100ms

## 🐛 Known Issues

1. **Real LLM Sometimes Used**: Integration tests may use real LLM if mock not properly injected
2. **Temp Directory Cleanup**: May leave `/tmp/labacc_test_*` on test failure
3. **PDF Conversion**: Mock PDF content can't actually be converted

## 📝 Writing New Tests

### Template
```python
async def test_new_feature():
    """Test description."""
    
    # Setup
    test_session = TestSession(use_temp_dir=True)
    project_root, experiment_id, session_id = test_session.setup()
    
    try:
        # Test logic
        result = await some_function()
        assert result == expected, "Clear error message"
        
        # Cleanup
        test_session.cleanup()
        print("✅ PASSED: New Feature")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        test_session.cleanup()
        return False
```

### Best Practices
1. **One test, one purpose**
2. **Clear error messages**
3. **Always cleanup**
4. **Print progress**
5. **Return success boolean**

## 🚦 CI/CD Integration

### GitHub Actions (Future)
```yaml
name: File Upload Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install uv
        run: pip install uv
      - name: Run tests
        run: ./tests/run_tests.sh file-upload
```

---

**Created**: 2025-01-16  
**Test Count**: 8 tests  
**Runtime**: <30 seconds  
**Philosophy**: "Perfection is achieved when there is nothing left to take away"