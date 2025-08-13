"""
Realistic Test Scenarios Based on Real User Behavior

This addresses the critical gap identified: our test cases were too naive and didn't
cover real-world usage patterns that expose agent failures.

Real Failures Observed:
1. Agent gave generic response instead of using tools to understand actual project
2. Agent failed on multi-turn context requiring cross-experiment reasoning  
3. User expects domain-specific insights, not generic project structure

Enhanced Test Scenarios Include:
- Multi-turn conversations with context carryover
- Cross-experiment reasoning and synthesis
- Domain-specific expectations (scRNAseq lung cancer)
- Error recovery and graceful degradation
- Progressive disclosure through folder navigation
"""

import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

from .evaluator_agent import TestCase, TestCategory


@dataclass
class MultiTurnTestScenario:
    """Test scenario with multiple turns and context evolution"""
    scenario_id: str
    description: str
    turns: List[Tuple[str, str, Optional[List[str]]]]  # (query, folder, selected_files)
    expected_tool_sequence: List[str]  # Tools agent should use across turns
    expected_context_carryover: List[str]  # Key info that should carry between turns
    critical_requirements: List[str]  # Must-have behaviors
    language: str = "Chinese"


class RealisticTestScenarioGenerator:
    """Generate test scenarios based on real user behavior patterns"""
    
    def generate_project_discovery_scenario(self) -> MultiTurnTestScenario:
        """Scenario: User discovers project from top level"""
        
        return MultiTurnTestScenario(
            scenario_id="project_discovery_multilingual",
            description="User asks about project overview, expects domain-specific insights",
            turns=[
                ("这个项目是啥，给我讲讲", "/bob_projects", None),
                ("有几个实验？都在研究什么？", "/bob_projects", None), 
                ("exp_001做得怎么样？", "/bob_projects", None)
            ],
            expected_tool_sequence=[
                "scan_project",  # Turn 1: Should scan to see experiments
                "list_folder_contents",  # Turn 1: Should list bob_projects contents  
                "analyze_data",  # Turn 3: Should read exp_001 results
            ],
            expected_context_carryover=[
                "lung cancer scRNAseq research project",
                "exp_001 has immune cell bias problem", 
                "exp_002 is optimization experiment"
            ],
            critical_requirements=[
                "Must identify this as lung cancer scRNAseq project",
                "Must use scan_project to get actual experiment list",
                "Must NOT give generic project structure explanation",
                "Must mention specific findings (8% epithelial, 65% immune)"
            ],
            language="Chinese"
        )
    
    def generate_cross_experiment_optimization_scenario(self) -> MultiTurnTestScenario:
        """Scenario: User wants optimization based on previous experiment results"""
        
        return MultiTurnTestScenario(
            scenario_id="cross_experiment_optimization", 
            description="User navigates to exp_002 and asks for optimization based on exp_001",
            turns=[
                ("exp_001的主要问题是什么？", "/bob_projects/exp_001_protocol_test", None),
                ("结合exp_001结果，怎么优化exp_002？", "/bob_projects/exp_002_optimization", None),
                ("具体消化时间应该改成多少分钟？", "/bob_projects/exp_002_optimization", None)
            ],
            expected_tool_sequence=[
                "analyze_data",  # Turn 1: Read exp_001 results
                "list_folder_contents",  # Turn 2: Check exp_002 contents
                "suggest_optimization",  # Turn 2: Generate optimization recommendations
            ],
            expected_context_carryover=[
                "45min digestion caused over-digestion",
                "8.2% epithelial vs 65% immune cells",
                "high mitochondrial genes (16.8%)",
                "cold pre-digestion recommendation"
            ],
            critical_requirements=[
                "Must identify specific exp_001 problems (over-digestion, immune bias)",
                "Must recommend specific optimization (cold pre-digestion, shorter time)",
                "Must suggest specific time ranges (20-25min vs 45min)",
                "Must reference exp_001 findings when suggesting exp_002 changes"
            ],
            language="Chinese"
        )
    
    def generate_error_recovery_scenario(self) -> MultiTurnTestScenario:
        """Scenario: Test how agent handles tool failures and missing files"""
        
        return MultiTurnTestScenario(
            scenario_id="error_recovery_graceful",
            description="Test graceful error recovery when files don't exist or tools fail",
            turns=[
                ("分析这个不存在的文件", "/bob_projects/exp_001_protocol_test", ["nonexistent_file.csv"]),
                ("那exp_001里有什么文件可以分析？", "/bob_projects/exp_001_protocol_test", None),
                ("帮我分析cell_markers_analysis.csv", "/bob_projects/exp_001_protocol_test", ["cell_markers_analysis.csv"])
            ],
            expected_tool_sequence=[
                "analyze_data",  # Turn 1: Will fail, but should handle gracefully
                "list_folder_contents",  # Turn 2: Should show available files
                "analyze_data",  # Turn 3: Should succeed with real file
            ],
            expected_context_carryover=[
                "Previous file analysis failed",
                "Available files in exp_001",
                "Cell markers analysis contains important results"
            ],
            critical_requirements=[
                "Must handle file not found gracefully (not crash with generic error)",
                "Must suggest alternatives when requested file doesn't exist",
                "Must successfully analyze real file after failure",
                "Should explain what went wrong and how user can fix it"
            ],
            language="Chinese"
        )
    
    def generate_domain_expertise_scenario(self) -> MultiTurnTestScenario:
        """Scenario: Test domain-specific knowledge and scientific reasoning"""
        
        return MultiTurnTestScenario(
            scenario_id="scientific_reasoning_scrna",
            description="Test scientific understanding of scRNAseq protocol issues",
            turns=[
                ("为什么上皮细胞只有8%？", "/bob_projects/exp_001_protocol_test", None),
                ("过度消化是什么意思？", "/bob_projects/exp_001_protocol_test", None),
                ("冷消化法如何解决这个问题？", "/bob_projects/exp_001_protocol_test", None)
            ],
            expected_tool_sequence=[
                "analyze_data",  # Turn 1: Should read cell markers analysis
                "run_deep_research",  # Turn 2: Should research digestion protocols
                "suggest_optimization",  # Turn 3: Should reference optimization strategies
            ],
            expected_context_carryover=[
                "Epithelial cells are fragile compared to immune cells",
                "Over-digestion at 37°C for 45min caused cell death", 
                "Cold pre-digestion preserves fragile cells"
            ],
            critical_requirements=[
                "Must explain biological mechanism (fragile epithelial vs resistant immune)",
                "Must understand over-digestion = cell stress/death from heat/enzymes",
                "Must explain cold digestion = reduced enzymatic activity = gentler",
                "Must connect experimental observations to biological principles"
            ],
            language="Chinese"
        )
    
    def generate_progressive_disclosure_scenario(self) -> MultiTurnTestScenario:
        """Scenario: User navigates through folders building understanding"""
        
        return MultiTurnTestScenario(
            scenario_id="progressive_folder_navigation",
            description="User navigates through project structure expecting context to build",
            turns=[
                ("这个项目在研究什么？", "/bob_projects", None),
                ("exp_001做了什么？", "/bob_projects/exp_001_protocol_test", None),
                ("这里面哪个文件最重要？", "/bob_projects/exp_001_protocol_test", None),
                ("分析最重要的文件", "/bob_projects/exp_001_protocol_test", ["cell_markers_analysis.csv"]),
                ("基于这个结果，下一步应该怎么做？", "/bob_projects/exp_001_protocol_test", None)
            ],
            expected_tool_sequence=[
                "scan_project",  # Turn 1
                "list_folder_contents",  # Turn 2 
                "list_folder_contents",  # Turn 3 (already in folder)
                "analyze_data",  # Turn 4
                "suggest_optimization",  # Turn 5
            ],
            expected_context_carryover=[
                "lung cancer scRNAseq project", 
                "exp_001 tested standard protocol",
                "cell_markers_analysis.csv shows cell type distribution",
                "immune bias problem identified",
                "optimization needed for exp_002"
            ],
            critical_requirements=[
                "Context should build progressively through navigation",
                "Agent should remember project type throughout",
                "Should prioritize most informative files when asked",
                "Should connect current findings to next steps logically"
            ],
            language="Chinese"
        )
    
    def generate_all_realistic_scenarios(self) -> List[MultiTurnTestScenario]:
        """Generate all realistic test scenarios"""
        
        return [
            self.generate_project_discovery_scenario(),
            self.generate_cross_experiment_optimization_scenario(), 
            self.generate_error_recovery_scenario(),
            self.generate_domain_expertise_scenario(),
            self.generate_progressive_disclosure_scenario()
        ]
    
    def convert_to_test_cases(self, scenarios: List[MultiTurnTestScenario]) -> List[TestCase]:
        """Convert multi-turn scenarios to individual test cases for existing framework"""
        
        test_cases = []
        
        for scenario in scenarios:
            for turn_idx, (query, folder, selected_files) in enumerate(scenario.turns):
                # Create context from previous turns
                context_info = ""
                if turn_idx > 0:
                    prev_context = scenario.expected_context_carryover[:turn_idx]
                    context_info = f"Previous context: {'; '.join(prev_context)}"
                
                test_case = TestCase(
                    id=f"{scenario.scenario_id}_turn_{turn_idx + 1}",
                    category=TestCategory.EXPERIMENT_INSIGHTS,  # Most realistic scenarios are about insights
                    user_query=query,
                    language=scenario.language,
                    current_folder=folder,
                    selected_files=selected_files,
                    expected_content=f"Domain-specific response about lung cancer scRNAseq research. {context_info}",
                    expected_insights=scenario.critical_requirements,
                    ground_truth={
                        "scenario_description": scenario.description,
                        "expected_tools": scenario.expected_tool_sequence,
                        "context_carryover": scenario.expected_context_carryover,
                        "critical_requirements": scenario.critical_requirements,
                        "turn_index": turn_idx,
                        "total_turns": len(scenario.turns)
                    }
                )
                
                test_cases.append(test_case)
        
        return test_cases
    
    def save_realistic_scenarios(self, output_file: str):
        """Save realistic scenarios to JSON for evaluation"""
        
        scenarios = self.generate_all_realistic_scenarios()
        test_cases = self.convert_to_test_cases(scenarios)
        
        # Save scenarios
        scenario_data = {
            "metadata": {
                "description": "Realistic multi-turn test scenarios based on actual user behavior",
                "total_scenarios": len(scenarios),
                "total_test_cases": len(test_cases),
                "languages": list(set(s.language for s in scenarios)),
                "key_improvements": [
                    "Multi-turn context carryover",
                    "Cross-experiment reasoning", 
                    "Domain-specific expectations",
                    "Error recovery testing",
                    "Progressive disclosure patterns"
                ]
            },
            "scenarios": [
                {
                    "scenario_id": s.scenario_id,
                    "description": s.description,
                    "turns": s.turns,
                    "expected_tool_sequence": s.expected_tool_sequence,
                    "expected_context_carryover": s.expected_context_carryover,
                    "critical_requirements": s.critical_requirements,
                    "language": s.language
                }
                for s in scenarios
            ]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(scenario_data, f, indent=2, ensure_ascii=False)
        
        print(f"📁 Saved {len(scenarios)} realistic scenarios ({len(test_cases)} test cases) to {output_file}")
        
        return test_cases


if __name__ == "__main__":
    # Generate realistic scenarios
    generator = RealisticTestScenarioGenerator()
    
    # Save scenarios for evaluation
    output_dir = Path("tests/test_cases")
    output_dir.mkdir(exist_ok=True)
    
    test_cases = generator.save_realistic_scenarios(
        str(output_dir / "realistic_scenarios.json")
    )
    
    print(f"\n🎯 REALISTIC SCENARIO COVERAGE:")
    print(f"=" * 50)
    
    scenarios = generator.generate_all_realistic_scenarios()
    for scenario in scenarios:
        print(f"\n📋 {scenario.scenario_id}:")
        print(f"   Description: {scenario.description}")
        print(f"   Turns: {len(scenario.turns)}")
        print(f"   Language: {scenario.language}")
        print(f"   Key Requirements: {len(scenario.critical_requirements)}")
        
        # Show first turn as example
        first_query, first_folder, first_files = scenario.turns[0]
        print(f"   Example: '{first_query}' (in {first_folder})")
    
    print(f"\n🚀 These scenarios will catch:")
    print(f"   ✅ Tool selection failures (generic responses without using tools)")
    print(f"   ✅ Context carryover problems (forgetting previous conversation)")
    print(f"   ✅ Domain knowledge gaps (generic vs specific scientific insights)")
    print(f"   ✅ Error recovery issues (crashes vs graceful handling)")
    print(f"   ✅ Cross-experiment reasoning failures")
    print(f"\n📊 Ready to integrate with trajectory evaluation system!")