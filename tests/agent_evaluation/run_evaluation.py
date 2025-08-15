#!/usr/bin/env python3
"""
Multi-User Agent Evaluation CLI

Main command-line interface for running agent evaluations with the new multi-user,
project-based architecture. Supports both compatibility mode for legacy tests
and native multi-user testing.

Usage:
    python -m tests.agent_evaluation.run_evaluation [options]
    
Examples:
    # Run all tests with compatibility mode
    python -m tests.agent_evaluation.run_evaluation --compatibility
    
    # Run native multi-user tests only  
    python -m tests.agent_evaluation.run_evaluation --native
    
    # Run specific test categories
    python -m tests.agent_evaluation.run_evaluation --categories project_isolation,session_management
    
    # Generate and run new multi-user test suite
    python -m tests.agent_evaluation.run_evaluation --generate-multiuser --save-tests tests/test_cases/multiuser_suite.json
    
    # Custom evaluator model and parallel settings
    python -m tests.agent_evaluation.run_evaluation --evaluator-model claude-3-haiku --max-parallel 5
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from .multiuser_test_runner import MultiUserTestRunner, MultiUserTestCase
from .multiuser_test_cases import MultiUserTestGenerator, MultiUserTestCategory, load_legacy_tests_as_multiuser
from .evaluator_agent import TestCase
from .test_generator import TestCaseGenerator


class EvaluationCLI:
    """Command-line interface for multi-user agent evaluation"""
    
    def __init__(self):
        self.parser = self._create_parser()
        
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create command-line argument parser"""
        parser = argparse.ArgumentParser(
            description="Multi-User Agent Evaluation CLI",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=__doc__
        )
        
        # Test mode selection
        mode_group = parser.add_mutually_exclusive_group()
        mode_group.add_argument(
            "--compatibility", 
            action="store_true",
            help="Run tests in compatibility mode (legacy test format)"
        )
        mode_group.add_argument(
            "--native",
            action="store_true", 
            help="Run tests in native multi-user mode only"
        )
        mode_group.add_argument(
            "--mixed",
            action="store_true",
            default=True,
            help="Run both compatibility and native tests (default)"
        )
        
        # Test case sources
        parser.add_argument(
            "--test-file",
            type=str,
            help="JSON file containing test cases to run"
        )
        parser.add_argument(
            "--generate-legacy",
            action="store_true",
            help="Generate and run legacy test cases"
        )
        parser.add_argument(
            "--generate-multiuser", 
            action="store_true",
            help="Generate and run new multi-user test cases"
        )
        
        # Test filtering
        parser.add_argument(
            "--categories",
            type=str,
            help="Comma-separated list of test categories to run"
        )
        parser.add_argument(
            "--languages",
            type=str,
            help="Comma-separated list of languages to test (e.g., English,Chinese)"
        )
        parser.add_argument(
            "--test-ids",
            type=str,
            help="Comma-separated list of specific test IDs to run"
        )
        
        # Execution settings
        parser.add_argument(
            "--max-parallel",
            type=int,
            default=3,
            help="Maximum number of parallel test executions (default: 3)"
        )
        parser.add_argument(
            "--evaluator-model",
            type=str,
            help="LLM model to use for evaluation (default: from config)"
        )
        parser.add_argument(
            "--timeout",
            type=int,
            default=300,
            help="Timeout in seconds for individual tests (default: 300)"
        )
        
        # Output settings
        parser.add_argument(
            "--output-dir",
            type=str, 
            default="tests/reports",
            help="Output directory for results (default: tests/reports)"
        )
        parser.add_argument(
            "--save-tests",
            type=str,
            help="Save generated test cases to JSON file"
        )
        parser.add_argument(
            "--quiet",
            action="store_true",
            help="Reduce output verbosity"
        )
        parser.add_argument(
            "--detailed",
            action="store_true", 
            help="Show detailed test results and trajectories"
        )
        
        # Feature toggles
        parser.add_argument(
            "--no-restore-backup",
            action="store_true",
            help="Skip restoring bob_projects from backup"
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what tests would be run without executing them"
        )
        
        return parser
    
    async def run(self, args: Optional[List[str]] = None) -> int:
        """Main CLI entry point"""
        parsed_args = self.parser.parse_args(args)
        
        try:
            if parsed_args.dry_run:
                return await self._dry_run(parsed_args)
            else:
                return await self._execute_evaluation(parsed_args)
        except KeyboardInterrupt:
            print("\n⚠️ Evaluation interrupted by user")
            return 1
        except Exception as e:
            print(f"❌ Evaluation failed: {e}")
            if parsed_args.detailed:
                import traceback
                traceback.print_exc()
            return 1
    
    async def _dry_run(self, args) -> int:
        """Show what tests would be run without executing"""
        print("🔍 DRY RUN - Showing evaluation plan")
        print("=" * 50)
        
        # Load test cases
        test_cases = await self._load_test_cases(args)
        
        # Group by mode
        compatibility_tests = []
        native_tests = []
        
        for tc in test_cases:
            if isinstance(tc, MultiUserTestCase):
                native_tests.append(tc)
            else:
                compatibility_tests.append(tc)
        
        print(f"📊 Test Summary:")
        print(f"  Total Tests: {len(test_cases)}")
        print(f"  Compatibility Mode Tests: {len(compatibility_tests)}")
        print(f"  Native Multi-User Tests: {len(native_tests)}")
        print(f"  Max Parallel: {args.max_parallel}")
        print(f"  Evaluator Model: {args.evaluator_model or 'default'}")
        
        if args.categories:
            categories = args.categories.split(',')
            print(f"  Filtered Categories: {categories}")
        
        if compatibility_tests:
            print(f"\n🔄 Compatibility Tests:")
            for tc in compatibility_tests[:5]:  # Show first 5
                print(f"  - {tc.id}: {tc.user_query[:50]}...")
            if len(compatibility_tests) > 5:
                print(f"  ... and {len(compatibility_tests) - 5} more")
        
        if native_tests:
            print(f"\n🏗️ Native Multi-User Tests:")
            for tc in native_tests[:5]:  # Show first 5
                project = tc.project_context.project_id if tc.project_context else "none"
                print(f"  - {tc.id} [{project}]: {tc.user_query[:50]}...")
            if len(native_tests) > 5:
                print(f"  ... and {len(native_tests) - 5} more")
        
        print(f"\n💾 Output Directory: {args.output_dir}")
        print("=" * 50)
        print("Use --no-dry-run to execute the evaluation")
        
        return 0
    
    async def _execute_evaluation(self, args) -> int:
        """Execute the evaluation with given parameters"""
        
        if not args.quiet:
            print("🚀 Multi-User Agent Evaluation")
            print("=" * 50)
        
        # Setup test runner
        runner = MultiUserTestRunner(
            evaluator_model=args.evaluator_model,
            max_parallel=args.max_parallel
        )
        
        # Configure compatibility mode
        if args.compatibility:
            runner.set_compatibility_mode(True)
            if not args.quiet:
                print("🔄 Compatibility mode: ENABLED")
        elif args.native:
            runner.set_compatibility_mode(False)
            if not args.quiet:
                print("🏗️ Native mode: ENABLED")
        else:
            # Mixed mode (default)
            if not args.quiet:
                print("🔀 Mixed mode: ENABLED (compatibility + native)")
        
        # Load test cases
        test_cases = await self._load_test_cases(args)
        
        if not test_cases:
            print("❌ No test cases found to execute")
            return 1
        
        if not args.quiet:
            print(f"📊 Running {len(test_cases)} test cases...")
        
        # Save test cases if requested
        if args.save_tests:
            await self._save_test_cases(test_cases, args.save_tests)
        
        # Run evaluation
        try:
            summary = await runner.run_comprehensive_evaluation(
                test_cases=test_cases,
                use_compatibility=args.compatibility if args.compatibility or args.native else None
            )
            
            # Save results
            runner.save_results(summary, f"{args.output_dir}/evaluation_summary.json")
            
            # Determine return code based on results
            if summary.overall_pass_rate >= 0.8:
                if not args.quiet:
                    print("🎉 Evaluation PASSED - Agent ready for production!")
                return 0
            elif summary.overall_pass_rate >= 0.7:
                if not args.quiet:
                    print("⚠️ Evaluation ACCEPTABLE - Minor improvements needed")
                return 0
            else:
                if not args.quiet:
                    print("❌ Evaluation FAILED - Significant improvements needed")
                return 1
                
        except Exception as e:
            print(f"❌ Evaluation execution failed: {e}")
            return 1
    
    async def _load_test_cases(self, args) -> List[TestCase]:
        """Load test cases based on arguments"""
        test_cases = []
        
        # Load from file if specified
        if args.test_file:
            test_cases.extend(await self._load_from_file(args.test_file))
        
        # Generate legacy tests if requested
        if args.generate_legacy:
            legacy_generator = TestCaseGenerator()
            legacy_tests = legacy_generator.generate_all_test_cases()
            test_cases.extend(legacy_tests)
        
        # Generate multi-user tests if requested
        if args.generate_multiuser:
            mu_generator = MultiUserTestGenerator()
            mu_tests = mu_generator.generate_all_multiuser_tests()
            test_cases.extend(mu_tests)
        
        # If no specific source specified, generate default test suite
        if not any([args.test_file, args.generate_legacy, args.generate_multiuser]):
            # Mixed test suite: legacy + multi-user
            legacy_generator = TestCaseGenerator()
            mu_generator = MultiUserTestGenerator()
            
            legacy_tests = legacy_generator.generate_all_test_cases()
            mu_tests = mu_generator.generate_all_multiuser_tests()
            
            test_cases.extend(legacy_tests)
            test_cases.extend(mu_tests)
        
        # Apply filters
        test_cases = self._apply_filters(test_cases, args)
        
        return test_cases
    
    async def _load_from_file(self, file_path: str) -> List[TestCase]:
        """Load test cases from JSON file"""
        try:
            # Try to load as multi-user format first
            mu_tests = MultiUserTestGenerator.load_test_cases(file_path)
            return mu_tests
        except:
            try:
                # Fallback to legacy format
                legacy_tests = load_legacy_tests_as_multiuser(file_path)
                return legacy_tests
            except Exception as e:
                print(f"⚠️ Failed to load test file {file_path}: {e}")
                return []
    
    def _apply_filters(self, test_cases: List[TestCase], args) -> List[TestCase]:
        """Apply filters to test case list"""
        filtered_cases = test_cases
        
        # Filter by categories
        if args.categories:
            category_filter = [cat.strip() for cat in args.categories.split(',')]
            filtered_cases = [
                tc for tc in filtered_cases 
                if any(cat in tc.category.value for cat in category_filter)
            ]
        
        # Filter by languages
        if args.languages:
            language_filter = [lang.strip() for lang in args.languages.split(',')]
            filtered_cases = [
                tc for tc in filtered_cases
                if tc.language in language_filter
            ]
        
        # Filter by test IDs
        if args.test_ids:
            id_filter = [tid.strip() for tid in args.test_ids.split(',')]
            filtered_cases = [
                tc for tc in filtered_cases
                if tc.id in id_filter
            ]
        
        return filtered_cases
    
    async def _save_test_cases(self, test_cases: List[TestCase], output_path: str):
        """Save test cases to JSON file"""
        try:
            # Convert legacy test cases to multi-user format for saving
            mu_test_cases = []
            for tc in test_cases:
                if isinstance(tc, MultiUserTestCase):
                    mu_test_cases.append(tc)
                else:
                    # Convert legacy to multi-user
                    mu_tc = MultiUserTestCase.from_legacy_test_case(tc)
                    mu_test_cases.append(mu_tc)
            
            # Use the multi-user generator to save
            generator = MultiUserTestGenerator()
            generator.save_test_cases(mu_test_cases, output_path)
            
            print(f"💾 Test cases saved to {output_path}")
            
        except Exception as e:
            print(f"⚠️ Failed to save test cases: {e}")


# Convenience functions for direct use
async def quick_evaluation(
    compatibility_mode: bool = True,
    max_parallel: int = 3,
    categories: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Quick evaluation for programmatic use"""
    
    runner = MultiUserTestRunner(max_parallel=max_parallel)
    runner.set_compatibility_mode(compatibility_mode)
    
    # Generate test cases
    if compatibility_mode:
        generator = TestCaseGenerator() 
        test_cases = generator.generate_all_test_cases()
    else:
        generator = MultiUserTestGenerator()
        test_cases = generator.generate_all_multiuser_tests()
    
    # Filter by categories if specified
    if categories:
        test_cases = [
            tc for tc in test_cases
            if any(cat in tc.category.value for cat in categories)
        ]
    
    # Run evaluation
    summary = await runner.run_comprehensive_evaluation(test_cases)
    
    return {
        "summary": summary,
        "passed": summary.overall_pass_rate >= 0.7,
        "score": summary.overall_pass_rate
    }


async def regression_test(
    baseline_results_path: str,
    tolerance: float = 0.05
) -> Dict[str, Any]:
    """Run regression test against baseline"""
    
    # Load baseline
    with open(baseline_results_path, 'r') as f:
        baseline = json.load(f)
    
    baseline_pass_rate = baseline.get("overall_pass_rate", 0.0)
    
    # Run current evaluation
    current = await quick_evaluation()
    current_pass_rate = current["score"]
    
    # Check regression
    regression_detected = current_pass_rate < baseline_pass_rate - tolerance
    
    return {
        "regression_detected": regression_detected,
        "baseline_pass_rate": baseline_pass_rate,
        "current_pass_rate": current_pass_rate,
        "difference": current_pass_rate - baseline_pass_rate,
        "tolerance": tolerance
    }


def main():
    """Main CLI entry point"""
    cli = EvaluationCLI()
    exit_code = asyncio.run(cli.run())
    sys.exit(exit_code)


if __name__ == "__main__":
    main()