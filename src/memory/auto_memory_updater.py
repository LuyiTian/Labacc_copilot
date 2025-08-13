"""
Automatic Memory Updater - Extracts and applies memory updates from conversations
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from pathlib import Path

from src.memory.memory_tools import (
    update_file_registry,
    append_insight,
    write_memory
)
from src.components.llm import get_llm_instance
from langchain_core.messages import HumanMessage

logger = logging.getLogger(__name__)


class AutoMemoryUpdater:
    """Automatically updates README memory based on conversation content."""
    
    def __init__(self):
        self.llm = get_llm_instance()
    
    async def extract_memory_updates(
        self, 
        user_message: str, 
        agent_response: str,
        experiment_id: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """Extract memory updates from a conversation turn using LLM."""
        
        if not experiment_id:
            return []
        
        prompt = f"""Analyze this conversation and extract any information that should update the experiment README memory.

User message: {user_message}
Agent response: {agent_response}
Experiment: {experiment_id}

Extract the following types of updates:
1. FILE_CORRECTION: User corrects information about a file (e.g., "figure_b.png is western blot of condition 2, not condition 1")
2. NEW_RESULT: User mentions a new experimental result (e.g., "PCR yield was 85%")
3. PARAMETER_UPDATE: User mentions experimental parameters (e.g., "annealing temperature was 58°C")
4. INSIGHT: Important observation or conclusion (e.g., "contamination found in control")
5. STATUS_CHANGE: Experiment status update (e.g., "experiment completed", "failed due to...")

Return a JSON list of updates. Each update should have:
- type: one of the types above
- content: the specific information to update
- section: which README section to update (files/parameters/results/insights/overview)
- action: how to update (replace/append/correct)

Example response:
[
  {{
    "type": "FILE_CORRECTION",
    "content": "figure_b.png: Western blot result of condition 2 (not condition 1)",
    "section": "files",
    "action": "correct"
  }},
  {{
    "type": "NEW_RESULT",
    "content": "PCR yield: 85% (260/280 ratio: 1.8)",
    "section": "results",
    "action": "append"
  }}
]

If no updates are needed, return an empty list: []
"""
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            content = response.content
            
            # Extract JSON from response
            import json
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0]
            elif "[" in content:
                # Find the JSON array
                start = content.index("[")
                end = content.rindex("]") + 1
                json_str = content[start:end]
            else:
                return []
            
            updates = json.loads(json_str)
            return updates
            
        except Exception as e:
            logger.error(f"Failed to extract memory updates: {e}")
            return []
    
    async def apply_memory_updates(
        self,
        updates: List[Dict[str, str]],
        experiment_id: str
    ) -> int:
        """Apply the extracted updates to the README memory."""
        
        applied_count = 0
        
        for update in updates:
            try:
                update_type = update.get("type", "")
                content = update.get("content", "")
                section = update.get("section", "")
                action = update.get("action", "")
                
                if update_type == "FILE_CORRECTION":
                    # Extract file name and corrected description
                    if ":" in content:
                        file_name, description = content.split(":", 1)
                        file_name = file_name.strip()
                        description = description.strip()
                        
                        await update_file_registry.ainvoke({
                            "experiment_id": experiment_id,
                            "file_name": file_name,
                            "file_type": "Data",  # Will be determined by extension
                            "file_size": "Unknown",
                            "summary": description
                        })
                        applied_count += 1
                        logger.info(f"Corrected file info: {file_name}")
                
                elif update_type == "NEW_RESULT":
                    # Add to results section
                    await write_memory.ainvoke({
                        "experiment_id": experiment_id,
                        "section": "results",
                        "content": content
                    })
                    applied_count += 1
                    logger.info(f"Added new result: {content[:50]}...")
                
                elif update_type == "PARAMETER_UPDATE":
                    # Update parameters section
                    await write_memory.ainvoke({
                        "experiment_id": experiment_id,
                        "section": "parameters",
                        "content": content
                    })
                    applied_count += 1
                    logger.info(f"Updated parameter: {content[:50]}...")
                
                elif update_type == "INSIGHT":
                    # Add as insight
                    await append_insight.ainvoke({
                        "experiment_id": experiment_id,
                        "insight": content,
                        "source": "user_conversation"
                    })
                    applied_count += 1
                    logger.info(f"Added insight: {content[:50]}...")
                
                elif update_type == "STATUS_CHANGE":
                    # Update overview/status
                    await write_memory.ainvoke({
                        "experiment_id": experiment_id,
                        "section": "overview",
                        "content": f"Status: {content}"
                    })
                    applied_count += 1
                    logger.info(f"Updated status: {content}")
                    
            except Exception as e:
                logger.error(f"Failed to apply update {update_type}: {e}")
                continue
        
        return applied_count
    
    async def process_conversation(
        self,
        user_message: str,
        agent_response: str,
        experiment_id: Optional[str] = None
    ) -> str:
        """Process a conversation turn and apply any memory updates."""
        
        if not experiment_id or not experiment_id.startswith("exp_"):
            return "No experiment context for memory updates"
        
        # Extract updates
        updates = await self.extract_memory_updates(
            user_message, 
            agent_response,
            experiment_id
        )
        
        if not updates:
            return "No memory updates needed"
        
        # Apply updates
        applied = await self.apply_memory_updates(updates, experiment_id)
        
        return f"Applied {applied} memory updates to {experiment_id}"


# Pattern-based extraction for common cases (faster than LLM)
class QuickMemoryExtractor:
    """Quick pattern-based extraction for common memory updates."""
    
    # Patterns for common corrections
    CORRECTION_PATTERNS = [
        (r"(\w+\.\w+)\s+(?:is|shows|contains)\s+(.+?)(?:,\s*not|instead of)\s+(.+)", "file_correction"),
        (r"(?:actually|correction:|fix:)\s*(.+)", "correction"),
        (r"(.+?)\s+(?:should be|is actually|is)\s+(.+)", "value_correction"),
    ]
    
    # Patterns for results
    RESULT_PATTERNS = [
        (r"(?:yield|efficiency|purity)(?:\s+was|\s+is|:)?\s*([\d.]+%?)", "result"),
        (r"(?:concentration|amount)(?:\s+was|\s+is|:)?\s*([\d.]+\s*\w+)", "result"),
        (r"(?:ratio|factor)(?:\s+was|\s+is|:)?\s*([\d.]+)", "result"),
    ]
    
    # Patterns for parameters
    PARAM_PATTERNS = [
        (r"(?:temperature|temp)(?:\s+was|\s+is|:)?\s*([\d.]+\s*°?C?)", "parameter"),
        (r"(?:time|duration)(?:\s+was|\s+is|:)?\s*([\d.]+\s*(?:min|hour|hr|s))", "parameter"),
        (r"(?:volume|amount)(?:\s+was|\s+is|:)?\s*([\d.]+\s*(?:ml|ul|μl|L))", "parameter"),
    ]
    
    @classmethod
    def extract_quick_updates(cls, text: str) -> List[Tuple[str, str, str]]:
        """Extract updates using patterns. Returns (type, key, value) tuples."""
        
        updates = []
        text_lower = text.lower()
        
        # Check correction patterns
        for pattern, update_type in cls.CORRECTION_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                updates.append((update_type, match.group(1), match.group(2)))
        
        # Check result patterns
        for pattern, update_type in cls.RESULT_PATTERNS:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                # Get context around the match
                start = max(0, match.start() - 20)
                context = text[start:match.end() + 20]
                updates.append((update_type, context, match.group(1)))
        
        # Check parameter patterns
        for pattern, update_type in cls.PARAM_PATTERNS:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                start = max(0, match.start() - 20)
                context = text[start:match.end() + 20]
                updates.append((update_type, context, match.group(1)))
        
        return updates


# Global instance for easy access
_auto_updater = None

def get_auto_updater() -> AutoMemoryUpdater:
    """Get or create the global auto memory updater."""
    global _auto_updater
    if _auto_updater is None:
        _auto_updater = AutoMemoryUpdater()
    return _auto_updater


async def auto_update_memory(
    user_message: str,
    agent_response: str,
    experiment_id: Optional[str] = None
) -> str:
    """Convenience function to automatically update memory from conversation."""
    
    updater = get_auto_updater()
    return await updater.process_conversation(
        user_message,
        agent_response,
        experiment_id
    )