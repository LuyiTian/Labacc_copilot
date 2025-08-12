"""Base agent class for LabAcc Copilot multi-agent system"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import asyncio
from datetime import datetime

from src.components.llm import get_llm_instance


class AgentRole(Enum):
    ORCHESTRATOR = "orchestrator"
    EXPLORER = "explorer" 
    ANALYZER = "analyzer"
    RESEARCHER = "researcher"
    ADVISOR = "advisor"


@dataclass
class Task:
    id: str
    type: str
    content: str
    metadata: Dict[str, Any]
    created_at: datetime
    priority: int = 1


@dataclass
class Result:
    task_id: str
    agent: str
    success: bool
    content: str
    metadata: Dict[str, Any]
    processing_time: float


class BaseAgent(ABC):
    """Base class for all LabAcc Copilot agents"""
    
    def __init__(self, role: AgentRole, llm_model: str = "siliconflow-qwen-8b"):
        self.role = role
        self.name = role.value
        self.llm = get_llm_instance(llm_model)
        self.state: Dict[str, Any] = {}
        self.active_tasks: List[Task] = []
        
    @abstractmethod
    async def process(self, task: Task) -> Result:
        """Process a task and return result"""
        pass
    
    def can_handle(self, task_type: str) -> bool:
        """Check if this agent can handle the given task type"""
        return task_type in self.get_supported_tasks()
    
    @abstractmethod 
    def get_supported_tasks(self) -> List[str]:
        """Return list of task types this agent can handle"""
        pass
        
    async def update_state(self, key: str, value: Any):
        """Update agent state"""
        self.state[key] = value
        
    def get_state(self, key: str, default: Any = None) -> Any:
        """Get value from agent state"""
        return self.state.get(key, default)
        
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(role={self.role.value})"