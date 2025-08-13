# LabAcc Copilot Testing Guide

## System Overview

LabAcc Copilot is an AI-powered laboratory assistant that uses README files as memory for each experiment. The system helps wet-lab biologists analyze data, diagnose issues, and optimize protocols.

## Prerequisites

### Required Environment Variables
```bash
# For GPT-OSS 120B (recommended)
export OPENROUTER_API_KEY="your-openrouter-api-key"

# Alternative: For Qwen models
export SILICONFLOW_API_KEY="your-siliconflow-api-key"

# Optional: For literature search
export TAVILY_API_KEY="your-tavily-api-key"
```

### Model Configuration
The LLM model is configured in `src/config/llm_config.json`. Default is GPT-OSS 120B via OpenRouter.

## Starting the System

### 1. Start the Backend API
```bash
# Terminal 1: Start FastAPI backend on port 8002
uv run uvicorn src.api.app:app --port 8002 --reload
```

### 2. Start the Frontend (Optional)
```bash
# Terminal 2: Start React frontend on port 5173
cd frontend
npm run dev
```

### 3. Alternative: Use Start Script
```bash
# Start both backend and frontend
./start-dev.sh
```

## Testing Methods

### Method 1: Direct Python Testing

Run the test script to verify core functionality:

```bash
# Test the React agent with memory tools
uv run python test_react_agent.py
```

### Method 2: API Testing with curl

Test the REST API directly:

```bash
# Initialize session
curl -X POST http://localhost:8002/api/chat/init \
  -H "Content-Type: application/json" \
  -d '{"currentFolder": null, "selectedFiles": []}'

# Send a message (use the sessionId from init response)
curl -X POST http://localhost:8002/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "YOUR_SESSION_ID",
    "message": "Scan my experiments",
    "currentFolder": null,
    "selectedFiles": []
  }'
```

### Method 3: Interactive Frontend

1. Open http://localhost:5173 in your browser
2. Use the chat interface to interact with the agent
3. Navigate folders in the file manager
4. The agent will have context of your current folder and selected files

## Test Scenarios

### Scenario 1: Create and Manage Experiments

**Test Commands:**
```
1. "Create a new experiment for PCR optimization"
2. "Read the overview of exp_001_pcr_optimization"
3. "Add an insight: Temperature of 62°C shows best results"
4. "Update the results section with my findings"
```

**Expected Results:**
- New experiment folder created in `data/alice_projects/`
- README.md file created with proper structure
- Insights added with timestamps
- Sections updated while preserving other content

### Scenario 2: Data Analysis with Context

**Test Commands:**
```
1. "Analyze the file data_001.csv in exp_001_pcr_optimization"
2. "What do the results tell us?"
3. "Compare this with other PCR experiments"
```

**Expected Results:**
- File analyzed with experiment context from README
- Statistical summary provided
- File registry updated in README
- Insights added automatically for significant findings
- Comparison shows patterns across experiments

### Scenario 3: Problem Diagnosis

**Test Commands:**
```
1. "My PCR isn't working - no bands visible"
2. "Why did my Western blot fail?"
3. "Diagnose the issue with exp_002"
```

**Expected Results:**
- LLM reasoning based on context (no hardcoded patterns!)
- Practical suggestions specific to the experiment
- Similar issues found in other experiments
- Diagnosis added as insight to README

### Scenario 4: Cross-Experiment Learning

**Test Commands:**
```
1. "Search for temperature settings across all experiments"
2. "What are the project insights?"
3. "Compare experiments exp_001, exp_002, exp_003"
4. "What patterns lead to success?"
```

**Expected Results:**
- Search results from all README files
- Project-wide patterns identified
- Detailed comparison of methods and results
- Success factors highlighted

## Expected System Behavior

### Memory System
- **README Format**: Simple markdown without YAML
- **Auto-updates**: Files added to registry when analyzed
- **Insights**: Timestamped and attributed to source
- **Change Log**: All updates tracked with timestamps

### React Agent
- **Natural Language**: Understands queries in any language
- **Context Aware**: Knows current folder and selected files
- **Tool Selection**: Automatically chooses appropriate tools
- **Memory Updates**: Writes findings back to README

### Performance
- **Response Time**: 2-3 seconds for simple queries
- **Analysis Time**: 3-5 seconds for data files
- **Search Time**: <2 seconds across all experiments

## File Structure After Testing

```
data/alice_projects/
├── exp_001_pcr_optimization/
│   ├── README.md           # Memory with all updates
│   ├── data_001.csv       # Your data files
│   └── gel_image.jpg      # Your images
├── exp_002_western_blot/
│   └── README.md
└── exp_003_cell_culture/
    └── README.md
```

## Sample README After Testing

```markdown
# Experiment: exp_001_pcr_optimization

**Status:** Active
**Created:** 2025-01-13
**Updated:** 2025-01-13 15:30
**ID:** exp_001_pcr_optimization

## Overview

**Motivation:** Optimize PCR conditions for difficult template
**Key Question:** What annealing temperature gives best yield?
**Hypothesis:** 60-65°C range will be optimal

## Files

| File | Type | Size | Summary | Added |
|------|------|------|---------|-------|
| data_001.csv | Data | 2.3MB | PCR results, 96 samples, mean Ct 22.3 | 2025-01-13 |
| gel_image.jpg | Image | 1.2MB | Agarose gel showing single band at 500bp | 2025-01-13 |

## Results

**Key Findings:**
- Optimal temperature: 62°C
- Yield: 450ng/μL
- Single specific band observed

## Insights

- **2025-01-13 14:30** - [agent] Temperature 62°C shows 15% better efficiency than 60°C
- **2025-01-13 15:00** - [user] DMSO addition helps with GC-rich regions
- **2025-01-13 15:30** - [analysis] Data shows low variance (CV 2.2%), good reproducibility

## Change Log

- **2025-01-13 14:00** - Experiment initialized
- **2025-01-13 14:30** - Added file data_001.csv
- **2025-01-13 15:00** - Updated results section
- **2025-01-13 15:30** - Added insights from analysis
```

## Troubleshooting

### Issue: "No LLM providers configured"
**Solution:** Set the OPENROUTER_API_KEY or SILICONFLOW_API_KEY environment variable

### Issue: Agent not responding
**Solution:** Check that the backend is running on port 8002

### Issue: Memory not updating
**Solution:** Check file permissions in data/alice_projects/

### Issue: Slow responses
**Solution:** GPT-OSS 120B may be slow; you can switch to Qwen-30B in llm_config.json

## Advanced Testing

### Testing Memory Persistence
1. Create an experiment
2. Add data and insights
3. Restart the system
4. Verify README content persists

### Testing Context Propagation
1. Navigate to an experiment folder in frontend
2. Ask "What's in this experiment?"
3. Agent should know current context without being told

### Testing Pattern Learning
1. Create multiple similar experiments
2. Mark some as successful
3. Ask for patterns
4. System should identify success factors

## Success Criteria

✅ **Memory System Works**: READMEs created and updated correctly
✅ **Tools Function**: All tools execute without errors
✅ **Context Flows**: Agent knows experiment context
✅ **Natural Language**: Works without keywords
✅ **Learning Occurs**: Patterns identified across experiments

---

## Quick Test Script

Save this as `test_system.py`:

```python
import asyncio
from src.agents.react_agent import handle_message

async def quick_test():
    """Quick test of core functionality"""
    
    tests = [
        "Scan my experiments",
        "Create experiment for Western blot optimization",
        "What experiments do I have?",
        "Search for temperature across all experiments"
    ]
    
    for test in tests:
        print(f"\n📝 Test: {test}")
        response = await handle_message(test)
        print(f"✅ Response: {response[:200]}...")

if __name__ == "__main__":
    asyncio.run(quick_test())
```

Run with: `uv run python test_system.py`