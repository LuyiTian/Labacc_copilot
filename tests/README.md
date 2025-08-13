# LabAcc Copilot Agent Evaluation Framework

**State-of-the-Art Agent Testing System**

Comprehensive test-driven development framework implementing the latest research in LLM agent evaluation, including **Agent-as-a-Judge** methodology, multilingual testing, and automated regression detection.

## 🎯 Problem Solved

**Before**: Slow, manual development-test cycle
- Developer edits code → starts dev server → opens webpage → types message → waits for response → manually copies output → evaluates by hand
- 15+ minute cycle time, prone to human error, no systematic evaluation

**After**: Fast, automated evaluation
- Developer edits code → runs `python run_evaluation.py --quick` → gets comprehensive evaluation in 3 minutes
- Systematic testing across 100+ scenarios, multilingual support, objective scoring

## 🏗️ Architecture

### Core Components

```
tests/
├── agent_evaluation/
│   ├── evaluator_agent.py     # LLM-as-a-Judge evaluation
│   ├── test_generator.py      # Comprehensive test case generation  
│   ├── test_runner.py         # Parallel test execution & reporting
│   └── __init__.py           # Framework API
├── test_cases/               # Generated test scenarios
├── reports/                  # Evaluation results & analytics
└── README.md                # This file
```

### Framework Features

✅ **LLM-as-a-Judge Evaluation**: Uses advanced LLM to objectively score responses  
✅ **Multilingual Testing**: Ensures no English-only pattern matching (supports Chinese)  
✅ **Test-Driven Development**: Write tests first, then develop to pass them  
✅ **Automated Regression Testing**: Prevents new code from breaking existing functionality  
✅ **Performance Benchmarking**: Tracks response times, API costs, system performance  
✅ **Realistic Test Environment**: Uses Bob's scRNAseq project as ground truth  
✅ **Parallel Execution**: Fast testing with configurable parallelism  
✅ **Comprehensive Reporting**: Detailed analytics with visual summaries  

## 🧪 Test Categories

### 1. Context Understanding
Tests agent's ability to understand experimental context:
- **English**: "What is in this folder?"
- **Chinese**: "这个文件夹里有什么？"
- **Expected**: Should identify scRNAseq files, experimental context

### 2. File Analysis  
Tests specific file understanding:
- **English**: "Tell me about this file" (dissociation_notes.txt selected)
- **Chinese**: "告诉我这个文件的内容"
- **Expected**: Should understand protocol notes, identify issues

### 3. Experiment Insights
Tests scientific reasoning:
- **English**: "What went wrong with this experiment?"
- **Chinese**: "这个实验出了什么问题？"
- **Expected**: Should identify immune enrichment bias (8% epithelial, 65% immune)

### 4. Protocol Optimization
Tests recommendation capability:
- **English**: "How should we optimize the protocol?" 
- **Chinese**: "我们应该如何优化这个协议？"
- **Expected**: Should suggest cold pre-digestion, shorter warm digestion

### 5. Edge Cases & Robustness
- Ambiguous queries: "Analyze" (without context)
- Mixed languages: "Tell me about 这个实验"
- Error handling: Empty folders, corrupted files

## 🚀 Quick Start

### 1. Setup
```bash
# Ensure API keys are set
export OPENROUTER_API_KEY="your-key"
export SILICONFLOW_API_KEY="your-key"  
export TAVILY_API_KEY="your-key"

# Install dependencies (if not already installed)
pip install -r requirements.txt
```

### 2. Run Quick Test (3 minutes)
```bash
python run_evaluation.py --quick
```

### 3. Run Full Evaluation (10-15 minutes)
```bash
python run_evaluation.py --full
```

### 4. Test Specific Category
```bash
python run_evaluation.py --full --category context_understanding
```

### 5. Test Specific Language
```bash
python run_evaluation.py --full --language chinese
```

## 🔧 Advanced Usage

### Test-Driven Development Workflow

**1. Write Failing Test**
```bash
# Add new capability test case
python run_evaluation.py --generate-tests
# Edit tests/test_cases/generated_test_suite.json to add your test
```

**2. Run Test (Should Fail)**  
```bash
python run_evaluation.py --full --test-file tests/test_cases/your_test.json
```

**3. Implement Feature**
```python
# Edit src/agents/react_agent.py to add capability
```

**4. Verify Test Passes**
```bash
python run_evaluation.py --full --test-file tests/test_cases/your_test.json
```

### Continuous Integration

Add to your CI/CD pipeline:
```bash
# Run evaluation and fail build if below threshold
python run_evaluation.py --full --threshold 0.8
```

### Regression Testing

```bash
# Save current results as baseline
cp tests/reports/test_summary_latest.json baseline.json

# Later, test for regressions
python run_evaluation.py --full --baseline baseline.json
```

## 📊 Evaluation Criteria

### Scoring System (1-10 scale)

**Accuracy** (30% weight): Factual correctness vs ground truth  
**Relevance** (25% weight): Addresses user's intent  
**Completeness** (20% weight): Includes key details  
**Context Awareness** (15% weight): Understands experimental context  
**Language Understanding** (10% weight): Handles non-English correctly  

### Pass/Fail Thresholds

- **Production Ready**: ≥8.0 overall score
- **Acceptable**: ≥7.0 overall score  
- **Needs Improvement**: <7.0 overall score

### Performance Metrics

- **Response Time**: Target <3 seconds for simple queries
- **API Cost**: Track token usage per query
- **Throughput**: Concurrent request handling
- **Memory Usage**: System resource consumption

## 📈 Example Results

```
🧪 LABACC COPILOT AGENT EVALUATION REPORT
================================================================================

📊 OVERALL RESULTS:
  Total Tests: 94
  Passed: 82 ✅  
  Failed: 12 ❌
  Pass Rate: 87.2%
  Status: 🟢 EXCELLENT

📈 PERFORMANCE METRICS:
  Average Response Time: 2,847ms
  Total Execution Time: 8.2s

📋 CATEGORY BREAKDOWN:
  Context Understanding: 8.7/10 ✅
  File Analysis: 8.2/10 ✅  
  Experiment Insights: 7.9/10 ✅
  Protocol Optimization: 8.5/10 ✅
  Multilingual: 8.1/10 ✅

🌍 LANGUAGE PERFORMANCE:
  English: 8.4/10 ✅
  Chinese: 8.0/10 ✅
  Mixed: 7.8/10 ✅
```

## 🛠️ Customization

### Adding New Test Categories

1. **Extend TestCategory enum** in `evaluator_agent.py`
2. **Add generation method** in `test_generator.py`  
3. **Create test cases** with expected outputs
4. **Run tests** to validate

### Custom Evaluation Criteria

```python
from tests.agent_evaluation import AgentEvaluator

# Custom evaluator with different criteria weights
evaluator = AgentEvaluator()
evaluator.criteria_weights = {
    'accuracy': 0.4,      # Increase accuracy weight
    'relevance': 0.3,     # Increase relevance weight  
    'completeness': 0.2,
    'context_awareness': 0.1,
    'language_understanding': 0.0  # Disable language scoring
}
```

### Adding New Languages

1. **Add test queries** in target language to `test_generator.py`
2. **Update evaluation prompts** to handle new language
3. **Test evaluation** with native speakers

## 📋 Command Reference

### Main Commands
```bash
# Full evaluation with all tests
python run_evaluation.py --full

# Quick test (4 key scenarios) 
python run_evaluation.py --quick

# Generate test cases only
python run_evaluation.py --generate-tests
```

### Filtering Options
```bash
# Test specific category
python run_evaluation.py --full --category context_understanding

# Test specific language  
python run_evaluation.py --full --language chinese

# Custom test file
python run_evaluation.py --full --test-file my_tests.json
```

### Configuration Options
```bash
# Custom evaluator model
python run_evaluation.py --full --evaluator-model gpt-4

# Adjust parallelism
python run_evaluation.py --full --parallel 5

# Custom pass threshold
python run_evaluation.py --full --threshold 0.9
```

### Output Options
```bash
# Custom output directory
python run_evaluation.py --full --output-dir /path/to/results

# Debug mode
python run_evaluation.py --full --debug

# Verbose output
python run_evaluation.py --full --verbose
```

## 🔍 Troubleshooting

### Common Issues

**"No API keys found"**
- Set `OPENROUTER_API_KEY` or `SILICONFLOW_API_KEY`
- At minimum, one LLM provider key is required

**"Failed to import agent modules"**
- Ensure you're running from the project root directory
- Check that `src/agents/react_agent.py` exists

**"Low pass rates on Chinese tests"**  
- Agent may have English-only pattern matching
- Review agent code for hardcoded English keywords
- Ensure LLM supports Chinese language processing

**"Tests timing out"**
- Reduce `--parallel` parameter (try 1-2)
- Check network connectivity for API calls
- Verify LLM provider service status

### Debug Mode

```bash
# Run with detailed error information
python run_evaluation.py --full --debug

# Examine specific test failures
cat tests/reports/failed_tests_*.json
```

### Performance Optimization

**Too Slow**:
- Increase `--parallel` (but watch API rate limits)
- Use faster evaluator model (e.g., `siliconflow-qwen-30b`) or set `EVALUATOR_MODEL` env var
- Filter to specific categories for development

**Too Expensive**:
- Use cheaper models for development testing
- Reduce test suite size during development
- Save full evaluation for CI/CD only

## 🎯 Best Practices

### Development Workflow

1. **Start with Quick Test**: `--quick` for rapid feedback
2. **Category-Specific Testing**: Focus on areas you're developing
3. **Full Evaluation Before Merge**: Ensure no regressions
4. **Baseline Tracking**: Save results for regression testing

### Test Case Design

- **Specific Ground Truth**: Know exactly what the correct answer should be
- **Realistic Scenarios**: Use actual lab data and situations
- **Edge Case Coverage**: Test unusual inputs and error conditions  
- **Multilingual Parity**: Ensure same functionality across languages

### CI/CD Integration

```yaml
# Example GitHub Actions workflow
- name: Run Agent Evaluation
  run: |
    python run_evaluation.py --full --threshold 0.8
    # Fail build if evaluation doesn't meet threshold
```

## 📚 Research Background

This framework implements state-of-the-art methodologies from recent research:

**Agent-as-a-Judge** (2024): More sophisticated than LLM-as-a-Judge, uses specialized agents for evaluation
**Multi-Agent Evaluation** (2024): Comprehensive evaluation across multiple dimensions
**Cross-Language Testing** (2024): Ensures multilingual capability without pattern matching
**Test-Driven Agent Development** (2024): Systematic approach to agent capability development

### Key Papers Referenced

- "Agent-as-a-Judge: Evaluate Agents with Agents" (ArXiv 2024)
- "Evaluation and Benchmarking of LLM Agents: A Survey" (ArXiv 2024)  
- "Survey on Evaluation of LLM-based Agents" (ArXiv 2024)
- "Multi-agent LLM Evaluations" (LessWrong 2024)

## 🤝 Contributing

### Adding Test Cases

1. Fork the repository
2. Add test cases to `test_generator.py`
3. Include expected outputs and ground truth
4. Test with both English and Chinese queries
5. Submit pull request

### Improving Evaluation

1. Review failed test cases in `tests/reports/failed_tests_*.json`
2. Identify patterns in evaluation errors
3. Improve evaluation prompts or criteria
4. Validate improvements don't cause regressions

### Performance Optimization

1. Profile test execution with `--debug --verbose`
2. Identify bottlenecks (API calls, file I/O, evaluation)
3. Implement optimizations while maintaining accuracy
4. Benchmark improvements

## 📄 License

This evaluation framework is part of the LabAcc Copilot project. Use in accordance with project licensing.

---

**🎉 Ready to revolutionize your agent development workflow?**

Start with: `python run_evaluation.py --quick`