"""Explorer agent - scans and maps project structure"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from .base_agent import BaseAgent, AgentRole, Task, Result


class ExplorerAgent(BaseAgent):
    """Scans project structure and maps experiments"""
    
    def __init__(self):
        super().__init__(AgentRole.EXPLORER, "siliconflow-qwen-8b")
    
    async def process(self, task: Task) -> Result:
        """Process exploration tasks"""
        start_time = datetime.now()
        
        try:
            if task.type == "scan_project":
                result_content = await self.scan_project(task.metadata.get("project_root", "data/alice_projects"))
            elif task.type == "map_experiments":
                result_content = await self.map_experiments(task.metadata.get("project_root", "data/alice_projects"))
            else:
                result_content = await self.general_exploration(task.content, task.metadata)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return Result(
                task_id=task.id,
                agent=self.name,
                success=True,
                content=result_content,
                metadata={"exploration_type": task.type},
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            return Result(
                task_id=task.id,
                agent=self.name,
                success=False,
                content=f"Exploration failed: {str(e)}",
                metadata={"error": str(e)},
                processing_time=processing_time
            )
    
    async def scan_project(self, project_root: str) -> str:
        """Scan entire project and provide overview"""
        project_path = Path(project_root)
        
        if not project_path.exists():
            return f"Project root {project_root} does not exist."
        
        # Discover experiments
        experiments = []
        experiment_pattern = r"exp_\d+.*"
        
        for item in project_path.iterdir():
            if item.is_dir() and any(char.isdigit() for char in item.name):
                exp_info = self.analyze_experiment_folder(item)
                experiments.append(exp_info)
        
        # Generate project overview
        total_experiments = len(experiments)
        experiment_types = {}
        recent_experiments = []
        
        for exp in experiments:
            exp_type = exp.get("type", "unknown")
            experiment_types[exp_type] = experiment_types.get(exp_type, 0) + 1
            
            if exp.get("created_recently"):
                recent_experiments.append(exp["name"])
        
        overview = f"""
**Project Scan Complete**

📊 **Project Overview:**
- Total experiments: {total_experiments}
- Experiment types: {', '.join([f"{k}: {v}" for k, v in experiment_types.items()])}
- Recent experiments (last 7 days): {len(recent_experiments)}

📁 **Recent Activity:**
{chr(10).join([f"- {exp}" for exp in recent_experiments[-5:]])}

🔍 **Project Structure Mapped:**
I've analyzed all experiment folders and can now help with cross-experiment comparisons, pattern recognition, and optimization suggestions.
        """.strip()
        
        # Store project map in agent state
        await self.update_state("project_map", {
            "total_experiments": total_experiments,
            "experiments": experiments,
            "experiment_types": experiment_types,
            "last_scan": datetime.now().isoformat()
        })
        
        return overview
    
    def analyze_experiment_folder(self, folder_path: Path) -> Dict[str, Any]:
        """Analyze individual experiment folder"""
        info = {
            "name": folder_path.name,
            "path": str(folder_path),
            "created_recently": False,
            "type": "unknown",
            "file_count": 0,
            "has_readme": False,
            "has_data": False,
            "has_images": False
        }
        
        try:
            # Check modification time (recent = last 7 days)
            mtime = folder_path.stat().st_mtime
            days_ago = (datetime.now().timestamp() - mtime) / 86400
            info["created_recently"] = days_ago <= 7
            
            # Analyze contents
            files = list(folder_path.glob("*"))
            info["file_count"] = len(files)
            
            for file_path in files:
                if file_path.is_file():
                    filename = file_path.name.lower()
                    
                    # Check for README
                    if filename.startswith("readme"):
                        info["has_readme"] = True
                    
                    # Check for data files
                    elif any(ext in filename for ext in [".csv", ".xlsx", ".json", ".txt"]):
                        info["has_data"] = True
                    
                    # Check for images
                    elif any(ext in filename for ext in [".png", ".jpg", ".jpeg", ".tiff"]):
                        info["has_images"] = True
            
            # Infer experiment type from folder name
            name_lower = folder_path.name.lower()
            if "pcr" in name_lower:
                info["type"] = "pcr"
            elif "gel" in name_lower:
                info["type"] = "gel_electrophoresis"
            elif "western" in name_lower or "blot" in name_lower:
                info["type"] = "western_blot"
            elif "cell" in name_lower or "culture" in name_lower:
                info["type"] = "cell_culture"
            elif "clone" in name_lower or "cloning" in name_lower:
                info["type"] = "cloning"
            
        except Exception as e:
            info["error"] = str(e)
        
        return info
    
    async def map_experiments(self, project_root: str) -> str:
        """Create detailed experiment relationship map"""
        # For now, simple implementation
        await self.scan_project(project_root)
        project_map = self.get_state("project_map", {})
        
        experiments = project_map.get("experiments", [])
        
        # Group by type
        type_groups = {}
        for exp in experiments:
            exp_type = exp.get("type", "unknown")
            if exp_type not in type_groups:
                type_groups[exp_type] = []
            type_groups[exp_type].append(exp["name"])
        
        mapping = "**Experiment Relationship Map:**\n\n"
        for exp_type, exp_list in type_groups.items():
            mapping += f"**{exp_type.replace('_', ' ').title()}** ({len(exp_list)} experiments):\n"
            for exp_name in exp_list:
                mapping += f"- {exp_name}\n"
            mapping += "\n"
        
        return mapping
    
    async def general_exploration(self, query: str, metadata: Dict[str, Any]) -> str:
        """Handle general exploration queries"""
        project_root = metadata.get("project_root", "data/alice_projects")
        
        # Quick project scan if we don't have state
        if not self.get_state("project_map"):
            await self.scan_project(project_root)
        
        project_map = self.get_state("project_map", {})
        
        exploration_prompt = f"""
        Based on this project structure:
        {json.dumps(project_map, indent=2)}
        
        User query: {query}
        
        Provide insights about the project structure, experiments, or suggest what to explore:
        """
        
        try:
            response = await self.llm.ainvoke(exploration_prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            return f"Project analysis available. {len(project_map.get('experiments', []))} experiments found. What would you like to explore?"
    
    def get_supported_tasks(self) -> List[str]:
        """Explorer handles project scanning and mapping"""
        return ["scan_project", "map_experiments", "analyze_experiment", "general_query"]