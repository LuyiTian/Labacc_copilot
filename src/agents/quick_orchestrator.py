"""Quick orchestrator for testing - minimal LLM usage"""

from typing import Dict, Any
from datetime import datetime
import uuid

from .base_agent import BaseAgent, AgentRole, Task, Result


class QuickOrchestratorAgent(BaseAgent):
    """Simple orchestrator for testing - fast responses"""
    
    def __init__(self):
        super().__init__(AgentRole.ORCHESTRATOR, "siliconflow-qwen-8b")
    
    async def process(self, task: Task) -> Result:
        """Process task with quick, non-LLM responses"""
        start_time = datetime.now()
        
        try:
            response = await self.quick_response(task)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return Result(
                task_id=task.id,
                agent=self.name,
                success=True,
                content=response,
                metadata={"quick_mode": True},
                processing_time=processing_time
            )
            
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
    
    async def quick_response(self, task: Task) -> str:
        """Generate quick responses without LLM calls"""
        query = task.content.lower()
        current_folder = task.metadata.get("current_folder", "")
        
        # Quick pattern matching for demo
        if "scan" in query and "project" in query:
            return self.scan_response()
        elif "analyze" in query and current_folder and current_folder != "/":
            return self.analyze_response(current_folder)
        elif "research" in query:
            return self.research_response()
        elif "optimize" in query or "improve" in query:
            return self.optimize_response()
        elif any(greeting in query for greeting in ["hi", "hello", "hey", "good morning", "good afternoon"]):
            return self.greeting_response()
        else:
            return self.general_response()
    
    def scan_response(self) -> str:
        return """
🔍 **Project Scan Complete**

**Found 4 experiments:**
- exp_001_pcr_optimization (PCR experiment)
- exp_002_gel_electrophoresis (Gel analysis)
- exp_001_pcr_test (PCR testing)
- exp_001_type_2025-08-12 (Recent experiment)

**Recent Activity:** 2 experiments from today
**Success Rate:** Estimated 75% based on folder structure

🤖 *Multi-agent system operational - Explorer agent scanned your project structure.*
        """.strip()
    
    def analyze_response(self, folder: str) -> str:
        if "pcr" in folder.lower():
            return f"""
🧪 **PCR Analysis - {folder}**

**Protocol Review:**
- Standard PCR conditions identified
- GC-rich template optimizations noted
- Success rate: Good with DMSO addition

**Key Findings:**
- High GC buffer most effective
- Touchdown PCR showed clean products
- DMSO concentration critical

🤖 *Analyzer agent reviewed your PCR protocol.*
            """.strip()
        else:
            return f"""
📊 **Experiment Analysis - {folder}**

**Protocol Status:** Under review
**Data Quality:** Analyzing file structure
**Next Steps:** Detailed protocol comparison available

🤖 *Analyzer agent is ready to review your experimental data.*
            """.strip()
    
    def research_response(self) -> str:
        return """
📚 **Literature Research**

**Research Capabilities:**
- Scientific paper search
- Protocol validation
- Method optimization references

**Available Topics:**
- PCR optimization strategies
- Gel electrophoresis protocols
- Molecular biology troubleshooting

🤖 *Researcher agent ready for literature search (full research coming soon).*
        """.strip()
    
    def optimize_response(self) -> str:
        return """
⚡ **Optimization Suggestions**

**Strategic Recommendations:**
- Review successful protocol conditions
- Test parameter variations systematically
- Include proper controls for validation

**Best Practices:**
- Document all parameter changes
- Compare to successful experiments
- Use statistical analysis for optimization

🤖 *Advisor agent providing strategic guidance.*
        """.strip()
    
    def greeting_response(self) -> str:
        return """
👋 **Hello! Welcome to LabAcc Copilot v2.0**

I'm your AI-powered laboratory assistant with a multi-agent system ready to help you with:

**🔬 Available Agents:**
- 🔍 **Explorer**: Scan and map your experimental projects
- 🧪 **Analyzer**: Analyze protocols and identify patterns
- 📚 **Researcher**: Search scientific literature
- ⚡ **Advisor**: Provide optimization suggestions

**💡 Quick Start:**
- Say **"scan my project"** to see all your experiments
- Browse to an experiment folder and say **"analyze this"**
- Ask **"how can I optimize my PCR?"** for advice
- Try **"research gel electrophoresis methods"** for literature

How can I help you with your research today?
        """.strip()
    
    def general_response(self) -> str:
        return """
🤖 **LabAcc Copilot v2.0 - Multi-Agent System**

**Available Capabilities:**
- 🔍 **Explorer**: "scan my project" - Map all experiments
- 🧪 **Analyzer**: "analyze my data" - Protocol comparison
- 📚 **Researcher**: "research PCR methods" - Literature search  
- ⚡ **Advisor**: "optimize my protocol" - Strategic suggestions

**Quick Commands:**
- Ask about specific experiments
- Request protocol analysis
- Get optimization recommendations

*Try: "scan my project" or "analyze my PCR experiment"*
        """.strip()
    
    def get_supported_tasks(self):
        return ["general_query", "scan_project", "analyze_experiment", "research_problem", "suggest_optimization"]