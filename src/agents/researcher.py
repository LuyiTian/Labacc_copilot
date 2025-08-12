"""Researcher agent - handles literature search and validation"""

import asyncio
from typing import List, Dict, Any
from datetime import datetime

from .base_agent import BaseAgent, AgentRole, Task, Result
from src.tools.deep_research import run_deep_research


class ResearcherAgent(BaseAgent):
    """Handles literature search and method validation"""
    
    def __init__(self):
        super().__init__(AgentRole.RESEARCHER, "siliconflow-qwen-30b")
    
    async def process(self, task: Task) -> Result:
        """Process research tasks"""
        start_time = datetime.now()
        
        try:
            if task.type == "research_problem":
                result_content = await self.research_specific_problem(task.content, task.metadata)
            else:
                result_content = await self.general_research(task.content, task.metadata)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return Result(
                task_id=task.id,
                agent=self.name,
                success=True,
                content=result_content,
                metadata={"research_type": task.type},
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            return Result(
                task_id=task.id,
                agent=self.name,
                success=False,
                content=f"Research failed: {str(e)}",
                metadata={"error": str(e)},
                processing_time=processing_time
            )
    
    async def research_specific_problem(self, query: str, metadata: Dict[str, Any]) -> str:
        """Research a specific experimental problem"""
        try:
            # Extract research keywords from query
            research_query = self.extract_research_query(query)
            
            # Run deep research (async in background for speed)
            loop = asyncio.get_event_loop()
            research_result = await loop.run_in_executor(
                None, 
                lambda: run_deep_research(research_query, max_research_loops=2)
            )
            
            if research_result and 'final_text' in research_result:
                return f"""
**Literature Research Results:**

**Query**: {research_query}

**Key Findings**:
{research_result['final_text'][:1500]}...

**Research completed** - Full reports saved to `data/history/`
                """.strip()
            else:
                return self.fallback_research_response(research_query)
                
        except Exception as e:
            return self.fallback_research_response(query)
    
    def extract_research_query(self, user_query: str) -> str:
        """Extract research-focused query from user input"""
        # Simple keyword extraction for speed
        research_keywords = ["PCR", "gel electrophoresis", "western blot", "cloning", 
                           "cell culture", "protein", "DNA", "RNA", "optimization", 
                           "troubleshooting", "protocol"]
        
        for keyword in research_keywords:
            if keyword.lower() in user_query.lower():
                return f"{keyword} {user_query}"
        
        return user_query
    
    def fallback_research_response(self, query: str) -> str:
        """Provide fallback research response"""
        return f"""
**Research Available:**

I can search scientific literature for: {query}

**Research Capabilities:**
- Literature search via Tavily API
- Method validation
- Protocol recommendations
- Troubleshooting guides

*Use "research [your question]" for detailed literature analysis.*
        """.strip()
    
    async def general_research(self, query: str, metadata: Dict[str, Any]) -> str:
        """Handle general research queries"""
        if "research" in query.lower() or "literature" in query.lower():
            return await self.research_specific_problem(query, metadata)
        
        return f"""
**Research Support:**

I can help with literature research on laboratory methods and troubleshooting.

**Research Areas:**
- Experimental protocols
- Method optimization
- Troubleshooting approaches
- Latest scientific findings

*Ask specific questions about protocols or methods for targeted literature search.*
        """.strip()
    
    def get_supported_tasks(self) -> List[str]:
        """Researcher handles literature and method research"""
        return ["research_problem", "general_query"]