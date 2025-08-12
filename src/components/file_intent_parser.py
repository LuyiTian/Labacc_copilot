"""Natural language file intent parser for LabAcc Copilot

This module uses LLM to parse user intent from natural language messages,
supporting multiple languages without keyword dependency.
"""

import json
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Literal
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.language_models import BaseLLM


@dataclass
class FileIntent:
    """Parsed intent from user's natural language file management request"""
    operation_type: Literal["organize", "analyze", "save", "compare"]
    experiment_type: Optional[str]  # "PCR", "Western blot", "gel", etc.
    date_context: Optional[str]     # Extracted dates
    folder_suggestion: str          # AI-generated folder name
    analysis_request: bool          # Whether user wants analysis
    files_description: str          # User's description of files
    confidence_score: float         # Parser confidence (0-1)
    raw_message: str               # Original user message
    detected_language: str         # Language of the message


class FileIntentParser:
    """Parse natural language messages to extract file management intent
    
    Uses LLM for robust parsing that works across languages without
    relying on brittle keyword matching.
    """
    
    def __init__(self, llm: BaseLLM):
        self.llm = llm
        
        # System prompt for consistent parsing
        self.system_prompt = """You are a file management intent parser for a laboratory assistant system.
Your job is to analyze user messages with file attachments and extract their intent.

You must return a valid JSON object with these fields:
- operation_type: "organize", "analyze", "save", or "compare"
- experiment_type: Type of experiment (PCR, gel, Western blot, etc.) or null
- date_context: Any mentioned date or time reference, normalized to YYYY-MM-DD format
- folder_suggestion: Suggested folder name following pattern exp_XXX_type_YYYY-MM-DD OR "most_recent" for most recent folder OR "current_folder" if user refers to current/this folder
- analysis_request: boolean indicating if user wants analysis
- files_description: Brief description of the files from user's perspective
- confidence_score: 0.0 to 1.0 indicating parsing confidence
- detected_language: Language code (en, zh, es, fr, etc.)

Important:
- Work with ANY language - detect and understand intent regardless of language
- If date mentioned as "today", "yesterday", "last week" etc., convert to actual date
- For folder naming, always use English and follow the exp_XXX_type_date pattern
- If user mentions "most recent", "latest", "last experiment" or similar, set folder_suggestion to "most_recent"
- CRITICAL: If user mentions "this folder", "current folder", "here", "to this folder" or ANY similar reference (in any language), you MUST set folder_suggestion to exactly "current_folder" (not a folder name)
- Be intelligent about understanding context, not just keywords
- Consider cultural and linguistic variations in expressing intent

Today's date: {current_date}

Return ONLY valid JSON, no other text."""
    
    async def parse_intent(
        self, 
        message: str, 
        attachments: List[str],
        current_date: Optional[datetime] = None,
        current_folder: Optional[str] = None
    ) -> Optional[FileIntent]:
        """Parse natural language message to extract file management intent
        
        Args:
            message: User's message in any language
            attachments: List of attached file paths
            current_date: Override current date for testing
            current_folder: Currently browsing folder in the UI
            
        Returns:
            FileIntent object with parsed information, or None if not a file operation
        """
        
        if not attachments:
            return None
        
        if current_date is None:
            current_date = datetime.now()
            
        # Create context for LLM
        file_list = [f"- {attachment.split('/')[-1]}" for attachment in attachments]
        file_list_str = "\n".join(file_list)
        
        # Format the system prompt with current date
        system_msg = SystemMessage(content=self.system_prompt.format(
            current_date=current_date.strftime("%Y-%m-%d")
        ))
        
        # Create user message with context
        context_info = ""
        if current_folder:
            context_info = f"\nCurrent browsing folder: {current_folder}"
        
        user_prompt = f"""User message: "{message}"

Attached files:
{file_list_str}{context_info}

CRITICAL INSTRUCTION: 
- If user says "this folder", "current folder", "here", "to this folder" or ANY similar reference (in any language), you MUST set folder_suggestion to "current_folder" 
- Current browsing folder is: {current_folder if current_folder else 'root'}
- DO NOT create a new folder name when user refers to current/this folder - just return "current_folder" as folder_suggestion

Analyze this message and return the JSON object with file management intent."""

        user_msg = HumanMessage(content=user_prompt)
        
        try:
            # Get LLM response
            response = await self.llm.ainvoke([system_msg, user_msg])
            response_text = response.content.strip()
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group()
            
            # Parse JSON response
            parsed = json.loads(response_text)
            
            # Validate and create FileIntent
            return FileIntent(
                operation_type=parsed.get("operation_type", "organize"),
                experiment_type=parsed.get("experiment_type"),
                date_context=parsed.get("date_context"),
                folder_suggestion=parsed.get("folder_suggestion", self._generate_default_folder(current_date)),
                analysis_request=parsed.get("analysis_request", False),
                files_description=parsed.get("files_description", "Uploaded files"),
                confidence_score=parsed.get("confidence_score", 0.5),
                raw_message=message,
                detected_language=parsed.get("detected_language", "en")
            )
            
        except (json.JSONDecodeError, KeyError, Exception) as e:
            # If LLM parsing fails, return a basic intent
            return FileIntent(
                operation_type="save",
                experiment_type=None,
                date_context=current_date.strftime("%Y-%m-%d"),
                folder_suggestion=self._generate_default_folder(current_date),
                analysis_request=False,
                files_description=f"{len(attachments)} files uploaded",
                confidence_score=0.1,
                raw_message=message,
                detected_language="unknown"
            )
    
    def _generate_default_folder(self, date: datetime) -> str:
        """Generate a default folder name when parsing fails"""
        return f"exp_001_upload_{date.strftime('%Y-%m-%d')}"
    
    async def is_file_management_request(
        self,
        message: str,
        has_attachments: bool
    ) -> bool:
        """Determine if a message is a file management request
        
        Uses LLM to intelligently detect file management intent
        without relying on keywords, supporting all languages.
        
        Args:
            message: User's message
            has_attachments: Whether files are attached
            
        Returns:
            True if this appears to be a file management request
        """
        
        if not has_attachments:
            return False
        
        # Quick check - if message is very short, likely a file operation
        if len(message.strip()) < 10:
            return True
            
        # Use LLM for intelligent detection
        detection_prompt = """Is this message requesting file management operations?
Consider: saving files, organizing data, analyzing attachments, creating folders.
Reply with just "yes" or "no".

Message: {message}"""
        
        try:
            response = await self.llm.ainvoke([
                HumanMessage(content=detection_prompt.format(message=message))
            ])
            
            response_text = response.content.strip().lower()
            return "yes" in response_text
            
        except Exception:
            # Default to true if LLM fails and there are attachments
            return True


class FileIntentEnhancer:
    """Enhance file intent with additional context and validation"""
    
    @staticmethod
    def enhance_experiment_type(intent: FileIntent, file_names: List[str]) -> FileIntent:
        """Enhance experiment type detection based on file names"""
        
        if not intent.experiment_type:
            # Try to infer from file names
            file_names_lower = [f.lower() for f in file_names]
            
            experiment_patterns = {
                "pcr": ["pcr", "amplification", "primer"],
                "gel": ["gel", "electrophoresis", "agarose", "lane"],
                "western": ["western", "blot", "antibody"],
                "cell_culture": ["cell", "culture", "passage"],
                "sequencing": ["seq", "sequencing", "fastq"],
                "microscopy": ["microscopy", "image", "fluorescence"]
            }
            
            for exp_type, patterns in experiment_patterns.items():
                if any(pattern in name for name in file_names_lower for pattern in patterns):
                    intent.experiment_type = exp_type
                    break
        
        return intent
    
    @staticmethod
    def validate_date_context(intent: FileIntent) -> FileIntent:
        """Validate and normalize date context"""
        
        if intent.date_context:
            try:
                # Try to parse the date
                date = datetime.strptime(intent.date_context, "%Y-%m-%d")
                
                # Check if date is reasonable (not too far in future/past)
                today = datetime.now()
                days_diff = abs((date - today).days)
                
                if days_diff > 365:  # More than a year difference
                    intent.date_context = today.strftime("%Y-%m-%d")
                    intent.confidence_score *= 0.8  # Reduce confidence
                    
            except ValueError:
                # Invalid date format, use today
                intent.date_context = datetime.now().strftime("%Y-%m-%d")
                intent.confidence_score *= 0.9
        
        return intent