"""Smart orchestrator - uses quick responses by default, full agents when needed"""

import asyncio
from typing import List, Dict, Any
from datetime import datetime
import uuid

from .base_agent import BaseAgent, AgentRole, Task, Result
from .explorer import ExplorerAgent
from .analyzer import AnalyzerAgent
from .researcher import ResearcherAgent
from .advisor import AdvisorAgent
from .quick_orchestrator import QuickOrchestratorAgent


class SmartOrchestratorAgent(BaseAgent):
    """Smart orchestrator that balances speed and depth"""
    
    def __init__(self):
        super().__init__(AgentRole.ORCHESTRATOR, "siliconflow-qwen-8b")
        
        # Initialize agents
        self.quick_agent = QuickOrchestratorAgent()
        self.explorer = ExplorerAgent()
        self.analyzer = AnalyzerAgent()
        self.researcher = ResearcherAgent()
        self.advisor = AdvisorAgent()
    
    async def process(self, task: Task) -> Result:
        """Process task - use quick responses unless deep processing requested"""
        start_time = datetime.now()
        
        try:
            query = task.content.lower()
            
            # Determine if deep processing is needed
            needs_deep_processing = self.needs_deep_processing(query)
            
            if needs_deep_processing:
                result = await self.deep_process(task)
            else:
                result = await self.quick_agent.process(task)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            result.processing_time = processing_time
            
            return result
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            return Result(
                task_id=task.id,
                agent=self.name,
                success=False,
                content=f"Error: {str(e)}",
                metadata={"error": str(e)},
                processing_time=processing_time
            )
    
    def needs_deep_processing(self, query: str) -> bool:
        """Determine if query needs deep processing"""
        deep_keywords = [
            "deep research", "literature search", "research paper",
            "detailed analysis", "comprehensive", "in-depth",
            "scientific papers", "publications", "studies"
        ]
        
        return any(keyword in query for keyword in deep_keywords)
    
    async def deep_process(self, task: Task) -> Result:
        """Process with full agent capabilities"""
        query = task.content.lower()
        
        # Route to appropriate agent
        if "research" in query or "literature" in query or "paper" in query:
            # Use real researcher with deep research
            return await self.researcher.process(task)
        elif "analyze" in query and task.metadata.get("current_folder"):
            # Use real analyzer for specific folder
            return await self.analyzer.process(task)
        elif "scan" in query and "detail" in query:
            # Use real explorer for detailed scan
            return await self.explorer.process(task)
        elif "optimize" in query or "suggest" in query:
            # Use real advisor
            return await self.advisor.process(task)
        else:
            # Fallback to quick agent
            return await self.quick_agent.process(task)
    
    def get_supported_tasks(self):
        return ["general_query", "scan_project", "analyze_experiment", "research_problem", "suggest_optimization"]