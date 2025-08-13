"""
LLM-based Agent Evaluator (Agent-as-a-Judge)
Uses advanced LLM to evaluate agent responses against ground truth
"""

import asyncio
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from src.components.llm import get_llm_instance
from src.components.llm import get_evaluation_model_name


class TestCategory(Enum):
    CONTEXT_UNDERSTANDING = "context_understanding"
    FILE_ANALYSIS = "file_analysis"  
    EXPERIMENT_INSIGHTS = "experiment_insights"
    PROTOCOL_OPTIMIZATION = "protocol_optimization"
    MULTILINGUAL = "multilingual"


@dataclass
class EvaluationCriteria:
    accuracy: float      # Does response match ground truth facts?
    relevance: float     # Does response address user intent?
    completeness: float  # Are key details included?
    context_awareness: float  # Does agent understand experimental context?
    language_understanding: float  # For non-English queries
    
    @property
    def overall_score(self) -> float:
        """Calculate weighted overall score"""
        weights = {
            'accuracy': 0.3,
            'relevance': 0.25, 
            'completeness': 0.2,
            'context_awareness': 0.15,
            'language_understanding': 0.1
        }
        
        return (
            self.accuracy * weights['accuracy'] +
            self.relevance * weights['relevance'] +
            self.completeness * weights['completeness'] +
            self.context_awareness * weights['context_awareness'] +
            self.language_understanding * weights['language_understanding']
        )


@dataclass 
class TestCase:
    id: str
    category: TestCategory
    user_query: str
    language: str
    current_folder: Optional[str]
    selected_files: Optional[List[str]]
    expected_content: str
    expected_insights: List[str]
    ground_truth: Dict
    

@dataclass
class EvaluationResult:
    test_case_id: str
    criteria: EvaluationCriteria
    reasoning: Dict[str, str]  # Detailed reasoning for each criterion
    agent_response: str
    passed: bool
    timestamp: str


class AgentEvaluator:
    """Advanced LLM-based evaluator for agent responses"""
    
    def __init__(self, model_name: Optional[str] = None):
        resolved = model_name or get_evaluation_model_name()
        self.llm = get_llm_instance(resolved)
        
    def create_evaluation_prompt(self, test_case: TestCase, agent_response: str) -> str:
        """Create detailed evaluation prompt for LLM judge"""
        
        prompt = f"""You are an expert evaluator for laboratory AI assistants. Your task is to objectively evaluate the agent's response quality.

EVALUATION CONTEXT:
- User Query: "{test_case.user_query}"
- Language: {test_case.language}
- Current Folder: {test_case.current_folder or 'None'}
- Selected Files: {test_case.selected_files or 'None'}
- Test Category: {test_case.category.value}

GROUND TRUTH INFORMATION:
Expected Content: {test_case.expected_content}
Key Insights Agent Should Identify: {', '.join(test_case.expected_insights)}
Ground Truth Data: {json.dumps(test_case.ground_truth, indent=2)}

AGENT'S RESPONSE:
{agent_response}

EVALUATION CRITERIA:
Please score each criterion from 1-10 and provide detailed reasoning:

1. ACCURACY (1-10): How factually correct is the response compared to ground truth?
   - 10: Perfect accuracy, all facts correct
   - 7-9: Mostly accurate with minor errors
   - 4-6: Some accuracy but notable mistakes  
   - 1-3: Major factual errors or hallucinations

2. RELEVANCE (1-10): How well does the response address the user's intent?
   - 10: Directly answers the user's question
   - 7-9: Addresses most aspects of the question
   - 4-6: Partially relevant but misses key points
   - 1-3: Off-topic or misunderstood the question

3. COMPLETENESS (1-10): Are the important details and insights included?
   - 10: Comprehensive coverage of all key points
   - 7-9: Covers most important information
   - 4-6: Basic information but missing details
   - 1-3: Incomplete or superficial response

4. CONTEXT_AWARENESS (1-10): Does the agent demonstrate understanding of experimental context?
   - 10: Perfect understanding of lab context and implications
   - 7-9: Good contextual understanding with minor gaps
   - 4-6: Basic context awareness but lacks depth
   - 1-3: Poor contextual understanding

5. LANGUAGE_UNDERSTANDING (1-10): For non-English queries, did the agent understand correctly?
   - 10: Perfect language comprehension and appropriate response
   - 7-9: Good understanding with minor language issues
   - 4-6: Basic understanding but some language confusion
   - 1-3: Poor language comprehension
   - N/A: For English queries, rate as 10

RESPONSE FORMAT:
Provide your evaluation in this exact JSON format:
{{
    "accuracy": {{
        "score": <1-10>,
        "reasoning": "<detailed explanation>"
    }},
    "relevance": {{
        "score": <1-10>, 
        "reasoning": "<detailed explanation>"
    }},
    "completeness": {{
        "score": <1-10>,
        "reasoning": "<detailed explanation>"
    }},
    "context_awareness": {{
        "score": <1-10>,
        "reasoning": "<detailed explanation>"
    }},
    "language_understanding": {{
        "score": <1-10 or "N/A">,
        "reasoning": "<detailed explanation>"
    }},
    "overall_assessment": "<summary of strengths and weaknesses>",
    "critical_issues": ["<list of any critical problems>"],
    "recommendations": ["<suggestions for improvement>"]
}}"""

        return prompt
    
    async def evaluate_response(self, test_case: TestCase, agent_response: str) -> EvaluationResult:
        """Evaluate an agent response using LLM-as-a-Judge"""
        
        evaluation_prompt = self.create_evaluation_prompt(test_case, agent_response)
        
        try:
            # Get evaluation from LLM judge
            evaluation_text = await self.llm.ainvoke(evaluation_prompt)
            
            # Parse JSON response
            evaluation_data = json.loads(evaluation_text.content)
            
            # Extract scores
            criteria = EvaluationCriteria(
                accuracy=float(evaluation_data['accuracy']['score']),
                relevance=float(evaluation_data['relevance']['score']),
                completeness=float(evaluation_data['completeness']['score']),
                context_awareness=float(evaluation_data['context_awareness']['score']),
                language_understanding=float(evaluation_data['language_understanding']['score']) 
                    if evaluation_data['language_understanding']['score'] != "N/A" else 10.0
            )
            
            # Extract reasoning
            reasoning = {
                'accuracy': evaluation_data['accuracy']['reasoning'],
                'relevance': evaluation_data['relevance']['reasoning'], 
                'completeness': evaluation_data['completeness']['reasoning'],
                'context_awareness': evaluation_data['context_awareness']['reasoning'],
                'language_understanding': evaluation_data['language_understanding']['reasoning'],
                'overall_assessment': evaluation_data['overall_assessment'],
                'critical_issues': evaluation_data['critical_issues'],
                'recommendations': evaluation_data['recommendations']
            }
            
            # Determine pass/fail (threshold: 7.0)
            passed = criteria.overall_score >= 7.0
            
            return EvaluationResult(
                test_case_id=test_case.id,
                criteria=criteria,
                reasoning=reasoning,
                agent_response=agent_response,
                passed=passed,
                timestamp=str(asyncio.get_event_loop().time())
            )
            
        except Exception as e:
            # Fallback evaluation on error
            return EvaluationResult(
                test_case_id=test_case.id,
                criteria=EvaluationCriteria(0.0, 0.0, 0.0, 0.0, 0.0),
                reasoning={'error': f"Evaluation failed: {str(e)}"},
                agent_response=agent_response,
                passed=False,
                timestamp=str(asyncio.get_event_loop().time())
            )
    
    async def batch_evaluate(self, test_cases: List[TestCase], agent_responses: List[str]) -> List[EvaluationResult]:
        """Evaluate multiple responses in parallel"""
        
        tasks = [
            self.evaluate_response(test_case, response)
            for test_case, response in zip(test_cases, agent_responses)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_results = [r for r in results if isinstance(r, EvaluationResult)]
        
        return valid_results


# Convenience functions for common evaluation patterns
async def quick_evaluate(user_query: str, agent_response: str, expected_content: str, 
                        current_folder: str = None, language: str = "English") -> EvaluationResult:
    """Quick evaluation for simple test cases"""
    
    evaluator = AgentEvaluator()
    
    test_case = TestCase(
        id="quick_test",
        category=TestCategory.CONTEXT_UNDERSTANDING,
        user_query=user_query,
        language=language,
        current_folder=current_folder,
        selected_files=None,
        expected_content=expected_content,
        expected_insights=[],
        ground_truth={}
    )
    
    return await evaluator.evaluate_response(test_case, agent_response)


if __name__ == "__main__":
    # Example usage
    async def test_evaluator():
        test_case = TestCase(
            id="test_001",
            category=TestCategory.CONTEXT_UNDERSTANDING,
            user_query="What is in this folder?",
            language="English", 
            current_folder="exp_001_protocol_test",
            selected_files=None,
            expected_content="scRNAseq experiment data, dissociation protocol notes, cell analysis results",
            expected_insights=["immune cell enrichment problem", "epithelial cell loss"],
            ground_truth={"files": ["dissociation_notes.txt", "cell_markers_analysis.csv"]}
        )
        
        agent_response = "This folder contains files related to a single-cell RNA sequencing experiment..."
        
        evaluator = AgentEvaluator()
        result = await evaluator.evaluate_response(test_case, agent_response)
        
        print(f"Overall Score: {result.criteria.overall_score:.1f}")
        print(f"Passed: {result.passed}")
        print(f"Reasoning: {result.reasoning['overall_assessment']}")
    
    asyncio.run(test_evaluator())