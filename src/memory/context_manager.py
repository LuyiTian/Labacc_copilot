"""
Context Management System
Builds rich context from README memories for intelligent tool execution
"""

import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import logging

from src.memory.readme_memory import MemoryManager, ExperimentMemory

logger = logging.getLogger(__name__)


@dataclass
class ProjectContext:
    """Project-level context from all experiments"""
    project_root: str
    total_experiments: int
    active_experiments: List[str]
    recent_insights: List[Dict[str, str]]
    success_patterns: List[str]
    common_methods: List[str]


@dataclass
class SessionContext:
    """User session context"""
    session_id: str
    current_folder: Optional[str]
    selected_files: List[str]
    conversation_history: List[Dict[str, str]]
    user_intent: Optional[str]


@dataclass 
class EnrichedContext:
    """Full context for tool execution"""
    session: SessionContext
    experiment: Optional[ExperimentMemory]
    project: Optional[ProjectContext]
    related_experiments: List[str]
    timestamp: str


class ContextBuilder:
    """Builds rich context from README memories and session state"""
    
    def __init__(self, project_root: str = None):
        """Initialize context builder"""
        if project_root is None:
            project_root = os.path.join(os.getcwd(), "data", "alice_projects")
        self.project_root = Path(project_root)
        self.memory_manager = MemoryManager(str(self.project_root))
    
    async def build_context(
        self,
        session_id: str,
        user_message: str,
        current_folder: Optional[str] = None,
        selected_files: Optional[List[str]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> EnrichedContext:
        """Build enriched context for tool execution"""
        
        # Build session context
        session_context = SessionContext(
            session_id=session_id,
            current_folder=current_folder,
            selected_files=selected_files or [],
            conversation_history=conversation_history or [],
            user_intent=self._extract_intent(user_message)
        )
        
        # Load experiment context if in experiment folder
        experiment_context = None
        if current_folder and current_folder.startswith("exp_"):
            experiment_context = self.memory_manager.read_memory(current_folder)
        
        # Load project context
        project_context = await self._build_project_context()
        
        # Find related experiments
        related_experiments = []
        if experiment_context:
            related_experiments = await self._find_related_experiments(experiment_context)
        
        return EnrichedContext(
            session=session_context,
            experiment=experiment_context,
            project=project_context,
            related_experiments=related_experiments,
            timestamp=datetime.now().isoformat()
        )
    
    def _extract_intent(self, message: str) -> str:
        """Extract user intent from message"""
        message_lower = message.lower()
        
        # Simple intent detection (will be replaced by LLM in production)
        if any(word in message_lower for word in ['analyze', 'analysis', 'look at']):
            return 'analyze'
        elif any(word in message_lower for word in ['compare', 'difference', 'versus']):
            return 'compare'
        elif any(word in message_lower for word in ['why', 'diagnose', 'problem', 'issue', 'fail']):
            return 'diagnose'
        elif any(word in message_lower for word in ['optimize', 'improve', 'better']):
            return 'optimize'
        elif any(word in message_lower for word in ['search', 'find', 'literature']):
            return 'search'
        else:
            return 'general'
    
    async def _build_project_context(self) -> ProjectContext:
        """Build project-level context from all experiments"""
        
        # Get all experiment directories
        exp_dirs = [d for d in self.project_root.iterdir() 
                   if d.is_dir() and d.name.startswith("exp_")]
        
        active_experiments = []
        recent_insights = []
        success_patterns = []
        common_methods = []
        
        for exp_dir in exp_dirs:
            memory = self.memory_manager.read_memory(exp_dir.name)
            if memory:
                # Track active experiments
                if memory.status == "active":
                    active_experiments.append(exp_dir.name)
                
                # Collect recent insights
                for insight in memory.insights[-2:]:  # Last 2 insights per experiment
                    recent_insights.append({
                        'experiment': exp_dir.name,
                        'insight': insight.get('insight', ''),
                        'timestamp': insight.get('timestamp', '')
                    })
                
                # Collect successful patterns
                if memory.status == "completed" and memory.results.get('key_findings'):
                    for finding in memory.results['key_findings']:
                        success_patterns.append(f"{exp_dir.name}: {finding}")
                
                # Collect methods
                if memory.methods:
                    common_methods.append(memory.methods[:100])  # First 100 chars
        
        # Sort insights by timestamp
        recent_insights.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return ProjectContext(
            project_root=str(self.project_root),
            total_experiments=len(exp_dirs),
            active_experiments=active_experiments,
            recent_insights=recent_insights[:10],  # Keep 10 most recent
            success_patterns=success_patterns[:5],  # Keep 5 patterns
            common_methods=list(set(common_methods))[:3]  # 3 unique methods
        )
    
    async def _find_related_experiments(
        self,
        current_experiment: ExperimentMemory,
        max_related: int = 3
    ) -> List[str]:
        """Find experiments related to the current one"""
        
        related = []
        
        # Get all experiments
        exp_dirs = [d for d in self.project_root.iterdir() 
                   if d.is_dir() and d.name.startswith("exp_")]
        
        # Simple similarity based on parameters and methods
        for exp_dir in exp_dirs:
            if exp_dir.name == current_experiment.experiment_id:
                continue
            
            memory = self.memory_manager.read_memory(exp_dir.name)
            if memory:
                # Check for similar parameters
                if memory.parameters and current_experiment.parameters:
                    # Check if they share parameter keys
                    current_params = set()
                    for param_type in current_experiment.parameters.values():
                        if isinstance(param_type, dict):
                            current_params.update(param_type.keys())
                    
                    other_params = set()
                    for param_type in memory.parameters.values():
                        if isinstance(param_type, dict):
                            other_params.update(param_type.keys())
                    
                    # If significant overlap, consider related
                    if current_params and other_params:
                        overlap = len(current_params & other_params)
                        if overlap > len(current_params) * 0.3:  # 30% overlap
                            related.append(exp_dir.name)
        
        return related[:max_related]
    
    def extract_context_for_tool(
        self,
        context: EnrichedContext,
        tool_name: str
    ) -> Dict[str, Any]:
        """Extract relevant context for a specific tool"""
        
        tool_context = {
            'session_id': context.session.session_id,
            'timestamp': context.timestamp
        }
        
        # Add experiment context if available
        if context.experiment:
            tool_context['current_experiment'] = {
                'id': context.experiment.experiment_id,
                'status': context.experiment.status,
                'overview': context.experiment.overview,
                'recent_results': context.experiment.results.get('key_findings', [])[:3]
            }
        
        # Add project insights for comparison tools
        if tool_name in ['compare_experiments', 'get_project_insights']:
            if context.project:
                tool_context['project_insights'] = {
                    'total_experiments': context.project.total_experiments,
                    'success_patterns': context.project.success_patterns,
                    'recent_insights': context.project.recent_insights[:5]
                }
        
        # Add file context for analysis tools
        if tool_name in ['analyze_data', 'update_file_registry']:
            tool_context['selected_files'] = context.session.selected_files
            tool_context['current_folder'] = context.session.current_folder
        
        # Add conversation history for chat tools
        if tool_name in ['chat_update', 'append_insight']:
            tool_context['recent_conversation'] = context.session.conversation_history[-3:]
        
        # Add related experiments for diagnosis
        if tool_name == 'diagnose_issue':
            tool_context['related_experiments'] = context.related_experiments
        
        return tool_context


class ContextAwareRouter:
    """Routes user requests to appropriate tools with context"""
    
    def __init__(self):
        self.context_builder = ContextBuilder()
    
    async def route_with_context(
        self,
        user_message: str,
        session_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Route user request to appropriate tool with enriched context"""
        
        # Build context
        context = await self.context_builder.build_context(
            session_id=session_info.get('session_id', 'default'),
            user_message=user_message,
            current_folder=session_info.get('current_folder'),
            selected_files=session_info.get('selected_files'),
            conversation_history=session_info.get('conversation_history', [])
        )
        
        # Determine tool based on intent and context
        tool_name = self._select_tool(context.session.user_intent, context)
        
        # Extract tool-specific context
        tool_context = self.context_builder.extract_context_for_tool(context, tool_name)
        
        return {
            'tool': tool_name,
            'context': tool_context,
            'full_context': context
        }
    
    def _select_tool(self, intent: str, context: EnrichedContext) -> str:
        """Select appropriate tool based on intent and context"""
        
        # If in experiment folder, prefer experiment-specific tools
        if context.experiment:
            if intent == 'analyze':
                return 'analyze_data'
            elif intent == 'diagnose':
                return 'diagnose_issue'
            elif intent == 'compare':
                return 'compare_experiments'
        
        # General routing based on intent
        tool_mapping = {
            'analyze': 'analyze_data',
            'compare': 'compare_experiments',
            'diagnose': 'diagnose_issue',
            'optimize': 'suggest_optimization',
            'search': 'search_memories',
            'general': 'read_memory'
        }
        
        return tool_mapping.get(intent, 'read_memory')