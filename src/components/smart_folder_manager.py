"""Smart folder creation and management for LabAcc Copilot"""

import os
import re
from datetime import datetime
from typing import List, Optional, Dict, Tuple
from pathlib import Path

from src.components.file_intent_parser import FileIntent


class SmartFolderManager:
    """Intelligently create and manage experiment folders"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        
        # Standardized naming conventions
        self.naming_conventions = {
            "pcr": "pcr_optimization",
            "qpcr": "qpcr_analysis", 
            "gel": "gel_electrophoresis",
            "western": "western_blot",
            "cell": "cell_culture",
            "cloning": "cloning_experiment",
            "protein": "protein_purification"
        }
        
        # Experiment sequence tracking
        self._sequence_cache = {}
    
    def get_existing_folders(self) -> List[str]:
        """Get list of existing experiment folders"""
        if not os.path.exists(self.project_root):
            os.makedirs(self.project_root, exist_ok=True)
            return []
        
        folders = []
        for item in os.listdir(self.project_root):
            if os.path.isdir(os.path.join(self.project_root, item)):
                if item.startswith("exp_"):
                    folders.append(item)
        
        return sorted(folders)
    
    def get_most_recent_folder(self) -> Optional[str]:
        """Get the most recently created experiment folder"""
        existing_folders = self.get_existing_folders()
        if not existing_folders:
            return None
        
        # Sort by creation time
        folder_times = []
        for folder in existing_folders:
            folder_path = os.path.join(self.project_root, folder)
            try:
                stat = os.stat(folder_path)
                folder_times.append((folder, stat.st_ctime))
            except:
                continue
        
        if folder_times:
            folder_times.sort(key=lambda x: x[1], reverse=True)
            return folder_times[0][0]
        
        # Fallback to lexicographic sorting (latest exp number)
        return existing_folders[-1]
    
    def get_next_sequence_number(self, experiment_type: Optional[str] = None) -> int:
        """Get next sequence number for experiment folders"""
        existing_folders = self.get_existing_folders()
        
        if not existing_folders:
            return 1
        
        # Extract sequence numbers
        sequence_numbers = []
        for folder in existing_folders:
            match = re.match(r'exp_(\d+)_', folder)
            if match:
                sequence_numbers.append(int(match.group(1)))
        
        if sequence_numbers:
            return max(sequence_numbers) + 1
        else:
            return 1
    
    def normalize_experiment_type(self, experiment_type: Optional[str]) -> str:
        """Normalize experiment type to standard naming"""
        if not experiment_type:
            return "experiment"
        
        exp_type_lower = experiment_type.lower()
        
        # Check for exact matches first
        for key, standardized in self.naming_conventions.items():
            if key in exp_type_lower:
                return standardized
        
        # Fallback to cleaned version of input
        normalized = re.sub(r'[^a-z0-9_]', '_', exp_type_lower)
        normalized = re.sub(r'_+', '_', normalized)  # Remove multiple underscores
        normalized = normalized.strip('_')
        
        return normalized or "experiment"
    
    def normalize_date(self, date_context: Optional[str]) -> str:
        """Normalize date to YYYY-MM-DD format"""
        if not date_context:
            return datetime.now().strftime("%Y-%m-%d")
        
        # Try to parse various date formats
        date_patterns = [
            r'(\d{4}-\d{2}-\d{2})',  # YYYY-MM-DD
            r'(\d{2}-\d{2})',        # MM-DD (assume current year)
            r'(\d{1,2}/\d{1,2})',    # M/D or MM/DD
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, date_context)
            if match:
                date_str = match.group(1)
                try:
                    if '-' in date_str and len(date_str) == 10:  # YYYY-MM-DD
                        return date_str
                    elif '-' in date_str and len(date_str) == 5:  # MM-DD
                        current_year = datetime.now().year
                        return f"{current_year}-{date_str}"
                    elif '/' in date_str:  # M/D format
                        current_year = datetime.now().year
                        month, day = date_str.split('/')
                        return f"{current_year}-{month.zfill(2)}-{day.zfill(2)}"
                except:
                    pass
        
        # Fallback to today
        return datetime.now().strftime("%Y-%m-%d")
    
    def generate_folder_name(
        self,
        intent: FileIntent,
        sequence_number: Optional[int] = None
    ) -> str:
        """Generate standardized folder name"""
        
        if sequence_number is None:
            sequence_number = self.get_next_sequence_number(intent.experiment_type)
        
        experiment_type = self.normalize_experiment_type(intent.experiment_type)
        date_str = self.normalize_date(intent.date_context)
        
        folder_name = f"exp_{sequence_number:03d}_{experiment_type}_{date_str}"
        
        return folder_name
    
    def check_folder_conflicts(self, folder_name: str) -> Tuple[bool, List[str]]:
        """Check if folder name conflicts with existing folders"""
        existing_folders = self.get_existing_folders()
        conflicts = []
        
        # Exact match
        if folder_name in existing_folders:
            conflicts.append(folder_name)
        
        # Similar names (same experiment type and date)
        base_pattern = folder_name.split('_')[2:]  # Remove exp_XXX part
        if len(base_pattern) >= 2:
            pattern_str = '_'.join(base_pattern)
            for folder in existing_folders:
                if pattern_str in folder:
                    conflicts.append(folder)
        
        return len(conflicts) > 0, conflicts
    
    def resolve_naming_conflict(
        self,
        base_folder_name: str,
        conflicts: List[str]
    ) -> str:
        """Resolve naming conflicts by adjusting sequence number"""
        
        # Extract base components
        parts = base_folder_name.split('_')
        if len(parts) < 4:
            # Fallback naming
            sequence = self.get_next_sequence_number()
            return f"exp_{sequence:03d}_experiment_{datetime.now().strftime('%Y-%m-%d')}"
        
        exp_type = parts[2]
        date_part = parts[3]
        
        # Find highest sequence number for this experiment type and date
        max_sequence = 0
        pattern = f"_{exp_type}_{date_part}"
        
        for conflict in conflicts:
            if pattern in conflict:
                match = re.match(r'exp_(\d+)_', conflict)
                if match:
                    max_sequence = max(max_sequence, int(match.group(1)))
        
        # Use next available sequence number
        new_sequence = max_sequence + 1
        return f"exp_{new_sequence:03d}_{exp_type}_{date_part}"
    
    async def create_experiment_folder(
        self,
        intent: FileIntent,
        auto_resolve_conflicts: bool = True,
        current_folder: Optional[str] = None
    ) -> Tuple[str, str]:  # (folder_name, full_path)
        """Create experiment folder based on parsed intent"""
        
        # Check if user wants to use current folder
        print(f"DEBUG SmartFolderManager: intent.folder_suggestion = {intent.folder_suggestion}")
        print(f"DEBUG SmartFolderManager: current_folder = {current_folder}")
        
        if intent.folder_suggestion and "current_folder" in intent.folder_suggestion.lower():
            if current_folder:
                folder_name = current_folder
                full_path = os.path.join(self.project_root, folder_name)
                print(f"DEBUG: Using current folder: {folder_name}")
                # Return existing folder without creating new one
                return folder_name, full_path
            else:
                print("DEBUG: No current folder set, creating new folder")
        
        # Check if user wants to use most recent folder
        if intent.folder_suggestion and "recent" in intent.folder_suggestion.lower():
            recent_folder = self.get_most_recent_folder()
            if recent_folder:
                folder_name = recent_folder
                full_path = os.path.join(self.project_root, folder_name)
                # Return existing folder without creating new one
                return folder_name, full_path
        
        # Generate initial folder name
        folder_name = intent.folder_suggestion
        
        # If no suggestion provided, generate one
        if not folder_name or folder_name == "exp_001_new_experiment":
            folder_name = self.generate_folder_name(intent)
        
        # Check for conflicts
        has_conflict, conflicts = self.check_folder_conflicts(folder_name)
        
        if has_conflict and auto_resolve_conflicts:
            folder_name = self.resolve_naming_conflict(folder_name, conflicts)
        
        # Create the folder
        full_path = os.path.join(self.project_root, folder_name)
        os.makedirs(full_path, exist_ok=True)
        
        # Create README.md with experiment context
        readme_path = os.path.join(full_path, "README.md")
        if not os.path.exists(readme_path):
            await self._create_experiment_readme(readme_path, intent, folder_name)
        
        return folder_name, full_path
    
    async def _create_experiment_readme(
        self,
        readme_path: str,
        intent: FileIntent,
        folder_name: str
    ) -> None:
        """Create initial README.md for experiment folder"""
        
        content = f"""# {folder_name.replace('_', ' ').title()}

**Created**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Type**: {intent.experiment_type or "General Experiment"}  
**Status**: In Progress

## Objective
{intent.files_description}

## Files
<!-- Files will be listed here automatically -->

## Results
<!-- Analysis results will be added here -->

## Notes
- Created from natural language request: "{intent.raw_message}"
- Operation type: {intent.operation_type}
- Analysis requested: {"Yes" if intent.analysis_request else "No"}

## Next Steps
<!-- AI suggestions will be added here -->
"""
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def get_folder_info(self, folder_name: str) -> Dict:
        """Get information about an experiment folder"""
        folder_path = os.path.join(self.project_root, folder_name)
        
        if not os.path.exists(folder_path):
            return {}
        
        # Count files by type
        file_counts = {}
        total_size = 0
        
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if os.path.isfile(file_path):
                ext = Path(file_name).suffix.lower()
                file_counts[ext] = file_counts.get(ext, 0) + 1
                total_size += os.path.getsize(file_path)
        
        # Read README if exists
        readme_path = os.path.join(folder_path, "README.md")
        readme_content = ""
        if os.path.exists(readme_path):
            try:
                with open(readme_path, 'r', encoding='utf-8') as f:
                    readme_content = f.read()[:500]  # First 500 chars
            except:
                pass
        
        return {
            "folder_name": folder_name,
            "full_path": folder_path,
            "file_counts": file_counts,
            "total_files": sum(file_counts.values()),
            "total_size_bytes": total_size,
            "readme_preview": readme_content,
            "created_date": datetime.fromtimestamp(os.path.getctime(folder_path)).strftime("%Y-%m-%d")
        }