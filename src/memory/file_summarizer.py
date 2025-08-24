"""
File Summarizer - Uses LLM to create context-aware summaries of uploaded files
"""

import logging
from pathlib import Path
from typing import Optional

from langchain_core.messages import HumanMessage
from src.components.llm import get_llm_instance
from src.memory.memory_tools import read_memory

logger = logging.getLogger(__name__)


class FileContextSummarizer:
    """Summarizes files with experiment context using LLM."""
    
    def __init__(self):
        # Use fast LLM for summarization
        self.llm = get_llm_instance("openrouter-gpt-oss-120b")  # Fast model
    
    async def summarize_with_context(
        self,
        file_path: str,
        experiment_id: Optional[str] = None,
        max_chars: int = 10000
    ) -> str:
        """Summarize a file with experiment context.
        
        Args:
            file_path: Path to the file
            experiment_id: Experiment ID for context
            max_chars: Maximum characters to read from file
        
        Returns:
            Context-aware summary of the file
        """
        try:
            # Read file content
            full_path = Path(file_path)
            if not full_path.exists():
                return "File not found"
            
            file_ext = full_path.suffix.lower()
            file_name = full_path.name
            
            # Handle different file types
            if file_ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg']:
                # Image analysis is implemented in src/components/image_analyzer.py
                return f"Image file - {file_name} (use analyze_image tool for detailed analysis)"
            
            if file_ext == '.pdf':
                # PDFs are converted to markdown via file_conversion.py
                return f"PDF file - {file_name} (will be converted to markdown for analysis)"
            
            if file_ext in ['.xlsx', '.xls']:
                # Excel analysis is implemented in src/components/file_analyzer.py
                return f"Excel file - {file_name} (use file analyzer for detailed analysis)"
            
            if file_ext not in ['.txt', '.csv', '.tsv', '.md', '.json', '.yaml', '.yml', 
                               '.py', '.ipynb', '.log', '.dat', '.xml', '.html']:
                return f"Binary file - {file_name}"
            
            # Read text file content
            try:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(max_chars)
                    
                if not content:
                    return f"Empty file - {file_name}"
            except Exception as e:
                logger.error(f"Error reading file {file_path}: {e}")
                return f"Could not read file - {file_name}"
            
            # Get experiment context if available
            experiment_context = ""
            if experiment_id:
                try:
                    readme_content = await read_memory.ainvoke({
                        "experiment_id": experiment_id
                    })
                    if readme_content and "not found" not in readme_content.lower():
                        # Extract key sections
                        lines = readme_content.split('\n')
                        overview = []
                        parameters = []
                        in_overview = False
                        in_parameters = False
                        
                        for line in lines[:50]:  # First 50 lines
                            if "## Overview" in line:
                                in_overview = True
                                in_parameters = False
                            elif "## Parameters" in line:
                                in_parameters = True
                                in_overview = False
                            elif "##" in line:
                                in_overview = False
                                in_parameters = False
                            elif in_overview:
                                overview.append(line)
                            elif in_parameters:
                                parameters.append(line)
                        
                        if overview:
                            experiment_context = f"Experiment Overview:\n" + "\n".join(overview[:5])
                        if parameters:
                            experiment_context += f"\n\nExperiment Parameters:\n" + "\n".join(parameters[:5])
                except Exception as e:
                    logger.error(f"Could not get experiment context: {e}")
            
            # Create prompt for LLM
            prompt = f"""Summarize this uploaded file in the context of a laboratory experiment.

File name: {file_name}
File type: {file_ext}
{experiment_context}

File content (first {len(content)} characters):
---
{content}
---

Provide a concise 1-2 sentence summary that:
1. Describes what the file contains
2. Relates it to the experiment context if relevant
3. Highlights any key data, results, or parameters found

Summary:"""
            
            # Get LLM summary
            response = self.llm.invoke([HumanMessage(content=prompt)])
            summary = response.content.strip()
            
            # Ensure summary is not too long
            if len(summary) > 200:
                summary = summary[:197] + "..."
            
            return summary
            
        except Exception as e:
            logger.error(f"Error summarizing file: {e}")
            return f"Error summarizing - {file_name}"
    
    async def quick_summary(self, file_path: str, file_type: str) -> str:
        """Quick summary without context for non-experiment files.
        
        Args:
            file_path: Path to the file
            file_type: Type of file (Data, Document, Code, etc.)
        
        Returns:
            Quick summary
        """
        try:
            full_path = Path(file_path)
            file_name = full_path.name
            file_ext = full_path.suffix.lower()
            
            if not full_path.exists():
                return f"Uploaded {file_type.lower()} file"
            
            # For non-text files
            if file_ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg']:
                return f"Image file: {file_name}"
            if file_ext in ['.pdf']:
                return f"PDF document: {file_name}"
            if file_ext in ['.xlsx', '.xls']:
                return f"Spreadsheet: {file_name}"
            
            # For text files, get first meaningful line
            try:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines(100)  # Read first 100 lines
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith('#') and not line.startswith('//'):
                            if len(line) > 100:
                                return line[:97] + "..."
                            return line
            except:
                pass
            
            return f"Uploaded {file_type.lower()} file"
            
        except Exception as e:
            logger.error(f"Error in quick summary: {e}")
            return f"Uploaded file"


# Global instance
_summarizer = None

def get_file_summarizer() -> FileContextSummarizer:
    """Get or create the global file summarizer."""
    global _summarizer
    if _summarizer is None:
        _summarizer = FileContextSummarizer()
    return _summarizer


async def summarize_uploaded_file(
    file_path: str,
    experiment_id: Optional[str] = None
) -> str:
    """Convenience function to summarize an uploaded file.
    
    Args:
        file_path: Path to the file
        experiment_id: Optional experiment ID for context
    
    Returns:
        Context-aware summary
    """
    summarizer = get_file_summarizer()
    return await summarizer.summarize_with_context(file_path, experiment_id)