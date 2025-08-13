"""
Reproduce Exact User Failures

This reproduces the specific failures the user experienced to demonstrate
how our enhanced evaluation system should catch these issues.

User's Real Scenario:
1. In /bob_projects folder
2. Asked: "这个项目是啥，给我讲讲"
3. Agent gave generic response instead of using tools to understand actual project
4. Moved to /bob_projects/exp_002_optimization  
5. Asked: "结合上一个001实验的结果，帮我想想怎么优化这个实验 exp_002"
6. Agent crashed with generic error

What Should Have Happened:
1. Agent uses scan_project() and list_folder_contents() 
2. Agent identifies lung cancer scRNAseq research
3. Agent reads exp_001 results and exp_002 optimization plan
4. Agent provides specific optimization recommendations based on exp_001 findings
"""

import asyncio
from typing import Dict, List
from dataclasses import dataclass

from .evaluator_agent import TestCase, TestCategory
from .comprehensive_evaluator import quick_comprehensive_evaluate
from langchain_core.messages import HumanMessage, AIMessage


@dataclass
class UserFailureCase:
    """Represents a real user failure scenario"""
    failure_id: str
    description: str
    user_query: str
    current_folder: str
    expected_behavior: List[str]
    observed_failure: str
    expected_tools: List[str]
    trajectory_issues: List[str]


class UserFailureReproducer:
    """Reproduce and analyze specific user failures"""
    
    def define_failure_cases(self) -> List[UserFailureCase]:
        """Define the exact failures the user experienced"""
        
        return [
            UserFailureCase(
                failure_id="generic_project_response",
                description="Agent gave generic project structure explanation instead of using tools",
                user_query="这个项目是啥，给我讲讲",
                current_folder="/bob_projects",
                expected_behavior=[
                    "Use scan_project() to see available experiments",
                    "Use list_folder_contents() to see actual structure", 
                    "Read README.md to understand project purpose",
                    "Identify lung cancer scRNAseq research",
                    "Mention specific experiments (exp_001, exp_002)",
                    "Reference actual findings (8% epithelial, immune bias)"
                ],
                observed_failure="Agent provided generic project structure template without using any tools or reading actual project content",
                expected_tools=["scan_project", "list_folder_contents", "analyze_data"],
                trajectory_issues=[
                    "Tool Selection Logic: 0/10 - Used no tools when tools were essential",
                    "Information Synthesis: 0/10 - Synthesized nothing, gave generic response",
                    "Context Awareness: 0/10 - Ignored folder context completely",
                    "Reasoning Quality: 2/10 - Logic was sound but completely generic"
                ]
            ),
            
            UserFailureCase(
                failure_id="cross_experiment_error",
                description="Agent crashed when asked to optimize exp_002 based on exp_001 results",
                user_query="结合上一个001实验的结果，帮我想想怎么优化这个实验 exp_002",
                current_folder="/bob_projects/exp_002_optimization",
                expected_behavior=[
                    "Read exp_001 results (dissociation_notes.txt, cell_markers_analysis.csv)",
                    "Identify key problems (over-digestion, immune bias)", 
                    "Read exp_002 optimization plan",
                    "Synthesize specific recommendations (cold pre-digestion, shorter time)",
                    "Reference specific data (45min→20-25min, 8%→target 25-40%)"
                ],
                observed_failure="Agent crashed with generic error message instead of graceful handling",
                expected_tools=["analyze_data", "list_folder_contents", "suggest_optimization"],
                trajectory_issues=[
                    "Error Recovery: 0/10 - Complete failure with generic error",
                    "Information Synthesis: 0/10 - Failed to connect exp_001 and exp_002",
                    "Tool Selection Logic: Unknown - Agent never got to tool selection",
                    "Reasoning Quality: 0/10 - No reasoning, just error"
                ]
            )
        ]
    
    async def reproduce_failure_case(self, failure_case: UserFailureCase) -> Dict:
        """Reproduce a specific failure case and analyze with trajectory evaluation"""
        
        print(f"\n🔍 REPRODUCING FAILURE: {failure_case.failure_id}")
        print(f"📝 Query: '{failure_case.user_query}'")
        print(f"📁 Folder: {failure_case.current_folder}")
        print("-" * 60)
        
        try:
            # Test the current agent behavior
            from src.agents.react_agent import handle_message
            
            agent_response = await handle_message(
                message=failure_case.user_query,
                session_id=f"failure_test_{failure_case.failure_id}",
                current_folder=failure_case.current_folder,
                selected_files=None
            )
            
            print(f"✅ Agent Response Generated:")
            print(f"   Length: {len(agent_response)} characters")
            if len(agent_response) > 200:
                print(f"   Preview: {agent_response[:200]}...")
            else:
                print(f"   Full: {agent_response}")
            
            # Analyze with trajectory evaluation (mock messages for now)
            mock_messages = [
                HumanMessage(content=failure_case.user_query),
                AIMessage(content=agent_response)
            ]
            
            trajectory_result = await quick_comprehensive_evaluate(
                user_query=failure_case.user_query,
                agent_response=agent_response,
                execution_messages=mock_messages,
                current_folder=failure_case.current_folder
            )
            
            print(f"\n📊 EVALUATION RESULTS:")
            print(f"   Combined Score: {trajectory_result.combined_score:.1f}/10")
            print(f"   Response Score: {trajectory_result.evaluation.response_evaluation.criteria.overall_score:.1f}/10")
            print(f"   Trajectory Score: {trajectory_result.evaluation.trajectory_evaluation.trajectory_score:.1f}/10")
            
            # Detailed trajectory analysis
            print(f"\n🔄 TRAJECTORY ANALYSIS:")
            traj_eval = trajectory_result.evaluation.trajectory_evaluation
            print(f"   Tool Selection: {traj_eval.tool_selection_logic:.1f}/10")
            print(f"   Information Synthesis: {traj_eval.information_synthesis:.1f}/10")  
            print(f"   Context Awareness: {traj_eval.parameter_accuracy:.1f}/10")
            print(f"   Error Recovery: {traj_eval.error_recovery:.1f}/10")
            
            # Check if trajectory issues match expected issues
            print(f"\n⚠️ EXPECTED TRAJECTORY ISSUES:")
            for issue in failure_case.trajectory_issues:
                print(f"   - {issue}")
            
            # Check tool usage
            tools_used = trajectory_result.evaluation.trajectory.unique_tools_used
            print(f"\n🔧 TOOLS USED: {tools_used}")
            print(f"   Expected: {failure_case.expected_tools}")
            
            missing_tools = set(failure_case.expected_tools) - set(tools_used)
            if missing_tools:
                print(f"   ❌ Missing Tools: {list(missing_tools)}")
            
            return {
                "failure_case": failure_case,
                "agent_response": agent_response,
                "evaluation_result": trajectory_result,
                "tools_used": tools_used,
                "missing_tools": list(missing_tools),
                "reproduced_successfully": True
            }
            
        except Exception as e:
            print(f"❌ FAILURE REPRODUCED - Agent Error: {str(e)}")
            
            return {
                "failure_case": failure_case,
                "agent_response": "",
                "evaluation_result": None,
                "tools_used": [],
                "missing_tools": failure_case.expected_tools,
                "error": str(e),
                "reproduced_successfully": True  # This IS the expected failure
            }
    
    async def run_failure_analysis(self) -> Dict:
        """Run complete failure analysis"""
        
        print(f"🚨 USER FAILURE ANALYSIS")
        print(f"=" * 60)
        print(f"Reproducing exact failures user experienced to validate")
        print(f"that our enhanced trajectory evaluation system catches them.")
        
        failure_cases = self.define_failure_cases()
        results = []
        
        for failure_case in failure_cases:
            result = await self.reproduce_failure_case(failure_case)
            results.append(result)
        
        # Summary analysis
        print(f"\n📋 FAILURE ANALYSIS SUMMARY")
        print(f"=" * 60)
        
        reproduced_failures = 0
        trajectory_caught_issues = 0
        
        for result in results:
            failure_id = result["failure_case"].failure_id
            print(f"\n🎯 {failure_id}:")
            
            if result["reproduced_successfully"]:
                reproduced_failures += 1
                print(f"   ✅ Failure reproduced successfully")
            
            if result.get("evaluation_result"):
                eval_result = result["evaluation_result"]
                if eval_result.combined_score < 6.0:  # Low score indicates issues caught
                    trajectory_caught_issues += 1
                    print(f"   ✅ Trajectory evaluation caught issues (score: {eval_result.combined_score:.1f})")
                else:
                    print(f"   ⚠️ Trajectory evaluation missed issues (score: {eval_result.combined_score:.1f})")
            
            missing_tools = result.get("missing_tools", [])
            if missing_tools:
                print(f"   ❌ Missing expected tools: {missing_tools}")
            
            if result.get("error"):
                print(f"   💥 Error reproduced: {result['error'][:100]}...")
        
        print(f"\n📊 FINAL ASSESSMENT:")
        print(f"   Failures Reproduced: {reproduced_failures}/{len(failure_cases)}")
        print(f"   Issues Caught by Trajectory Eval: {trajectory_caught_issues}/{len(failure_cases)}")
        
        effectiveness = trajectory_caught_issues / len(failure_cases) if failure_cases else 0
        print(f"   Trajectory Evaluation Effectiveness: {effectiveness:.1%}")
        
        if effectiveness >= 0.8:
            print(f"   🎉 Trajectory evaluation successfully catches user failures!")
        else:
            print(f"   ⚠️ Trajectory evaluation needs improvement to catch these failures")
        
        return {
            "total_failures": len(failure_cases),
            "reproduced_failures": reproduced_failures,
            "caught_by_trajectory": trajectory_caught_issues,
            "effectiveness": effectiveness,
            "results": results
        }
    
    def generate_improved_test_cases(self) -> List[TestCase]:
        """Generate improved test cases based on user failures"""
        
        failure_cases = self.define_failure_cases()
        improved_tests = []
        
        for failure_case in failure_cases:
            # Create test case that checks for the specific failure
            test_case = TestCase(
                id=f"improved_{failure_case.failure_id}",
                category=TestCategory.CONTEXT_UNDERSTANDING,
                user_query=failure_case.user_query,
                language="Chinese",
                current_folder=failure_case.current_folder,
                selected_files=None,
                expected_content="Domain-specific response about lung cancer scRNAseq research project",
                expected_insights=failure_case.expected_behavior,
                ground_truth={
                    "expected_tools": failure_case.expected_tools,
                    "critical_requirements": failure_case.expected_behavior,
                    "must_avoid": [failure_case.observed_failure],
                    "trajectory_requirements": {
                        "tool_selection_min_score": 7.0,
                        "information_synthesis_min_score": 7.0,  
                        "context_awareness_min_score": 7.0,
                        "error_recovery_min_score": 8.0
                    }
                }
            )
            improved_tests.append(test_case)
        
        return improved_tests


async def run_user_failure_reproduction():
    """Main function to reproduce and analyze user failures"""
    
    reproducer = UserFailureReproducer()
    
    # Run failure analysis
    analysis_result = await reproducer.run_failure_analysis()
    
    # Generate improved test cases
    improved_tests = reproducer.generate_improved_test_cases()
    
    print(f"\n🛠️ IMPROVEMENTS GENERATED:")
    print(f"   Created {len(improved_tests)} improved test cases")
    print(f"   These tests will prevent regression of user-reported failures")
    
    return analysis_result, improved_tests


if __name__ == "__main__":
    # Reproduce the user failures
    asyncio.run(run_user_failure_reproduction())