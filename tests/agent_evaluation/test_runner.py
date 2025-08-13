"""
Test Runner for LabAcc Copilot Agent Evaluation
Orchestrates comprehensive testing with parallel execution and detailed reporting
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import concurrent.futures

from .evaluator_agent import AgentEvaluator, EvaluationResult, TestCase, TestCategory
from .test_generator import TestCaseGenerator
from src.agents.react_agent import handle_message


@dataclass
class TestRunSummary:
    total_tests: int
    passed_tests: int
    failed_tests: int
    overall_pass_rate: float
    category_scores: Dict[str, float]
    language_scores: Dict[str, float]
    average_response_time: float
    total_execution_time: float
    timestamp: str


@dataclass
class PerformanceMetrics:
    response_time_ms: float
    token_usage: Optional[int]
    api_calls: int
    memory_usage_mb: Optional[float]


class AgentTestRunner:
    """Comprehensive test runner for agent evaluation"""
    
    def __init__(self, evaluator_model: Optional[str] = None, max_parallel: int = 5):
        self.evaluator = AgentEvaluator(evaluator_model)
        self.max_parallel = max_parallel
        self.test_results: List[EvaluationResult] = []
        self.performance_metrics: List[PerformanceMetrics] = []
        
    async def run_single_test(self, test_case: TestCase) -> tuple[EvaluationResult, PerformanceMetrics]:
        """Run a single test case and measure performance"""
        
        start_time = time.time()
        api_calls = 1
        
        try:
            # Execute agent query
            agent_response = await handle_message(
                message=test_case.user_query,
                session_id=f"test_{test_case.id}",
                current_folder=test_case.current_folder,
                selected_files=test_case.selected_files
            )
            
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Evaluate response
            evaluation_result = await self.evaluator.evaluate_response(test_case, agent_response)
            
            # Create performance metrics
            performance = PerformanceMetrics(
                response_time_ms=response_time,
                token_usage=None,  # Would need to track from LLM calls
                api_calls=api_calls,
                memory_usage_mb=None  # Would need to implement memory tracking
            )
            
            return evaluation_result, performance
            
        except Exception as e:
            # Handle test execution errors
            error_result = EvaluationResult(
                test_case_id=test_case.id,
                criteria=self.evaluator.EvaluationCriteria(0.0, 0.0, 0.0, 0.0, 0.0),
                reasoning={'error': f"Test execution failed: {str(e)}"},
                agent_response="",
                passed=False,
                timestamp=str(time.time())
            )
            
            error_performance = PerformanceMetrics(
                response_time_ms=(time.time() - start_time) * 1000,
                token_usage=None,
                api_calls=0,
                memory_usage_mb=None
            )
            
            return error_result, error_performance
    
    async def run_batch_tests(self, test_cases: List[TestCase], 
                             progress_callback: Optional[callable] = None) -> List[tuple[EvaluationResult, PerformanceMetrics]]:
        """Run tests in parallel batches"""
        
        semaphore = asyncio.Semaphore(self.max_parallel)
        
        async def run_with_semaphore(test_case):
            async with semaphore:
                result = await self.run_single_test(test_case)
                if progress_callback:
                    progress_callback(test_case.id, result[0].passed)
                return result
        
        # Create tasks for all tests
        tasks = [run_with_semaphore(tc) for tc in test_cases]
        
        # Execute with progress tracking
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_results = [r for r in results if not isinstance(r, Exception)]
        
        return valid_results
    
    def analyze_results(self, results: List[EvaluationResult], 
                       performance_metrics: List[PerformanceMetrics]) -> TestRunSummary:
        """Analyze test results and generate summary"""
        
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.passed)
        failed_tests = total_tests - passed_tests
        overall_pass_rate = passed_tests / total_tests if total_tests > 0 else 0.0
        
        # Analyze by category
        category_scores = {}
        category_counts = {}
        
        for result in results:
            # Extract category from test_case_id (assuming format: category_lang_num)
            category = result.test_case_id.split('_')[0] 
            
            if category not in category_scores:
                category_scores[category] = 0.0
                category_counts[category] = 0
            
            category_scores[category] += result.criteria.overall_score
            category_counts[category] += 1
        
        # Average scores by category
        for category in category_scores:
            category_scores[category] /= category_counts[category]
        
        # Analyze by language 
        language_scores = {}
        language_counts = {}
        
        for result in results:
            # Extract language from test_case_id
            parts = result.test_case_id.split('_')
            lang = 'english' if 'en' in parts else 'chinese' if 'cn' in parts else 'other'
            
            if lang not in language_scores:
                language_scores[lang] = 0.0
                language_counts[lang] = 0
            
            language_scores[lang] += result.criteria.overall_score
            language_counts[lang] += 1
        
        # Average scores by language
        for lang in language_scores:
            language_scores[lang] /= language_counts[lang]
        
        # Performance analysis
        response_times = [pm.response_time_ms for pm in performance_metrics if pm.response_time_ms > 0]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0.0
        
        return TestRunSummary(
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            overall_pass_rate=overall_pass_rate,
            category_scores=category_scores,
            language_scores=language_scores,
            average_response_time=avg_response_time,
            total_execution_time=sum(response_times) / 1000,  # Convert to seconds
            timestamp=datetime.now().isoformat()
        )
    
    def save_detailed_results(self, results: List[EvaluationResult], 
                             performance_metrics: List[PerformanceMetrics],
                             summary: TestRunSummary, output_dir: str):
        """Save detailed results to files"""
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save summary
        summary_file = output_path / f"test_summary_{timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump(asdict(summary), f, indent=2)
        
        # Save detailed results
        detailed_file = output_path / f"detailed_results_{timestamp}.json"
        detailed_data = {
            "summary": asdict(summary),
            "results": [asdict(r) for r in results],
            "performance": [asdict(pm) for pm in performance_metrics]
        }
        
        with open(detailed_file, 'w') as f:
            json.dump(detailed_data, f, indent=2)
        
        # Save failed tests for debugging
        failed_results = [r for r in results if not r.passed]
        if failed_results:
            failed_file = output_path / f"failed_tests_{timestamp}.json"
            failed_data = {
                "failed_count": len(failed_results),
                "failed_tests": [asdict(r) for r in failed_results]
            }
            
            with open(failed_file, 'w') as f:
                json.dump(failed_data, f, indent=2)
        
        print(f"\n📁 Results saved to {output_path}:")
        print(f"  - Summary: {summary_file.name}")
        print(f"  - Detailed: {detailed_file.name}")
        if failed_results:
            print(f"  - Failed Tests: {failed_file.name}")
    
    def print_summary_report(self, summary: TestRunSummary):
        """Print human-readable summary report"""
        
        print("\n" + "="*80)
        print("🧪 LABACC COPILOT AGENT EVALUATION REPORT")
        print("="*80)
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"  Total Tests: {summary.total_tests}")
        print(f"  Passed: {summary.passed_tests} ✅")
        print(f"  Failed: {summary.failed_tests} ❌")
        print(f"  Pass Rate: {summary.overall_pass_rate:.1%}")
        
        if summary.overall_pass_rate >= 0.8:
            status = "🟢 EXCELLENT"
        elif summary.overall_pass_rate >= 0.7:
            status = "🟡 ACCEPTABLE"
        else:
            status = "🔴 NEEDS IMPROVEMENT"
        
        print(f"  Status: {status}")
        
        print(f"\n📈 PERFORMANCE METRICS:")
        print(f"  Average Response Time: {summary.average_response_time:.0f}ms")
        print(f"  Total Execution Time: {summary.total_execution_time:.1f}s")
        
        print(f"\n📋 CATEGORY BREAKDOWN:")
        for category, score in summary.category_scores.items():
            status_emoji = "✅" if score >= 7.0 else "❌"
            print(f"  {category.replace('_', ' ').title()}: {score:.1f}/10 {status_emoji}")
        
        print(f"\n🌍 LANGUAGE PERFORMANCE:")
        for language, score in summary.language_scores.items():
            status_emoji = "✅" if score >= 7.0 else "❌"
            print(f"  {language.title()}: {score:.1f}/10 {status_emoji}")
        
        print(f"\n🎯 RECOMMENDATIONS:")
        if summary.overall_pass_rate < 0.7:
            print("  - ⚠️ Critical: Overall pass rate below acceptable threshold")
            print("  - 🔧 Review failed test cases and improve agent logic")
        
        if summary.language_scores.get('chinese', 10) < summary.language_scores.get('english', 10):
            print("  - 🌏 Improve Chinese language understanding")
            
        if summary.average_response_time > 5000:  # 5 seconds
            print("  - ⚡ Optimize response time for better user experience")
        
        print("\n" + "="*80)
    
    async def run_comprehensive_evaluation(self, test_cases: Optional[List[TestCase]] = None,
                                         output_dir: str = "tests/reports") -> TestRunSummary:
        """Run comprehensive evaluation suite"""
        
        if test_cases is None:
            print("📝 Generating test cases...")
            generator = TestCaseGenerator()
            test_cases = generator.generate_all_test_cases()
        
        print(f"\n🚀 Starting evaluation of {len(test_cases)} test cases...")
        print(f"   Max parallel execution: {self.max_parallel}")
        
        # Progress tracking
        completed = 0
        
        def progress_callback(test_id: str, passed: bool):
            nonlocal completed
            completed += 1
            status = "✅" if passed else "❌"
            print(f"   Progress: {completed}/{len(test_cases)} {status} {test_id}")
        
        # Run tests
        start_time = time.time()
        results_and_metrics = await self.run_batch_tests(test_cases, progress_callback)
        
        # Separate results and metrics
        results = [rm[0] for rm in results_and_metrics]
        metrics = [rm[1] for rm in results_and_metrics]
        
        # Analyze results
        print(f"\n📊 Analyzing results...")
        summary = self.analyze_results(results, metrics)
        
        # Save results
        print(f"\n💾 Saving results...")
        self.save_detailed_results(results, metrics, summary, output_dir)
        
        # Print report
        self.print_summary_report(summary)
        
        return summary


# Convenience functions for common testing scenarios
async def quick_test(query: str, current_folder: str = None, language: str = "English", evaluator_model: Optional[str] = None) -> bool:
    """Quick single test for debugging"""
    
    runner = AgentTestRunner(evaluator_model=evaluator_model)
    
    test_case = TestCase(
        id="quick_test",
        category=TestCategory.CONTEXT_UNDERSTANDING,
        user_query=query,
        language=language,
        current_folder=current_folder,
        selected_files=None,
        expected_content="Quick test response",
        expected_insights=[],
        ground_truth={}
    )
    
    result, _ = await runner.run_single_test(test_case)
    
    print(f"\n🧪 Quick Test Result:")
    print(f"Query: {query}")
    print(f"Folder: {current_folder}")
    print(f"Score: {result.criteria.overall_score:.1f}/10")
    print(f"Passed: {'✅' if result.passed else '❌'}")
    print(f"Response: {result.agent_response[:200]}...")
    
    return result.passed


async def regression_test(baseline_file: str, current_results: List[EvaluationResult]) -> Dict:
    """Compare current results against baseline for regression testing"""
    
    with open(baseline_file, 'r') as f:
        baseline_data = json.load(f)
    
    baseline_pass_rate = baseline_data['summary']['overall_pass_rate']
    current_pass_rate = sum(1 for r in current_results if r.passed) / len(current_results)
    
    regression_detected = current_pass_rate < baseline_pass_rate - 0.05  # 5% threshold
    
    return {
        'regression_detected': regression_detected,
        'baseline_pass_rate': baseline_pass_rate,
        'current_pass_rate': current_pass_rate,
        'difference': current_pass_rate - baseline_pass_rate
    }


if __name__ == "__main__":
    async def main():
        # Run comprehensive evaluation
        runner = AgentTestRunner(max_parallel=3)
        summary = await runner.run_comprehensive_evaluation()
        
        print(f"\n✨ Evaluation completed!")
        print(f"   Overall score: {summary.overall_pass_rate:.1%}")
        
        if summary.overall_pass_rate >= 0.8:
            print("🎉 Agent is ready for production!")
        elif summary.overall_pass_rate >= 0.7:
            print("⚠️ Agent needs minor improvements")
        else:
            print("🔧 Agent needs significant improvements")
    
    asyncio.run(main())