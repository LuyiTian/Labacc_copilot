# LabAcc Copilot - Practical Testing Framework

**Status**: Implementation Ready  
**Date**: 2025-01-14  
**Version**: v1.0  
**Philosophy**: Test what matters, skip the rest

---

## Executive Summary

A **pragmatic testing framework** for LabAcc Copilot that focuses on **actual system behavior** rather than theoretical completeness. Tests the critical paths: memory updates, multi-round conversations, tool selection, and user corrections.

**Key Focus Areas:**
1. **Memory System Testing** - File uploads trigger README updates
2. **User Correction Handling** - Disagreements update memory correctly  
3. **Multi-Round Conversations** - Context carries between turns
4. **Tool Selection Logic** - Right tool for the task
5. **Natural Language Understanding** - Works in Chinese/English/Mixed

---

## 🎯 Testing Architecture (Simple & Effective)

```
┌─────────────────────────────────────────────────────────┐
│                  Core Test Categories                    │
├─────────────────────────────────────────────────────────┤
│ 1. Memory Tests      │ Tests README updates & persistence│
│ 2. Conversation Tests│ Multi-turn context & coherence    │
│ 3. Tool Tests        │ Correct tool selection & execution│
│ 4. Integration Tests │ File upload → Memory → Response   │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 Test Categories & Scenarios

### 1. Memory System Tests (25 scenarios)

#### 1.1 File Upload Memory Updates (10 tests)
```python
test_scenarios = [
    {
        "name": "csv_upload_triggers_readme",
        "action": "Upload results.csv to exp_001",
        "expected": "README.md updated with data summary",
        "verify": [
            "File registry contains results.csv",
            "Key insights extracted and saved",
            "Timestamp added to change log"
        ]
    },
    {
        "name": "image_upload_memory",
        "action": "Upload gel_image.png",
        "expected": "Image analysis saved to README",
        "verify": ["Band patterns noted", "Issues identified"]
    },
    {
        "name": "multi_file_batch_upload",
        "action": "Upload 5 files simultaneously",
        "expected": "All files processed, README updated once",
        "verify": ["Batch processing", "Single coherent update"]
    }
]
```

#### 1.2 User Correction Memory Updates (10 tests)
```python
correction_tests = [
    {
        "name": "disagree_with_analysis",
        "user_says": "我不同意你的总结，我认为这次实验细胞数量少是因为载入10X的初始细胞数少导致的，不是由于温度太高",
        "expected_memory_update": {
            "section": "User Corrections",
            "content": "User disagrees with temperature hypothesis. Attributes low cell count to initial loading quantity.",
            "timestamp": True
        }
    },
    {
        "name": "provide_missing_context",
        "user_says": "You missed that we used old reagents past expiration",
        "expected_memory_update": {
            "section": "Experimental Notes",
            "content": "Expired reagents used (user-reported)",
            "critical": True
        }
    },
    {
        "name": "correct_protocol_details",
        "user_says": "Actually we incubated for 30 minutes not 45",
        "expected_memory_update": {
            "section": "Protocol Details",
            "update": "Incubation time: 30 min (corrected from 45 min)"
        }
    }
]
```

#### 1.3 Memory Persistence Tests (5 tests)
```python
persistence_tests = [
    {
        "name": "memory_survives_session",
        "steps": [
            "Create memory in session_1",
            "End session_1",
            "Start session_2",
            "Verify memory accessible"
        ]
    },
    {
        "name": "cross_experiment_memory",
        "test": "Memory from exp_001 influences exp_002 suggestions"
    }
]
```

### 2. Multi-Round Conversation Tests (20 scenarios)

#### 2.1 Context Carryover (10 tests)
```python
conversation_tests = [
    {
        "name": "three_turn_analysis",
        "turns": [
            ("What experiments do I have?", "scan_project"),
            ("Tell me about the first one", "analyze_data"),  # Should remember exp list
            ("What went wrong?", "diagnose_issue")  # Should use previous analysis
        ],
        "verify_context": [
            "Turn 2 knows which is 'first' from Turn 1",
            "Turn 3 uses data from Turn 2 analysis"
        ]
    },
    {
        "name": "folder_navigation_context",
        "turns": [
            ("进入exp_001文件夹", "list_folder_contents"),
            ("分析这里的数据", "analyze_data"),  # Should know current folder
            ("和exp_002对比如何？", "compare_experiments")  # Should remember both
        ]
    }
]
```

#### 2.2 Progressive Disclosure (5 tests)
```python
progressive_tests = [
    {
        "name": "drill_down_analysis",
        "turns": [
            "General project overview",
            "Specific experiment details",
            "Particular data point investigation",
            "Root cause analysis"
        ],
        "verify": "Each turn builds on previous depth"
    }
]
```

#### 2.3 Topic Switching (5 tests)
```python
topic_switch_tests = [
    {
        "name": "context_switch_recovery",
        "turns": [
            "Analyze exp_001 PCR results",
            "Search literature on CRISPR",  # Topic switch
            "Back to the PCR problem"  # Should remember exp_001 context
        ]
    }
]
```

### 3. Tool Selection Tests (25 scenarios)

#### 3.1 Correct Tool for Task (15 tests)
```python
tool_selection_tests = [
    {
        "query": "What's in this folder?",
        "expected_tool": "list_folder_contents",
        "not": ["scan_project", "analyze_data"]
    },
    {
        "query": "分析experiment_results.csv",
        "expected_tool": "analyze_data",
        "context": {"selected_files": ["experiment_results.csv"]}
    },
    {
        "query": "Find papers about cold digestion",
        "expected_tool": "run_deep_research"
    },
    {
        "query": "Why did my cells die?",
        "expected_tools_sequence": [
            "analyze_data",  # First understand the data
            "diagnose_issue"  # Then diagnose
        ]
    }
]
```

#### 3.2 Tool Chaining (5 tests)
```python
tool_chain_tests = [
    {
        "name": "discovery_to_analysis",
        "query": "Analyze all CSV files in exp_001",
        "expected_sequence": [
            "list_folder_contents",  # Find CSV files
            "analyze_data"  # Analyze them
        ]
    }
]
```

#### 3.3 Tool Failure Recovery (5 tests)
```python
failure_recovery_tests = [
    {
        "name": "file_not_found_recovery",
        "scenario": "User requests non-existent file",
        "expected_behavior": [
            "analyze_data fails gracefully",
            "list_folder_contents shows available files",
            "Suggests alternatives"
        ]
    }
]
```

### 4. Integration Tests (15 scenarios)

#### 4.1 End-to-End Workflows (10 tests)
```python
workflow_tests = [
    {
        "name": "complete_experiment_analysis",
        "workflow": [
            "Upload new data file",
            "Automatic README update",
            "User asks about the data",
            "Agent uses updated memory",
            "User corrects interpretation",
            "Memory updates with correction",
            "Future queries use corrected info"
        ]
    },
    {
        "name": "cross_experiment_optimization",
        "workflow": [
            "Analyze exp_001 failures",
            "Save insights to memory",
            "Create exp_002",
            "Apply lessons from exp_001",
            "Verify recommendations use memory"
        ]
    }
]
```

#### 4.2 Language Mixing (5 tests)
```python
language_tests = [
    {
        "name": "chinese_english_mix",
        "query": "这个PCR protocol有什么问题？",
        "verify": "Handles mixed terminology naturally"
    },
    {
        "name": "technical_terms_preserved",
        "query": "分析这个scRNAseq的clustering结果",
        "verify": "Technical terms understood regardless of language"
    }
]
```

### 5. Regression Tests (10 scenarios)

#### 5.1 Known Issues Prevention
```python
regression_tests = [
    {
        "name": "no_generic_responses",
        "query": "Tell me about this project",
        "must_not_contain": [
            "typical project structure",
            "generally includes",
            "common folders"
        ],
        "must_use_tools": ["scan_project", "list_folder_contents"]
    },
    {
        "name": "no_tool_spam",
        "query": "Simple greeting",
        "max_tools_used": 0,  # Should not trigger tools
        "response": "Natural greeting without analysis"
    }
]
```

---

## 🚀 Implementation Plan

### Phase 1: Memory Testing Infrastructure (Week 1)
```python
# tests/test_memory_system.py
class MemorySystemTests:
    def test_file_upload_triggers_update(self):
        """Upload file → README update → Verify content"""
        
    def test_user_correction_updates_memory(self):
        """User disagrees → Memory updates → Future queries use correction"""
        
    def test_memory_persistence_across_sessions(self):
        """Create memory → New session → Memory still there"""
```

### Phase 2: Conversation Testing (Week 2)
```python
# tests/test_conversations.py
class ConversationTests:
    def test_multi_turn_context(self):
        """3+ turns with context carryover"""
        
    def test_topic_switching_recovery(self):
        """Switch topics and return with context intact"""
```

### Phase 3: Tool Testing (Week 3)
```python
# tests/test_tool_selection.py
class ToolSelectionTests:
    def test_correct_tool_for_query(self):
        """Verify optimal tool selection"""
        
    def test_tool_chaining_logic(self):
        """Complex queries use multiple tools correctly"""
```

### Phase 4: Integration & CI/CD (Week 4)
```python
# tests/test_integration.py
class IntegrationTests:
    def test_end_to_end_workflow(self):
        """Complete user journey from upload to analysis"""
```

---

## 📈 Test Metrics & Reporting

### Key Metrics
```python
metrics = {
    "memory_accuracy": "% of memory updates that are correct",
    "context_retention": "% of context maintained across turns",
    "tool_selection_accuracy": "% of queries using optimal tools",
    "response_time": "Average time per query type",
    "error_recovery_rate": "% of errors handled gracefully"
}
```

### Simple Dashboard Output
```
========================================
LabAcc Copilot Test Results - v2.2.1
========================================
Memory Tests:         18/20 passed (90%)
Conversation Tests:   17/20 passed (85%)
Tool Selection:       23/25 passed (92%)
Integration Tests:    14/15 passed (93%)
Regression Tests:     10/10 passed (100%)
----------------------------------------
Overall:              82/90 passed (91%)
Average Response:     2.3 seconds
Memory Update Rate:   95% successful
Context Retention:    88% across turns
========================================
```

---

## 🔧 Test Execution

### Quick Test Suite (3 minutes)
```bash
# Run essential tests only
python run_tests.py --quick
# Tests: 15 critical scenarios across all categories
```

### Standard Test Suite (10 minutes)  
```bash
# Run standard test coverage
python run_tests.py --standard
# Tests: 50 key scenarios
```

### Full Test Suite (20 minutes)
```bash
# Run all tests
python run_tests.py --full
# Tests: All 90 scenarios
```

### Specific Category
```bash
# Test only memory system
python run_tests.py --category memory

# Test only conversations
python run_tests.py --category conversation
```

---

## 🎯 Success Criteria

### Must Pass (Blocking)
- ✅ Memory updates work for file uploads
- ✅ User corrections update memory
- ✅ Multi-turn conversations maintain context
- ✅ Correct tools selected >85% of time
- ✅ No generic responses when tools should be used

### Should Pass (Important)
- ✅ Memory persists across sessions
- ✅ Tool failures handled gracefully
- ✅ Works in Chinese and English
- ✅ Response time <5 seconds

### Nice to Have (Future)
- Cross-experiment learning
- Complex workflow automation
- Advanced reasoning chains

---

## 📝 Test Data Setup

### Use Existing Bob's Projects
```python
test_data = {
    "base_path": "data/bob_projects/",
    "experiments": [
        "exp_001_protocol_test",  # Has real scRNAseq data
        "exp_002_optimization",   # For cross-experiment tests
        "exp_003_troubleshooting" # For error scenarios
    ],
    "backup": "data/bob_projects_backup_*/"  # Restore after tests
}
```

### Memory Test Files
```python
test_files = {
    "csv": "test_results.csv",  # Trigger data analysis
    "image": "gel_image.png",   # Trigger image analysis
    "text": "protocol_notes.txt", # Trigger text extraction
    "excel": "cell_counts.xlsx"  # Trigger spreadsheet analysis
}
```

---

## 🚫 What We're NOT Testing (Yet)

### Out of Scope for Now
- ❌ Bio-safety validation (too early)
- ❌ Cost optimization (not critical)
- ❌ Complex multi-agent coordination (using single agent)
- ❌ Performance under load (early stage)
- ❌ Security/injection attacks (later phase)
- ❌ Internationalization beyond Chinese/English

### Why This Approach Works
1. **Focuses on actual user pain points** (memory, context, tools)
2. **Tests real workflows** not theoretical scenarios
3. **Quick to implement** with existing infrastructure
4. **Easy to debug** when tests fail
5. **Provides clear pass/fail** criteria

---

## 🔄 Continuous Improvement

### Weekly Test Review
- Review failed tests from the week
- Add regression tests for new bugs
- Update test data with real user cases
- Adjust success thresholds based on user feedback

### Monthly Test Expansion
- Add new scenarios based on user behavior
- Increase conversation turn depth
- Add more language variations
- Enhance memory complexity tests

---

## 💡 Key Insights

### From Research & Current System Analysis

1. **Memory is Critical**: The README-based memory system is unique and must work flawlessly
2. **Context is King**: Multi-turn conversations are where most agents fail
3. **Tools Must Be Smart**: Wrong tool = wrong answer = user frustration
4. **Corrections Matter**: Users will correct the agent - this must update memory
5. **Language is Natural**: No patterns, just understanding

### Testing Philosophy

> "Test what users actually do, not what we think they might do"

Focus on the **critical path** through the system:
1. User uploads file
2. Memory updates automatically  
3. User asks questions
4. Agent uses updated memory
5. User corrects if needed
6. Memory updates again
7. Future queries are smarter

If this loop works, the system works.

---

**Document Status**: Ready for Implementation  
**Next Step**: Create test files in /tests/ following this framework  
**Timeline**: 4 weeks to full test coverage