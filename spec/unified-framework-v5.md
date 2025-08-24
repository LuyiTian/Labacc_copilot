# Unified Memory-Agent Framework v5.1 (SIMPLIFIED)

## Executive Summary

This specification documents the CURRENT simplified memory-agent framework implemented in v3.1. README files store raw text, React agents extract information on demand using LLM, no parsing or patterns.

**Key Implementation**: Raw text storage - NO structured parsing at all. LLM extracts what it needs when asked.

**Status**: ✅ IMPLEMENTED in v3.1  
**Version**: 5.1  
**Last Updated**: 2025-01-23

## 🎯 Core Design Principles (IMPLEMENTED)

1. **README as Memory**: Each experiment folder has a README.md that stores everything as text
2. **No Structure Enforced**: READMEs can be in ANY format - LLM understands naturally
3. **LLM Extraction**: When info needed, LLM extracts it from raw text on demand
4. **Continuous Learning**: Agent reads READMEs, performs actions, updates with insights
5. **Human-Friendly**: Write READMEs however you want - no format requirements

## 📝 README Memory Format (NO REQUIREMENTS)

### Example README Template (NOT ENFORCED - just a suggestion)

```markdown
# Experiment: PCR Optimization for Gene X

**Status:** Active  
**Created:** 2025-01-13  
**Updated:** 2025-01-13 14:30  
**ID:** exp_001_pcr_optimization  

## Overview

**Motivation:** Need to optimize PCR conditions for difficult GC-rich template  
**Key Question:** What annealing temperature gives best specificity and yield?  
**Hypothesis:** Temperature between 60-65°C will be optimal based on primer Tm  

## Files

| File | Type | Size | Summary | Added |
|------|------|------|---------|-------|
| data_001.csv | Data | 2.3MB | PCR results, 96 samples, Ct values 18-35 | 2025-01-13 |
| gel_image.jpg | Image | 1.2MB | Agarose gel showing bands at 500bp and 750bp | 2025-01-13 |
| protocol.pdf | Document | 340KB | Detailed PCR protocol with cycling conditions | 2025-01-12 |

## Parameters

**Independent Variables:**
- Annealing temperature: 50-70°C (2°C steps)
- Template concentration: 10ng, 50ng, 100ng

**Dependent Variables:**
- Amplification efficiency (Ct values)
- Band specificity (gel analysis)
- Product yield (ng/μL)

**Constants:**
- Primer concentration: 0.5μM
- Mg2+ concentration: 2.5mM  
- Polymerase: Q5 High-Fidelity
- Cycles: 35

## Results

**Key Findings:**
- Optimal annealing temperature: 62°C (Ct = 22.3 ± 0.5)
- Yield at optimal conditions: 450ng/μL
- Single specific band observed at 62-66°C range
- Sharp efficiency drop below 58°C

**Statistical Summary:**
- Mean Ct at 62°C: 22.3
- Standard deviation: 0.5
- Coefficient of variation: 2.2%
- ANOVA p-value: <0.001

## Insights

- **2025-01-13 14:30** - Temperature sensitivity window is narrower than expected (58-66°C)
- **2025-01-13 15:00** - DMSO addition (5%) improved amplification of GC-rich regions  
- **2025-01-13 15:30** - This protocol outperforms our standard by 15% efficiency

## Methods

Standard PCR protocol using Q5 High-Fidelity polymerase. Gradient PCR from 50-70°C. 
Initial denaturation: 98°C for 30s. Cycling: 98°C for 10s, variable annealing for 30s, 
72°C for 30s. Final extension: 72°C for 2min. Total 35 cycles.

## Notes

- Wells A1-A3 showed low yield due to pipetting error, excluded from analysis
- Consider testing with longer amplicons (>1kb) in next experiment
- New antibody lot requires validation before use

## Change Log

- **2025-01-13 14:30** - Added statistical analysis after data upload
- **2025-01-13 15:00** - User corrected gel band count from 2 to 3
- **2025-01-13 15:30** - Added comparison with previous experiments
```

### Why This Format Works

✅ **Human-Friendly**: 
- Standard markdown anyone can write
- No indentation errors
- No syntax to break
- Easy to read and edit

✅ **Machine-Parseable**:
- Clear section headers with `##`
- Markdown tables for structured data
- Key: Value pairs with `**bold**` markers
- Bullet points for lists
- Consistent date formats

✅ **Robust Parsing**:
```python
# Simple parsing examples:
# Extract status
status = re.search(r'\*\*Status:\*\*\s*(\w+)', readme).group(1)

# Parse table
lines = readme.split('\n')
for line in lines:
    if '|' in line and '.csv' in line:
        parts = line.split('|')
        file_name = parts[1].strip()
        summary = parts[4].strip()

# Extract key findings
findings = []
for line in lines:
    if line.startswith('- ') and 'Key Findings' in previous_section:
        findings.append(line[2:])
```

## 🤖 React Agent Tools (Simplified)

### Tool Categories

#### 1. Memory Tools
```python
@tool
async def read_memory(
    experiment_id: str,
    section: Optional[str] = None  # "overview", "results", "files", etc.
) -> str:
    """
    Read experiment README with smart markdown parsing.
    Returns requested section or full content.
    """
    
@tool
async def update_memory(
    experiment_id: str,
    updates: Dict[str, str],  # {"section": "content"}
    preserve_rest: bool = True
) -> str:
    """
    Update README sections while preserving the rest.
    Smart merge without breaking markdown.
    """

@tool
async def search_memories(
    query: str,
    scope: str = "all"  # "all", "project", "recent"
) -> str:
    """
    Search across all README files.
    Returns relevant excerpts with context.
    """
```

#### 2. Analysis Tools  
```python
@tool
async def analyze_data(
    file_path: str,
    context_experiment: Optional[str] = None
) -> str:
    """
    Analyze data file with experiment context.
    Always reads README first for background.
    """

@tool
async def diagnose_issue(
    problem: str,
    experiment_id: Optional[str] = None  
) -> str:
    """
    Use LLM reasoning to diagnose problems.
    No patterns - reads context and reasons.
    """

@tool
async def compare_experiments(
    experiment_ids: List[str],
    focus: Optional[str] = None  # "results", "methods", etc.
) -> str:
    """
    Compare multiple experiments.
    Finds patterns across README memories.
    """
```

#### 3. Interaction Tools
```python
@tool
async def chat_correct(
    correction: str,
    context: List[str]  # Recent messages
) -> str:
    """
    Apply user corrections to README.
    Resolves "that", "it" from context.
    """

@tool
async def explain_finding(
    question: str,
    experiment_id: Optional[str] = None
) -> str:
    """
    Explain based on README content.
    Always cites sources from memory.
    """

@tool  
async def suggest_next(
    experiment_id: str
) -> str:
    """
    Suggest next steps based on patterns.
    Learns from successful experiments.
    """
```

## 🔄 Data Flow (Simplified)

### Core Pipeline

```
User Input
    ↓
Intent Detection (LLM-based, no patterns)
    ↓
Load Context from README
    ↓
Execute Tool with Context
    ↓
Update README if needed
    ↓
Return Response
```

### Context Building

```python
class ContextBuilder:
    """Builds rich context from README memories"""
    
    def build_context(self, user_input: str, session: dict) -> dict:
        context = {
            "user_input": user_input,
            "session_id": session.get("id"),
            "current_experiment": None,
            "recent_conversation": [],
            "experiment_memory": None,
            "project_insights": None
        }
        
        # Load current experiment README if exists
        if session.get("current_experiment"):
            readme = read_file(f"{session['current_experiment']}/README.md")
            context["experiment_memory"] = parse_readme(readme)
            
        # Load recent conversation
        context["recent_conversation"] = session.get("messages", [])[-5:]
        
        # Load project insights if needed
        if needs_comparison(user_input):
            context["project_insights"] = load_project_insights()
            
        return context
```

### Memory Updates

```python
class MemoryUpdater:
    """Updates README memories preserving human content"""
    
    def update_section(self, readme: str, section: str, new_content: str) -> str:
        lines = readme.split('\n')
        new_lines = []
        in_section = False
        section_level = 0
        
        for line in lines:
            # Detect section start
            if line.startswith('#') and section.lower() in line.lower():
                in_section = True
                section_level = line.count('#')
                new_lines.append(line)
                continue
                
            # Detect next section (same or higher level)
            if in_section and line.startswith('#'):
                if line.count('#') <= section_level:
                    in_section = False
                    # Insert new content before next section
                    new_lines.extend(new_content.split('\n'))
                    
            if not in_section:
                new_lines.append(line)
                
        return '\n'.join(new_lines)
```

## 💬 Chat-Based Interactions

### Conversational Corrections

```python
# User views results
User: "Show me the PCR results"
System: [Displays Results section from README]

User: "The temperature should be 63°C not 62°C"
System: 
  1. Identifies "temperature" refers to "Optimal annealing temperature: 62°C"
  2. Updates to "Optimal annealing temperature: 63°C"  
  3. Adds to Change Log
  4. Confirms: "Updated optimal temperature to 63°C"

User: "Also add a note that we used a different primer lot"
System:
  1. Adds to Notes section
  2. "Added note about different primer lot"
```

### Natural Language Queries

```python
# No keyword matching needed!
User: "为什么我的PCR失败了?" (Chinese: Why did my PCR fail?)
System: Reads context, uses LLM reasoning, responds appropriately

User: "Pourquoi pas de bandes?" (French: Why no bands?)
System: Understands intent, diagnoses issue, suggests solutions

User: "Compare with last week's experiment"
System: Finds recent experiment, compares READMEs, highlights differences
```

## 🔧 Implementation Plan

### Phase 1: Core Memory System (Week 1)
- [x] Design simple markdown README format
- [ ] Implement markdown parser (no YAML!)
- [ ] Build read_memory and update_memory tools
- [ ] Create context builder
- [ ] Test memory persistence

### Phase 2: Smart Tools (Week 2)  
- [ ] Implement analysis tools with context
- [ ] Build comparison engine
- [ ] Create chat correction system
- [ ] Add LLM reasoning layer
- [ ] Test context propagation

### Phase 3: Integration (Week 3)
- [ ] Connect to React frontend
- [ ] Implement file watcher
- [ ] Add background updates
- [ ] Create validation system
- [ ] End-to-end testing

## 📊 Example Scenarios

### Scenario 1: File Analysis with Context

```python
# User uploads new data
User: "Analyze the new results"

# System flow:
1. Detect new file: "pcr_results_day2.csv"
2. Read experiment README for context
3. See this is day 2 (day 1 exists)
4. Analyze with comparison:
   "Day 2 shows 15% improvement over day 1.
    Ct values dropped from 25.3 to 22.8.
    The temperature adjustment to 62°C worked."
5. Update README with findings
```

### Scenario 2: Pattern Learning

```python
# System background task
1. Read all experiment READMEs
2. Extract Results sections
3. Find patterns:
   - "Experiments with 62°C succeed 85% of time"
   - "DMSO helps in 4/5 GC-rich cases"
4. Update project insights
5. Use for future suggestions
```

### Scenario 3: Smart Diagnosis

```python
User: "My Western blot has high background"

# System (no patterns!):
1. Read current experiment README
2. Check recent Western blot experiments
3. Use LLM to reason:
   "Based on your blocking conditions (3% BSA for 30min)
    and comparing with successful experiment exp_012 
    (5% milk for 1hr), the issue is likely insufficient
    blocking. Also, your antibody dilution (1:500) is 
    higher than typical (1:1000-1:2000)."
```

## 🎯 Why This Works

### Advantages of Simple Markdown

| Aspect | Benefit |
|--------|---------|
| **Human Editing** | Anyone can edit without fear of breaking syntax |
| **Error Recovery** | Malformed sections don't break entire file |
| **Version Control** | Git diffs are clean and readable |
| **Parsing** | Simple regex/string matching vs. YAML parser |
| **Flexibility** | Can add new sections without schema changes |

### Robust Parsing Strategy

```python
def parse_readme_section(readme: str, section: str) -> str:
    """Extract section with fault tolerance"""
    lines = readme.split('\n')
    content = []
    in_section = False
    
    for i, line in enumerate(lines):
        # Multiple ways to detect section
        if any([
            f"## {section}" in line,
            f"# {section}" in line,  
            f"**{section}**" in line,
            section.lower() in line.lower() and line.startswith('#')
        ]):
            in_section = True
            continue
            
        if in_section:
            # Stop at next section
            if line.startswith('#') and i > 0:
                break
            content.append(line)
            
    return '\n'.join(content).strip()
```

## 📋 Key Specifications Summary

### Memory System
- **Format**: Simple markdown (no YAML!)
- **Location**: `{experiment_folder}/README.md`
- **Sections**: Flexible, agent adapts to what's there
- **Updates**: Preserve human edits, append don't replace

### React Agent
- **Tools**: 9 core tools in 3 layers
- **Context**: Always includes README memory
- **Reasoning**: LLM-based, no patterns
- **Language**: Works in any language

### Data Flow
- **Pipeline**: Input → Context → Tool → Memory → Response
- **Context**: Rich, includes conversation history
- **Updates**: Atomic, validated, logged
- **Background**: File watcher for auto-updates

### User Experience  
- **Chat**: Natural corrections and queries
- **Transparency**: Can see and edit README
- **Learning**: System improves from patterns
- **Errors**: Graceful degradation

## 🚀 Next Steps

1. **Implement markdown parser** (simple, robust)
2. **Build memory tools** (read, write, search)
3. **Create context system** (rich context from README)
4. **Test with real data** (actual experiment files)
5. **Connect to frontend** (chat + file manager)

---

**Philosophy**: "Simple formats enable robust systems"  
**Reminder**: No YAML, no complex schemas - just markdown that works!