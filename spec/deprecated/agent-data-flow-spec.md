# Agent Data Flow & Context Management Specification v3.0

## Executive Summary

This specification defines the **data flow, context management, and routing logic** for the LabAcc Copilot React Agent. It emphasizes proper context propagation, structured inputs/outputs, and seamless chat-based interactions with README memory system.

**Core Principle**: Every tool receives rich context, not raw data. Context flows through the system maintaining coherence.

**Status**: Specification Complete  
**Version**: 3.0  
**Last Updated**: 2025-01-13  
**Author**: LabAcc Development Team

## 🔄 Data Flow Architecture

### System Overview
```
┌─────────────────────────────────────────────────────────────┐
│                     Context Manager                          │
│  (Maintains: Project Context, Session State, User Intent)   │
└─────────────────┬───────────────────────────┬───────────────┘
                  │                           │
        ┌─────────▼─────────┐       ┌────────▼────────┐
        │   Chat Interface   │       │  File Watcher   │
        │  (User Commands)   │       │  (Auto Updates) │
        └─────────┬─────────┘       └────────┬────────┘
                  │                           │
        ┌─────────▼───────────────────────────▼─────────┐
        │            Intent Router & Enricher            │
        │    (Routes to tools with enriched context)     │
        └─────────┬───────────────────────────┬─────────┘
                  │                           │
        ┌─────────▼─────────┐       ┌────────▼────────┐
        │   Tool Execution   │       │  README Memory  │
        │  (With Full Context)│◄─────►│   (Read/Write)  │
        └─────────┬─────────┘       └─────────────────┘
                  │
        ┌─────────▼─────────┐
        │  Response Builder  │
        │ (Formats & Returns)│
        └───────────────────┘
```

## 📊 Context Management System

### Context Hierarchy
```python
@dataclass
class ProjectContext:
    """Top-level project context"""
    project_root: str = "data/alice_projects"
    project_readme: str  # Project-level README content
    global_insights: Dict[str, str]  # Cross-experiment learnings
    experiment_history: List[str]  # List of all experiments
    active_experiments: List[str]  # Currently active ones
    success_patterns: Dict[str, Any]  # What works
    failure_patterns: Dict[str, Any]  # What doesn't
    
@dataclass
class ExperimentContext:
    """Individual experiment context"""
    experiment_id: str  # exp_001_pcr_optimization
    readme_content: str  # Current README.md
    files_metadata: Dict[str, FileInfo]  # All files with metadata
    recent_changes: List[ChangeEvent]  # Recent file changes
    parent_project: ProjectContext  # Link to project
    related_experiments: List[str]  # Similar experiments
    
@dataclass
class SessionContext:
    """User session context"""
    session_id: str
    user_intent: str  # What user is trying to achieve
    conversation_history: List[Message]
    current_experiment: Optional[str]
    current_files: List[str]  # Files user is working with
    preferences: Dict[str, Any]  # User preferences
    
@dataclass
class ToolContext:
    """Context passed to every tool"""
    session: SessionContext
    experiment: Optional[ExperimentContext]
    project: ProjectContext
    trigger: str  # "user_command", "file_change", "scheduled"
    enrichments: Dict[str, Any]  # Additional context
```

## 🛠️ Tool Input/Output Specifications

### 1. read_project
**Purpose**: Read and summarize project or experiment from README

```python
@dataclass
class ReadProjectInput:
    target: str  # "project" or experiment ID like "exp_001"
    focus: Optional[str]  # "results", "methods", "overview", None for all
    depth: str = "summary"  # "summary", "detailed", "full"
    context: ToolContext  # Always included
    
@dataclass
class ReadProjectOutput:
    summary: str  # Human-readable summary
    structured_data: Dict[str, Any]  # Parsed sections
    key_insights: List[str]  # Bullet points
    files_mentioned: List[str]  # Files referenced in README
    confidence: float  # How complete the README is
    suggestions: List[str]  # What's missing
    
# Example usage in chat:
User: "Show me the PCR optimization project"
System: 
  1. Identifies target="exp_001_pcr_optimization"
  2. Reads README with project context
  3. Returns formatted summary with key results
```

### 2. update_readme
**Purpose**: Update README based on changes or user corrections

```python
@dataclass
class UpdateReadmeInput:
    experiment_id: str  # Which experiment to update
    update_type: str  # "file_added", "result_update", "correction", "insight"
    update_data: Dict[str, Any]  # The actual update
    context: ToolContext  # Full context including conversation
    preserve_sections: List[str] = ["Overview", "Methods"]  # Don't touch these
    
@dataclass 
class UpdateReadmeOutput:
    success: bool
    updated_sections: List[str]  # Which sections changed
    diff: str  # Git-style diff of changes
    new_insights: List[str]  # Any new insights generated
    change_summary: str  # Human-readable summary
    
# Example usage in chat:
User: "The gel image actually shows 3 bands, not 2. Please update."
System:
  1. Extracts correction from conversation context
  2. Identifies which file/result to update
  3. Updates README with correction + timestamp
  4. Returns confirmation with diff
```

### 3. analyze_with_context
**Purpose**: Analyze new data with full experimental context

```python
@dataclass
class AnalyzeWithContextInput:
    file_path: str  # File to analyze
    file_type: str  # "csv", "image", "document"
    experiment_context: ExperimentContext  # Full experiment history
    project_context: ProjectContext  # Related experiments
    analysis_prompt: Optional[str]  # Specific analysis request
    
@dataclass
class AnalyzeWithContextOutput:
    file_summary: str  # What this file contains
    key_findings: List[str]  # Important observations
    statistical_summary: Optional[Dict]  # For data files
    comparison_with_previous: Optional[str]  # How it compares
    readme_update: str  # Suggested README update
    confidence: float
    
# Context enrichment example:
When analyzing "pcr_results_day3.csv":
  1. System reads experiment README for context
  2. Finds this is 3rd attempt at optimization
  3. Compares with day1 and day2 results
  4. Generates insight: "15% improvement from day1"
  5. Suggests README update with trend analysis
```

### 4. compare_experiments
**Purpose**: Cross-experiment analysis with pattern recognition

```python
@dataclass
class CompareExperimentsInput:
    experiment_ids: List[str]  # Experiments to compare
    comparison_aspect: str  # "methods", "results", "all"
    project_context: ProjectContext  # Full project knowledge
    generate_recommendations: bool = True
    
@dataclass
class CompareExperimentsOutput:
    comparison_table: Dict[str, Dict]  # Structured comparison
    common_patterns: List[str]  # What's consistent
    key_differences: List[str]  # What varies
    success_factors: List[str]  # What correlates with success
    recommendations: List[str]  # For future experiments
    meta_insights: str  # High-level learning
    
# Rich context example:
Comparing 5 PCR experiments:
  1. System reads all 5 README files
  2. Extracts methods, results, issues from each
  3. Identifies: "DMSO addition helps in 4/5 cases"
  4. Recommends: "Standard protocol should include DMSO"
  5. Updates project-level insights
```

### 5. chat_update
**Purpose**: Handle conversational updates to experiments

```python
@dataclass
class ChatUpdateInput:
    user_message: str  # Natural language update
    conversation_context: List[Message]  # Full conversation
    current_view: str  # What user is looking at
    experiment_context: Optional[ExperimentContext]
    intent_classification: str  # "correction", "addition", "question"
    
@dataclass
class ChatUpdateOutput:
    action_taken: str  # What was done
    updated_content: Optional[str]  # New content if any
    confirmation_message: str  # Response to user
    follow_up_questions: List[str]  # Clarifications needed
    
# Conversational update examples:
User: "Actually, the optimal temperature was 63°C, not 62°C"
System: Updates README Results section, confirms change

User: "This gel shows contamination in lane 3"
System: Adds note to gel image entry, updates troubleshooting log

User: "Compare this with last week's results"
System: Retrieves context, performs comparison, updates insights
```

## 🧭 Routing Logic

### Intent Classification & Routing

```python
class IntentRouter:
    """Routes user intents to appropriate tools with context"""
    
    def route(self, user_input: str, session: SessionContext) -> ToolCall:
        # Step 1: Classify intent
        intent = self.classify_intent(user_input)
        
        # Step 2: Identify scope
        scope = self.identify_scope(user_input, session)
        
        # Step 3: Gather relevant context
        context = self.build_context(intent, scope, session)
        
        # Step 4: Route to appropriate tool
        tool_mapping = {
            "read": read_project,
            "update": update_readme,
            "analyze": analyze_with_context,
            "compare": compare_experiments,
            "correct": chat_update,
            "question": ask_with_context
        }
        
        return ToolCall(
            tool=tool_mapping[intent],
            inputs=self.prepare_inputs(intent, context),
            context=context
        )
    
    def classify_intent(self, user_input: str) -> str:
        """Use LLM to classify user intent"""
        prompt = f"""
        Classify this user input into one of these intents:
        - read: User wants to see/understand something
        - update: User wants to change/add something
        - analyze: User wants analysis of data
        - compare: User wants comparison
        - correct: User is correcting information
        - question: User is asking a question
        
        User input: {user_input}
        
        Return only the intent keyword.
        """
        return llm.generate(prompt)
```

### Context Building Pipeline

```python
class ContextBuilder:
    """Builds rich context for tool execution"""
    
    def build_context(
        self, 
        intent: str, 
        scope: str,
        session: SessionContext
    ) -> ToolContext:
        
        # Step 1: Load project context (always needed)
        project_context = self.load_project_context()
        
        # Step 2: Load experiment context if relevant
        experiment_context = None
        if scope != "project":
            experiment_context = self.load_experiment_context(scope)
            
        # Step 3: Enrich with related information
        enrichments = self.gather_enrichments(
            intent, 
            experiment_context,
            project_context
        )
        
        # Step 4: Add conversation context
        enrichments["recent_conversation"] = session.conversation_history[-5:]
        
        return ToolContext(
            session=session,
            experiment=experiment_context,
            project=project_context,
            trigger="user_command",
            enrichments=enrichments
        )
    
    def gather_enrichments(self, intent, exp_ctx, proj_ctx):
        """Gather additional context based on intent"""
        enrichments = {}
        
        if intent == "analyze":
            # Add previous analyses for comparison
            enrichments["previous_analyses"] = self.get_previous_analyses(exp_ctx)
            enrichments["expected_results"] = self.get_expected_results(exp_ctx)
            
        elif intent == "compare":
            # Add success metrics from project
            enrichments["success_criteria"] = proj_ctx.success_patterns
            enrichments["known_issues"] = proj_ctx.failure_patterns
            
        elif intent == "correct":
            # Add original content for comparison
            enrichments["original_content"] = self.get_original_content(exp_ctx)
            
        return enrichments
```

## 📝 Chat-Based README Interaction

### Interactive README Updates

```python
class ChatReadmeManager:
    """Handles conversational README interactions"""
    
    async def handle_correction(
        self,
        user_message: str,
        conversation: List[Message]
    ) -> str:
        # Step 1: Identify what needs correction
        correction_target = await self.identify_correction_target(
            user_message,
            conversation
        )
        
        # Step 2: Extract the correction
        correction_content = await self.extract_correction(
            user_message,
            correction_target
        )
        
        # Step 3: Update README with context
        update_result = await update_readme(
            UpdateReadmeInput(
                experiment_id=correction_target.experiment,
                update_type="correction",
                update_data={
                    "section": correction_target.section,
                    "old_value": correction_target.old_value,
                    "new_value": correction_content,
                    "reason": f"User correction: {user_message}",
                    "timestamp": datetime.now()
                },
                context=self.current_context
            )
        )
        
        # Step 4: Confirm with user
        return f"""
        ✅ Updated {correction_target.section} in {correction_target.experiment}:
        
        Changed: "{correction_target.old_value}"
        To: "{correction_content}"
        
        {update_result.diff}
        """
    
    async def handle_insight_addition(
        self,
        user_insight: str,
        experiment_id: str
    ) -> str:
        # Add user's insight to README
        update_result = await update_readme(
            UpdateReadmeInput(
                experiment_id=experiment_id,
                update_type="insight",
                update_data={
                    "section": "AI Insights",
                    "content": user_insight,
                    "source": "user",
                    "timestamp": datetime.now()
                },
                context=self.current_context
            )
        )
        
        return "Added your insight to the experiment README."
```

### Conversational Patterns

```python
# Pattern 1: Correction during review
User: "Show me the PCR optimization results"
Assistant: [Displays README summary with key results]
User: "The primer concentration should be 0.4μM, not 0.5μM"
Assistant: [Updates README, shows diff, confirms]

# Pattern 2: Adding missing information
User: "We also tested with Q5 polymerase"
Assistant: "I'll add that to the Methods section. What were the results with Q5?"
User: "Better specificity but lower yield"
Assistant: [Updates both Methods and Results sections]

# Pattern 3: Clarification and update
User: "The gel doesn't look right"
Assistant: "What specifically is incorrect about the gel analysis?"
User: "There's a faint band at 300bp we didn't mention"
Assistant: [Updates gel image description, adds to unexpected observations]

# Pattern 4: Batch corrections
User: "Several things need updating: temperature was 64°C, we used 35 cycles, and the yield was 280ng/μL"
Assistant: [Parses all corrections, updates multiple sections, shows comprehensive diff]
```

## 🔄 Background Context Propagation

### File Change Context Flow

```python
class FileChangeHandler:
    """Handles file changes with proper context"""
    
    async def on_file_added(self, file_path: str):
        # Step 1: Determine experiment
        experiment_id = self.get_experiment_from_path(file_path)
        
        # Step 2: Load full experiment context
        exp_context = await self.load_experiment_context(experiment_id)
        
        # Step 3: Load project context for comparison
        proj_context = await self.load_project_context()
        
        # Step 4: Analyze with full context
        analysis = await analyze_with_context(
            AnalyzeWithContextInput(
                file_path=file_path,
                file_type=self.detect_file_type(file_path),
                experiment_context=exp_context,
                project_context=proj_context,
                analysis_prompt=f"""
                This file was just added to {experiment_id}.
                Based on the experiment's goals and previous results,
                analyze what this new data shows and how it advances
                the experiment.
                """
            )
        )
        
        # Step 5: Update README with analysis
        await update_readme(
            UpdateReadmeInput(
                experiment_id=experiment_id,
                update_type="file_added",
                update_data={
                    "file_path": file_path,
                    "analysis": analysis.file_summary,
                    "key_findings": analysis.key_findings,
                    "comparison": analysis.comparison_with_previous
                },
                context=ToolContext(
                    session=None,  # Background operation
                    experiment=exp_context,
                    project=proj_context,
                    trigger="file_change",
                    enrichments={"analysis_result": analysis}
                )
            )
        )
```

## 📊 Context-Aware Analysis Examples

### Example 1: Analyzing PCR Results with Context

```python
# When analyzing "pcr_results_day3.csv"

# WITHOUT CONTEXT (Bad):
analysis = analyze_file("pcr_results_day3.csv")
# Result: "CSV with 96 rows, mean Ct value 24.5"

# WITH CONTEXT (Good):
analysis = analyze_with_context(
    file_path="pcr_results_day3.csv",
    experiment_context=exp_context,  # Contains day1, day2 results
    project_context=proj_context,  # Contains successful PCR patterns
)
# Result: 
# "Day 3 PCR shows 15% improvement over day 1 (Ct 24.5 vs 28.3).
#  Approaching optimal range seen in exp_005 (Ct 23.0).
#  The annealing temperature adjustment to 62°C appears effective.
#  Recommend: Maintain current conditions, test reproducibility."
```

### Example 2: Smart Failure Diagnosis

```python
# User: "Why did this Western blot fail?"

# System loads:
# 1. Current experiment README (attempt 3 of Western blot)
# 2. Previous attempts (attempts 1 and 2)
# 3. Successful Western blots from other experiments
# 4. Recent changes (new antibody lot)

# Context-aware response:
"Based on your experiment history, this is the third attempt with 
consistent high background. Comparing with your successful Western 
in exp_012, the key difference is the blocking buffer (5% milk vs 
3% BSA). Also, the new antibody lot (received last week) might 
require different dilution. Your previous lot worked at 1:1000, 
but similar antibody changes in exp_018 required 1:2000 dilution."
```

## 🎯 Implementation Priorities

### Phase 1: Core Context System (Week 1)
- [ ] Implement ToolContext dataclasses
- [ ] Build ContextBuilder class
- [ ] Create IntentRouter
- [ ] Implement read_project tool
- [ ] Implement update_readme with context

### Phase 2: Interactive Updates (Week 2)
- [ ] Implement ChatReadmeManager
- [ ] Build conversation context tracking
- [ ] Create chat_update tool
- [ ] Implement correction patterns
- [ ] Add diff generation

### Phase 3: Smart Analysis (Week 3)
- [ ] Implement analyze_with_context
- [ ] Build comparison engine
- [ ] Create enrichment pipeline
- [ ] Add background file monitoring
- [ ] Implement context propagation

## 📈 Success Metrics

### Context Quality
- Context completeness: >95% relevant info included
- Context relevance: <10% irrelevant info
- Propagation accuracy: 100% context preservation
- Enrichment value: >30% better insights with context

### User Experience
- Correction accuracy: >95% correct interpretation
- Update speed: <2 seconds for chat updates
- Context loading: <1 second
- Natural conversation: >90% user satisfaction

### System Performance
- Memory usage: <100MB per session
- Context cache hit rate: >80%
- Concurrent sessions: 50+
- Context switches: <100ms

## 🔒 Data Privacy in Context

### Sensitive Data Handling
```python
class ContextSanitizer:
    """Ensures sensitive data doesn't leak through context"""
    
    def sanitize_context(self, context: ToolContext) -> ToolContext:
        # Remove sensitive fields
        if context.experiment:
            context.experiment.readme_content = self.redact_sensitive(
                context.experiment.readme_content
            )
        
        # Clear personal information
        context.session.user_info = self.anonymize_user(
            context.session.user_info
        )
        
        return context
    
    def redact_sensitive(self, text: str) -> str:
        # Redact patient IDs, personal info, etc.
        patterns = [
            r'patient_id:\s*\w+',
            r'email:\s*[\w@.]+',
            r'phone:\s*[\d-]+'
        ]
        for pattern in patterns:
            text = re.sub(pattern, '[REDACTED]', text)
        return text
```

## 🎓 Context Learning Examples

### Learning from Context Over Time

```python
class ContextLearner:
    """Learns patterns from accumulated context"""
    
    def learn_from_successes(self, project_context: ProjectContext):
        successful_experiments = self.get_successful_experiments(project_context)
        
        patterns = {}
        for exp in successful_experiments:
            # Extract what made it successful
            patterns[exp.id] = {
                "methods": self.extract_methods(exp),
                "parameters": self.extract_parameters(exp),
                "conditions": self.extract_conditions(exp)
            }
        
        # Find commonalities
        common_success_factors = self.find_commonalities(patterns)
        
        # Update project context
        project_context.success_patterns.update(common_success_factors)
        
        # Generate recommendations
        return self.generate_recommendations(common_success_factors)
```

## Appendix A: Context Schema Examples

### Full Tool Invocation with Context

```python
# Example: User wants to analyze new data file

# Step 1: User message
user_message = "Analyze the new Western blot image I just added"

# Step 2: System builds context
context = ToolContext(
    session=SessionContext(
        session_id="sess_123",
        user_intent="analyze_western_blot",
        conversation_history=[...],
        current_experiment="exp_024_western_optimization",
        current_files=["western_blot_day3.tif"],
        preferences={"detail_level": "high"}
    ),
    experiment=ExperimentContext(
        experiment_id="exp_024_western_optimization",
        readme_content="[Full README content]",
        files_metadata={
            "western_blot_day1.tif": FileInfo(...),
            "western_blot_day2.tif": FileInfo(...),
            "western_blot_day3.tif": FileInfo(...)  # New file
        },
        recent_changes=[
            ChangeEvent(
                type="file_added",
                file="western_blot_day3.tif",
                timestamp="2025-01-13T10:30:00"
            )
        ],
        parent_project=project_context,
        related_experiments=["exp_012_western_standard", "exp_018_antibody_test"]
    ),
    project=ProjectContext(
        project_root="data/alice_projects",
        project_readme="[Project README]",
        global_insights={
            "western_blot": "5% milk blocking works better than 3% BSA",
            "antibodies": "New lots often need dilution adjustment"
        },
        experiment_history=["exp_001", "exp_002", ...],
        active_experiments=["exp_024", "exp_025"],
        success_patterns={
            "western_blot": {
                "blocking": "5% milk for 1 hour",
                "antibody_dilution": "1:1000-1:2000",
                "exposure_time": "30-60 seconds"
            }
        },
        failure_patterns={
            "western_blot": {
                "high_background": "Usually blocking or antibody concentration",
                "no_signal": "Often transfer or antibody issue"
            }
        }
    ),
    trigger="user_command",
    enrichments={
        "previous_analyses": [
            "Day 1: High background, weak signal",
            "Day 2: Better signal, still some background"
        ],
        "expected_results": "Clear bands at 50kDa and 37kDa",
        "recent_conversation": [...]
    }
)

# Step 3: Tool execution with full context
result = await analyze_with_context(
    AnalyzeWithContextInput(
        file_path="western_blot_day3.tif",
        file_type="image",
        experiment_context=context.experiment,
        project_context=context.project,
        analysis_prompt="Analyze considering previous attempts"
    )
)

# Step 4: Context-aware response
# "The Day 3 Western blot shows significant improvement:
#  - Background reduced by ~70% compared to Day 1
#  - Clear bands at expected 50kDa and 37kDa positions
#  - Signal intensity improved 2x from Day 2
#  - The blocking buffer change to 5% milk (as successful in exp_012) was effective
#  - Recommend: This protocol is ready for routine use"
```

## Document History

- **v3.0** (2025-01-13): Complete data flow and context specification
  - Detailed input/output schemas
  - Context propagation system
  - Chat-based README updates
  - Routing logic
  - Rich examples

---

**Key Insight**: "Context is everything - tools are just functions, but context makes them intelligent."