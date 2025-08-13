"""
README Memory System for LabAcc Copilot
Simple markdown-based memory without YAML - robust and human-friendly
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ExperimentMemory:
    """Structured representation of experiment README memory"""
    experiment_id: str
    status: str
    created: Optional[str]
    updated: Optional[str]
    overview: Dict[str, str]  # motivation, key_question, hypothesis
    files: List[Dict[str, str]]  # file registry
    parameters: Dict[str, Any]  # experimental parameters
    results: Dict[str, Any]  # results and statistics
    insights: List[Dict[str, str]]  # timestamped insights
    methods: str  # methods description
    notes: List[str]  # notes and observations
    change_log: List[Dict[str, str]]  # change history
    raw_content: str  # original README content


class ReadmeParser:
    """Parse README.md files without YAML - simple and robust"""
    
    def parse(self, readme_content: str) -> ExperimentMemory:
        """Parse README content into structured memory"""
        
        # Initialize memory structure
        memory = ExperimentMemory(
            experiment_id="",
            status="unknown",
            created=None,
            updated=None,
            overview={},
            files=[],
            parameters={},
            results={},
            insights=[],
            methods="",
            notes=[],
            change_log=[],
            raw_content=readme_content
        )
        
        # Extract metadata from header
        memory.experiment_id = self._extract_experiment_id(readme_content)
        memory.status = self._extract_status(readme_content)
        memory.created = self._extract_date(readme_content, "Created")
        memory.updated = self._extract_date(readme_content, "Updated")
        
        # Parse sections
        sections = self._split_into_sections(readme_content)
        
        # Parse each section
        if "overview" in sections:
            memory.overview = self._parse_overview(sections["overview"])
        
        if "files" in sections:
            memory.files = self._parse_files_table(sections["files"])
        
        if "parameters" in sections:
            memory.parameters = self._parse_parameters(sections["parameters"])
        
        if "results" in sections:
            memory.results = self._parse_results(sections["results"])
        
        if "insights" in sections:
            memory.insights = self._parse_insights(sections["insights"])
        
        if "methods" in sections:
            memory.methods = sections["methods"].strip()
        
        if "notes" in sections:
            memory.notes = self._parse_notes(sections["notes"])
        
        if "change log" in sections:
            memory.change_log = self._parse_change_log(sections["change log"])
        
        return memory
    
    def _extract_experiment_id(self, content: str) -> str:
        """Extract experiment ID from README"""
        # Look for ID: exp_XXX pattern
        match = re.search(r'\*\*ID:\*\*\s*(exp_\d+_\w+)', content)
        if match:
            return match.group(1)
        
        # Try to extract from title
        match = re.search(r'#\s+Experiment:\s*(.+)', content)
        if match:
            # Convert title to ID format
            title = match.group(1).lower()
            title = re.sub(r'[^a-z0-9_]', '_', title)
            return f"exp_{title}"
        
        return "exp_unknown"
    
    def _extract_status(self, content: str) -> str:
        """Extract experiment status"""
        match = re.search(r'\*\*Status:\*\*\s*(\w+)', content, re.IGNORECASE)
        if match:
            return match.group(1).lower()
        return "unknown"
    
    def _extract_date(self, content: str, field: str) -> Optional[str]:
        """Extract date field from README"""
        pattern = rf'\*\*{field}:\*\*\s*([\d\-T:\.]+)'
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1)
        return None
    
    def _split_into_sections(self, content: str) -> Dict[str, str]:
        """Split README into sections by headers"""
        sections = {}
        current_section = None
        current_content = []
        
        lines = content.split('\n')
        
        for line in lines:
            # Check if this is a section header
            if line.startswith('##'):
                # Save previous section
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                
                # Start new section
                header = line.lstrip('#').strip().lower()
                # Remove emojis and clean up
                header = re.sub(r'[^\w\s]', '', header).strip()
                current_section = header
                current_content = []
            elif current_section:
                current_content.append(line)
        
        # Save last section
        if current_section:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def _parse_overview(self, content: str) -> Dict[str, str]:
        """Parse overview section"""
        overview = {}
        
        # Extract motivation
        match = re.search(r'\*\*Motivation:\*\*\s*(.+?)(?:\n|$)', content)
        if match:
            overview['motivation'] = match.group(1).strip()
        
        # Extract key question
        match = re.search(r'\*\*Key Question:\*\*\s*(.+?)(?:\n|$)', content)
        if match:
            overview['key_question'] = match.group(1).strip()
        
        # Extract hypothesis
        match = re.search(r'\*\*Hypothesis:\*\*\s*(.+?)(?:\n|$)', content)
        if match:
            overview['hypothesis'] = match.group(1).strip()
        
        return overview
    
    def _parse_files_table(self, content: str) -> List[Dict[str, str]]:
        """Parse files table from markdown"""
        files = []
        lines = content.split('\n')
        
        in_table = False
        for line in lines:
            # Skip header and separator lines
            if '|' not in line:
                continue
            if '---' in line:
                in_table = True
                continue
            if not in_table:
                continue
            
            # Parse table row
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 5:  # File | Type | Size | Summary | Added
                # Skip empty first/last elements from split
                parts = [p for p in parts if p]
                if len(parts) >= 4 and parts[0] not in ['File', 'file']:
                    files.append({
                        'name': parts[0],
                        'type': parts[1] if len(parts) > 1 else '',
                        'size': parts[2] if len(parts) > 2 else '',
                        'summary': parts[3] if len(parts) > 3 else '',
                        'added': parts[4] if len(parts) > 4 else ''
                    })
        
        return files
    
    def _parse_parameters(self, content: str) -> Dict[str, Any]:
        """Parse parameters section"""
        parameters = {
            'independent': {},
            'dependent': {},
            'constants': {}
        }
        
        current_type = None
        lines = content.split('\n')
        
        for line in lines:
            # Check for parameter type headers
            if 'Independent Variable' in line:
                current_type = 'independent'
            elif 'Dependent Variable' in line:
                current_type = 'dependent'
            elif 'Constants:' in line or 'Constant:' in line:
                current_type = 'constants'
            # Parse parameter lines (- key: value format)
            elif line.strip().startswith('-') and ':' in line and current_type:
                match = re.match(r'-\s*([^:]+):\s*(.+)', line.strip())
                if match:
                    key = match.group(1).strip()
                    value = match.group(2).strip()
                    parameters[current_type][key] = value
        
        return parameters
    
    def _parse_results(self, content: str) -> Dict[str, Any]:
        """Parse results section"""
        results = {
            'key_findings': [],
            'statistics': {}
        }
        
        lines = content.split('\n')
        current_subsection = None
        
        for line in lines:
            # Check for subsections
            if 'Key Finding' in line:
                current_subsection = 'findings'
            elif 'Statistical' in line or 'Statistic' in line:
                current_subsection = 'statistics'
            # Parse findings (bullet points)
            elif line.strip().startswith('-') and current_subsection == 'findings':
                finding = line.strip()[1:].strip()
                results['key_findings'].append(finding)
            # Parse statistics (key: value pairs)
            elif ':' in line and current_subsection == 'statistics':
                match = re.match(r'-?\s*([^:]+):\s*(.+)', line.strip())
                if match:
                    key = match.group(1).strip()
                    value = match.group(2).strip()
                    results['statistics'][key] = value
        
        return results
    
    def _parse_insights(self, content: str) -> List[Dict[str, str]]:
        """Parse insights section"""
        insights = []
        lines = content.split('\n')
        
        for line in lines:
            # Parse insights with timestamps (- **timestamp** - insight text)
            if line.strip().startswith('-'):
                # Try to extract timestamp
                match = re.match(r'-\s*\*\*([\d\-T:\.]+)\*\*\s*[-–]\s*(.+)', line.strip())
                if match:
                    insights.append({
                        'timestamp': match.group(1),
                        'insight': match.group(2).strip()
                    })
                else:
                    # Insight without timestamp
                    insight_text = line.strip()[1:].strip()
                    if insight_text:
                        insights.append({
                            'timestamp': datetime.now().isoformat(),
                            'insight': insight_text
                        })
        
        return insights
    
    def _parse_notes(self, content: str) -> List[str]:
        """Parse notes section"""
        notes = []
        lines = content.split('\n')
        
        for line in lines:
            if line.strip().startswith('-'):
                note = line.strip()[1:].strip()
                if note:
                    notes.append(note)
        
        return notes
    
    def _parse_change_log(self, content: str) -> List[Dict[str, str]]:
        """Parse change log section"""
        changes = []
        lines = content.split('\n')
        
        for line in lines:
            # Parse change entries (- **timestamp** - change description)
            if line.strip().startswith('-'):
                match = re.match(r'-\s*\*\*([\d\-T:\.]+)\*\*\s*[-–]\s*(.+)', line.strip())
                if match:
                    changes.append({
                        'timestamp': match.group(1),
                        'change': match.group(2).strip()
                    })
        
        return changes


class ReadmeWriter:
    """Write structured memory back to README format"""
    
    def write(self, memory: ExperimentMemory) -> str:
        """Convert memory structure to README markdown"""
        
        lines = []
        
        # Header
        lines.append(f"# Experiment: {memory.experiment_id}")
        lines.append("")
        lines.append(f"**Status:** {memory.status.title()}")
        if memory.created:
            lines.append(f"**Created:** {memory.created}")
        if memory.updated:
            lines.append(f"**Updated:** {memory.updated}")
        lines.append(f"**ID:** {memory.experiment_id}")
        lines.append("")
        
        # Overview
        if memory.overview:
            lines.append("## Overview")
            lines.append("")
            if 'motivation' in memory.overview:
                lines.append(f"**Motivation:** {memory.overview['motivation']}")
            if 'key_question' in memory.overview:
                lines.append(f"**Key Question:** {memory.overview['key_question']}")
            if 'hypothesis' in memory.overview:
                lines.append(f"**Hypothesis:** {memory.overview['hypothesis']}")
            lines.append("")
        
        # Files
        if memory.files:
            lines.append("## Files")
            lines.append("")
            lines.append("| File | Type | Size | Summary | Added |")
            lines.append("|------|------|------|---------|-------|")
            for file in memory.files:
                lines.append(f"| {file.get('name', '')} | {file.get('type', '')} | "
                           f"{file.get('size', '')} | {file.get('summary', '')} | "
                           f"{file.get('added', '')} |")
            lines.append("")
        
        # Parameters
        if memory.parameters:
            lines.append("## Parameters")
            lines.append("")
            
            if memory.parameters.get('independent'):
                lines.append("**Independent Variables:**")
                for key, value in memory.parameters['independent'].items():
                    lines.append(f"- {key}: {value}")
                lines.append("")
            
            if memory.parameters.get('dependent'):
                lines.append("**Dependent Variables:**")
                for key, value in memory.parameters['dependent'].items():
                    lines.append(f"- {key}: {value}")
                lines.append("")
            
            if memory.parameters.get('constants'):
                lines.append("**Constants:**")
                for key, value in memory.parameters['constants'].items():
                    lines.append(f"- {key}: {value}")
                lines.append("")
        
        # Results
        if memory.results:
            lines.append("## Results")
            lines.append("")
            
            if memory.results.get('key_findings'):
                lines.append("**Key Findings:**")
                for finding in memory.results['key_findings']:
                    lines.append(f"- {finding}")
                lines.append("")
            
            if memory.results.get('statistics'):
                lines.append("**Statistical Summary:**")
                for key, value in memory.results['statistics'].items():
                    lines.append(f"- {key}: {value}")
                lines.append("")
        
        # Insights
        if memory.insights:
            lines.append("## Insights")
            lines.append("")
            for insight in memory.insights:
                lines.append(f"- **{insight.get('timestamp', '')}** - {insight.get('insight', '')}")
            lines.append("")
        
        # Methods
        if memory.methods:
            lines.append("## Methods")
            lines.append("")
            lines.append(memory.methods)
            lines.append("")
        
        # Notes
        if memory.notes:
            lines.append("## Notes")
            lines.append("")
            for note in memory.notes:
                lines.append(f"- {note}")
            lines.append("")
        
        # Change Log
        if memory.change_log:
            lines.append("## Change Log")
            lines.append("")
            for change in memory.change_log:
                lines.append(f"- **{change.get('timestamp', '')}** - {change.get('change', '')}")
            lines.append("")
        
        return '\n'.join(lines)


class MemoryManager:
    """Manage README memories for experiments"""
    
    def __init__(self, project_root: str = None):
        """Initialize memory manager"""
        if project_root is None:
            project_root = os.path.join(os.getcwd(), "data", "alice_projects")
        self.project_root = Path(project_root)
        self.parser = ReadmeParser()
        self.writer = ReadmeWriter()
        
        # Ensure project root exists
        self.project_root.mkdir(parents=True, exist_ok=True)
    
    def read_memory(self, experiment_id: str) -> Optional[ExperimentMemory]:
        """Read experiment memory from README"""
        readme_path = self.project_root / experiment_id / "README.md"
        
        if not readme_path.exists():
            logger.warning(f"README not found for {experiment_id}")
            return None
        
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            memory = self.parser.parse(content)
            # Ensure experiment ID is set
            if not memory.experiment_id:
                memory.experiment_id = experiment_id
            
            return memory
        
        except Exception as e:
            logger.error(f"Error reading memory for {experiment_id}: {e}")
            return None
    
    def write_memory(self, memory: ExperimentMemory) -> bool:
        """Write memory back to README"""
        if not memory.experiment_id:
            logger.error("Cannot write memory without experiment ID")
            return False
        
        exp_dir = self.project_root / memory.experiment_id
        exp_dir.mkdir(parents=True, exist_ok=True)
        
        readme_path = exp_dir / "README.md"
        
        try:
            # Update timestamp
            memory.updated = datetime.now().isoformat()
            
            # Convert to markdown
            content = self.writer.write(memory)
            
            # Write to file
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Written memory for {memory.experiment_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error writing memory for {memory.experiment_id}: {e}")
            return False
    
    def update_section(self, experiment_id: str, section: str, content: Any) -> bool:
        """Update a specific section of the README"""
        # Read current memory
        memory = self.read_memory(experiment_id)
        
        if memory is None:
            # Create new memory
            memory = ExperimentMemory(
                experiment_id=experiment_id,
                status="active",
                created=datetime.now().isoformat(),
                updated=datetime.now().isoformat(),
                overview={},
                files=[],
                parameters={},
                results={},
                insights=[],
                methods="",
                notes=[],
                change_log=[],
                raw_content=""
            )
        
        # Update the specific section
        section_lower = section.lower()
        
        if section_lower == "overview":
            memory.overview.update(content if isinstance(content, dict) else {})
        elif section_lower == "files":
            if isinstance(content, list):
                memory.files = content
            elif isinstance(content, dict) and content.get('action') == 'append':
                memory.files.append(content.get('entry', {}))
        elif section_lower == "parameters":
            memory.parameters.update(content if isinstance(content, dict) else {})
        elif section_lower == "results":
            if isinstance(content, dict):
                memory.results.update(content)
        elif section_lower == "insights":
            if isinstance(content, list):
                memory.insights = content
            elif isinstance(content, dict) and content.get('action') == 'append':
                memory.insights.append({
                    'timestamp': datetime.now().isoformat(),
                    'insight': content.get('insight', '')
                })
        elif section_lower == "methods":
            memory.methods = str(content)
        elif section_lower == "notes":
            if isinstance(content, list):
                memory.notes = content
            elif isinstance(content, str):
                memory.notes.append(content)
        
        # Add to change log
        memory.change_log.append({
            'timestamp': datetime.now().isoformat(),
            'change': f"Updated {section} section"
        })
        
        # Write back
        return self.write_memory(memory)
    
    def search_memories(self, query: str, scope: str = "all") -> List[Dict[str, Any]]:
        """Search across README memories"""
        results = []
        
        # Get all experiment directories
        exp_dirs = [d for d in self.project_root.iterdir() 
                   if d.is_dir() and d.name.startswith("exp_")]
        
        for exp_dir in exp_dirs:
            readme_path = exp_dir / "README.md"
            if not readme_path.exists():
                continue
            
            try:
                with open(readme_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Simple text search
                if query.lower() in content.lower():
                    # Find matching lines
                    matches = []
                    for line in content.split('\n'):
                        if query.lower() in line.lower():
                            matches.append(line.strip())
                    
                    results.append({
                        'experiment_id': exp_dir.name,
                        'matches': matches[:3],  # First 3 matches
                        'readme_path': str(readme_path)
                    })
            
            except Exception as e:
                logger.error(f"Error searching {exp_dir.name}: {e}")
        
        return results
    
    def create_experiment_readme(self, experiment_id: str, title: str = None) -> bool:
        """Create a new experiment with README template"""
        exp_dir = self.project_root / experiment_id
        exp_dir.mkdir(parents=True, exist_ok=True)
        
        # Create initial memory
        memory = ExperimentMemory(
            experiment_id=experiment_id,
            status="active",
            created=datetime.now().isoformat(),
            updated=datetime.now().isoformat(),
            overview={
                'motivation': 'To be filled',
                'key_question': 'What is the research question?',
                'hypothesis': 'Initial hypothesis'
            },
            files=[],
            parameters={
                'independent': {},
                'dependent': {},
                'constants': {}
            },
            results={
                'key_findings': [],
                'statistics': {}
            },
            insights=[],
            methods="Experimental protocol to be documented",
            notes=[],
            change_log=[{
                'timestamp': datetime.now().isoformat(),
                'change': 'Experiment initialized'
            }],
            raw_content=""
        )
        
        if title:
            memory.overview['motivation'] = f"Experiment: {title}"
        
        return self.write_memory(memory)