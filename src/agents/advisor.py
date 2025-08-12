"""Advisor agent - provides optimization suggestions and strategic planning"""

from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from .base_agent import BaseAgent, AgentRole, Task, Result


class AdvisorAgent(BaseAgent):
    """Provides optimization suggestions and strategic planning"""
    
    def __init__(self):
        super().__init__(AgentRole.ADVISOR, "siliconflow-qwen-30b")
    
    async def process(self, task: Task) -> Result:
        """Process advisory tasks"""
        start_time = datetime.now()
        
        try:
            if task.type == "suggest_optimization":
                result_content = await self.suggest_optimizations(task.content, task.metadata)
            else:
                result_content = await self.general_advice(task.content, task.metadata)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return Result(
                task_id=task.id,
                agent=self.name,
                success=True,
                content=result_content,
                metadata={"advice_type": task.type},
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            return Result(
                task_id=task.id,
                agent=self.name,
                success=False,
                content=f"Advisory failed: {str(e)}",
                metadata={"error": str(e)},
                processing_time=processing_time
            )
    
    async def suggest_optimizations(self, query: str, metadata: Dict[str, Any]) -> str:
        """Provide specific optimization suggestions"""
        current_folder = metadata.get("current_folder", "")
        previous_result = metadata.get("previous_result", "")
        
        context = f"""
Query: {query}
Current experiment: {current_folder}
Previous analysis: {previous_result}
"""
        
        optimization_prompt = f"""
Based on this experimental context:
{context}

Provide specific, actionable optimization suggestions:

1. **Protocol Improvements**: What specific steps can be optimized?
2. **Parameter Adjustments**: Which variables should be modified?
3. **Controls**: What controls are essential for validation?
4. **Next Steps**: What experiments should be done next?
5. **Risk Mitigation**: What could go wrong and how to prevent it?

Be practical and specific with recommendations.
        """
        
        try:
            response = await self.llm.ainvoke(optimization_prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            return self.fallback_optimization_advice(query)
    
    def fallback_optimization_advice(self, query: str) -> str:
        """Provide fallback optimization advice"""
        return f"""
**Optimization Strategy:**

For experimental optimization, consider:

**🔧 Protocol Optimization:**
- Standardize critical parameters
- Include proper controls
- Document all variables
- Replicate successful conditions

**📊 Data Quality:**
- Ensure adequate sample size
- Use consistent measurement methods
- Track environmental conditions
- Record all modifications

**🔍 Next Steps:**
- Identify the most variable step
- Test one variable at a time
- Compare to successful protocols
- Document all changes

*Share specific experimental details for targeted optimization suggestions.*
        """.strip()
    
    async def general_advice(self, query: str, metadata: Dict[str, Any]) -> str:
        """Handle general advisory queries"""
        advice_prompt = f"""
User query: {query}

Provide strategic advice for this laboratory research question.
Focus on:
1. Best practices
2. Strategic planning
3. Resource optimization
4. Risk assessment
5. Next steps

Be practical and actionable.
        """
        
        try:
            response = await self.llm.ainvoke(advice_prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            return f"""
**Strategic Guidance:**

I can provide advice on:

**🎯 Experimental Strategy:**
- Protocol design and optimization
- Control selection and validation
- Resource planning and allocation

**📈 Project Planning:**
- Next experiment prioritization
- Risk assessment and mitigation
- Success metrics definition

**🛠️ Best Practices:**
- Documentation standards
- Quality control measures
- Troubleshooting approaches

*Ask specific questions about your experimental strategy for detailed guidance.*
            """.strip()
    
    def get_supported_tasks(self) -> List[str]:
        """Advisor handles optimization and strategic planning"""
        return ["suggest_optimization", "general_query"]