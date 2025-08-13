"""
Test Case Generator for LabAcc Copilot Agent Evaluation
Generates comprehensive test scenarios using Bob's scRNAseq project as ground truth
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict

from .evaluator_agent import TestCase, TestCategory


class TestCaseGenerator:
    """Generates comprehensive test cases for agent evaluation"""
    
    def __init__(self, data_dir: str = "data/bob_projects"):
        self.data_dir = Path(data_dir)
        self.ground_truth = self._load_ground_truth()
    
    def _load_ground_truth(self) -> Dict:
        """Load ground truth information about Bob's scRNAseq project"""
        
        ground_truth = {
            "project_overview": {
                "title": "Lung Cancer scRNAseq Optimization",
                "cell_types": ["tumor_epithelial", "immune_cells", "fibroblasts", "endothelial"],
                "main_problem": "epithelial cell loss during dissociation",
                "optimization_strategy": "cold pre-digestion"
            },
            "experiments": {
                "exp_001_protocol_test": {
                    "files": [
                        "README.md",
                        "dissociation_notes.txt", 
                        "cell_markers_analysis.csv",
                        "raw_data_qc.csv"
                    ],
                    "key_findings": [
                        "Only 8% tumor epithelial cells captured",
                        "65% immune cells (severe bias)", 
                        "High cell stress (16.8% mitochondrial genes)",
                        "Over-digestion suspected at 45min/37°C"
                    ],
                    "problems": [
                        "immune enrichment bias",
                        "epithelial cell fragility",
                        "incomplete mechanical disruption"
                    ]
                },
                "exp_002_optimization": {
                    "files": [
                        "README.md",
                        "protocol_draft.md"
                    ],
                    "status": "planned",
                    "key_innovations": [
                        "Cold pre-digestion at 4°C for 15 minutes",
                        "Shortened warm digestion (20-25 min vs 45 min)", 
                        "Enhanced mechanical disruption",
                        "Real-time monitoring every 10 minutes"
                    ]
                }
            }
        }
        
        return ground_truth
    
    def generate_context_understanding_tests(self) -> List[TestCase]:
        """Generate tests for folder/file context understanding"""
        
        tests = []
        
        # English context tests
        english_queries = [
            "What is in this folder?",
            "What files are here?", 
            "Tell me about this experiment",
            "What's the content of this directory?",
            "Show me what's in this folder"
        ]
        
        # Chinese equivalent queries
        chinese_queries = [
            "这个文件夹里有什么？",
            "这里有什么文件？",
            "告诉我这个实验的情况",
            "这个目录里有什么内容？", 
            "给我看看这个文件夹里有什么"
        ]
        
        # Test for exp_001
        for i, (en_query, cn_query) in enumerate(zip(english_queries, chinese_queries)):
            # English test
            tests.append(TestCase(
                id=f"context_en_{i+1}",
                category=TestCategory.CONTEXT_UNDERSTANDING,
                user_query=en_query,
                language="English",
                current_folder="exp_001_protocol_test",
                selected_files=None,
                expected_content="scRNAseq experiment files including dissociation protocol notes, cell analysis results, and quality control data",
                expected_insights=self.ground_truth["experiments"]["exp_001_protocol_test"]["key_findings"][:2],
                ground_truth=self.ground_truth["experiments"]["exp_001_protocol_test"]
            ))
            
            # Chinese test  
            tests.append(TestCase(
                id=f"context_cn_{i+1}",
                category=TestCategory.MULTILINGUAL,
                user_query=cn_query, 
                language="Chinese",
                current_folder="exp_001_protocol_test",
                selected_files=None,
                expected_content="scRNAseq实验文件，包括解离协议记录、细胞分析结果和质量控制数据",
                expected_insights=self.ground_truth["experiments"]["exp_001_protocol_test"]["key_findings"][:2],
                ground_truth=self.ground_truth["experiments"]["exp_001_protocol_test"]
            ))
        
        return tests
    
    def generate_file_analysis_tests(self) -> List[TestCase]:
        """Generate tests for specific file analysis"""
        
        tests = []
        
        # File-specific queries
        file_queries = {
            "dissociation_notes.txt": {
                "english": [
                    "What is in this file?",
                    "Tell me about this file",
                    "Analyze this file content",
                    "What does this file contain?"
                ],
                "chinese": [
                    "这个文件里是什么？",
                    "告诉我这个文件的内容",
                    "分析这个文件的内容",
                    "这个文件包含什么？"
                ],
                "expected_content": "Dissociation protocol notes documenting tissue processing, observations, and technical issues",
                "expected_insights": [
                    "45-minute digestion time caused over-digestion",
                    "Large epithelial cell clumps were resistant to dissociation",
                    "Cell viability was low at 76%"
                ]
            },
            "cell_markers_analysis.csv": {
                "english": [
                    "What's in this CSV file?",
                    "Analyze this data file",
                    "Tell me about this analysis"
                ],
                "chinese": [
                    "这个CSV文件里是什么？",
                    "分析这个数据文件",
                    "告诉我这个分析的内容"
                ],
                "expected_content": "Single-cell RNA sequencing analysis results with cell type classifications and marker genes",
                "expected_insights": [
                    "Only 8.2% tumor epithelial cells captured",
                    "65.5% immune cells total (T cells, NK cells, macrophages)",
                    "High stress response genes in epithelial cells"
                ]
            }
        }
        
        for filename, queries_data in file_queries.items():
            for i, (en_query, cn_query) in enumerate(zip(queries_data["english"], queries_data["chinese"])):
                # English test
                tests.append(TestCase(
                    id=f"file_analysis_en_{filename}_{i+1}",
                    category=TestCategory.FILE_ANALYSIS,
                    user_query=en_query,
                    language="English",
                    current_folder="exp_001_protocol_test",
                    selected_files=[filename],
                    expected_content=queries_data["expected_content"],
                    expected_insights=queries_data["expected_insights"],
                    ground_truth={"target_file": filename}
                ))
                
                # Chinese test
                tests.append(TestCase(
                    id=f"file_analysis_cn_{filename}_{i+1}",
                    category=TestCategory.MULTILINGUAL,
                    user_query=cn_query,
                    language="Chinese", 
                    current_folder="exp_001_protocol_test",
                    selected_files=[filename],
                    expected_content=queries_data["expected_content"],
                    expected_insights=queries_data["expected_insights"],
                    ground_truth={"target_file": filename}
                ))
        
        return tests
    
    def generate_experiment_insights_tests(self) -> List[TestCase]:
        """Generate tests for experimental insight and problem identification"""
        
        tests = []
        
        insight_queries = {
            "english": [
                "What went wrong with this experiment?",
                "What problems do you see?", 
                "Identify issues in this experiment",
                "What needs to be optimized?",
                "Analyze the experimental problems"
            ],
            "chinese": [
                "这个实验出了什么问题？",
                "你看到了什么问题？",
                "识别这个实验中的问题",
                "什么需要优化？",
                "分析实验中的问题"
            ]
        }
        
        expected_problems = [
            "Severe immune cell enrichment bias (65% vs expected 35%)",
            "Poor epithelial cell recovery (8% vs expected 30%)",
            "Over-digestion causing cell stress and death",
            "Inadequate mechanical disruption of epithelial clumps"
        ]
        
        for i, (en_query, cn_query) in enumerate(zip(insight_queries["english"], insight_queries["chinese"])):
            # English test
            tests.append(TestCase(
                id=f"insights_en_{i+1}",
                category=TestCategory.EXPERIMENT_INSIGHTS,
                user_query=en_query,
                language="English",
                current_folder="exp_001_protocol_test",
                selected_files=None,
                expected_content="Analysis of experimental problems including cell type bias, over-digestion, and protocol limitations",
                expected_insights=expected_problems,
                ground_truth=self.ground_truth["experiments"]["exp_001_protocol_test"]
            ))
            
            # Chinese test
            tests.append(TestCase(
                id=f"insights_cn_{i+1}",
                category=TestCategory.MULTILINGUAL,
                user_query=cn_query,
                language="Chinese",
                current_folder="exp_001_protocol_test", 
                selected_files=None,
                expected_content="实验问题分析，包括细胞类型偏差、过度消化和协议限制",
                expected_insights=expected_problems,
                ground_truth=self.ground_truth["experiments"]["exp_001_protocol_test"]
            ))
        
        return tests
    
    def generate_protocol_optimization_tests(self) -> List[TestCase]:
        """Generate tests for protocol optimization recommendations"""
        
        tests = []
        
        optimization_queries = {
            "english": [
                "How should we optimize this protocol?",
                "What improvements do you recommend?",
                "How can we fix these problems?",
                "Suggest protocol modifications",
                "What changes should we make?"
            ],
            "chinese": [
                "我们应该如何优化这个协议？", 
                "你推荐什么改进？",
                "我们如何解决这些问题？",
                "建议协议修改",
                "我们应该做什么改变？"
            ]
        }
        
        expected_optimizations = [
            "Cold pre-digestion at 4°C for 15 minutes",
            "Reduce warm digestion time to 20-25 minutes",
            "Enhanced mechanical disruption with additional gentleMACS cycles",
            "Real-time monitoring every 10 minutes",
            "DNase treatment to reduce ambient RNA"
        ]
        
        for i, (en_query, cn_query) in enumerate(zip(optimization_queries["english"], optimization_queries["chinese"])):
            # English test
            tests.append(TestCase(
                id=f"optimization_en_{i+1}",
                category=TestCategory.PROTOCOL_OPTIMIZATION,
                user_query=en_query,
                language="English",
                current_folder="exp_001_protocol_test",
                selected_files=None,
                expected_content="Protocol optimization recommendations based on identified problems",
                expected_insights=expected_optimizations,
                ground_truth={
                    "optimization_plan": self.ground_truth["experiments"]["exp_002_optimization"]["key_innovations"]
                }
            ))
            
            # Chinese test  
            tests.append(TestCase(
                id=f"optimization_cn_{i+1}",
                category=TestCategory.MULTILINGUAL,
                user_query=cn_query,
                language="Chinese",
                current_folder="exp_001_protocol_test",
                selected_files=None,
                expected_content="基于已识别问题的协议优化建议",
                expected_insights=expected_optimizations,
                ground_truth={
                    "optimization_plan": self.ground_truth["experiments"]["exp_002_optimization"]["key_innovations"]
                }
            ))
        
        return tests
    
    def generate_edge_case_tests(self) -> List[TestCase]:
        """Generate edge case and robustness tests"""
        
        tests = []
        
        # Ambiguous queries that require context
        ambiguous_queries = [
            "Analyze",
            "Check",
            "Look at this", 
            "What's wrong?",
            "Help"
        ]
        
        for i, query in enumerate(ambiguous_queries):
            tests.append(TestCase(
                id=f"edge_ambiguous_{i+1}",
                category=TestCategory.CONTEXT_UNDERSTANDING,
                user_query=query,
                language="English",
                current_folder="exp_001_protocol_test",
                selected_files=["dissociation_notes.txt"],
                expected_content="Agent should understand context and provide relevant analysis",
                expected_insights=["Agent asks for clarification or makes reasonable assumptions based on context"],
                ground_truth={"test_type": "ambiguous_query"}
            ))
        
        # Mixed language queries
        mixed_queries = [
            "Tell me about 这个实验",
            "What's the 问题 with this protocol?",
            "Analyze the 细胞 data"
        ]
        
        for i, query in enumerate(mixed_queries):
            tests.append(TestCase(
                id=f"edge_mixed_{i+1}",
                category=TestCategory.MULTILINGUAL,
                user_query=query,
                language="Mixed",
                current_folder="exp_001_protocol_test", 
                selected_files=None,
                expected_content="Agent should handle mixed language appropriately",
                expected_insights=["Agent understands mixed language context"],
                ground_truth={"test_type": "mixed_language"}
            ))
        
        return tests
    
    def generate_all_test_cases(self) -> List[TestCase]:
        """Generate comprehensive test suite"""
        
        all_tests = []
        
        print("Generating context understanding tests...")
        all_tests.extend(self.generate_context_understanding_tests())
        
        print("Generating file analysis tests...")
        all_tests.extend(self.generate_file_analysis_tests())
        
        print("Generating experiment insights tests...")
        all_tests.extend(self.generate_experiment_insights_tests())
        
        print("Generating protocol optimization tests...")
        all_tests.extend(self.generate_protocol_optimization_tests())
        
        print("Generating edge case tests...")
        all_tests.extend(self.generate_edge_case_tests())
        
        print(f"Generated {len(all_tests)} test cases total")
        
        return all_tests
    
    def save_test_cases(self, test_cases: List[TestCase], output_file: str):
        """Save test cases to JSON file"""
        
        # Convert test cases to JSON-serializable format
        serializable_test_cases = []
        for tc in test_cases:
            tc_dict = asdict(tc)
            tc_dict["category"] = tc.category.value  # Convert enum to string
            serializable_test_cases.append(tc_dict)
        
        test_data = {
            "metadata": {
                "total_tests": len(test_cases),
                "categories": list(set(tc.category.value for tc in test_cases)),
                "languages": list(set(tc.language for tc in test_cases))
            },
            "test_cases": serializable_test_cases
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(test_cases)} test cases to {output_file}")
    
    def load_test_cases(self, input_file: str) -> List[TestCase]:
        """Load test cases from JSON file"""
        
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        test_cases = []
        for tc_data in data["test_cases"]:
            tc_data["category"] = TestCategory(tc_data["category"])
            test_cases.append(TestCase(**tc_data))
        
        return test_cases


if __name__ == "__main__":
    # Generate comprehensive test suite
    generator = TestCaseGenerator()
    
    # Generate all tests
    test_cases = generator.generate_all_test_cases()
    
    # Save to file
    output_dir = Path("tests/test_cases")
    output_dir.mkdir(exist_ok=True)
    
    generator.save_test_cases(test_cases, str(output_dir / "comprehensive_test_suite.json"))
    
    # Show summary
    categories = {}
    languages = {}
    
    for tc in test_cases:
        categories[tc.category.value] = categories.get(tc.category.value, 0) + 1
        languages[tc.language] = languages.get(tc.language, 0) + 1
    
    print("\n📊 Test Suite Summary:")
    print(f"Total Tests: {len(test_cases)}")
    print(f"Categories: {dict(categories)}")
    print(f"Languages: {dict(languages)}")