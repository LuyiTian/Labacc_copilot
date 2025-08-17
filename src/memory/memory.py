"""
Simple memory system for LabAcc Copilot.
No parsing, no patterns, just raw README storage with LLM-based extraction.

Philosophy: Trust the LLM. Keep it simple.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class SimpleMemory:
    """
    Dead simple memory storage - just the README content.
    No parsing, no sections, no complex structures.
    """
    experiment_id: str
    raw_content: str
    file_path: Path
    last_modified: datetime
    
    def save(self, new_content: str) -> None:
        """Save updated content to file."""
        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            self.file_path.write_text(new_content, encoding='utf-8')
            self.raw_content = new_content
            self.last_modified = datetime.now()
            logger.info(f"Saved README for {self.experiment_id}")
        except Exception as e:
            logger.error(f"Failed to save README for {self.experiment_id}: {e}")
            raise
    
    async def extract_info(self, query: str, llm) -> str:
        """
        Use LLM to extract information from README.
        Works in ANY language - no patterns!
        """
        if not self.raw_content:
            return f"No README content found for {self.experiment_id}"
        
        prompt = f"""Extract information from this experiment README based on the user's query.
        
User Query: {query}

README Content:
{self.raw_content}

Extract and return the relevant information. If the information is not found, say so clearly.
Preserve the original language when appropriate."""
        
        try:
            response = await llm.ainvoke(prompt)
            # Handle both string and message responses
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            # Fallback: return the raw content
            return f"Here's the full README:\n\n{self.raw_content}"


class SimpleMemoryManager:
    """
    Minimal memory manager - just loads and saves README files.
    No complex parsing, no pattern matching.
    """
    
    def __init__(self, project_root: str = "data/alice_projects"):
        self.project_root = Path(project_root)
    
    def load_memory(self, experiment_id: str) -> SimpleMemory:
        """
        Load README content for an experiment.
        If it doesn't exist, create a minimal one.
        """
        readme_path = self.project_root / experiment_id / "README.md"
        
        if readme_path.exists():
            try:
                content = readme_path.read_text(encoding='utf-8')
                logger.info(f"Loaded README for {experiment_id}")
            except Exception as e:
                logger.error(f"Failed to read README for {experiment_id}: {e}")
                content = f"# {experiment_id}\n\nError reading README: {e}"
        else:
            # Create minimal README
            content = f"""# {experiment_id}

**Status:** Active  
**Created:** {datetime.now().strftime('%Y-%m-%d')}

## Overview

This experiment is being set up.
"""
            logger.info(f"Created new README for {experiment_id}")
        
        return SimpleMemory(
            experiment_id=experiment_id,
            raw_content=content,
            file_path=readme_path,
            last_modified=datetime.now()
        )
    
    def list_experiments(self) -> list[str]:
        """List all experiments with README files."""
        experiments = []
        
        if not self.project_root.exists():
            return experiments
        
        for exp_dir in self.project_root.iterdir():
            if exp_dir.is_dir() and exp_dir.name.startswith("exp_"):
                readme_path = exp_dir / "README.md"
                if readme_path.exists():
                    experiments.append(exp_dir.name)
        
        return sorted(experiments)
    
    async def update_memory(self, experiment_id: str, updates: str, llm) -> str:
        """
        Update README with new information.
        LLM figures out how to integrate it - no templates!
        """
        memory = self.load_memory(experiment_id)
        
        prompt = f"""Update this experiment README with new information.
        
Current README:
{memory.raw_content}

New Information to Add:
{updates}

IMPORTANT RULES:
1. Only add information that is explicitly stated in the "New Information to Add" section
2. Do NOT make up or invent any collaborations, institutions, or data that isn't mentioned
3. Do NOT create fictional narratives or backstories
4. Use the EXACT filenames provided, do not change them
5. If the new information references a file, use the actual filename given

Return the complete updated README, preserving the existing structure and language.
Add the new information in the appropriate section or create a new section if needed.
Keep the markdown formatting clean and readable.
Be factual and accurate - only include what is explicitly provided."""
        
        try:
            response = await llm.ainvoke(prompt)
            # Handle both string and message responses
            new_content = response.content if hasattr(response, 'content') else str(response)
            
            memory.save(new_content)
            return f"Updated README for {experiment_id}"
        except Exception as e:
            logger.error(f"Failed to update README for {experiment_id}: {e}")
            return f"Error updating README: {e}"