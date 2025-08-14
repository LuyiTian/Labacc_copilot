#!/usr/bin/env python3
"""
LabAcc Copilot Agent Evaluation CLI
Runs LLM-as-judge evaluation for complex agent behavior assessment

This script ONLY runs agent-driven evaluation using LLM-as-judge.
For unit tests, use: uv run pytest tests/unit/
"""

import asyncio
import argparse
import sys
from pathlib import Path
from typing import List, Optional
import time

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))
sys.path.append(str(Path(__file__).parent / "tests"))

from tests.agent_evaluation.enhanced_test_runner import (
    EnhancedAgentTestRunner,
    ComprehensiveTestSummary
)
from tests.agent_evaluation.test_generator import TestCaseGenerator
from tests.agent_evaluation.realistic_test_scenarios import RealisticTestScenarioGenerator


class EvaluationCLI:
    """CLI interface for agent evaluation"""
    
    def __init__(self):
        self.runner = EnhancedAgentTestRunner()
        self.test_generator = TestCaseGenerator()
        self.scenario_generator = RealisticTestScenarioGenerator()
    
    
    async def run_full_evaluation(self) -> ComprehensiveTestSummary:
        """Run full evaluation (50+ test cases including realistic scenarios)"""
        print("🚀 Running Full Evaluation (50+ tests)")
        print("Estimated time: 10-15 minutes")
        print("Includes: Basic tests + Multi-round conversations + Memory tests")
        print("-" * 50)
        
        # Generate all test cases
        test_cases = []
        
        # Basic test cases
        test_cases.extend(self.test_generator.generate_context_understanding_tests())
        test_cases.extend(self.test_generator.generate_file_analysis_tests())
        test_cases.extend(self.test_generator.generate_experiment_insights_tests())
        test_cases.extend(self.test_generator.generate_protocol_optimization_tests())
        test_cases.extend(self.test_generator.generate_edge_case_tests())
        
        # Advanced realistic scenarios (converted to test cases)
        realistic_scenarios = [
            self.scenario_generator.generate_project_discovery_scenario(),
            self.scenario_generator.generate_cross_experiment_optimization_scenario(),
            self.scenario_generator.generate_error_recovery_scenario(),
            self.scenario_generator.generate_domain_expertise_scenario()
        ]
        
        # Convert multi-turn scenarios to single test cases for evaluation
        for scenario in realistic_scenarios:
            # Use the first turn as a representative test
            if scenario.turns:
                first_turn = scenario.turns[0]
                from tests.agent_evaluation.evaluator_agent import TestCase, TestCategory
                
                # first_turn is a tuple: (query, folder, selected_files)
                query, folder, selected_files = first_turn
                
                test_case = TestCase(
                    id=f"realistic_{scenario.scenario_id}",
                    category=TestCategory.CONTEXT_UNDERSTANDING,
                    user_query=query,
                    language=scenario.language,
                    current_folder=folder if folder else "/data/luyit/script/git/Labacc_copilot/data/bob_projects",
                    selected_files=selected_files,
                    expected_content=scenario.critical_requirements,
                    expected_insights=scenario.expected_tool_sequence,  # Use tool sequence as insights
                    ground_truth={"scenario": scenario.description}
                )
                test_cases.append(test_case)
        
        return await self.runner.run_comprehensive_evaluation(test_cases)
    


async def main():
    """Main CLI entry point"""
    
    # Set TEST_MODE environment variable for bob_projects access
    import os
    os.environ["TEST_MODE"] = "true"
    
    parser = argparse.ArgumentParser(
        description="LabAcc Copilot Agent Evaluation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_evaluation.py                 # Default: full comprehensive evaluation
  python run_evaluation.py --full          # Same as above (explicit)
  python run_evaluation.py --generate-report # Show what tests would run
        """
    )
    
    # Evaluation mode
    parser.add_argument(
        "--full",
        action="store_true",
        help="Full comprehensive evaluation (50+ tests, ~15 minutes)"
    )
    
    # Options
    parser.add_argument(
        "--generate-report",
        action="store_true",
        help="Show what tests would be run without executing"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="tests/reports",
        help="Directory to save evaluation reports"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed progress and test results"
    )
    
    args = parser.parse_args()
    
    # Default to full if no mode specified
    if not args.full:
        args.full = True
    
    cli = EvaluationCLI()
    
    if args.generate_report:
        print("📋 Test Cases That Would Be Run:")
        print("=" * 50)
        print("Full Mode: 50+ comprehensive tests including:")
        print("- Context understanding (multi-language)")
        print("- File analysis and data interpretation") 
        print("- Experimental insights and problem diagnosis")
        print("- Protocol optimization suggestions")
        print("- Multi-round conversation scenarios")
        print("- Memory system testing (README updates, corrections)")
        print("- Error recovery and edge cases")
        return
    
    print("🧪 LabAcc Copilot Agent Evaluation System")
    print("=" * 80)
    print(f"🕒 Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run evaluation based on mode
    start_time = time.time()
    summary = None
    
    try:
        # Always run full evaluation (since that's all we have now)
        summary = await cli.run_full_evaluation()
        
        # Print results
        if summary:
            execution_time = time.time() - start_time
            print(f"\n⏱️  Total execution time: {execution_time:.1f} seconds")
            
            # Save results
            output_dir = Path(args.output_dir)
            output_dir.mkdir(exist_ok=True)
            
            # Determine if this was a good run
            if summary.overall_pass_rate >= 0.85:
                print("\n🎉 EXCELLENT PERFORMANCE!")
                print("The agent is performing very well across all test categories.")
            elif summary.overall_pass_rate >= 0.75:
                print("\n✅ GOOD PERFORMANCE")  
                print("The agent is performing well with room for minor improvements.")
            else:
                print("\n⚠️  NEEDS IMPROVEMENT")
                print("The agent has significant issues that should be addressed.")
                
                if summary.critical_issues:
                    print("\n🚨 Critical Issues Found:")
                    for issue in summary.critical_issues[:3]:
                        print(f"  - {issue}")
            
            if summary.recommendations:
                print(f"\n💡 Top Recommendations:")
                for rec in summary.recommendations[:3]:
                    print(f"  - {rec}")
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Evaluation interrupted by user")
    except Exception as e:
        print(f"\n❌ Evaluation failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)