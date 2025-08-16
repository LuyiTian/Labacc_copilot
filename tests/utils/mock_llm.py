"""
Mock LLM for testing - returns predictable responses.

This replaces the actual LLM during tests for:
1. Speed (no API calls)
2. Predictability (same output every time)
3. Cost (no token usage)
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class MockMessage:
    """Mock message object that mimics LangChain message structure."""
    content: str
    
    def __str__(self):
        return self.content


class MockLLM:
    """Mock LLM that returns predictable responses for testing."""
    
    def __init__(self):
        # Load mock responses
        fixtures_path = Path(__file__).parent.parent / "fixtures" / "mock_responses.json"
        with open(fixtures_path, 'r') as f:
            self.responses = json.load(f)
        
        # Track calls for assertions
        self.call_history = []
    
    def invoke(self, messages):
        """Synchronous invoke for compatibility."""
        if isinstance(messages, list):
            prompt = messages[0].content if hasattr(messages[0], 'content') else str(messages[0])
        else:
            prompt = str(messages)
        
        self.call_history.append(prompt)
        
        # Return appropriate mock response based on prompt content
        response = self._get_response_for_prompt(prompt)
        return MockMessage(content=response)
    
    async def ainvoke(self, prompt):
        """Async invoke for compatibility."""
        return self.invoke(prompt)
    
    def _get_response_for_prompt(self, prompt: str) -> str:
        """Determine which mock response to return based on prompt content."""
        
        # File analysis requests
        if "analyze" in prompt.lower() and "file" in prompt.lower():
            if "context" in prompt.lower() or "README" in prompt:
                return self.responses["file_analysis"]["with_context"]
            elif "error" in prompt.lower() or "corrupt" in prompt.lower():
                return self.responses["file_analysis"]["error_case"]
            else:
                return self.responses["file_analysis"]["default"]
        
        # Memory update requests
        elif "update" in prompt.lower() and "readme" in prompt.lower():
            # Extract details from prompt if needed
            template = self.responses["memory_update"]["default"]
            return template.format(
                experiment_id="test_experiment",
                existing_content="Existing README content",
                date=datetime.now().strftime('%Y-%m-%d'),
                filename="test_file.pdf",
                analysis="Test analysis",
                user_response="Test user response"
            )
        
        # Tool responses
        elif "read" in prompt.lower():
            return self.responses["tool_responses"]["read_file"].format(
                content="Test file content"
            )
        elif "scan" in prompt.lower():
            return self.responses["tool_responses"]["scan_project"].format(
                count=3
            )
        elif "list" in prompt.lower():
            return self.responses["tool_responses"]["list_folder_contents"].format(
                files="file1.txt, file2.csv, file3.pdf"
            )
        
        # Default response
        else:
            return "Mock LLM response for: " + prompt[:50]
    
    def reset(self):
        """Reset call history for clean test state."""
        self.call_history = []
    
    def assert_called_with(self, expected_substring: str) -> bool:
        """Assert that LLM was called with a prompt containing the substring."""
        for call in self.call_history:
            if expected_substring in call:
                return True
        return False
    
    def get_call_count(self) -> int:
        """Get the number of times the LLM was called."""
        return len(self.call_history)


class MockAgent:
    """Mock agent that uses the mock LLM."""
    
    def __init__(self, llm: Optional[MockLLM] = None):
        self.llm = llm or MockLLM()
        self.tool_calls = []
    
    async def astream_events(self, input_data, config=None, version=None):
        """Mock event stream for agent execution."""
        # Simulate tool calls
        yield {
            "event": "on_tool_start",
            "name": "read_file",
            "data": {"input": {"file_path": "test.pdf"}}
        }
        yield {
            "event": "on_tool_end",
            "name": "read_file",
            "data": {"output": "File content"}
        }
        
        # Simulate chat response
        response = self.llm.invoke([input_data["messages"][0]])
        yield {
            "event": "on_chat_model_end",
            "data": {"output": response}
        }
    
    def invoke(self, input_data):
        """Synchronous invoke."""
        messages = input_data.get("messages", [])
        if messages:
            return {"messages": [self.llm.invoke(messages)]}
        return {"messages": [MockMessage("No input provided")]}


def get_mock_llm() -> MockLLM:
    """Factory function to get a mock LLM instance."""
    return MockLLM()


def patch_llm_for_tests():
    """Monkey-patch the LLM module to use mocks during testing."""
    import src.components.llm as llm_module
    
    mock_llm = MockLLM()
    
    # Replace the get_llm_instance function
    original_get_llm = llm_module.get_llm_instance
    
    def mock_get_llm_instance(*args, **kwargs):
        return mock_llm
    
    llm_module.get_llm_instance = mock_get_llm_instance
    
    # Return the mock and original for cleanup
    return mock_llm, original_get_llm


def unpatch_llm(original_get_llm):
    """Restore the original LLM function."""
    import src.components.llm as llm_module
    llm_module.get_llm_instance = original_get_llm