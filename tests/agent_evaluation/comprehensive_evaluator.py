"""
Comprehensive Agent Evaluator - Combines Response + Trajectory Evaluation

This addresses the critical gap identified: evaluating both WHAT the agent 
produced (final response) AND HOW it got there (execution trajectory).

Key Innovation: 
- Response Evaluation (60%): Accuracy, relevance, completeness (existing system)
- Trajectory Evaluation (40%): Tool selection, reasoning quality, error recovery
- Combined Score: Holistic assessment of agent performance

For LabAcc specifically, this catches issues like:
- Wrong tool selection (efficiency problems)
- Poor error recovery (user experience issues)  
- Weak information synthesis (scientific accuracy problems)
- Unsound reasoning chains (reliability concerns)
"""

import asyncio
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from langchain_core.messages import BaseMessage

from .evaluator_agent import AgentEvaluator, EvaluationResult, TestCase
from .trajectory_evaluator import TrajectoryEvaluator, TrajectoryEvaluation, TrajectoryExtractor, AgentTrajectory


@dataclass
class ComprehensiveEvaluationResult:
    """Complete evaluation covering both response quality and execution trajectory"""
    
    # Existing response evaluation
    response_evaluation: EvaluationResult
    
    # New trajectory evaluation  
    trajectory_evaluation: TrajectoryEvaluation
    
    # Raw trajectory data for debugging
    trajectory: AgentTrajectory
    
    # Combined metrics
    test_case_id: str
    timestamp: str
    
    @property
    def combined_score(self) -> float:
        """Calculate weighted combination of response and trajectory scores"""
        response_weight = 0.6  # What the agent produced
        trajectory_weight = 0.4  # How the agent got there
        
        return (
            self.response_evaluation.criteria.overall_score * response_weight +
            self.trajectory_evaluation.trajectory_score * trajectory_weight
        )
    
    @property
    def comprehensive_passed(self) -> bool:
        """Pass/fail based on combined evaluation"""
        return self.combined_score >= 7.0
    
    @property
    def performance_breakdown(self) -> Dict[str, float]:
        """Detailed breakdown of all performance metrics"""
        return {
            # Response metrics (existing)
            'response_accuracy': self.response_evaluation.criteria.accuracy,
            'response_relevance': self.response_evaluation.criteria.relevance,
            'response_completeness': self.response_evaluation.criteria.completeness,
            'response_context_awareness': self.response_evaluation.criteria.context_awareness,
            'response_language': self.response_evaluation.criteria.language_understanding,
            'response_overall': self.response_evaluation.criteria.overall_score,
            
            # Trajectory metrics (new)
            'trajectory_tool_selection': self.trajectory_evaluation.tool_selection_logic,
            'trajectory_parameters': self.trajectory_evaluation.parameter_accuracy,
            'trajectory_synthesis': self.trajectory_evaluation.information_synthesis,
            'trajectory_error_recovery': self.trajectory_evaluation.error_recovery,
            'trajectory_reasoning': self.trajectory_evaluation.reasoning_quality,
            'trajectory_efficiency': self.trajectory_evaluation.efficiency,
            'trajectory_overall': self.trajectory_evaluation.trajectory_score,
            
            # Combined score
            'combined_score': self.combined_score
        }
    
    @property
    def critical_issues(self) -> List[str]:
        """All critical issues from both evaluations"""
        issues = []
        
        # Response evaluation issues
        if hasattr(self.response_evaluation.reasoning, 'critical_issues'):
            issues.extend(self.response_evaluation.reasoning.get('critical_issues', []))
        
        # Trajectory evaluation issues  
        issues.extend(self.trajectory_evaluation.critical_issues)
        
        return issues
    
    @property
    def recommendations(self) -> List[str]:
        """All recommendations from both evaluations"""
        recs = []
        
        # Response evaluation recommendations
        if hasattr(self.response_evaluation.reasoning, 'recommendations'):
            recs.extend(self.response_evaluation.reasoning.get('recommendations', []))
            
        # Trajectory evaluation recommendations
        recs.extend(self.trajectory_evaluation.recommendations)
        
        return recs


class ComprehensiveAgentEvaluator:
    """Enhanced evaluator that assesses both response quality and execution trajectory"""
    
    def __init__(self, model_name: str = "gpt-4o"):
        self.response_evaluator = AgentEvaluator(model_name)
        self.trajectory_evaluator = TrajectoryEvaluator(model_name)
        self.trajectory_extractor = TrajectoryExtractor()
    
    async def evaluate_comprehensive(
        self, 
        test_case: TestCase, 
        agent_response: str,
        execution_messages: List[BaseMessage],
        execution_start_time: float = 0.0
    ) -> ComprehensiveEvaluationResult:
        """
        Perform comprehensive evaluation of both response and trajectory
        
        Args:
            test_case: Test case with expected outcomes
            agent_response: Final response from agent
            execution_messages: Complete LangGraph message sequence
            execution_start_time: When agent execution started
        """
        
        # Extract trajectory from execution messages
        trajectory = self.trajectory_extractor.extract_from_messages(
            execution_messages, 
            execution_start_time
        )
        
        # Evaluate response quality (existing system)
        response_eval_task = self.response_evaluator.evaluate_response(test_case, agent_response)
        
        # Evaluate trajectory quality (new system)
        trajectory_eval_task = self.trajectory_evaluator.evaluate_trajectory(
            trajectory, test_case, agent_response
        )
        
        # Run both evaluations in parallel for efficiency
        response_eval, trajectory_eval = await asyncio.gather(
            response_eval_task, 
            trajectory_eval_task,
            return_exceptions=True
        )
        
        # Handle evaluation errors gracefully
        if isinstance(response_eval, Exception):
            response_eval = self._create_error_response_eval(test_case, str(response_eval))
        
        if isinstance(trajectory_eval, Exception):
            trajectory_eval = self._create_error_trajectory_eval(str(trajectory_eval))
        
        return ComprehensiveEvaluationResult(
            response_evaluation=response_eval,
            trajectory_evaluation=trajectory_eval,
            trajectory=trajectory,
            test_case_id=test_case.id,
            timestamp=datetime.now().isoformat()
        )
    
    def _create_error_response_eval(self, test_case: TestCase, error_msg: str) -> EvaluationResult:
        """Create fallback response evaluation on error"""
        from .evaluator_agent import EvaluationCriteria
        
        return EvaluationResult(
            test_case_id=test_case.id,
            criteria=EvaluationCriteria(0.0, 0.0, 0.0, 0.0, 0.0),
            reasoning={'error': f"Response evaluation failed: {error_msg}"},
            agent_response="",
            passed=False,
            timestamp=datetime.now().isoformat()
        )
    
    def _create_error_trajectory_eval(self, error_msg: str) -> TrajectoryEvaluation:
        """Create fallback trajectory evaluation on error"""
        return TrajectoryEvaluation(
            tool_selection_logic=0.0,
            parameter_accuracy=0.0,
            information_synthesis=0.0,
            error_recovery=0.0,
            reasoning_quality=0.0,
            efficiency=0.0,
            reasoning_details={'error': f"Trajectory evaluation failed: {error_msg}"},
            critical_issues=[f"Evaluation system error: {error_msg}"],
            recommendations=["Fix trajectory evaluation system"]
        )
    
    async def batch_evaluate_comprehensive(
        self,
        test_cases: List[TestCase],
        agent_responses: List[str],
        execution_message_sequences: List[List[BaseMessage]],
        execution_start_times: List[float] = None
    ) -> List[ComprehensiveEvaluationResult]:
        """Evaluate multiple test cases with comprehensive analysis"""
        
        if execution_start_times is None:
            execution_start_times = [0.0] * len(test_cases)
        
        # Create evaluation tasks
        tasks = []
        for i, (test_case, response, messages) in enumerate(zip(
            test_cases, agent_responses, execution_message_sequences
        )):
            task = self.evaluate_comprehensive(
                test_case=test_case,
                agent_response=response,
                execution_messages=messages,
                execution_start_time=execution_start_times[i]
            )
            tasks.append(task)
        
        # Run evaluations in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return valid results
        valid_results = [r for r in results if isinstance(r, ComprehensiveEvaluationResult)]
        
        return valid_results
    
    def generate_comprehensive_report(self, results: List[ComprehensiveEvaluationResult]) -> Dict:
        """Generate detailed report from comprehensive evaluation results"""
        
        if not results:
            return {"error": "No evaluation results to report"}
        
        # Calculate aggregate metrics
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.comprehensive_passed)
        pass_rate = passed_tests / total_tests
        
        # Aggregate scores
        avg_combined_score = sum(r.combined_score for r in results) / total_tests
        avg_response_score = sum(r.response_evaluation.criteria.overall_score for r in results) / total_tests
        avg_trajectory_score = sum(r.trajectory_evaluation.trajectory_score for r in results) / total_tests
        
        # Detailed breakdowns
        response_breakdown = {
            'accuracy': sum(r.response_evaluation.criteria.accuracy for r in results) / total_tests,
            'relevance': sum(r.response_evaluation.criteria.relevance for r in results) / total_tests,
            'completeness': sum(r.response_evaluation.criteria.completeness for r in results) / total_tests,
            'context_awareness': sum(r.response_evaluation.criteria.context_awareness for r in results) / total_tests,
            'language_understanding': sum(r.response_evaluation.criteria.language_understanding for r in results) / total_tests,
        }
        
        trajectory_breakdown = {
            'tool_selection_logic': sum(r.trajectory_evaluation.tool_selection_logic for r in results) / total_tests,
            'parameter_accuracy': sum(r.trajectory_evaluation.parameter_accuracy for r in results) / total_tests,
            'information_synthesis': sum(r.trajectory_evaluation.information_synthesis for r in results) / total_tests,
            'error_recovery': sum(r.trajectory_evaluation.error_recovery for r in results) / total_tests,
            'reasoning_quality': sum(r.trajectory_evaluation.reasoning_quality for r in results) / total_tests,
            'efficiency': sum(r.trajectory_evaluation.efficiency for r in results) / total_tests,
        }
        
        # Collect all critical issues and recommendations
        all_critical_issues = []
        all_recommendations = []
        for result in results:
            all_critical_issues.extend(result.critical_issues)
            all_recommendations.extend(result.recommendations)
        
        # Remove duplicates while preserving order
        unique_critical_issues = list(dict.fromkeys(all_critical_issues))
        unique_recommendations = list(dict.fromkeys(all_recommendations))
        
        # Trajectory efficiency metrics
        trajectory_metrics = {
            'avg_tool_calls': sum(r.trajectory.tool_call_count for r in results) / total_tests,
            'avg_errors': sum(r.trajectory.error_count for r in results) / total_tests,
            'avg_recovery_attempts': sum(r.trajectory.recovery_attempts for r in results) / total_tests,
            'tool_diversity': sum(len(r.trajectory.unique_tools_used) for r in results) / total_tests,
        }
        
        return {
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "pass_rate": pass_rate,
                "status": "EXCELLENT" if pass_rate >= 0.9 else 
                         "GOOD" if pass_rate >= 0.8 else
                         "ACCEPTABLE" if pass_rate >= 0.7 else "NEEDS_IMPROVEMENT"
            },
            "scores": {
                "combined_score": avg_combined_score,
                "response_score": avg_response_score,
                "trajectory_score": avg_trajectory_score
            },
            "response_breakdown": response_breakdown,
            "trajectory_breakdown": trajectory_breakdown,
            "trajectory_metrics": trajectory_metrics,
            "issues_and_recommendations": {
                "critical_issues": unique_critical_issues[:10],  # Top 10
                "recommendations": unique_recommendations[:10]   # Top 10
            },
            "evaluation_timestamp": datetime.now().isoformat()
        }


# Convenience functions for common patterns
async def quick_comprehensive_evaluate(
    user_query: str,
    agent_response: str, 
    execution_messages: List[BaseMessage],
    current_folder: str = None,
    language: str = "English"
) -> ComprehensiveEvaluationResult:
    """Quick comprehensive evaluation for testing and debugging"""
    
    from .evaluator_agent import TestCase, TestCategory
    
    evaluator = ComprehensiveAgentEvaluator()
    
    test_case = TestCase(
        id="quick_comprehensive_test",
        category=TestCategory.CONTEXT_UNDERSTANDING,
        user_query=user_query,
        language=language,
        current_folder=current_folder,
        selected_files=None,
        expected_content="General experimental context and file information",
        expected_insights=[],
        ground_truth={}
    )
    
    return await evaluator.evaluate_comprehensive(
        test_case=test_case,
        agent_response=agent_response,
        execution_messages=execution_messages
    )


if __name__ == "__main__":
    # Example usage
    async def test_comprehensive_evaluator():
        from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
        
        # Mock agent execution with trajectory
        messages = [
            HumanMessage(content="What went wrong with this experiment?"),
            AIMessage(
                content="I'll analyze the experimental data to identify issues.",
                tool_calls=[{
                    "name": "list_folder_contents",
                    "args": {"folder_path": "exp_001_protocol_test"},
                    "id": "call_1"
                }]
            ),
            ToolMessage(
                content="Files: dissociation_notes.txt, cell_markers_analysis.csv, raw_data_qc.csv",
                name="list_folder_contents",
                tool_call_id="call_1"  
            ),
            AIMessage(
                content="Let me analyze the cell markers data to understand the cell type distribution.",
                tool_calls=[{
                    "name": "analyze_data",
                    "args": {"file_path": "exp_001_protocol_test/cell_markers_analysis.csv"},
                    "id": "call_2"
                }]
            ),
            ToolMessage(
                content="Analysis shows severe bias: only 8.2% tumor epithelial cells vs 65.5% immune cells total.",
                name="analyze_data",
                tool_call_id="call_2"
            ),
            AIMessage(
                content="Based on the analysis, the main issue is severe immune cell enrichment bias with poor epithelial cell recovery, likely due to over-digestion at 45min/37°C causing fragile tumor cells to die while resistant immune cells survived."
            )
        ]
        
        result = await quick_comprehensive_evaluate(
            user_query="What went wrong with this experiment?",
            agent_response="Based on the analysis, the main issue is severe immune cell enrichment bias...",
            execution_messages=messages,
            current_folder="exp_001_protocol_test"
        )
        
        print(f"🎯 COMPREHENSIVE EVALUATION RESULTS")
        print(f"=" * 50)
        print(f"Combined Score: {result.combined_score:.1f}/10")
        print(f"Passed: {'✅' if result.comprehensive_passed else '❌'}")
        print()
        print(f"Response Score: {result.response_evaluation.criteria.overall_score:.1f}/10")
        print(f"Trajectory Score: {result.trajectory_evaluation.trajectory_score:.1f}/10")
        print()
        print("Trajectory Breakdown:")
        print(f"- Tool Selection: {result.trajectory_evaluation.tool_selection_logic:.1f}/10")
        print(f"- Parameter Accuracy: {result.trajectory_evaluation.parameter_accuracy:.1f}/10")
        print(f"- Information Synthesis: {result.trajectory_evaluation.information_synthesis:.1f}/10")
        print(f"- Error Recovery: {result.trajectory_evaluation.error_recovery:.1f}/10")
        print(f"- Reasoning Quality: {result.trajectory_evaluation.reasoning_quality:.1f}/10")
        print(f"- Efficiency: {result.trajectory_evaluation.efficiency:.1f}/10")
        print()
        print("Trajectory Summary:")
        print(f"- Tool calls: {result.trajectory.tool_call_count}")
        print(f"- Tools used: {', '.join(result.trajectory.unique_tools_used)}")
        print(f"- Errors: {result.trajectory.error_count}")
        
        if result.recommendations:
            print(f"\nRecommendations:")
            for rec in result.recommendations[:3]:
                print(f"- {rec}")
    
    asyncio.run(test_comprehensive_evaluator())