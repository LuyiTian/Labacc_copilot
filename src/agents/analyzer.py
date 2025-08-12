"""Analyzer agent - compares protocols and identifies patterns"""

import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from .base_agent import BaseAgent, AgentRole, Task, Result


class AnalyzerAgent(BaseAgent):
    """Analyzes experimental data and identifies patterns"""
    
    def __init__(self):
        super().__init__(AgentRole.ANALYZER, "siliconflow-qwen-30b")
    
    async def process(self, task: Task) -> Result:
        """Process analysis tasks"""
        start_time = datetime.now()
        
        try:
            if task.type == "analyze_experiment":
                result_content = await self.analyze_single_experiment(task.content, task.metadata)
            elif task.type == "compare_experiments":
                result_content = await self.compare_experiments(task.metadata)
            else:
                result_content = await self.general_analysis(task.content, task.metadata)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return Result(
                task_id=task.id,
                agent=self.name,
                success=True,
                content=result_content,
                metadata={"analysis_type": task.type},
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            return Result(
                task_id=task.id,
                agent=self.name,
                success=False,
                content=f"Analysis failed: {str(e)}",
                metadata={"error": str(e)},
                processing_time=processing_time
            )
    
    async def analyze_single_experiment(self, query: str, metadata: Dict[str, Any]) -> str:
        """Analyze a single experiment"""
        current_folder = metadata.get("current_folder", "")
        selected_files = metadata.get("selected_files", [])
        
        # Read README if available
        readme_content = ""
        if current_folder:
            readme_path = Path(current_folder) / "README.md"
            if readme_path.exists():
                readme_content = readme_path.read_text()
        
        analysis_prompt = f"""
        Analyze this experiment:
        
        Query: {query}
        Current folder: {current_folder}
        Selected files: {selected_files}
        
        README content:
        {readme_content}
        
        Provide insights about:
        1. Experimental approach and methods
        2. Potential issues or optimizations
        3. Success factors
        4. Comparison to typical protocols
        
        Be specific and actionable.
        """
        
        try:
            response = await self.llm.ainvoke(analysis_prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            return f"**Experiment Analysis:**\n\nI can analyze experimental protocols and data. Please share specific details about your experiment for detailed insights."
    
    async def compare_experiments(self, metadata: Dict[str, Any]) -> str:
        """Compare multiple experiments"""
        project_root = metadata.get("project_root", "data/alice_projects")
        
        comparison_result = f"""
**Cross-Experiment Analysis:**

I can compare protocols, success rates, and methodologies across your experiments. 

**Key Comparison Areas:**
- Protocol variations and their outcomes
- Success factors across similar experiments  
- Parameter optimization trends
- Common failure modes

*To perform detailed comparisons, I'll need access to experiment READMEs and data files.*
        """.strip()
        
        return comparison_result
    
    async def general_analysis(self, query: str, metadata: Dict[str, Any]) -> str:
        """Handle general analysis queries"""
        analysis_prompt = f"""
        User query: {query}
        
        Provide analytical insights for this laboratory research question.
        Focus on:
        1. Scientific methodology
        2. Data interpretation
        3. Protocol optimization
        4. Troubleshooting approaches
        
        Be practical and evidence-based.
        """
        
        try:
            response = await self.llm.ainvoke(analysis_prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            return "**Analysis Available:** I can help analyze experimental protocols, compare results, and suggest optimizations. What specific analysis would you like?"
    
    def get_supported_tasks(self) -> List[str]:
        """Analyzer handles protocol and data analysis"""
        return ["analyze_experiment", "compare_experiments", "general_query"]