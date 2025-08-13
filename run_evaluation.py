#!/usr/bin/env python3
"""
LabAcc Copilot Agent Evaluation CLI

Comprehensive testing and evaluation system for the LabAcc Copilot agent.
Implements SOTA evaluation methods including LLM-as-a-Judge and multilingual testing.

Usage:
    python run_evaluation.py --full                    # Full evaluation suite
    python run_evaluation.py --quick                   # Quick test
    python run_evaluation.py --generate-tests          # Generate test cases only
    python run_evaluation.py --category context        # Test specific category  
    python run_evaluation.py --language chinese        # Test specific language
    python run_evaluation.py --regression baseline.json # Regression testing
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from tests.agent_evaluation import (
    AgentTestRunner, 
    TestCaseGenerator,
    TestCategory,
    quick_test
)

# Import enhanced evaluation system
from tests.agent_evaluation.enhanced_test_runner import (
    EnhancedAgentTestRunner,
    quick_comprehensive_test
)


async def run_full_evaluation(args):
    """Run comprehensive evaluation suite"""
    
    print("🚀 Starting LabAcc Copilot Agent Evaluation")
    print("=" * 60)
    
    # Check API keys
    api_keys = {
        "OPENROUTER_API_KEY": os.getenv("OPENROUTER_API_KEY"),
        "SILICONFLOW_API_KEY": os.getenv("SILICONFLOW_API_KEY"),
        "TAVILY_API_KEY": os.getenv("TAVILY_API_KEY")
    }
    
    missing_keys = [k for k, v in api_keys.items() if not v]
    if missing_keys:
        print(f"⚠️ Warning: Missing API keys: {', '.join(missing_keys)}")
        print("Some tests may fail without proper LLM provider configuration.")
        
        if not any(api_keys.values()):
            print("❌ No API keys found. Please set at least one LLM provider key.")
            return False
    
    # Initialize test runner
    runner = AgentTestRunner(
        evaluator_model=args.evaluator_model,
        max_parallel=args.parallel
    )
    
    # Generate or load test cases
    if args.test_file:
        print(f"📂 Loading test cases from {args.test_file}")
        generator = TestCaseGenerator()
        test_cases = generator.load_test_cases(args.test_file)
    else:
        print("📝 Generating fresh test cases...")
        generator = TestCaseGenerator()
        test_cases = generator.generate_all_test_cases()
        
        # Save generated tests
        test_file = f"tests/test_cases/generated_{generator.__class__.__name__.lower()}.json"
        generator.save_test_cases(test_cases, test_file)
    
    # Filter by category if specified
    if args.category:
        category_filter = TestCategory(args.category.lower())
        test_cases = [tc for tc in test_cases if tc.category == category_filter]
        print(f"🔍 Filtered to {len(test_cases)} tests in category: {args.category}")
    
    # Filter by language if specified
    if args.language:
        language_filter = args.language.lower()
        test_cases = [tc for tc in test_cases if language_filter in tc.language.lower()]
        print(f"🌍 Filtered to {len(test_cases)} tests in language: {args.language}")
    
    if not test_cases:
        print("❌ No test cases to run after filtering")
        return False
    
    # Run evaluation
    try:
        summary = await runner.run_comprehensive_evaluation(
            test_cases=test_cases,
            output_dir=args.output_dir
        )
        
        # Regression testing if baseline provided
        if args.baseline:
            print(f"\n🔍 Running regression analysis against {args.baseline}")
            regression_results = await runner.regression_test(
                args.baseline, 
                runner.test_results
            )
            
            if regression_results['regression_detected']:
                print(f"⚠️ REGRESSION DETECTED!")
                print(f"   Baseline: {regression_results['baseline_pass_rate']:.1%}")
                print(f"   Current: {regression_results['current_pass_rate']:.1%}")
                print(f"   Difference: {regression_results['difference']:.1%}")
                return False
            else:
                print(f"✅ No regression detected")
        
        # Check pass/fail criteria
        if summary.overall_pass_rate >= args.threshold:
            print(f"\n🎉 EVALUATION PASSED!")
            print(f"   Pass rate: {summary.overall_pass_rate:.1%} >= {args.threshold:.1%}")
            return True
        else:
            print(f"\n❌ EVALUATION FAILED!")
            print(f"   Pass rate: {summary.overall_pass_rate:.1%} < {args.threshold:.1%}")
            return False
            
    except Exception as e:
        print(f"❌ Evaluation failed with error: {str(e)}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return False


async def run_quick_test(args):
    """Run quick test for debugging"""
    
    print("⚡ Quick Test Mode")
    print("-" * 30)
    
    test_queries = [
        ("What is in this folder?", "exp_001_protocol_test", "English"),
        ("这个文件夹里有什么？", "exp_001_protocol_test", "Chinese"),
        ("What went wrong with this experiment?", "exp_001_protocol_test", "English"),
        ("我们应该如何优化这个协议？", "exp_001_protocol_test", "Chinese")
    ]
    
    passed = 0
    total = len(test_queries)
    
    for query, folder, language in test_queries:
        print(f"\n🧪 Testing: {query[:50]}...")
        
        try:
            result = await quick_test(
                query=query,
                current_folder=folder, 
                language=language,
                evaluator_model=args.evaluator_model
            )
            
            if result:
                passed += 1
                
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
    
    pass_rate = passed / total
    print(f"\n📊 Quick Test Results:")
    print(f"   Passed: {passed}/{total} ({pass_rate:.1%})")
    
    if pass_rate >= 0.75:
        print("✅ Agent appears to be working correctly")
        return True
    else:
        print("⚠️ Agent may have issues - run full evaluation")
        return False


async def run_comprehensive_evaluation(args):
    """Run comprehensive evaluation with trajectory analysis"""
    
    print("🎯 Comprehensive Evaluation Mode (Response + Trajectory)")
    print("=" * 60)
    
    # Check API keys
    api_keys = {
        "OPENROUTER_API_KEY": os.getenv("OPENROUTER_API_KEY"),
        "SILICONFLOW_API_KEY": os.getenv("SILICONFLOW_API_KEY"),
        "TAVILY_API_KEY": os.getenv("TAVILY_API_KEY")
    }
    
    missing_keys = [k for k, v in api_keys.items() if not v]
    if missing_keys:
        print(f"⚠️ Warning: Missing API keys: {', '.join(missing_keys)}")
        print("Some tests may fail without proper LLM provider configuration.")
        
        if not any(api_keys.values()):
            print("❌ No API keys found. Please set at least one LLM provider key.")
            return False
    
    # Initialize enhanced test runner with trajectory evaluation
    runner = EnhancedAgentTestRunner(
        evaluator_model=args.evaluator_model,
        max_parallel=args.parallel
    )
    
    # Generate or load test cases
    if args.test_file:
        print(f"📂 Loading test cases from {args.test_file}")
        generator = TestCaseGenerator()
        test_cases = generator.load_test_cases(args.test_file)
    else:
        print("📝 Generating fresh test cases...")
        generator = TestCaseGenerator()
        test_cases = generator.generate_all_test_cases()
        
        # Save generated tests
        test_file = f"tests/test_cases/comprehensive_{generator.__class__.__name__.lower()}.json"
        generator.save_test_cases(test_cases, test_file)
    
    # Filter by category if specified
    if args.category:
        category_filter = TestCategory(args.category.lower())
        test_cases = [tc for tc in test_cases if tc.category == category_filter]
        print(f"🔍 Filtered to {len(test_cases)} tests in category: {args.category}")
    
    # Filter by language if specified
    if args.language:
        language_filter = args.language.lower()
        test_cases = [tc for tc in test_cases if language_filter in tc.language.lower()]
        print(f"🌍 Filtered to {len(test_cases)} tests in language: {args.language}")
    
    if not test_cases:
        print("❌ No test cases to run after filtering")
        return False
    
    # Run comprehensive evaluation
    try:
        summary = await runner.run_comprehensive_evaluation(
            test_cases=test_cases,
            output_dir=args.output_dir
        )
        
        # Check pass/fail criteria  
        if summary.overall_pass_rate >= args.threshold:
            print(f"\n🎉 COMPREHENSIVE EVALUATION PASSED!")
            print(f"   Pass rate: {summary.overall_pass_rate:.1%} >= {args.threshold:.1%}")
            print(f"   Combined score: {summary.avg_combined_score:.1f}/10")
            return True
        else:
            print(f"\n❌ COMPREHENSIVE EVALUATION FAILED!")
            print(f"   Pass rate: {summary.overall_pass_rate:.1%} < {args.threshold:.1%}")
            print(f"   Combined score: {summary.avg_combined_score:.1f}/10")
            return False
            
    except Exception as e:
        print(f"❌ Comprehensive evaluation failed with error: {str(e)}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return False


async def run_trajectory_demo(args):
    """Run trajectory evaluation demo"""
    
    print("🔄 Trajectory Evaluation Demo")
    print("-" * 40)
    
    demo_queries = [
        ("What is in this folder?", "exp_001_protocol_test", "Context understanding with tool selection"),
        ("What went wrong with this experiment?", "exp_001_protocol_test", "Complex analysis with information synthesis"),
        ("How should we optimize this protocol?", "exp_001_protocol_test", "Multi-step reasoning and recommendations")
    ]
    
    for query, folder, description in demo_queries:
        print(f"\n📋 Test: {description}")
        print(f"Query: \"{query}\"")
        print(f"Folder: {folder}")
        
        try:
            result = await quick_comprehensive_test(
                user_query=query,
                current_folder=folder
            )
            
            print(f"Results:")
            print(f"  Combined Score: {result.combined_score:.1f}/10")
            print(f"  Response Score: {result.evaluation.response_evaluation.criteria.overall_score:.1f}/10")
            print(f"  Trajectory Score: {result.evaluation.trajectory_evaluation.trajectory_score:.1f}/10")
            print(f"  Tool Calls: {result.evaluation.trajectory.tool_call_count}")
            print(f"  Tools Used: {', '.join(result.evaluation.trajectory.unique_tools_used)}")
            print(f"  Execution Time: {result.execution_time_ms:.0f}ms")
            
            # Show key trajectory insights
            if result.evaluation.trajectory_evaluation.reasoning_details:
                tool_reasoning = result.evaluation.trajectory_evaluation.reasoning_details.get('tool_selection_logic', '')
                if tool_reasoning and len(tool_reasoning) > 10:
                    print(f"  Tool Selection: {tool_reasoning[:100]}...")
            
        except Exception as e:
            print(f"❌ Demo test failed: {str(e)}")
    
    print(f"\n📊 Trajectory evaluation captures:")
    print(f"  ✅ Tool selection efficiency")
    print(f"  ✅ Parameter accuracy") 
    print(f"  ✅ Information synthesis quality")
    print(f"  ✅ Error recovery capability")
    print(f"  ✅ Scientific reasoning chains")
    print(f"  ✅ Execution efficiency")
    
    return True


async def reproduce_user_failures(args):
    """Reproduce specific user-reported failures"""
    
    print("🚨 User Failure Reproduction & Analysis")
    print("=" * 50)
    
    try:
        from tests.agent_evaluation.reproduce_user_failures import run_user_failure_reproduction
        
        analysis_result, improved_tests = await run_user_failure_reproduction()
        
        print(f"\n🎯 FAILURE REPRODUCTION RESULTS:")
        print(f"   Total Failures Analyzed: {analysis_result['total_failures']}")
        print(f"   Successfully Reproduced: {analysis_result['reproduced_failures']}")
        print(f"   Caught by Trajectory Eval: {analysis_result['caught_by_trajectory']}")
        print(f"   Detection Effectiveness: {analysis_result['effectiveness']:.1%}")
        
        if analysis_result['effectiveness'] >= 0.8:
            print(f"\n✅ Trajectory evaluation successfully catches real user failures!")
            return True
        else:
            print(f"\n⚠️ Trajectory evaluation needs improvement for real-world scenarios")
            return False
            
    except Exception as e:
        print(f"❌ Failure reproduction failed: {str(e)}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return False


async def run_realistic_scenarios(args):
    """Run realistic multi-turn scenarios"""
    
    print("🎭 Realistic Scenario Testing")
    print("=" * 40)
    
    try:
        from tests.agent_evaluation.realistic_test_scenarios import RealisticTestScenarioGenerator
        
        generator = RealisticTestScenarioGenerator()
        
        # Generate realistic scenarios
        scenarios = generator.generate_all_realistic_scenarios()
        test_cases = generator.convert_to_test_cases(scenarios)
        
        print(f"📋 Generated {len(scenarios)} realistic scenarios ({len(test_cases)} test cases)")
        
        # Use enhanced test runner for evaluation
        runner = EnhancedAgentTestRunner(
            evaluator_model=args.evaluator_model,
            max_parallel=args.parallel
        )
        
        # Run evaluation on realistic scenarios  
        results = await runner.run_batch_tests_with_trajectory(test_cases[:10])  # Limit for demo
        
        # Analyze results
        passed = sum(1 for r in results if r.passed)
        total = len(results)
        pass_rate = passed / total if total > 0 else 0
        
        print(f"\n📊 REALISTIC SCENARIO RESULTS:")
        print(f"   Tests Run: {total}")
        print(f"   Passed: {passed}")
        print(f"   Pass Rate: {pass_rate:.1%}")
        
        # Show specific insights
        for result in results[:3]:  # Show first 3 as examples
            print(f"\n🧪 {result.test_case_id}:")
            print(f"   Query: {result.user_query[:50]}...")
            print(f"   Combined Score: {result.combined_score:.1f}/10")
            print(f"   Tools Used: {', '.join(result.evaluation.trajectory.unique_tools_used)}")
            
        if pass_rate >= 0.7:
            print(f"\n✅ Agent handles realistic scenarios well!")
            return True
        else:
            print(f"\n⚠️ Agent struggles with realistic user behavior patterns")
            return False
            
    except Exception as e:
        print(f"❌ Realistic scenario testing failed: {str(e)}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return False


async def generate_test_cases(args):
    """Generate test cases only"""
    
    print("📝 Generating Test Cases")
    print("-" * 30)
    
    generator = TestCaseGenerator()
    test_cases = generator.generate_all_test_cases()
    
    output_file = args.output_file or "tests/test_cases/generated_test_suite.json"
    generator.save_test_cases(test_cases, output_file)
    
    print(f"✅ Generated {len(test_cases)} test cases")
    print(f"📁 Saved to: {output_file}")
    
    return True


def setup_argparser():
    """Setup command line argument parser"""
    
    parser = argparse.ArgumentParser(
        description="LabAcc Copilot Agent Evaluation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run_evaluation.py --full                           # Original evaluation (response-only)
    python run_evaluation.py --comprehensive                  # New! Response + trajectory evaluation  
    python run_evaluation.py --trajectory-demo                # Demo trajectory evaluation features
    python run_evaluation.py --reproduce-failures             # Reproduce user-reported failures
    python run_evaluation.py --realistic-scenarios            # Test realistic user behavior patterns
    python run_evaluation.py --quick                          # Quick test
    python run_evaluation.py --comprehensive --category context_understanding # Test context only
    python run_evaluation.py --comprehensive --language chinese               # Test Chinese only
    python run_evaluation.py --generate-tests                 # Generate tests only
    python run_evaluation.py --comprehensive --threshold 0.8  # Require 80% pass rate
        """
    )
    
    # Main modes (mutually exclusive)
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('--full', action='store_true',
                           help='Run full evaluation (response-only, original system)')
    mode_group.add_argument('--quick', action='store_true',
                           help='Run quick test for debugging')
    mode_group.add_argument('--comprehensive', action='store_true',
                           help='Run comprehensive evaluation (response + trajectory)')
    mode_group.add_argument('--trajectory-demo', action='store_true',
                           help='Demonstrate trajectory evaluation capabilities')
    mode_group.add_argument('--reproduce-failures', action='store_true',
                           help='Reproduce user-reported failures and analyze with trajectory evaluation')
    mode_group.add_argument('--realistic-scenarios', action='store_true',
                           help='Run realistic multi-turn scenarios based on real user behavior')
    mode_group.add_argument('--generate-tests', action='store_true',
                           help='Generate test cases only')
    
    # Test filtering options
    parser.add_argument('--category', type=str,
                       choices=['context_understanding', 'file_analysis', 
                               'experiment_insights', 'protocol_optimization', 'multilingual'],
                       help='Filter tests by category')
    
    parser.add_argument('--language', type=str,
                       choices=['english', 'chinese', 'mixed'],
                       help='Filter tests by language')
    
    # Input/Output options  
    parser.add_argument('--test-file', type=str,
                       help='Load test cases from JSON file')
    
    parser.add_argument('--output-dir', type=str, default='tests/reports',
                       help='Output directory for results (default: tests/reports)')
    
    parser.add_argument('--output-file', type=str,
                       help='Output file for generated tests')
    
    # Evaluation configuration
    parser.add_argument('--evaluator-model', type=str, default=None,
                       help='LLM model for evaluation. If omitted, resolves via EVALUATOR_MODEL env or config default')
    
    parser.add_argument('--parallel', type=int, default=3,
                       help='Max parallel test execution (default: 3)')
    
    parser.add_argument('--threshold', type=float, default=0.7,
                       help='Pass rate threshold (default: 0.7)')
    
    # Regression testing
    parser.add_argument('--baseline', type=str,
                       help='Baseline results file for regression testing')
    
    # Debug options
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug output')
    
    parser.add_argument('--verbose', action='store_true',
                       help='Verbose output')
    
    return parser


async def main():
    """Main entry point"""
    
    parser = setup_argparser()
    args = parser.parse_args()
    
    # Create output directories
    Path("tests/test_cases").mkdir(exist_ok=True)
    Path("tests/reports").mkdir(exist_ok=True)
    
    try:
        if args.full:
            success = await run_full_evaluation(args)
        elif args.comprehensive:
            success = await run_comprehensive_evaluation(args)
        elif args.trajectory_demo:
            success = await run_trajectory_demo(args)
        elif args.reproduce_failures:
            success = await reproduce_user_failures(args)
        elif args.realistic_scenarios:
            success = await run_realistic_scenarios(args)
        elif args.quick:
            success = await run_quick_test(args)
        elif args.generate_tests:
            success = await generate_test_cases(args)
        else:
            print("❌ No mode selected")
            parser.print_help()
            success = False
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⏹️ Evaluation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    # Ensure we can import the agent modules
    try:
        from src.agents.react_agent import handle_message
        print("✅ Agent modules imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import agent modules: {e}")
        print("Make sure the src/ directory is in your Python path")
        sys.exit(1)
    
    # Run main
    asyncio.run(main())