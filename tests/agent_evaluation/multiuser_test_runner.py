"""
Multi-User Test Runner for LabAcc Copilot Agent Evaluation

Updated test runner that works with the new multi-user, project-based architecture
while maintaining backward compatibility with existing test cases.
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import concurrent.futures
import logging

from .evaluator_agent import AgentEvaluator, EvaluationResult, TestCase, TestCategory
from .test_generator import TestCaseGenerator
from ..utils.multiuser_test_utils import test_manager, create_test_session, cleanup_test_session
from ..utils.compatibility_layer import handle_message_with_compatibility, CompatibilityContext

logger = logging.getLogger(__name__)

@dataclass
class MultiUserTestCase(TestCase):
    """Extended test case with multi-user context"""
    project_id: Optional[str] = None
    user_id: str = "temp_user"
    requires_project_selection: bool = True
    
    @classmethod
    def from_legacy_test_case(cls, legacy_case: TestCase) -> 'MultiUserTestCase':
        """Convert legacy test case to multi-user format"""
        # Map folder to project if possible
        project_id = None
        if legacy_case.current_folder:
            mapping = test_manager.map_old_folder_to_project(legacy_case.current_folder)
            if mapping:
                project_id = mapping.project_id
        
        return cls(
            id=legacy_case.id,
            category=legacy_case.category,
            user_query=legacy_case.user_query,
            language=legacy_case.language,
            current_folder=legacy_case.current_folder,
            selected_files=legacy_case.selected_files,
            expected_content=legacy_case.expected_content,
            expected_insights=legacy_case.expected_insights,
            ground_truth=legacy_case.ground_truth,
            project_id=project_id,
            user_id="temp_user",
            requires_project_selection=project_id is not None
        )

@dataclass
class MultiUserTestRunSummary:
    """Extended test summary with multi-user metrics"""
    total_tests: int
    passed_tests: int
    failed_tests: int
    overall_pass_rate: float
    category_scores: Dict[str, float]
    language_scores: Dict[str, float]
    project_scores: Dict[str, float]  # New: scores by project
    session_management_score: float  # New: session management effectiveness
    average_response_time: float
    total_execution_time: float
    timestamp: str
    multi_user_features_tested: List[str]  # New: list of multi-user features tested

@dataclass
class PerformanceMetrics:
    response_time_ms: float
    token_usage: Optional[int]
    api_calls: int
    memory_usage_mb: Optional[float]
    session_setup_time_ms: Optional[float] = None  # New: time to set up session context

class MultiUserTestRunner:
    """Enhanced test runner for multi-user agent evaluation"""
    
    def __init__(self, evaluator_model: Optional[str] = None, max_parallel: int = 3):
        self.evaluator = AgentEvaluator(evaluator_model)
        self.max_parallel = max_parallel
        self.test_results: List[EvaluationResult] = []
        self.performance_metrics: List[PerformanceMetrics] = []
        self.compatibility_mode = True  # Enable by default for gradual migration
        
    async def run_single_test(self, test_case: TestCase, use_compatibility: bool = None) -> tuple[EvaluationResult, PerformanceMetrics]:
        """Run a single test case with multi-user support"""
        
        if use_compatibility is None:
            use_compatibility = self.compatibility_mode
            
        start_time = time.time()
        session_setup_time = 0
        api_calls = 1
        
        # Generate unique session ID for this test
        session_id = f"test_{test_case.id}_{int(time.time() * 1000)}"
        
        try:
            if use_compatibility:
                # Use compatibility layer for existing tests
                session_setup_start = time.time()
                
                agent_response = await handle_message_with_compatibility(
                    message=test_case.user_query,
                    session_id=session_id,
                    current_folder=test_case.current_folder,
                    selected_files=test_case.selected_files
                )
                
                session_setup_time = (time.time() - session_setup_start) * 1000
                
            else:
                # Native multi-user approach
                session_setup_start = time.time()
                
                # Convert to multi-user test case if needed
                if not isinstance(test_case, MultiUserTestCase):
                    mu_test_case = MultiUserTestCase.from_legacy_test_case(test_case)
                else:
                    mu_test_case = test_case
                
                # Create test session
                test_session = await create_test_session(
                    session_id=session_id,
                    user_id=mu_test_case.user_id,
                    project_id=mu_test_case.project_id if mu_test_case.requires_project_selection else None
                )
                
                session_setup_time = (time.time() - session_setup_start) * 1000
                
                # Import and use the new handle_message function
                from src.agents.react_agent import handle_message
                
                # Set session context and call agent
                from ..utils.multiuser_test_utils import set_test_session
                set_test_session(session_id)
                
                agent_response = await handle_message(
                    message=test_case.user_query,
                    session_id=session_id
                )
            
            response_time = (time.time() - start_time) * 1000
            
            # Evaluate response using existing evaluator
            evaluation_result = await self.evaluator.evaluate_response(test_case, agent_response)
            
            # Create performance metrics with session timing
            performance = PerformanceMetrics(
                response_time_ms=response_time,
                session_setup_time_ms=session_setup_time,
                token_usage=None,  # Would need to track from LLM calls
                api_calls=api_calls,
                memory_usage_mb=None  # Would need to implement memory tracking
            )
            
            return evaluation_result, performance
            
        except Exception as e:
            logger.error(f"Test execution failed for {test_case.id}: {str(e)}")
            
            # Handle test execution errors
            error_result = EvaluationResult(
                test_case_id=test_case.id,
                criteria=self.evaluator.EvaluationCriteria(0.0, 0.0, 0.0, 0.0, 0.0),
                reasoning={'error': f"Test execution failed: {str(e)}", 'stack_trace': str(e)},
                agent_response="",
                passed=False,
                timestamp=str(time.time())
            )
            
            error_performance = PerformanceMetrics(
                response_time_ms=(time.time() - start_time) * 1000,
                session_setup_time_ms=session_setup_time,
                token_usage=None,
                api_calls=0,
                memory_usage_mb=None
            )
            
            return error_result, error_performance
            
        finally:
            # Clean up session
            try:
                cleanup_test_session(session_id)
            except Exception as e:
                logger.debug(f"Session cleanup failed for {session_id}: {e}")

    async def run_batch_tests(self, 
                             test_cases: List[TestCase], 
                             progress_callback: Optional[callable] = None,
                             use_compatibility: bool = None) -> List[tuple[EvaluationResult, PerformanceMetrics]]:
        """Run tests in parallel batches with multi-user support"""
        
        if use_compatibility is None:
            use_compatibility = self.compatibility_mode
        
        semaphore = asyncio.Semaphore(self.max_parallel)
        
        async def run_with_semaphore(test_case):
            async with semaphore:
                result = await self.run_single_test(test_case, use_compatibility)
                if progress_callback:
                    progress_callback(test_case.id, result[0].passed)
                return result
        
        # Create tasks for all tests
        tasks = [run_with_semaphore(tc) for tc in test_cases]
        
        # Execute with progress tracking
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and log them
        valid_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Test batch execution exception: {result}")
            else:
                valid_results.append(result)
        
        return valid_results
    
    def analyze_results(self, 
                       results: List[EvaluationResult], 
                       performance_metrics: List[PerformanceMetrics]) -> MultiUserTestRunSummary:
        """Analyze test results with multi-user metrics"""
        
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.passed)
        failed_tests = total_tests - passed_tests
        overall_pass_rate = passed_tests / total_tests if total_tests > 0 else 0.0
        
        # Analyze by category
        category_scores = {}
        category_counts = {}
        
        # Analyze by project (new)
        project_scores = {}
        project_counts = {}
        
        for i, result in enumerate(results):
            # Category analysis
            category = result.test_case_id.split('_')[0] 
            
            if category not in category_scores:
                category_scores[category] = 0.0
                category_counts[category] = 0
            
            category_scores[category] += result.criteria.overall_score
            category_counts[category] += 1
            
            # Project analysis (extract from test ID or use heuristics)
            project = self._extract_project_from_test_id(result.test_case_id)
            if project not in project_scores:
                project_scores[project] = 0.0
                project_counts[project] = 0
            
            project_scores[project] += result.criteria.overall_score
            project_counts[project] += 1
        
        # Average scores by category
        for category in category_scores:
            if category_counts[category] > 0:
                category_scores[category] /= category_counts[category]
        
        # Average scores by project  
        for project in project_scores:
            if project_counts[project] > 0:
                project_scores[project] /= project_counts[project]
        
        # Analyze by language (existing logic)
        language_scores = self._analyze_language_scores(results)
        
        # Calculate session management score
        session_setup_times = [pm.session_setup_time_ms for pm in performance_metrics if pm.session_setup_time_ms]
        avg_session_setup = sum(session_setup_times) / len(session_setup_times) if session_setup_times else 0
        session_management_score = max(0, 10 - (avg_session_setup / 100))  # Score based on setup time
        
        # Average response time
        avg_response_time = sum(pm.response_time_ms for pm in performance_metrics) / len(performance_metrics) if performance_metrics else 0
        
        # Multi-user features tested
        multi_user_features = self._identify_tested_features(results)
        
        return MultiUserTestRunSummary(
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            overall_pass_rate=overall_pass_rate,
            category_scores=category_scores,
            language_scores=language_scores,
            project_scores=project_scores,
            session_management_score=session_management_score,
            average_response_time=avg_response_time,
            total_execution_time=sum(pm.response_time_ms for pm in performance_metrics),
            timestamp=datetime.now().isoformat(),
            multi_user_features_tested=multi_user_features
        )
    
    def _extract_project_from_test_id(self, test_id: str) -> str:
        """Extract project identifier from test ID"""
        # Look for known project patterns
        if 'alice' in test_id.lower():
            return 'alice_projects'
        elif 'bob' in test_id.lower():
            return 'bob_projects'
        elif 'exp_' in test_id.lower():
            return 'experiments'
        else:
            return 'unknown'
    
    def _analyze_language_scores(self, results: List[EvaluationResult]) -> Dict[str, float]:
        """Analyze scores by language"""
        language_scores = {}
        language_counts = {}
        
        for result in results:
            # Extract language from test ID or use heuristics
            if '_cn_' in result.test_case_id or 'chinese' in result.test_case_id.lower():
                language = 'Chinese'
            elif '_mixed_' in result.test_case_id:
                language = 'Mixed'
            else:
                language = 'English'
            
            if language not in language_scores:
                language_scores[language] = 0.0
                language_counts[language] = 0
            
            language_scores[language] += result.criteria.overall_score
            language_counts[language] += 1
        
        # Average by language
        for language in language_scores:
            if language_counts[language] > 0:
                language_scores[language] /= language_counts[language]
        
        return language_scores
    
    def _identify_tested_features(self, results: List[EvaluationResult]) -> List[str]:
        """Identify which multi-user features were tested"""
        features = set()
        
        for result in results:
            test_id = result.test_case_id.lower()
            
            if any(proj in test_id for proj in ['alice', 'bob', 'project']):
                features.add('project_isolation')
            if 'session' in test_id:
                features.add('session_management')
            if 'permission' in test_id:
                features.add('permission_control')
            if 'multiuser' in test_id:
                features.add('multi_user_workflows')
        
        # Add default features that are always tested
        features.update(['session_creation', 'project_selection'])
        
        return list(features)
    
    async def run_comprehensive_evaluation(self, 
                                          test_cases: List[TestCase],
                                          use_compatibility: bool = None) -> MultiUserTestRunSummary:
        """Run comprehensive evaluation with detailed reporting"""
        
        print("🚀 Running Multi-User Agent Evaluation")
        print(f"📊 Total Tests: {len(test_cases)}")
        print(f"🔧 Compatibility Mode: {'Enabled' if (use_compatibility or self.compatibility_mode) else 'Disabled'}")
        print(f"⚡ Parallel Workers: {self.max_parallel}")
        print("-" * 50)
        
        start_time = time.time()
        
        def progress_callback(test_id: str, passed: bool):
            status = "✅" if passed else "❌"
            print(f"{status} {test_id}")
        
        # Run all tests
        results = await self.run_batch_tests(
            test_cases, 
            progress_callback=progress_callback,
            use_compatibility=use_compatibility
        )
        
        # Separate results and metrics
        test_results = [r[0] for r in results]
        performance_metrics = [r[1] for r in results]
        
        # Analyze results
        summary = self.analyze_results(test_results, performance_metrics)
        
        print("-" * 50)
        print("📈 EVALUATION COMPLETE")
        print(f"⏱️  Total Time: {time.time() - start_time:.1f}s")
        print(f"✅ Pass Rate: {summary.overall_pass_rate:.1%}")
        print(f"🏆 Session Score: {summary.session_management_score:.1f}/10")
        print(f"🌐 Multi-User Features: {len(summary.multi_user_features_tested)}")
        
        return summary
    
    def set_compatibility_mode(self, enabled: bool):
        """Enable or disable compatibility mode"""
        self.compatibility_mode = enabled
        logger.info(f"Compatibility mode {'enabled' if enabled else 'disabled'}")
        
    def save_results(self, summary: MultiUserTestRunSummary, output_path: str):
        """Save test results to file"""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(asdict(summary), f, indent=2, default=str)
        
        logger.info(f"Test results saved to {output_path}")