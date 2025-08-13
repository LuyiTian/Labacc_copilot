"""
Agent Trajectory Evaluator for LabAcc Copilot

Evaluates the PROCESS (tool calls, reasoning chains, error recovery) 
not just the final outcome. This addresses the critical gap in current
evaluation systems that only look at final responses.

Key Capabilities:
- Tool selection logic evaluation
- Parameter accuracy assessment  
- Information synthesis quality
- Error recovery capability
- Scientific reasoning chain validation
- Efficiency analysis

Integration: Works alongside existing evaluator_agent.py to provide
comprehensive evaluation covering both HOW (trajectory) and WHAT (response).
"""

import json
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, BaseMessage
from src.components.llm import get_llm_instance, get_evaluation_model_name


class TrajectoryStepType(Enum):
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result" 
    AGENT_REASONING = "agent_reasoning"
    ERROR_RECOVERY = "error_recovery"


@dataclass
class TrajectoryStep:
    """Single step in agent's execution trajectory"""
    step_type: TrajectoryStepType
    tool_name: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    result: Optional[str] = None
    reasoning: Optional[str] = None
    error_message: Optional[str] = None
    timestamp: Optional[float] = None
    success: bool = True


@dataclass
class AgentTrajectory:
    """Complete execution trajectory of an agent"""
    steps: List[TrajectoryStep]
    total_duration: float
    tool_call_count: int
    error_count: int
    recovery_attempts: int
    unique_tools_used: List[str]
    
    @property
    def efficiency_metrics(self) -> Dict[str, float]:
        """Calculate trajectory efficiency metrics"""
        return {
            "tool_calls_per_step": self.tool_call_count / max(len(self.steps), 1),
            "error_rate": self.error_count / max(self.tool_call_count, 1),
            "recovery_success_rate": 1.0 if self.error_count == 0 else 
                                   (self.recovery_attempts / self.error_count),
            "tool_diversity": len(self.unique_tools_used) / max(self.tool_call_count, 1)
        }


@dataclass
class TrajectoryEvaluation:
    """Comprehensive trajectory evaluation results"""
    tool_selection_logic: float      # 1-10: Did agent pick optimal tools?
    parameter_accuracy: float        # 1-10: Were tool parameters correct?
    information_synthesis: float     # 1-10: How well combined tool outputs?
    error_recovery: float           # 1-10: Handled failures gracefully?
    reasoning_quality: float        # 1-10: Sound scientific logic chains?
    efficiency: float               # 1-10: Optimal path to answer?
    
    # Detailed reasoning for each score
    reasoning_details: Dict[str, str]
    
    # Critical issues identified
    critical_issues: List[str]
    
    # Specific recommendations
    recommendations: List[str]
    
    @property
    def trajectory_score(self) -> float:
        """Calculate weighted overall trajectory score"""
        weights = {
            'tool_selection_logic': 0.25,
            'parameter_accuracy': 0.15, 
            'information_synthesis': 0.20,
            'error_recovery': 0.15,
            'reasoning_quality': 0.15,
            'efficiency': 0.10
        }
        
        return (
            self.tool_selection_logic * weights['tool_selection_logic'] +
            self.parameter_accuracy * weights['parameter_accuracy'] +
            self.information_synthesis * weights['information_synthesis'] +
            self.error_recovery * weights['error_recovery'] +
            self.reasoning_quality * weights['reasoning_quality'] +
            self.efficiency * weights['efficiency']
        )


class TrajectoryExtractor:
    """Extracts structured trajectory from LangGraph execution messages"""
    
    @staticmethod
    def extract_from_messages(messages: List[BaseMessage], start_time: float = 0.0) -> AgentTrajectory:
        """Extract trajectory from LangGraph message sequence"""
        
        steps = []
        tool_call_count = 0
        error_count = 0
        recovery_attempts = 0
        tools_used = set()
        
        current_reasoning = ""
        pending_tool_calls = {}
        
        for i, message in enumerate(messages):
            timestamp = start_time + i * 0.1  # Approximate timestamps
            
            if isinstance(message, HumanMessage):
                # User input - not part of agent trajectory
                continue
                
            elif isinstance(message, AIMessage):
                # Agent reasoning and/or tool calls
                current_reasoning = message.content or ""
                
                # Check for tool calls in this message
                if hasattr(message, 'tool_calls') and message.tool_calls:
                    for tool_call in message.tool_calls:
                        tool_name = tool_call.get('name')
                        tool_args = tool_call.get('args', {})
                        tool_id = tool_call.get('id')
                        
                        if tool_name:
                            tools_used.add(tool_name)
                            tool_call_count += 1
                            
                            step = TrajectoryStep(
                                step_type=TrajectoryStepType.TOOL_CALL,
                                tool_name=tool_name,
                                parameters=tool_args,
                                reasoning=current_reasoning,
                                timestamp=timestamp
                            )
                            steps.append(step)
                            
                            # Track pending tool call for result matching
                            if tool_id:
                                pending_tool_calls[tool_id] = len(steps) - 1
                            
                elif current_reasoning.strip():
                    # Pure reasoning without tool calls
                    step = TrajectoryStep(
                        step_type=TrajectoryStepType.AGENT_REASONING,
                        reasoning=current_reasoning,
                        timestamp=timestamp
                    )
                    steps.append(step)
                    
            elif isinstance(message, ToolMessage):
                # Tool execution result
                tool_name = getattr(message, 'name', 'unknown')
                content = message.content
                tool_call_id = getattr(message, 'tool_call_id', None)
                
                # Check if this was an error
                is_error = ('error' in content.lower() or 
                           'failed' in content.lower() or
                           'exception' in content.lower())
                
                if is_error:
                    error_count += 1
                    # Check if next steps show recovery attempt
                    if i + 1 < len(messages):
                        recovery_attempts += 1
                
                step = TrajectoryStep(
                    step_type=TrajectoryStepType.TOOL_RESULT,
                    tool_name=tool_name,
                    result=content,
                    error_message=content if is_error else None,
                    timestamp=timestamp,
                    success=not is_error
                )
                steps.append(step)
        
        total_duration = len(messages) * 0.1  # Approximate duration
        
        return AgentTrajectory(
            steps=steps,
            total_duration=total_duration,
            tool_call_count=tool_call_count,
            error_count=error_count,
            recovery_attempts=recovery_attempts,
            unique_tools_used=list(tools_used)
        )


class TrajectoryEvaluator:
    """LLM-based evaluator for agent execution trajectories"""
    
    def __init__(self, model_name: Optional[str] = None):
        resolved = model_name or get_evaluation_model_name()
        self.llm = get_llm_instance(resolved)
        
    def create_trajectory_prompt(self, trajectory: AgentTrajectory, test_case, agent_response: str) -> str:
        """Create evaluation prompt for trajectory analysis"""
        
        # Format trajectory steps for evaluation
        trajectory_text = self._format_trajectory_for_prompt(trajectory)
        
        prompt = f"""You are an expert evaluator for AI agent behavior. Your task is to evaluate the PROCESS (trajectory) the agent used to arrive at its answer, not just the final response.

EVALUATION CONTEXT:
- User Query: "{test_case.user_query}"
- Language: {test_case.language}
- Current Folder: {test_case.current_folder or 'None'}
- Selected Files: {test_case.selected_files or 'None'}

AGENT'S EXECUTION TRAJECTORY:
{trajectory_text}

FINAL AGENT RESPONSE:
{agent_response}

TRAJECTORY EVALUATION CRITERIA:
Please score each aspect from 1-10 based on the agent's execution process:

1. TOOL SELECTION LOGIC (1-10): Did the agent choose optimal tools for this task?
   - 10: Perfect tool selection, optimal sequence for the query type
   - 7-9: Good tool choices with minor suboptimal selections
   - 4-6: Reasonable tools but missed opportunities or inefficiencies
   - 1-3: Wrong tools selected, inappropriate for the task
   
   Consider for LabAcc context:
   - Should use list_folder_contents() before analyze_data() for context
   - Should use analyze_data() for specific files, not scan_project()
   - Should use run_deep_research() only for literature questions

2. PARAMETER ACCURACY (1-10): Were tools called with correct parameters?
   - 10: All parameters correct, well-formed, and contextually appropriate
   - 7-9: Mostly correct with minor parameter issues
   - 4-6: Some parameter errors but tools still functioned
   - 1-3: Multiple parameter errors causing tool failures
   
   Check: file paths, folder names, parameter formats, required vs optional args

3. INFORMATION SYNTHESIS (1-10): How well did the agent combine outputs from multiple tools?
   - 10: Excellent integration creating coherent, insightful analysis
   - 7-9: Good synthesis with minor gaps in connection
   - 4-6: Basic combination but lacks depth or misses connections
   - 1-3: Poor integration, contradictory or confused synthesis
   
   Look for: connecting insights across files, building coherent narrative

4. ERROR RECOVERY (1-10): How did the agent handle tool failures or unexpected results?
   - 10: Graceful error handling with smart alternative approaches
   - 7-9: Good recovery with minor issues or delays
   - 4-6: Basic error handling but could be more sophisticated
   - 1-3: Poor recovery, gives up easily or provides unhelpful errors
   - N/A: No errors occurred (rate as 8.0 for neutral)

5. REASONING QUALITY (1-10): Is the step-by-step logic scientifically sound?
   - 10: Clear, logical reasoning with sound scientific connections
   - 7-9: Good reasoning with minor logical gaps
   - 4-6: Basic reasoning but lacks scientific rigor or depth
   - 1-3: Poor logic, unsupported conclusions, scientific errors
   
   For LabAcc: Check scientific reasoning about experiments, protocols, data

6. EFFICIENCY (1-10): Was this an optimal path to the answer?
   - 10: Minimal necessary steps, no redundancy, optimal sequence
   - 7-9: Efficient with minor unnecessary steps
   - 4-6: Reasonable efficiency but noticeable room for improvement
   - 1-3: Highly inefficient, many unnecessary or redundant tool calls

RESPONSE FORMAT:
Provide your evaluation in this exact JSON format:

{{
    "tool_selection_logic": {{
        "score": <1-10>,
        "reasoning": "<detailed analysis of tool choices and sequence>"
    }},
    "parameter_accuracy": {{
        "score": <1-10>,
        "reasoning": "<analysis of parameter correctness>"
    }},
    "information_synthesis": {{
        "score": <1-10>,
        "reasoning": "<evaluation of how well agent combined tool outputs>"
    }},
    "error_recovery": {{
        "score": <1-10 or "N/A">,
        "reasoning": "<analysis of error handling, or 'No errors occurred'>"
    }},
    "reasoning_quality": {{
        "score": <1-10>,
        "reasoning": "<evaluation of scientific logic and reasoning chains>"
    }},
    "efficiency": {{
        "score": <1-10>,
        "reasoning": "<analysis of path optimality and redundancy>"
    }},
    "overall_trajectory_assessment": "<summary of trajectory strengths and weaknesses>",
    "critical_issues": ["<list of serious trajectory problems>"],
    "recommendations": ["<specific suggestions for improvement>"],
    "notable_good_patterns": ["<highlight excellent trajectory behaviors>"]
}}"""

        return prompt
    
    def _format_trajectory_for_prompt(self, trajectory: AgentTrajectory) -> str:
        """Format trajectory steps for inclusion in evaluation prompt"""
        
        formatted_steps = []
        for i, step in enumerate(trajectory.steps):
            step_num = i + 1
            
            if step.step_type == TrajectoryStepType.TOOL_CALL:
                formatted_steps.append(
                    f"Step {step_num}: TOOL CALL - {step.tool_name}\n"
                    f"  Parameters: {json.dumps(step.parameters, indent=2)}\n"
                    f"  Agent reasoning: {step.reasoning}\n"
                )
                
            elif step.step_type == TrajectoryStepType.TOOL_RESULT:
                status = "SUCCESS" if step.success else "ERROR"
                result_preview = step.result[:200] + "..." if len(step.result or "") > 200 else step.result
                formatted_steps.append(
                    f"Step {step_num}: TOOL RESULT - {step.tool_name} [{status}]\n"
                    f"  Result: {result_preview}\n"
                )
                
            elif step.step_type == TrajectoryStepType.AGENT_REASONING:
                formatted_steps.append(
                    f"Step {step_num}: AGENT REASONING\n"
                    f"  Content: {step.reasoning}\n"
                )
        
        # Add trajectory summary
        metrics = trajectory.efficiency_metrics
        summary = f"""
TRAJECTORY SUMMARY:
- Total steps: {len(trajectory.steps)}
- Tool calls: {trajectory.tool_call_count}
- Tools used: {', '.join(trajectory.unique_tools_used)}
- Errors: {trajectory.error_count}
- Recovery attempts: {trajectory.recovery_attempts}
- Tool diversity: {metrics['tool_diversity']:.2f}
- Error rate: {metrics['error_rate']:.2f}

EXECUTION STEPS:
{chr(10).join(formatted_steps)}
        """
        
        return summary.strip()
    
    async def evaluate_trajectory(self, trajectory: AgentTrajectory, test_case, agent_response: str) -> TrajectoryEvaluation:
        """Evaluate agent trajectory using LLM-as-a-Judge"""
        
        evaluation_prompt = self.create_trajectory_prompt(trajectory, test_case, agent_response)
        
        try:
            # Get evaluation from LLM judge
            evaluation_text = await self.llm.ainvoke(evaluation_prompt)
            
            # Parse JSON response
            evaluation_data = json.loads(evaluation_text.content)
            
            # Extract scores
            trajectory_eval = TrajectoryEvaluation(
                tool_selection_logic=float(evaluation_data['tool_selection_logic']['score']),
                parameter_accuracy=float(evaluation_data['parameter_accuracy']['score']),
                information_synthesis=float(evaluation_data['information_synthesis']['score']),
                error_recovery=float(evaluation_data['error_recovery']['score']) 
                    if evaluation_data['error_recovery']['score'] != "N/A" else 8.0,
                reasoning_quality=float(evaluation_data['reasoning_quality']['score']),
                efficiency=float(evaluation_data['efficiency']['score']),
                
                reasoning_details={
                    'tool_selection_logic': evaluation_data['tool_selection_logic']['reasoning'],
                    'parameter_accuracy': evaluation_data['parameter_accuracy']['reasoning'],
                    'information_synthesis': evaluation_data['information_synthesis']['reasoning'],
                    'error_recovery': evaluation_data['error_recovery']['reasoning'],
                    'reasoning_quality': evaluation_data['reasoning_quality']['reasoning'],
                    'efficiency': evaluation_data['efficiency']['reasoning'],
                    'overall_assessment': evaluation_data['overall_trajectory_assessment']
                },
                
                critical_issues=evaluation_data.get('critical_issues', []),
                recommendations=evaluation_data.get('recommendations', [])
            )
            
            return trajectory_eval
            
        except Exception as e:
            # Fallback evaluation on error
            return TrajectoryEvaluation(
                tool_selection_logic=0.0,
                parameter_accuracy=0.0,
                information_synthesis=0.0,
                error_recovery=0.0,
                reasoning_quality=0.0,
                efficiency=0.0,
                reasoning_details={'error': f"Trajectory evaluation failed: {str(e)}"},
                critical_issues=[f"Evaluation system error: {str(e)}"],
                recommendations=["Fix trajectory evaluation system"]
            )


# Integration functions for easy testing
async def quick_trajectory_evaluate(messages: List[BaseMessage], user_query: str, 
                                  agent_response: str, current_folder: str = None) -> TrajectoryEvaluation:
    """Quick trajectory evaluation for testing"""
    
    # Extract trajectory
    extractor = TrajectoryExtractor()
    trajectory = extractor.extract_from_messages(messages)
    
    # Create mock test case
    from .evaluator_agent import TestCase, TestCategory
    test_case = TestCase(
        id="quick_trajectory_test",
        category=TestCategory.CONTEXT_UNDERSTANDING,
        user_query=user_query,
        language="English",
        current_folder=current_folder,
        selected_files=None,
        expected_content="",
        expected_insights=[],
        ground_truth={}
    )
    
    # Evaluate trajectory
    evaluator = TrajectoryEvaluator()
    return await evaluator.evaluate_trajectory(trajectory, test_case, agent_response)


if __name__ == "__main__":
    # Example usage and testing
    async def test_trajectory_evaluator():
        # Mock messages representing agent execution
        from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
        
        messages = [
            HumanMessage(content="What is in this folder?"),
            AIMessage(
                content="I'll check the contents of this folder for you.",
                tool_calls=[{
                    "name": "list_folder_contents", 
                    "args": {"folder_path": "exp_001_protocol_test"},
                    "id": "call_1"
                }]
            ),
            ToolMessage(
                content="Contents of exp_001_protocol_test:\nFiles:\n📄 dissociation_notes.txt (2.1KB)\n📄 cell_markers_analysis.csv (15.3KB)",
                name="list_folder_contents",
                tool_call_id="call_1"
            ),
            AIMessage(content="This folder contains experimental data including dissociation protocol notes and cell analysis results.")
        ]
        
        # Test trajectory extraction
        extractor = TrajectoryExtractor()
        trajectory = extractor.extract_from_messages(messages)
        
        print(f"Trajectory extracted:")
        print(f"- Steps: {len(trajectory.steps)}")
        print(f"- Tool calls: {trajectory.tool_call_count}")
        print(f"- Tools used: {trajectory.unique_tools_used}")
        
        # Test trajectory evaluation
        result = await quick_trajectory_evaluate(
            messages=messages,
            user_query="What is in this folder?",
            agent_response="This folder contains experimental data including dissociation protocol notes and cell analysis results.",
            current_folder="exp_001_protocol_test"
        )
        
        print(f"\nTrajectory Score: {result.trajectory_score:.1f}")
        print(f"Tool Selection: {result.tool_selection_logic}")
        print(f"Efficiency: {result.efficiency}")
        print(f"Reasoning Quality: {result.reasoning_quality}")
    
    asyncio.run(test_trajectory_evaluator())