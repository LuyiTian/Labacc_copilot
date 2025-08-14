"""
Enhanced Test Runner with Trajectory Evaluation

This runner captures the full agent execution trajectory (tool calls, reasoning steps, 
error recovery) and evaluates both WHAT the agent produced and HOW it got there.

Key enhancements over basic test runner:
- Captures LangGraph execution messages for trajectory analysis
- Uses ComprehensiveAgentEvaluator (response + trajectory evaluation)  
- Provides detailed trajectory metrics and debugging information
- Supports trajectory-specific CLI modes and reporting

Integration: Works with existing CLI while adding comprehensive evaluation capabilities.
"""

import asyncio
import json
import time
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from .comprehensive_evaluator import (
    ComprehensiveAgentEvaluator, 
    ComprehensiveEvaluationResult
)
from .test_generator import TestCaseGenerator
from .evaluator_agent import TestCase

# Import agent with trajectory capture capability
from src.agents.react_agent import handle_message_with_trajectory


@dataclass 
class TrajectoryTestResult:
    """Test result with comprehensive trajectory evaluation"""
    test_case_id: str
    user_query: str
    agent_response: str
    evaluation: ComprehensiveEvaluationResult
    performance_metrics: Dict[str, Any]
    execution_time_ms: float
    
    @property
    def passed(self) -> bool:
        return self.evaluation.comprehensive_passed
    
    @property
    def combined_score(self) -> float:
        return self.evaluation.combined_score


@dataclass
class ComprehensiveTestSummary:
    """Enhanced summary with trajectory metrics"""
    
    # Basic metrics
    total_tests: int
    passed_tests: int
    failed_tests: int
    overall_pass_rate: float
    
    # Score breakdowns  
    avg_combined_score: float
    avg_response_score: float
    avg_trajectory_score: float
    
    # Category breakdowns
    category_scores: Dict[str, float]
    language_scores: Dict[str, float]
    
    # Response evaluation breakdown
    response_breakdown: Dict[str, float]
    
    # Trajectory evaluation breakdown
    trajectory_breakdown: Dict[str, float]
    
    # Performance metrics
    average_response_time: float
    total_execution_time: float
    
    # Trajectory-specific metrics
    avg_tool_calls: float
    avg_trajectory_errors: float
    most_used_tools: List[str]
    
    # Issues and recommendations
    critical_issues: List[str]
    recommendations: List[str]
    
    timestamp: str


class EnhancedAgentTestRunner:
    """Test runner with comprehensive trajectory evaluation"""
    
    def __init__(self, evaluator_model: Optional[str] = None, max_parallel: int = 3):
        self.comprehensive_evaluator = ComprehensiveAgentEvaluator(evaluator_model)
        self.max_parallel = max_parallel
        self.test_results: List[TrajectoryTestResult] = []
        
    async def run_single_test_with_trajectory(self, test_case: TestCase) -> TrajectoryTestResult:
        """Run single test with full trajectory capture and evaluation"""
        
        start_time = time.time()
        
        try:
            # Execute agent with trajectory capture
            agent_response, execution_messages = await self._execute_agent_with_trajectory(
                message=test_case.user_query,
                session_id=f"test_{test_case.id}",
                current_folder=test_case.current_folder,
                selected_files=test_case.selected_files
            )
            
            execution_time_ms = (time.time() - start_time) * 1000
            
            # Comprehensive evaluation (response + trajectory)
            evaluation = await self.comprehensive_evaluator.evaluate_comprehensive(
                test_case=test_case,
                agent_response=agent_response,
                execution_messages=execution_messages,
                execution_start_time=start_time
            )
            
            # Performance metrics
            performance_metrics = {
                'execution_time_ms': execution_time_ms,
                'tool_calls': evaluation.trajectory.tool_call_count,
                'errors': evaluation.trajectory.error_count,
                'recovery_attempts': evaluation.trajectory.recovery_attempts,
                'tools_used': evaluation.trajectory.unique_tools_used,
                'trajectory_steps': len(evaluation.trajectory.steps)
            }
            
            return TrajectoryTestResult(
                test_case_id=test_case.id,
                user_query=test_case.user_query,
                agent_response=agent_response,
                evaluation=evaluation,
                performance_metrics=performance_metrics,
                execution_time_ms=execution_time_ms
            )
            
        except Exception as e:
            # Handle test execution errors gracefully
            execution_time_ms = (time.time() - start_time) * 1000
            
            # Create minimal error evaluation
            from .evaluator_agent import EvaluationResult, EvaluationCriteria
            from .trajectory_evaluator import TrajectoryEvaluation, AgentTrajectory
            
            error_response_eval = EvaluationResult(
                test_case_id=test_case.id,
                criteria=EvaluationCriteria(0.0, 0.0, 0.0, 0.0, 0.0),
                reasoning={'error': f"Test execution failed: {str(e)}"},
                agent_response="",
                passed=False,
                timestamp=datetime.now().isoformat()
            )
            
            error_trajectory_eval = TrajectoryEvaluation(
                tool_selection_logic=0.0,
                parameter_accuracy=0.0,
                information_synthesis=0.0,
                error_recovery=0.0,
                reasoning_quality=0.0,
                efficiency=0.0,
                reasoning_details={'error': f"Trajectory capture failed: {str(e)}"},
                critical_issues=[f"Test execution error: {str(e)}"],
                recommendations=["Fix test execution system"]
            )
            
            error_evaluation = ComprehensiveEvaluationResult(
                response_evaluation=error_response_eval,
                trajectory_evaluation=error_trajectory_eval,
                trajectory=AgentTrajectory([], execution_time_ms/1000, 0, 1, 0, []),
                test_case_id=test_case.id,
                timestamp=datetime.now().isoformat()
            )
            
            return TrajectoryTestResult(
                test_case_id=test_case.id,
                user_query=test_case.user_query,
                agent_response="",
                evaluation=error_evaluation,
                performance_metrics={'execution_time_ms': execution_time_ms, 'error': str(e)},
                execution_time_ms=execution_time_ms
            )
    
    async def _execute_agent_with_trajectory(
        self, 
        message: str, 
        session_id: str,
        current_folder: Optional[str] = None,
        selected_files: Optional[List[str]] = None
    ) -> Tuple[str, List]:
        """
        Execute agent and capture full trajectory
        
        Uses the enhanced handle_message_with_trajectory to get both
        response and execution messages.
        """
        
        # Call the enhanced function to get both response and trajectory
        agent_response, execution_messages = await handle_message_with_trajectory(
            message=message,
            session_id=session_id,
            current_folder=current_folder,
            selected_files=selected_files
        )
        
        # Return the real response and trajectory
        return agent_response, execution_messages
    
    async def run_batch_tests_with_trajectory(
        self, 
        test_cases: List[TestCase],
        max_parallel: Optional[int] = None
    ) -> List[TrajectoryTestResult]:
        """Run multiple tests with trajectory evaluation in parallel"""
        
        parallel_limit = max_parallel or self.max_parallel
        
        # Create semaphore to limit concurrent executions
        semaphore = asyncio.Semaphore(parallel_limit)
        
        async def run_with_semaphore(test_case):
            async with semaphore:
                return await self.run_single_test_with_trajectory(test_case)
        
        # Execute tests in parallel with concurrency limit
        tasks = [run_with_semaphore(tc) for tc in test_cases]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and collect valid results
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Test {test_cases[i].id} failed with exception: {result}")
                # Could create error result here
            elif isinstance(result, TrajectoryTestResult):
                valid_results.append(result)
        
        self.test_results = valid_results
        return valid_results
    
    async def run_comprehensive_evaluation(
        self,
        test_cases: Optional[List[TestCase]] = None,
        output_dir: str = "tests/reports"
    ) -> ComprehensiveTestSummary:
        """Run comprehensive evaluation with full reporting"""
        
        if test_cases is None:
            # Generate default test suite
            generator = TestCaseGenerator()
            test_cases = generator.generate_all_test_cases()
        
        print(f"🚀 Starting Comprehensive Agent Evaluation (Trajectory + Response)")
        print(f"📊 Total tests: {len(test_cases)}")
        print(f"⚡ Max parallel: {self.max_parallel}")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all tests with trajectory evaluation
        results = await self.run_batch_tests_with_trajectory(test_cases)
        
        total_execution_time = time.time() - start_time
        
        # Generate comprehensive summary
        summary = self._generate_comprehensive_summary(results, total_execution_time)
        
        # Save detailed results
        await self._save_comprehensive_results(results, summary, output_dir)
        
        # Print summary report
        self._print_comprehensive_report(summary)
        
        return summary
    
    def _generate_comprehensive_summary(
        self, 
        results: List[TrajectoryTestResult], 
        total_execution_time: float
    ) -> ComprehensiveTestSummary:
        """Generate comprehensive summary with trajectory metrics"""
        
        if not results:
            return ComprehensiveTestSummary(
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                overall_pass_rate=0.0,
                avg_combined_score=0.0,
                avg_response_score=0.0,
                avg_trajectory_score=0.0,
                category_scores={},
                language_scores={},
                response_breakdown={},
                trajectory_breakdown={},
                average_response_time=0.0,
                total_execution_time=total_execution_time,
                avg_tool_calls=0.0,
                avg_trajectory_errors=0.0,
                most_used_tools=[],
                critical_issues=[],
                recommendations=[],
                timestamp=datetime.now().isoformat()
            )
        
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.passed)
        failed_tests = total_tests - passed_tests
        overall_pass_rate = passed_tests / total_tests
        
        # Score aggregations
        avg_combined_score = sum(r.combined_score for r in results) / total_tests
        avg_response_score = sum(r.evaluation.response_evaluation.criteria.overall_score for r in results) / total_tests
        avg_trajectory_score = sum(r.evaluation.trajectory_evaluation.trajectory_score for r in results) / total_tests
        
        # Response breakdown
        response_breakdown = {
            'accuracy': sum(r.evaluation.response_evaluation.criteria.accuracy for r in results) / total_tests,
            'relevance': sum(r.evaluation.response_evaluation.criteria.relevance for r in results) / total_tests,
            'completeness': sum(r.evaluation.response_evaluation.criteria.completeness for r in results) / total_tests,
            'context_awareness': sum(r.evaluation.response_evaluation.criteria.context_awareness for r in results) / total_tests,
            'language_understanding': sum(r.evaluation.response_evaluation.criteria.language_understanding for r in results) / total_tests,
        }
        
        # Trajectory breakdown  
        trajectory_breakdown = {
            'tool_selection_logic': sum(r.evaluation.trajectory_evaluation.tool_selection_logic for r in results) / total_tests,
            'parameter_accuracy': sum(r.evaluation.trajectory_evaluation.parameter_accuracy for r in results) / total_tests,
            'information_synthesis': sum(r.evaluation.trajectory_evaluation.information_synthesis for r in results) / total_tests,
            'error_recovery': sum(r.evaluation.trajectory_evaluation.error_recovery for r in results) / total_tests,
            'reasoning_quality': sum(r.evaluation.trajectory_evaluation.reasoning_quality for r in results) / total_tests,
            'efficiency': sum(r.evaluation.trajectory_evaluation.efficiency for r in results) / total_tests,
        }
        
        # Trajectory metrics
        avg_tool_calls = sum(r.evaluation.trajectory.tool_call_count for r in results) / total_tests
        avg_trajectory_errors = sum(r.evaluation.trajectory.error_count for r in results) / total_tests
        
        # Most used tools
        tool_usage = {}
        for result in results:
            for tool in result.evaluation.trajectory.unique_tools_used:
                tool_usage[tool] = tool_usage.get(tool, 0) + 1
        
        most_used_tools = sorted(tool_usage.items(), key=lambda x: x[1], reverse=True)[:5]
        most_used_tools = [f"{tool} ({count}x)" for tool, count in most_used_tools]
        
        # Collect issues and recommendations
        all_critical_issues = []
        all_recommendations = []
        for result in results:
            all_critical_issues.extend(result.evaluation.critical_issues)
            all_recommendations.extend(result.evaluation.recommendations)
        
        # Remove duplicates while preserving order
        unique_critical_issues = list(dict.fromkeys(all_critical_issues))[:10]
        unique_recommendations = list(dict.fromkeys(all_recommendations))[:10]
        
        return ComprehensiveTestSummary(
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            overall_pass_rate=overall_pass_rate,
            avg_combined_score=avg_combined_score,
            avg_response_score=avg_response_score,
            avg_trajectory_score=avg_trajectory_score,
            category_scores={},  # Could implement category breakdowns
            language_scores={},  # Could implement language breakdowns
            response_breakdown=response_breakdown,
            trajectory_breakdown=trajectory_breakdown,
            average_response_time=sum(r.execution_time_ms for r in results) / total_tests,
            total_execution_time=total_execution_time,
            avg_tool_calls=avg_tool_calls,
            avg_trajectory_errors=avg_trajectory_errors,
            most_used_tools=most_used_tools,
            critical_issues=unique_critical_issues,
            recommendations=unique_recommendations,
            timestamp=datetime.now().isoformat()
        )
    
    def _print_comprehensive_report(self, summary: ComprehensiveTestSummary):
        """Print comprehensive evaluation report to console"""
        
        print(f"\n🧪 COMPREHENSIVE AGENT EVALUATION REPORT")
        print("=" * 80)
        
        # Overall results
        status_emoji = "🟢" if summary.overall_pass_rate >= 0.9 else "🟡" if summary.overall_pass_rate >= 0.7 else "🔴"
        status_text = "EXCELLENT" if summary.overall_pass_rate >= 0.9 else "GOOD" if summary.overall_pass_rate >= 0.8 else "ACCEPTABLE" if summary.overall_pass_rate >= 0.7 else "NEEDS IMPROVEMENT"
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"  Total Tests: {summary.total_tests}")
        print(f"  Passed: {summary.passed_tests} ✅")
        print(f"  Failed: {summary.failed_tests} ❌")
        print(f"  Pass Rate: {summary.overall_pass_rate:.1%}")
        print(f"  Status: {status_emoji} {status_text}")
        
        # Score breakdown
        print(f"\n🎯 SCORE BREAKDOWN:")
        print(f"  Combined Score: {summary.avg_combined_score:.1f}/10")
        print(f"  Response Score: {summary.avg_response_score:.1f}/10 (60% weight)")
        print(f"  Trajectory Score: {summary.avg_trajectory_score:.1f}/10 (40% weight)")
        
        # Response evaluation breakdown
        print(f"\n📝 RESPONSE EVALUATION:")
        for metric, score in summary.response_breakdown.items():
            status = "✅" if score >= 7.0 else "⚠️" if score >= 6.0 else "❌"
            print(f"  {metric.replace('_', ' ').title()}: {score:.1f}/10 {status}")
        
        # Trajectory evaluation breakdown  
        print(f"\n🔄 TRAJECTORY EVALUATION:")
        for metric, score in summary.trajectory_breakdown.items():
            status = "✅" if score >= 7.0 else "⚠️" if score >= 6.0 else "❌"
            print(f"  {metric.replace('_', ' ').title()}: {score:.1f}/10 {status}")
        
        # Performance metrics
        print(f"\n📈 PERFORMANCE METRICS:")
        print(f"  Average Response Time: {summary.average_response_time:.0f}ms")
        print(f"  Total Execution Time: {summary.total_execution_time:.1f}s")
        print(f"  Average Tool Calls: {summary.avg_tool_calls:.1f}")
        print(f"  Average Trajectory Errors: {summary.avg_trajectory_errors:.1f}")
        
        # Tool usage
        if summary.most_used_tools:
            print(f"\n🔧 MOST USED TOOLS:")
            for tool_info in summary.most_used_tools:
                print(f"  - {tool_info}")
        
        # Critical issues
        if summary.critical_issues:
            print(f"\n⚠️ CRITICAL ISSUES:")
            for issue in summary.critical_issues[:5]:
                print(f"  - {issue}")
        
        # Recommendations
        if summary.recommendations:
            print(f"\n💡 RECOMMENDATIONS:")
            for rec in summary.recommendations[:5]:
                print(f"  - {rec}")
        
        print("\n" + "=" * 80)
    
    async def _save_comprehensive_results(
        self, 
        results: List[TrajectoryTestResult],
        summary: ComprehensiveTestSummary,
        output_dir: str
    ):
        """Save comprehensive evaluation results to files"""
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save summary
        summary_file = output_path / f"comprehensive_summary_{timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump(asdict(summary), f, indent=2, default=str)
        
        # Save detailed results
        results_file = output_path / f"comprehensive_results_{timestamp}.json"
        detailed_results = []
        for result in results:
            detailed_results.append({
                'test_case_id': result.test_case_id,
                'user_query': result.user_query,
                'agent_response': result.agent_response[:500] + "..." if len(result.agent_response) > 500 else result.agent_response,
                'combined_score': result.combined_score,
                'passed': result.passed,
                'response_score': result.evaluation.response_evaluation.criteria.overall_score,
                'trajectory_score': result.evaluation.trajectory_evaluation.trajectory_score,
                'performance_metrics': result.performance_metrics,
                'critical_issues': result.evaluation.critical_issues,
                'recommendations': result.evaluation.recommendations[:3]  # Top 3
            })
        
        with open(results_file, 'w') as f:
            json.dump(detailed_results, f, indent=2)
        
        print(f"📁 Results saved:")
        print(f"   Summary: {summary_file}")
        print(f"   Detailed: {results_file}")


# Quick convenience function for testing
async def quick_comprehensive_test(
    user_query: str = "What is in this folder?",
    current_folder: str = "exp_001_protocol_test",
    language: str = "English"
) -> TrajectoryTestResult:
    """Quick comprehensive test for debugging"""
    
    from .evaluator_agent import TestCase, TestCategory
    
    runner = EnhancedAgentTestRunner()
    
    test_case = TestCase(
        id="quick_comprehensive_test",
        category=TestCategory.CONTEXT_UNDERSTANDING,
        user_query=user_query,
        language=language,
        current_folder=current_folder,
        selected_files=None,
        expected_content="Experimental folder contents and context",
        expected_insights=["File listings", "Experimental context"],
        ground_truth={"folder": current_folder}
    )
    
    return await runner.run_single_test_with_trajectory(test_case)


if __name__ == "__main__":
    # Test the comprehensive evaluation system
    async def main():
        print("🧪 Testing Comprehensive Agent Evaluation System")
        print("=" * 50)
        
        # Quick test
        result = await quick_comprehensive_test()
        
        print(f"Test Result:")
        print(f"- Combined Score: {result.combined_score:.1f}/10")
        print(f"- Response Score: {result.evaluation.response_evaluation.criteria.overall_score:.1f}/10")
        print(f"- Trajectory Score: {result.evaluation.trajectory_evaluation.trajectory_score:.1f}/10")
        print(f"- Passed: {'✅' if result.passed else '❌'}")
        print(f"- Execution Time: {result.execution_time_ms:.0f}ms")
        
        if result.evaluation.recommendations:
            print(f"\nTop Recommendations:")
            for rec in result.evaluation.recommendations[:3]:
                print(f"- {rec}")
    
    asyncio.run(main())