"""Orchestrator agent - coordinates all other agents"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from .base_agent import BaseAgent, AgentRole, Task, Result
from .explorer import ExplorerAgent
from .analyzer import AnalyzerAgent
from .researcher import ResearcherAgent
from .advisor import AdvisorAgent


class OrchestratorAgent(BaseAgent):
    """Coordinates multiple agents to handle complex queries"""
    
    def __init__(self):
        super().__init__(AgentRole.ORCHESTRATOR, "siliconflow-qwen-30b")
        
        # Initialize specialized agents
        self.agents = {
            AgentRole.EXPLORER.value: ExplorerAgent(),
            AgentRole.ANALYZER.value: AnalyzerAgent(),
            AgentRole.RESEARCHER.value: ResearcherAgent(),
            AgentRole.ADVISOR.value: AdvisorAgent()
        }
        
        # Task routing rules
        self.task_routing = {
            "scan_project": ["explorer"],
            "analyze_experiment": ["analyzer", "explorer"],
            "research_problem": ["researcher"],
            "suggest_optimization": ["advisor", "analyzer"],
            "compare_experiments": ["analyzer"],
            "general_query": ["analyzer", "researcher", "advisor"]
        }
    
    async def process(self, task: Task) -> Result:
        """Orchestrate multiple agents to handle a task"""
        start_time = datetime.now()
        
        try:
            # Determine which agents to use
            agents_needed = self.determine_agents(task)
            
            # Execute agents in parallel or sequence based on task
            if task.type in ["scan_project", "analyze_experiment"]:
                results = await self.execute_sequence(agents_needed, task)
            else:
                results = await self.execute_parallel(agents_needed, task)
            
            # Synthesize final response
            final_response = await self.synthesize_response(task, results)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return Result(
                task_id=task.id,
                agent=self.name,
                success=True,
                content=final_response,
                metadata={
                    "agents_used": agents_needed,
                    "sub_results": [r.content for r in results]
                },
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            return Result(
                task_id=task.id,
                agent=self.name,
                success=False,
                content=f"Orchestration failed: {str(e)}",
                metadata={"error": str(e)},
                processing_time=processing_time
            )
    
    def determine_agents(self, task: Task) -> List[str]:
        """Determine which agents should handle this task"""
        task_type = task.type
        
        # Use predefined routing
        if task_type in self.task_routing:
            return self.task_routing[task_type]
        
        # Fallback to general query routing
        return self.task_routing["general_query"]
    
    async def execute_sequence(self, agent_names: List[str], task: Task) -> List[Result]:
        """Execute agents in sequence (each builds on previous)"""
        results = []
        current_task = task
        
        for agent_name in agent_names:
            agent = self.agents[agent_name]
            result = await agent.process(current_task)
            results.append(result)
            
            # Create new task for next agent using previous result
            if result.success:
                current_task = Task(
                    id=str(uuid.uuid4()),
                    type=task.type,
                    content=f"{task.content}\n\nPrevious analysis: {result.content}",
                    metadata={**task.metadata, "previous_result": result.content},
                    created_at=datetime.now(),
                    priority=task.priority
                )
        
        return results
    
    async def execute_parallel(self, agent_names: List[str], task: Task) -> List[Result]:
        """Execute agents in parallel"""
        agent_tasks = []
        
        for agent_name in agent_names:
            agent = self.agents[agent_name]
            agent_tasks.append(agent.process(task))
        
        results = await asyncio.gather(*agent_tasks, return_exceptions=True)
        
        # Convert exceptions to failed results
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                final_results.append(Result(
                    task_id=task.id,
                    agent=agent_names[i],
                    success=False,
                    content=f"Agent failed: {str(result)}",
                    metadata={"error": str(result)},
                    processing_time=0.0
                ))
            else:
                final_results.append(result)
        
        return final_results
    
    async def synthesize_response(self, original_task: Task, results: List[Result]) -> str:
        """Combine results from multiple agents into coherent response"""
        successful_results = [r for r in results if r.success]
        
        if not successful_results:
            return "I encountered issues processing your request. Please try again."
        
        # Simple synthesis - combine all successful results
        synthesis_prompt = f"""
        User query: {original_task.content}
        
        Agent analyses:
        {chr(10).join([f"- {r.agent}: {r.content}" for r in successful_results])}
        
        Provide a coherent, unified response that synthesizes these analyses:
        """
        
        try:
            response = await self.llm.ainvoke(synthesis_prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            # Fallback to simple combination
            return "\n\n".join([f"**{r.agent.title()} Analysis:**\n{r.content}" for r in successful_results])
    
    def get_supported_tasks(self) -> List[str]:
        """Orchestrator handles all task types"""
        return list(self.task_routing.keys())
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get status of all agents in the system"""
        status = {
            "orchestrator": {
                "active": True,
                "tasks_processed": len(self.active_tasks)
            }
        }
        
        for agent_name, agent in self.agents.items():
            status[agent_name] = {
                "active": True,
                "state": agent.state,
                "active_tasks": len(agent.active_tasks)
            }
        
        return status