# Unified Memory-Agent Framework Specification v4.0

## Executive Summary

This specification defines a **unified framework** where the README Memory System and React Agent work as an integrated whole. README files serve as persistent memory, the React Agent provides intelligence, and a context management layer connects them seamlessly.

**Core Architecture**: Memory (README) ↔ Context Layer ↔ Intelligence (Agent) ↔ User

**Status**: Unified Specification  
**Version**: 4.0  
**Last Updated**: 2025-01-13  
**Author**: LabAcc Development Team

## 🏗️ Unified Architecture

### System Components Integration

```
┌──────────────────────────────────────────────────────────────────┐
│                         User Interface                            │
│                    (Chat + File Manager + API)                    │
└────────────────────────────┬─────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│                      React Agent System                           │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │                    Intent Router                          │    │
│  │              (Classifies user intent)                     │    │
│  └────────────────────────┬─────────────────────────────────┘    │
│  ┌────────────────────────▼─────────────────────────────────┐    │
│  │                  Context Builder                          │    │
│  │         (Reads from README Memory System)                 │    │
│  └────────────────────────┬─────────────────────────────────┘    │
│  ┌────────────────────────▼─────────────────────────────────┐    │
│  │                    Tool Layers                            │    │
│  │  ┌────────────────────────────────────────────────────┐  │    │
│  │  │ Memory Tools: read_memory, write_memory, search    │  │    │
│  │  ├────────────────────────────────────────────────────┤  │    │
│  │  │ Analysis Tools: analyze, diagnose, compare         │  │    │
│  │  ├────────────────────────────────────────────────────┤  │    │
│  │  │ Interaction Tools: chat_update, explain, suggest   │  │    │
│  │  ├────────────────────────────────────────────────────┤  │    │
│  │  │ Maintenance Tools: validate, cleanup, archive      │  │    │
│  │  └────────────────────────────────────────────────────┘  │    │
│  └────────────────────────┬─────────────────────────────────┘    │
│  ┌────────────────────────▼─────────────────────────────────┐    │
│  │                  Memory Updater                           │    │
│  │           (Writes back to README Memory)                  │    │
│  └───────────────────────────────────────────────────────────┘    │
└───────────────────────────┬──────────────────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────────────┐
│                     README Memory System                          │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  Experiment READMEs: Persistent memory per experiment     │    │
│  ├──────────────────────────────────────────────────────────┤    │
│  │  Project README: Cross-experiment insights & patterns     │    │
│  ├──────────────────────────────────────────────────────────┤    │
│  │  Structured Blocks: YAML/JSON for machine parsing         │    │
│  └──────────────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────────────┘
```

## 📝 README Memory Structure (Co-designed for Agent)

### Hybrid Human-Machine Format

```markdown
# Experiment: [Name]
<!-- YAML Block for Machine Parsing -->
```yaml
experiment_meta:
  id: exp_001_pcr_optimization
  status: active  # active, completed, failed, on_hold
  created: 2025-01-13T10:00:00Z
  updated: 2025-01-13T14:30:00Z
  tags: [pcr, optimization, temperature_gradient]
  success_score: 0.85  # 0-1 scale for agent learning
```

## 📋 Overview
*Human-readable section with embedded structure*

### Motivation
Understanding the optimal annealing temperature for our primers...

### Key Question
What annealing temperature yields maximum specificity and efficiency?

---

## 📁 File Registry
<!-- YAML Block for Agent File Tracking -->
```yaml
files:
  - path: data_001.csv
    type: data
    size: 2.3MB
    added: 2025-01-13T10:15:00Z
    checksum: md5:abc123...
    summary: "PCR results, 96 samples, Ct values 18-35"
    analysis_status: completed
    key_findings:
      - "Optimal Ct at 62°C: 22.3"
      - "Sharp efficiency drop below 58°C"
    confidence: 0.92
    
  - path: gel_image.jpg
    type: image
    size: 1.2MB
    added: 2025-01-13T11:00:00Z
    summary: "Agarose gel, bands at 500bp and 750bp"
    analysis_status: completed
    observations:
      - "Single band at 62-66°C"
      - "Primer dimers at 68°C"
```

---

## 🧪 Parameters
<!-- Structured for Agent Analysis -->
```yaml
experimental_parameters:
  independent:
    annealing_temperature:
      range: [50, 70]
      step: 2
      unit: "°C"
      optimal_found: 62
      
  dependent:
    amplification_efficiency:
      measurement: "Ct value"
      optimal_value: 22.3
      std_dev: 0.5
      
  constants:
    primer_concentration: 0.5  # μM
    mg_concentration: 2.5      # mM
    polymerase: "Q5 High-Fidelity"
    cycles: 35
```

---

## 📊 Results Data
<!-- Machine-Readable Results -->
```yaml
results:
  quantitative:
    mean_ct_optimal: 22.3
    std_dev: 0.5
    cv_percent: 2.2
    p_value: 0.001
    effect_size: 0.78
    
  qualitative:
    gel_quality: "excellent"
    specificity: "high"
    reproducibility: "confirmed"
    
  comparison:
    vs_previous:
      exp_002: "+15% efficiency"
      exp_005: "similar optimal temp"
    improvement_score: 0.85
```

*Human-readable summary*:
The optimization was successful with clear identification of 62°C as optimal...

---

## 💡 Insights Bank
<!-- Agent Learning Storage -->
```yaml
insights:
  - timestamp: 2025-01-13T14:30:00Z
    source: agent_analysis
    insight: "Temperature sensitivity window is 58-66°C"
    confidence: 0.95
    based_on: ["data_001.csv", "gel_image.jpg"]
    
  - timestamp: 2025-01-13T15:00:00Z
    source: user_correction
    insight: "DMSO addition helps with GC-rich regions"
    confidence: 1.0
    validated: true
    
  - timestamp: 2025-01-13T15:30:00Z
    source: cross_experiment_analysis
    insight: "Q5 polymerase consistently outperforms Taq"
    confidence: 0.88
    experiments_compared: ["exp_001", "exp_005", "exp_012"]
```

---

## 🔄 Change Log
<!-- Detailed History for Agent Learning -->
```yaml
changes:
  - timestamp: 2025-01-13T14:30:00Z
    actor: agent
    action: file_analyzed
    target: "data_001.csv"
    changes_made:
      - "Added statistical summary to results"
      - "Updated optimal temperature to 62°C"
      - "Generated efficiency comparison"
      
  - timestamp: 2025-01-13T15:00:00Z
    actor: user
    action: correction
    target: "results/gel_interpretation"
    changes_made:
      - "Corrected band count from 2 to 3"
      - "Added note about faint 300bp band"
    reason: "User spotted additional band"
```
```

## 🤖 React Agent Tool System

### Tool Organization (4 Layers)

#### Layer 1: Memory Tools
```python
@tool
async def read_memory(
    target: str,  # "experiment:exp_001", "project", "insights"
    section: Optional[str] = None,  # Specific section to read
    format: str = "full"  # "full", "summary", "structured"
) -> MemoryContent:
    """
    Read from README memory system with smart parsing.
    Extracts both human text and structured YAML blocks.
    """
    # Implementation:
    # 1. Locate target README
    # 2. Parse markdown + YAML blocks
    # 3. Extract requested section
    # 4. Return structured content
    
@tool  
async def write_memory(
    target: str,
    section: str,
    content: Union[str, dict],
    preserve_human_text: bool = True
) -> WriteResult:
    """
    Write to README memory while preserving structure.
    Updates YAML blocks without breaking markdown.
    """
    # Implementation:
    # 1. Read current README
    # 2. Parse structure
    # 3. Update specific section
    # 4. Preserve human edits
    # 5. Write back with validation
    
@tool
async def search_memory(
    query: str,
    scope: str = "all",  # "project", "experiment:id", "all"
    return_context: bool = True
) -> SearchResults:
    """
    Search across README memories with context.
    Returns relevant sections with surrounding context.
    """
    # Implementation:
    # 1. Build search index from READMEs
    # 2. Find matches
    # 3. Extract context windows
    # 4. Rank by relevance
```

#### Layer 2: Analysis Tools
```python
@tool
async def analyze_with_memory(
    file_path: str,
    load_context: bool = True,
    compare_previous: bool = True
) -> AnalysisResult:
    """
    Analyze files with full memory context.
    Always reads experiment README first for context.
    """
    # Implementation:
    # 1. Determine experiment from file path
    # 2. Read experiment memory (README)
    # 3. Read project insights
    # 4. Analyze file in context
    # 5. Compare with previous results
    # 6. Write findings back to memory
    
@tool
async def diagnose_with_context(
    issue_description: str,
    experiment_id: Optional[str] = None
) -> DiagnosisResult:
    """
    Diagnose issues using memory and LLM reasoning.
    No patterns - pure contextual understanding.
    """
    # Implementation:
    # 1. Read experiment memory
    # 2. Read similar experiments
    # 3. Extract failure patterns from memory
    # 4. Use LLM to reason about issue
    # 5. Update insights in memory
    
@tool
async def compare_experiments(
    experiment_ids: List[str],
    aspects: List[str] = ["methods", "results"]
) -> ComparisonResult:
    """
    Compare experiments using their README memories.
    Identifies patterns and updates project insights.
    """
    # Implementation:
    # 1. Read all experiment memories
    # 2. Extract comparable sections
    # 3. Use LLM for pattern recognition
    # 4. Update project-level insights
    # 5. Write comparison to project README
```

#### Layer 3: Interaction Tools
```python
@tool
async def chat_update_memory(
    user_message: str,
    conversation_context: List[Message],
    current_view: MemoryContent
) -> UpdateResult:
    """
    Handle conversational updates to memory.
    Resolves references from conversation context.
    """
    # Implementation:
    # 1. Parse user intent from message
    # 2. Resolve "that", "it" from context
    # 3. Identify target section in README
    # 4. Apply update with validation
    # 5. Show diff to user
    
@tool
async def explain_from_memory(
    query: str,
    experiment_id: Optional[str] = None
) -> Explanation:
    """
    Explain findings using memory as source.
    Provides traceable, grounded responses.
    """
    # Implementation:
    # 1. Search relevant memories
    # 2. Extract supporting evidence
    # 3. Generate explanation with citations
    # 4. Include confidence scores
    
@tool
async def suggest_next_step(
    experiment_id: str,
    goal: Optional[str] = None
) -> Suggestions:
    """
    Suggest next steps based on memory patterns.
    Learns from successful experiments.
    """
    # Implementation:
    # 1. Read current experiment state
    # 2. Find similar successful experiments
    # 3. Extract success patterns
    # 4. Generate recommendations
    # 5. Update suggestions in memory
```

#### Layer 4: Maintenance Tools
```python
@tool
async def validate_memory(
    target: str = "all",
    fix_issues: bool = False
) -> ValidationResult:
    """
    Validate README structure and consistency.
    Ensures memory integrity.
    """
    # Implementation:
    # 1. Check YAML block syntax
    # 2. Verify file references exist
    # 3. Check data consistency
    # 4. Fix issues if requested
    # 5. Report validation results
    
@tool
async def sync_memory_with_files(
    experiment_id: str,
    auto_update: bool = True
) -> SyncResult:
    """
    Sync README with actual files.
    Detects additions, deletions, changes.
    """
    # Implementation:
    # 1. List actual files
    # 2. Compare with README registry
    # 3. Analyze new files
    # 4. Remove deleted entries
    # 5. Update README if auto_update
    
@tool
async def archive_memory(
    experiment_id: str,
    reason: str
) -> ArchiveResult:
    """
    Archive completed experiments.
    Preserves memory for future reference.
    """
    # Implementation:
    # 1. Mark experiment as archived
    # 2. Extract key learnings
    # 3. Update project insights
    # 4. Move to archive folder
    # 5. Maintain reference link
```

## 🔄 Data Flow Pipeline

### Complete Flow: User Query → Memory → Agent → Memory → Response

```python
class UnifiedPipeline:
    """Main pipeline connecting memory and agent"""
    
    async def process_user_input(self, user_input: str, session: Session):
        # Step 1: Intent Classification
        intent = self.classify_intent(user_input)
        
        # Step 2: Load Memory Context
        memory_context = await self.load_relevant_memory(intent, session)
        
        # Step 3: Build Tool Context
        tool_context = ToolContext(
            session=session,
            memory=memory_context,
            intent=intent
        )
        
        # Step 4: Route to Tool
        tool_result = await self.execute_tool(intent, tool_context)
        
        # Step 5: Update Memory
        memory_update = await self.update_memory(tool_result, memory_context)
        
        # Step 6: Generate Response
        response = self.format_response(tool_result, memory_update)
        
        return response
    
    async def load_relevant_memory(self, intent: Intent, session: Session):
        """Load relevant README sections based on intent"""
        
        memory_sections = []
        
        # Always load current experiment if in context
        if session.current_experiment:
            exp_memory = await read_memory(
                target=f"experiment:{session.current_experiment}",
                format="structured"
            )
            memory_sections.append(exp_memory)
        
        # Load project insights for comparison
        if intent.requires_comparison:
            project_memory = await read_memory(
                target="project",
                section="insights",
                format="structured"
            )
            memory_sections.append(project_memory)
        
        # Load related experiments if needed
        if intent.requires_history:
            related = await search_memory(
                query=intent.topic,
                scope="all",
                return_context=True
            )
            memory_sections.extend(related)
        
        return MemoryContext(sections=memory_sections)
```

## 🎯 Context Management Strategy

### Context Building with Memory

```python
class MemoryAwareContextBuilder:
    """Builds context from README memory system"""
    
    async def build_context(
        self,
        user_input: str,
        session: Session
    ) -> EnrichedContext:
        
        # Level 1: Session Context
        session_ctx = self.get_session_context(session)
        
        # Level 2: Memory Context (from READMEs)
        memory_ctx = await self.get_memory_context(session)
        
        # Level 3: File Context
        file_ctx = await self.get_file_context(session.current_files)
        
        # Level 4: Historical Context
        history_ctx = await self.get_historical_context(
            memory_ctx.experiment_id
        )
        
        # Level 5: Project Context
        project_ctx = await self.get_project_context()
        
        # Combine all contexts
        return EnrichedContext(
            user_input=user_input,
            session=session_ctx,
            memory=memory_ctx,
            files=file_ctx,
            history=history_ctx,
            project=project_ctx,
            timestamp=datetime.now()
        )
    
    async def get_memory_context(self, session: Session):
        """Extract context from README memory"""
        
        if not session.current_experiment:
            return None
            
        # Read full experiment memory
        exp_memory = await read_memory(
            target=f"experiment:{session.current_experiment}",
            format="full"
        )
        
        # Parse structured sections
        return MemoryContext(
            experiment_id=exp_memory.meta.id,
            status=exp_memory.meta.status,
            parameters=exp_memory.parameters,
            results=exp_memory.results,
            insights=exp_memory.insights,
            files=exp_memory.files,
            recent_changes=exp_memory.changes[-10:]  # Last 10 changes
        )
```

## 💬 Chat-Memory Integration

### Conversational Memory Updates

```python
class ChatMemoryInterface:
    """Handles chat-based memory interactions"""
    
    async def handle_user_correction(
        self,
        correction: str,
        conversation: List[Message]
    ):
        # Step 1: Identify what to correct
        target = self.identify_correction_target(correction, conversation)
        
        # Step 2: Read current memory
        current = await read_memory(
            target=target.location,
            section=target.section
        )
        
        # Step 3: Apply correction
        updated = self.apply_correction(current, correction, target)
        
        # Step 4: Write back with audit trail
        result = await write_memory(
            target=target.location,
            section=target.section,
            content=updated,
            preserve_human_text=True
        )
        
        # Step 5: Add to change log
        await self.log_change(
            actor="user",
            action="correction",
            target=target,
            changes=correction,
            timestamp=datetime.now()
        )
        
        return f"Updated {target.section}: {correction}"
    
    async def show_memory_section(
        self,
        request: str,
        experiment_id: str
    ):
        """Show specific README section in chat"""
        
        # Parse request to identify section
        section = self.parse_section_request(request)
        
        # Read from memory
        content = await read_memory(
            target=f"experiment:{experiment_id}",
            section=section,
            format="full"
        )
        
        # Format for chat display
        return self.format_for_chat(content)
```

## 🔄 Background Memory Sync

### File Watcher Integration

```python
class MemoryFileWatcher:
    """Monitors files and updates README memory"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.watcher = FileSystemWatcher()
        self.queue = AsyncQueue()
        
    async def on_file_event(self, event: FileEvent):
        """Handle file system events"""
        
        if event.type == "created":
            await self.handle_new_file(event.path)
        elif event.type == "modified":
            await self.handle_file_change(event.path)
        elif event.type == "deleted":
            await self.handle_file_deletion(event.path)
    
    async def handle_new_file(self, file_path: str):
        """Process new file and update memory"""
        
        # Step 1: Determine experiment
        exp_id = self.get_experiment_id(file_path)
        
        # Step 2: Read current memory
        memory = await read_memory(f"experiment:{exp_id}")
        
        # Step 3: Analyze file with context
        analysis = await analyze_with_memory(
            file_path=file_path,
            load_context=True
        )
        
        # Step 4: Update file registry
        file_entry = {
            "path": file_path,
            "type": self.detect_type(file_path),
            "added": datetime.now(),
            "summary": analysis.summary,
            "key_findings": analysis.findings
        }
        
        # Step 5: Write to memory
        await write_memory(
            target=f"experiment:{exp_id}",
            section="files",
            content={"action": "append", "entry": file_entry}
        )
        
        # Step 6: Update insights if significant
        if analysis.significance > 0.7:
            await write_memory(
                target=f"experiment:{exp_id}",
                section="insights",
                content={
                    "action": "append",
                    "insight": analysis.main_insight
                }
            )
```

## 📊 Memory-Driven Analytics

### Cross-Experiment Learning

```python
class MemoryAnalytics:
    """Analyzes patterns across README memories"""
    
    async def learn_success_patterns(self):
        """Extract success patterns from all experiments"""
        
        # Step 1: Read all experiment memories
        all_experiments = await self.read_all_experiment_memories()
        
        # Step 2: Filter successful ones
        successful = [
            exp for exp in all_experiments 
            if exp.meta.success_score > 0.8
        ]
        
        # Step 3: Extract common patterns
        patterns = {
            "parameters": self.extract_parameter_patterns(successful),
            "methods": self.extract_method_patterns(successful),
            "conditions": self.extract_condition_patterns(successful)
        }
        
        # Step 4: Write to project memory
        await write_memory(
            target="project",
            section="success_patterns",
            content=patterns
        )
        
        return patterns
    
    async def suggest_optimizations(self, experiment_id: str):
        """Suggest optimizations based on memory patterns"""
        
        # Read current experiment
        current = await read_memory(f"experiment:{experiment_id}")
        
        # Read success patterns
        patterns = await read_memory("project", section="success_patterns")
        
        # Compare and suggest
        suggestions = []
        for param, optimal_value in patterns.parameters.items():
            if param in current.parameters:
                current_value = current.parameters[param]
                if abs(current_value - optimal_value) > threshold:
                    suggestions.append({
                        "parameter": param,
                        "current": current_value,
                        "suggested": optimal_value,
                        "reason": f"Based on {len(patterns.experiments)} successful experiments"
                    })
        
        return suggestions
```

## 🛡️ Memory Integrity & Recovery

### Validation and Recovery

```python
class MemoryIntegrity:
    """Ensures README memory consistency"""
    
    async def validate_memory_structure(self, experiment_id: str):
        """Validate README structure and content"""
        
        validations = {
            "structure": self.check_structure(),
            "yaml_syntax": self.check_yaml_blocks(),
            "file_references": self.check_file_refs(),
            "data_consistency": self.check_consistency(),
            "completeness": self.check_completeness()
        }
        
        issues = [v for v in validations.values() if not v.valid]
        
        if issues and auto_fix:
            await self.fix_issues(issues)
        
        return ValidationReport(validations, issues)
    
    async def recover_from_corruption(self, experiment_id: str):
        """Recover README from files and history"""
        
        # Step 1: Check git history
        git_versions = await self.get_git_history(f"{experiment_id}/README.md")
        
        if git_versions:
            # Restore from last known good
            await self.restore_from_git(git_versions[-1])
        else:
            # Rebuild from scratch
            await self.rebuild_memory(experiment_id)
    
    async def rebuild_memory(self, experiment_id: str):
        """Rebuild README from files"""
        
        # Create base structure
        readme = self.create_template()
        
        # Scan files
        files = self.scan_experiment_files(experiment_id)
        
        # Analyze each file
        for file in files:
            analysis = await analyze_with_memory(file, load_context=False)
            readme.add_file(file, analysis)
        
        # Write new README
        await write_memory(
            target=f"experiment:{experiment_id}",
            section="all",
            content=readme
        )
```

## 🎯 Implementation Roadmap

### Phase 1: Foundation (Week 1)
- [ ] Implement README template with YAML blocks
- [ ] Build memory read/write tools
- [ ] Create basic context builder
- [ ] Implement chat_update_memory tool
- [ ] Test memory persistence

### Phase 2: Intelligence (Week 2)
- [ ] Implement analysis tools with memory
- [ ] Build comparison engine
- [ ] Create suggestion system
- [ ] Add LLM reasoning layer
- [ ] Test context propagation

### Phase 3: Automation (Week 3)
- [ ] Implement file watcher
- [ ] Build background sync
- [ ] Create validation system
- [ ] Add recovery mechanisms
- [ ] Test end-to-end flow

### Phase 4: Optimization (Week 4)
- [ ] Performance tuning
- [ ] Memory caching
- [ ] Batch operations
- [ ] Error handling
- [ ] Production readiness

## 📈 Success Metrics

### Memory Quality
- Structure validity: 100%
- Update success rate: >99%
- Sync accuracy: >95%
- Recovery capability: 100%

### Agent Performance
- Context load time: <500ms
- Tool execution: <2s
- Memory update: <1s
- End-to-end: <3s

### User Experience
- Correction accuracy: >95%
- Suggestion relevance: >80%
- Natural conversation: >90% satisfaction
- Memory transparency: 100%

## 🔑 Key Design Decisions

### Why This Architecture?

1. **README as Memory**: Version controlled, human-readable, portable
2. **YAML Blocks**: Machine-parseable while maintaining readability
3. **Layered Tools**: Clear separation of concerns
4. **Context Pipeline**: Rich context for intelligent decisions
5. **Bidirectional Flow**: Agent reads and writes memory continuously

### Trade-offs

| Choice | Benefit | Cost |
|--------|---------|------|
| README files | Transparency | Parsing overhead |
| YAML blocks | Structure | Syntax complexity |
| Full context | Intelligence | Memory usage |
| Git integration | Version control | Disk operations |
| Background sync | Real-time updates | CPU usage |

## 📚 Example Scenarios

### Scenario 1: Complete Analysis Flow

```python
# User uploads new data file
User: "Analyze the PCR results I just uploaded"

# System flow:
1. File detected: "pcr_results_day4.csv"
2. Read memory: Load exp_001 README
3. Build context: Previous 3 days of results
4. Analyze: Compare with trends
5. Update memory: Add file entry, results, insights
6. Response: "Day 4 shows continued improvement..."

# Memory updated with:
- File registry entry
- Statistical results
- Trend analysis
- New insights
- Change log entry
```

### Scenario 2: Conversational Correction

```python
# User reviews results
User: "Show me the Western blot analysis"
System: [Displays README section]

User: "The molecular weight should be 55kDa, not 50kDa"

# System flow:
1. Identify target: results.western_blot.molecular_weight
2. Read current: 50kDa
3. Update to: 55kDa
4. Log change: User correction with timestamp
5. Confirm: "Updated molecular weight to 55kDa"
```

### Scenario 3: Pattern Learning

```python
# System background task
Every 24 hours:
1. Read all experiment memories
2. Extract success metrics
3. Identify patterns
4. Update project insights
5. Generate recommendations

# Result in project README:
"Pattern detected: Experiments with 62°C annealing 
 succeed 85% of the time across 12 experiments"
```

## 🏁 Conclusion

This unified framework creates a seamless integration between:
- **Persistent Memory** (README files with structure)
- **Intelligence** (React Agent with LLM reasoning)
- **Context** (Rich pipeline connecting them)
- **Interaction** (Natural chat with memory updates)
- **Learning** (Continuous improvement from patterns)

The system is designed to be:
- **Transparent**: All memory is readable
- **Intelligent**: Full context enables smart decisions
- **Reliable**: Git-backed with recovery
- **Scalable**: Handles thousands of experiments
- **Natural**: Conversational interaction

---

**Version**: 4.0 - Unified Memory-Agent Framework  
**Philosophy**: "Memory grounds intelligence, intelligence enriches memory"  
**Next Step**: Begin implementation with memory tools layer