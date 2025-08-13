"""
LabAcc Copilot Agent Evaluation Framework

State-of-the-art evaluation system for AI agents based on latest research:
- LLM-as-a-Judge/Agent-as-a-Judge evaluation
- Multilingual testing (English/Chinese) 
- Test-driven development approach
- Automated regression testing
- Performance benchmarking

Usage:
    from tests.agent_evaluation import AgentTestRunner, TestCaseGenerator
    
    # Generate comprehensive test suite
    generator = TestCaseGenerator()
    test_cases = generator.generate_all_test_cases()
    
    # Run evaluation
    runner = AgentTestRunner()
    summary = await runner.run_comprehensive_evaluation(test_cases)
"""

from .evaluator_agent import (
    AgentEvaluator,
    EvaluationCriteria,
    EvaluationResult,
    TestCase,
    TestCategory,
    quick_evaluate
)

from .test_generator import TestCaseGenerator

from .test_runner import (
    AgentTestRunner,
    TestRunSummary,
    PerformanceMetrics,
    quick_test,
    regression_test
)

# Import enhanced evaluation system components
from .trajectory_evaluator import (
    TrajectoryEvaluator,
    TrajectoryEvaluation, 
    AgentTrajectory,
    quick_trajectory_evaluate
)

from .comprehensive_evaluator import (
    ComprehensiveAgentEvaluator,
    ComprehensiveEvaluationResult,
    quick_comprehensive_evaluate
)

from .enhanced_test_runner import (
    EnhancedAgentTestRunner,
    ComprehensiveTestSummary,
    quick_comprehensive_test
)

# Import realistic testing components
from .realistic_test_scenarios import (
    RealisticTestScenarioGenerator,
    MultiTurnTestScenario
)

try:
    from .reproduce_user_failures import (
        UserFailureReproducer,
        UserFailureCase
    )
except ImportError:
    # Optional import for user failure analysis
    pass

__all__ = [
    # Original system
    'AgentEvaluator',
    'EvaluationCriteria', 
    'EvaluationResult',
    'TestCase',
    'TestCategory',
    'TestCaseGenerator',
    'AgentTestRunner',
    'TestRunSummary',
    'PerformanceMetrics',
    'quick_evaluate',
    'quick_test',
    'regression_test',
    
    # Enhanced trajectory evaluation system
    'TrajectoryEvaluator',
    'TrajectoryEvaluation',
    'AgentTrajectory', 
    'quick_trajectory_evaluate',
    
    # Comprehensive evaluation system
    'ComprehensiveAgentEvaluator',
    'ComprehensiveEvaluationResult',
    'quick_comprehensive_evaluate',
    
    # Enhanced test runner
    'EnhancedAgentTestRunner',
    'ComprehensiveTestSummary',
    'quick_comprehensive_test',
    
    # Realistic testing system
    'RealisticTestScenarioGenerator',
    'MultiTurnTestScenario'
]

__version__ = "1.0.0"