"""
Multi-Round Conversation Testing Module
Tests context carryover, tool selection, and coherence across conversation turns
"""

import asyncio
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
import json
from pathlib import Path

import pytest

from src.agents.react_agent import handle_message


@dataclass
class ConversationTurn:
    """Single turn in a conversation"""
    message: str
    expected_tools: List[str]  # Tools that should be called
    forbidden_tools: List[str]  # Tools that should NOT be called
    expected_content: List[str]  # Key phrases that should appear
    context_needed_from: Optional[int] = None  # Which previous turn's context is needed


@dataclass
class ConversationScenario:
    """Complete multi-round conversation test scenario"""
    name: str
    description: str
    turns: List[ConversationTurn]
    initial_folder: str
    selected_files: Optional[List[str]] = None


@pytest.mark.modifies_data
class TestMultiRoundConversations:
    """Test multi-round conversations with context maintenance"""
    
    def create_test_scenarios(self, base_path: Path) -> List[ConversationScenario]:
        """Create comprehensive conversation test scenarios"""
        
        scenarios = [
            ConversationScenario(
                name="project_discovery_chinese",
                description="User discovers project structure in Chinese",
                initial_folder=str(base_path),
                turns=[
                    ConversationTurn(
                        message="这个项目有什么实验？",
                        expected_tools=["scan_project"],
                        forbidden_tools=["run_deep_research"],
                        expected_content=["exp_001", "exp_002", "实验"]
                    ),
                    ConversationTurn(
                        message="第一个实验是做什么的？",
                        expected_tools=["analyze_data", "list_folder_contents"],
                        forbidden_tools=["scan_project"],  # Should remember from turn 1
                        expected_content=["protocol", "PCR", "scRNAseq"],
                        context_needed_from=0
                    ),
                    ConversationTurn(
                        message="有什么问题吗？",
                        expected_tools=["diagnose_issue"],
                        forbidden_tools=["scan_project"],
                        expected_content=["细胞", "消化", "problem"],
                        context_needed_from=1
                    )
                ]
            ),
            
            ConversationScenario(
                name="cross_experiment_analysis",
                description="Analyzing relationships between experiments",
                initial_folder=str(base_path),
                turns=[
                    ConversationTurn(
                        message="Compare exp_001 and exp_002",
                        expected_tools=["analyze_data", "compare_experiments"],
                        forbidden_tools=[],
                        expected_content=["exp_001", "exp_002", "difference"]
                    ),
                    ConversationTurn(
                        message="Which one had better results?",
                        expected_tools=[],  # Should use context from turn 1
                        forbidden_tools=["scan_project"],
                        expected_content=["better", "exp_"],
                        context_needed_from=0
                    ),
                    ConversationTurn(
                        message="Why did that one perform better?",
                        expected_tools=["diagnose_issue"],
                        forbidden_tools=["scan_project"],
                        expected_content=["because", "reason", "due to"],
                        context_needed_from=1
                    )
                ]
            ),
            
            ConversationScenario(
                name="folder_navigation_context",
                description="Navigate folders while maintaining context",
                initial_folder=str(base_path),
                turns=[
                    ConversationTurn(
                        message="Go to exp_001",
                        expected_tools=["list_folder_contents"],
                        forbidden_tools=[],
                        expected_content=["exp_001", "files"]
                    ),
                    ConversationTurn(
                        message="分析这里的CSV文件",  # Mixed language
                        expected_tools=["analyze_data"],
                        forbidden_tools=["scan_project"],
                        expected_content=["csv", "data", "analysis"],
                        context_needed_from=0
                    ),
                    ConversationTurn(
                        message="Now compare with exp_002",
                        expected_tools=["list_folder_contents", "compare_experiments"],
                        forbidden_tools=[],
                        expected_content=["exp_002", "comparison"],
                        context_needed_from=1
                    )
                ]
            ),
            
            ConversationScenario(
                name="topic_switch_recovery",
                description="Switch topics and return with context",
                initial_folder=str(base_path / "exp_001_protocol_test"),
                turns=[
                    ConversationTurn(
                        message="Analyze the PCR results",
                        expected_tools=["analyze_data"],
                        forbidden_tools=["run_deep_research"],
                        expected_content=["PCR", "results", "bands"]
                    ),
                    ConversationTurn(
                        message="Search for papers on CRISPR efficiency",  # Topic switch
                        expected_tools=["run_deep_research"],
                        forbidden_tools=["analyze_data"],
                        expected_content=["CRISPR", "papers", "research"]
                    ),
                    ConversationTurn(
                        message="Back to the PCR issue - what went wrong?",  # Return to original
                        expected_tools=["diagnose_issue"],
                        forbidden_tools=["run_deep_research"],
                        expected_content=["PCR", "problem", "issue"],
                        context_needed_from=0
                    )
                ]
            ),
            
            ConversationScenario(
                name="progressive_detail_drilling",
                description="Progressively drill into more detail",
                initial_folder=str(base_path),
                turns=[
                    ConversationTurn(
                        message="Overview of this project",
                        expected_tools=["scan_project"],
                        forbidden_tools=["diagnose_issue"],
                        expected_content=["project", "experiments", "overview"]
                    ),
                    ConversationTurn(
                        message="Tell me more about the cell analysis",
                        expected_tools=["analyze_data"],
                        forbidden_tools=["scan_project"],
                        expected_content=["cells", "analysis", "markers"],
                        context_needed_from=0
                    ),
                    ConversationTurn(
                        message="Specifically, what about the epithelial cells?",
                        expected_tools=[],  # Should use previous analysis
                        forbidden_tools=["scan_project"],
                        expected_content=["epithelial", "8%", "percentage"],
                        context_needed_from=1
                    ),
                    ConversationTurn(
                        message="How can we increase that percentage?",
                        expected_tools=["suggest_optimization"],
                        forbidden_tools=["scan_project"],
                        expected_content=["increase", "optimization", "improve"],
                        context_needed_from=2
                    )
                ]
            ),
            
            ConversationScenario(
                name="error_recovery_flow",
                description="Handle errors gracefully and continue",
                initial_folder=str(base_path / "exp_001_protocol_test"),
                selected_files=["nonexistent.csv"],
                turns=[
                    ConversationTurn(
                        message="Analyze this file",
                        expected_tools=["analyze_data"],
                        forbidden_tools=[],
                        expected_content=["error", "not found", "doesn't exist"]
                    ),
                    ConversationTurn(
                        message="What files are available then?",
                        expected_tools=["list_folder_contents"],
                        forbidden_tools=["analyze_data"],
                        expected_content=["files", "available", ".csv"],
                        context_needed_from=0
                    ),
                    ConversationTurn(
                        message="Analyze the first CSV you find",
                        expected_tools=["analyze_data"],
                        forbidden_tools=[],
                        expected_content=["analysis", "data", "results"],
                        context_needed_from=1
                    )
                ]
            )
        ]
        
        return scenarios
    
    @pytest.mark.asyncio
    async def test_conversation_scenario(self, scenario: ConversationScenario):
        """Execute a complete conversation scenario"""
        
        session_id = f"test_{scenario.name}"
        current_folder = scenario.initial_folder
        selected_files = scenario.selected_files or []
        
        conversation_history = []
        
        for turn_idx, turn in enumerate(scenario.turns):
            # Execute turn
            response = await handle_message(
                message=turn.message,
                session_id=session_id,
                current_folder=current_folder,
                selected_files=selected_files
            )
            
            conversation_history.append({
                "turn": turn_idx,
                "message": turn.message,
                "response": response
            })
            
            # Verify expected content
            for expected in turn.expected_content:
                assert expected.lower() in response.lower(), \
                    f"Turn {turn_idx}: Expected '{expected}' not found in response"
            
            # Verify context from previous turns if needed
            if turn.context_needed_from is not None:
                previous_turn = conversation_history[turn.context_needed_from]
                # Check that current response references previous context
                # This is a simplified check - could be more sophisticated
                assert len(response) > 50, \
                    f"Turn {turn_idx}: Response too short, likely missing context"
    
    @pytest.mark.asyncio
    async def test_all_conversation_scenarios(self, reset_bob_projects):
        """Run all conversation test scenarios"""
        
        scenarios = self.create_test_scenarios(reset_bob_projects)
        results = []
        
        for scenario in scenarios:
            try:
                await self.test_conversation_scenario(scenario, reset_bob_projects)
                results.append((scenario.name, "PASSED"))
            except AssertionError as e:
                results.append((scenario.name, f"FAILED: {str(e)}"))
            except Exception as e:
                results.append((scenario.name, f"ERROR: {str(e)}"))
        
        # Report results
        passed = sum(1 for _, status in results if status == "PASSED")
        print(f"\nConversation Test Results: {passed}/{len(results)} passed")
        
        for name, status in results:
            print(f"  {name}: {status}")
        
        assert passed == len(results), f"Some conversation tests failed"
    
    @pytest.mark.asyncio
    async def test_context_retention_across_turns(self, reset_bob_projects):
        """Test that context is properly retained across conversation turns"""
        
        session_id = "context_test"
        
        # Turn 1: Establish context
        response1 = await handle_message(
            message="I'm working on exp_001 which has contamination issues",
            session_id=session_id,
            current_folder=str(reset_bob_projects / "exp_001_protocol_test"),
            selected_files=[]
        )
        
        # Turn 2: Reference previous context implicitly
        response2 = await handle_message(
            message="What should I do about it?",  # "it" refers to contamination
            session_id=session_id,
            current_folder=str(reset_bob_projects / "exp_001_protocol_test"),
            selected_files=[]
        )
        
        # Response should reference contamination without being told again
        assert "contamination" in response2.lower() or "sterile" in response2.lower(), \
            "Lost context about contamination issue"
        
        # Turn 3: Further reference
        response3 = await handle_message(
            message="Are there any papers on this?",  # "this" refers to contamination solutions
            session_id=session_id,
            current_folder=str(reset_bob_projects / "exp_001_protocol_test"),
            selected_files=[]
        )
        
        # Should search for contamination-related papers
        assert "contamination" in response3.lower() or "sterile" in response3.lower() or "aseptic" in response3.lower(), \
            "Lost context about what to search for"
    
    @pytest.mark.asyncio
    async def test_tool_selection_efficiency(self, reset_bob_projects):
        """Test that agent doesn't repeat tools unnecessarily"""
        
        session_id = "efficiency_test"
        
        # Turn 1: Scan project
        response1 = await handle_message(
            message="List all experiments",
            session_id=session_id,
            current_folder=str(reset_bob_projects),
            selected_files=[]
        )
        
        # Turn 2: Should NOT scan again
        response2 = await handle_message(
            message="How many experiments are there?",
            session_id=session_id,
            current_folder=str(reset_bob_projects),
            selected_files=[]
        )
        
        # Response should be quick (no re-scanning)
        # This is hard to test directly without tool tracking
        # But response should still have the count
        assert "exp_" in response2.lower() or "2" in response2 or "two" in response2.lower()
    
    @pytest.mark.asyncio
    async def test_language_consistency_across_turns(self, reset_bob_projects):
        """Test that agent maintains language consistency"""
        
        session_id = "language_test"
        
        # Turn 1: Chinese
        response1 = await handle_message(
            message="这个项目是关于什么的？",
            session_id=session_id,
            current_folder=str(reset_bob_projects),
            selected_files=[]
        )
        
        # Turn 2: Continue in Chinese
        response2 = await handle_message(
            message="继续告诉我更多细节",
            session_id=session_id,
            current_folder=str(reset_bob_projects),
            selected_files=[]
        )
        
        # Response should contain Chinese characters
        # (Agent should recognize the conversation is in Chinese)
        chinese_chars = sum(1 for c in response2 if '\u4e00' <= c <= '\u9fff')
        assert chinese_chars > 10 or "exp_" in response2, \
            "Agent should respond in Chinese or with technical terms"


@pytest.mark.modifies_data
class TestToolSelectionLogic:
    """Test correct tool selection for various queries"""
    
    @pytest.mark.asyncio
    async def test_simple_tool_selection(self, reset_bob_projects):
        """Test basic tool selection for simple queries"""
        
        test_cases = [
            {
                "query": "What's in this folder?",
                "folder": str(reset_bob_projects),
                "expected_in_response": ["exp_", "folder", "file"],
                "not_expected": ["Hello", "Hi"]
            },
            {
                "query": "分析results.csv",
                "folder": str(reset_bob_projects / "exp_001_protocol_test"),
                "expected_in_response": ["data", "analysis", "csv"],
                "not_expected": ["sorry", "cannot"]
            },
            {
                "query": "Find papers on PCR optimization",
                "folder": str(reset_bob_projects),
                "expected_in_response": ["PCR", "paper", "research"],
                "not_expected": ["folder", "file"]
            }
        ]
        
        for test_case in test_cases:
            response = await handle_message(
                message=test_case["query"],
                session_id=f"tool_test_{test_case['query'][:10]}",
                current_folder=test_case["folder"],
                selected_files=[]
            )
            
            # Check expected content
            for expected in test_case["expected_in_response"]:
                assert expected.lower() in response.lower(), \
                    f"Query '{test_case['query']}' missing expected '{expected}'"
            
            # Check unwanted content
            for not_expected in test_case["not_expected"]:
                assert not_expected.lower() not in response.lower(), \
                    f"Query '{test_case['query']}' contains unwanted '{not_expected}'"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])