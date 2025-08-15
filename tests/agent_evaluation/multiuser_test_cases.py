"""
Multi-User Test Cases for LabAcc Copilot Agent Evaluation

Extended test case definitions that support the new multi-user, project-based
architecture while maintaining backward compatibility with existing test cases.
"""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

from .evaluator_agent import TestCase, TestCategory, EvaluationCriteria, EvaluationResult

class MultiUserTestCategory(Enum):
    """Extended test categories for multi-user functionality"""
    # Original categories
    CONTEXT_UNDERSTANDING = "context_understanding"
    FILE_ANALYSIS = "file_analysis"  
    EXPERIMENT_INSIGHTS = "experiment_insights"
    PROTOCOL_OPTIMIZATION = "protocol_optimization"
    MULTILINGUAL = "multilingual"
    
    # New multi-user categories
    PROJECT_ISOLATION = "project_isolation"
    SESSION_MANAGEMENT = "session_management"
    PERMISSION_CONTROL = "permission_control"
    CROSS_PROJECT_WORKFLOWS = "cross_project_workflows"
    USER_COLLABORATION = "user_collaboration"

@dataclass
class ProjectContext:
    """Represents project context for test cases"""
    project_id: str
    user_id: str
    permission: str = "owner"  # owner, shared, admin
    relative_path: str = "."  # Path relative to project root
    
@dataclass
class MultiUserTestCase:
    """Enhanced test case with multi-user support"""
    # Core test case fields (compatible with original TestCase)
    id: str
    category: MultiUserTestCategory
    user_query: str
    language: str
    expected_content: str
    expected_insights: List[str]
    ground_truth: Dict
    
    # Multi-user specific fields
    project_context: Optional[ProjectContext] = None
    requires_project_selection: bool = True
    test_session_setup: Optional[Dict[str, Any]] = None
    
    # Legacy compatibility fields
    current_folder: Optional[str] = None
    selected_files: Optional[List[str]] = None
    
    def __post_init__(self):
        """Auto-setup project context from legacy fields if needed"""
        if not self.project_context and self.current_folder:
            # Try to infer project context from current_folder
            self.project_context = self._infer_project_context(self.current_folder)
    
    def _infer_project_context(self, folder: str) -> ProjectContext:
        """Infer project context from legacy folder reference"""
        # Simple mapping logic - can be extended
        if 'alice' in folder.lower() or folder.startswith('exp_001') or folder.startswith('exp_002'):
            return ProjectContext(
                project_id="project_alice_projects",
                user_id="alice",
                permission="owner",
                relative_path=folder if not folder.startswith(('alice_projects/', 'bob_projects/')) else folder.split('/', 1)[1]
            )
        elif 'bob' in folder.lower():
            return ProjectContext(
                project_id="project_bob_projects", 
                user_id="bob",
                permission="owner",
                relative_path=folder if not folder.startswith(('alice_projects/', 'bob_projects/')) else folder.split('/', 1)[1]
            )
        else:
            return ProjectContext(
                project_id="project_experiments",
                user_id="temp_user",
                permission="owner", 
                relative_path=folder
            )
    
    def to_legacy_test_case(self) -> TestCase:
        """Convert to legacy TestCase format for compatibility"""
        return TestCase(
            id=self.id,
            category=TestCategory(self.category.value) if self.category.value in [c.value for c in TestCategory] else TestCategory.CONTEXT_UNDERSTANDING,
            user_query=self.user_query,
            language=self.language,
            current_folder=self.current_folder,
            selected_files=self.selected_files,
            expected_content=self.expected_content,
            expected_insights=self.expected_insights,
            ground_truth=self.ground_truth
        )
    
    @classmethod
    def from_legacy_test_case(cls, legacy_case: TestCase, **kwargs) -> 'MultiUserTestCase':
        """Create MultiUserTestCase from legacy TestCase"""
        return cls(
            id=legacy_case.id,
            category=MultiUserTestCategory(legacy_case.category.value),
            user_query=legacy_case.user_query,
            language=legacy_case.language,
            expected_content=legacy_case.expected_content,
            expected_insights=legacy_case.expected_insights,
            ground_truth=legacy_case.ground_truth,
            current_folder=legacy_case.current_folder,
            selected_files=legacy_case.selected_files,
            **kwargs
        )

@dataclass
class MultiUserEvaluationCriteria(EvaluationCriteria):
    """Extended evaluation criteria for multi-user functionality"""
    # Additional criteria for multi-user features
    project_isolation: float = 0.0  # Does agent respect project boundaries?
    session_management: float = 0.0  # Does agent handle sessions correctly?  
    permission_awareness: float = 0.0  # Does agent respect user permissions?
    
    @property
    def overall_score(self) -> float:
        """Calculate weighted overall score including multi-user criteria"""
        base_weights = {
            'accuracy': 0.25,
            'relevance': 0.2, 
            'completeness': 0.15,
            'context_awareness': 0.15,
            'language_understanding': 0.05
        }
        
        multiuser_weights = {
            'project_isolation': 0.1,
            'session_management': 0.05,
            'permission_awareness': 0.05
        }
        
        base_score = (
            self.accuracy * base_weights['accuracy'] +
            self.relevance * base_weights['relevance'] +
            self.completeness * base_weights['completeness'] +
            self.context_awareness * base_weights['context_awareness'] +
            self.language_understanding * base_weights['language_understanding']
        )
        
        multiuser_score = (
            self.project_isolation * multiuser_weights['project_isolation'] +
            self.session_management * multiuser_weights['session_management'] +
            self.permission_awareness * multiuser_weights['permission_awareness']
        )
        
        return base_score + multiuser_score

class MultiUserTestGenerator:
    """Generates test cases for multi-user functionality"""
    
    def __init__(self):
        self.base_project_contexts = {
            "alice": ProjectContext("project_alice_projects", "alice", "owner"),
            "bob": ProjectContext("project_bob_projects", "bob", "owner"),
            "shared": ProjectContext("project_shared_protocols", "temp_user", "shared"),
            "experiments": ProjectContext("project_experiments", "temp_user", "owner")
        }
    
    def generate_project_isolation_tests(self) -> List[MultiUserTestCase]:
        """Generate test cases for project isolation"""
        tests = []
        
        # Test 1: User can access their own project
        tests.append(MultiUserTestCase(
            id="isolation_own_project_1",
            category=MultiUserTestCategory.PROJECT_ISOLATION,
            user_query="What experiments do I have?",
            language="English",
            project_context=self.base_project_contexts["alice"],
            expected_content="Alice's PCR experiments and protocols",
            expected_insights=["User can see their own experiments", "Project-specific content loaded"],
            ground_truth={"accessible_projects": ["project_alice_projects"], "permission": "owner"}
        ))
        
        # Test 2: Cross-project access should be controlled
        tests.append(MultiUserTestCase(
            id="isolation_cross_project_1", 
            category=MultiUserTestCategory.PROJECT_ISOLATION,
            user_query="Show me Bob's experiments",
            language="English",
            project_context=self.base_project_contexts["alice"],
            expected_content="Cannot access other users' private projects",
            expected_insights=["Access denied to Bob's projects", "Project boundaries respected"],
            ground_truth={"should_deny_access": True, "reason": "project_isolation"}
        ))
        
        # Test 3: Shared project access
        tests.append(MultiUserTestCase(
            id="isolation_shared_access_1",
            category=MultiUserTestCategory.PROJECT_ISOLATION,
            user_query="What protocols are available?",
            language="English", 
            project_context=self.base_project_contexts["shared"],
            expected_content="Shared lab protocols and procedures",
            expected_insights=["Access to shared resources", "Collaborative project content"],
            ground_truth={"accessible_projects": ["project_shared_protocols"], "permission": "shared"}
        ))
        
        return tests
    
    def generate_session_management_tests(self) -> List[MultiUserTestCase]:
        """Generate test cases for session management"""
        tests = []
        
        # Test 1: Session creation and project selection
        tests.append(MultiUserTestCase(
            id="session_project_selection_1",
            category=MultiUserTestCategory.SESSION_MANAGEMENT,
            user_query="What's in this project?",
            language="English",
            project_context=self.base_project_contexts["alice"],
            requires_project_selection=True,
            expected_content="Project contents based on selected project",
            expected_insights=["Session context established", "Project selection working"],
            ground_truth={"session_required": True, "project_context": "alice_projects"}
        ))
        
        # Test 2: Session without project selection should prompt
        tests.append(MultiUserTestCase(
            id="session_no_project_1",
            category=MultiUserTestCategory.SESSION_MANAGEMENT,
            user_query="Analyze my data",
            language="English",
            project_context=None,
            requires_project_selection=False,
            expected_content="Please select a project first",
            expected_insights=["Project selection required", "Clear guidance provided"],
            ground_truth={"should_prompt_project_selection": True}
        ))
        
        return tests
    
    def generate_multilingual_multiuser_tests(self) -> List[MultiUserTestCase]:
        """Generate multilingual tests in multi-user context"""
        tests = []
        
        # Test 1: Chinese query in Alice's project
        tests.append(MultiUserTestCase(
            id="multilingual_chinese_alice_1",
            category=MultiUserTestCategory.MULTILINGUAL,
            user_query="这个项目里有什么实验？",  # "What experiments are in this project?"
            language="Chinese",
            project_context=self.base_project_contexts["alice"],
            expected_content="爱丽丝的PCR实验和协议",  # Alice's PCR experiments and protocols
            expected_insights=["Chinese language understanding", "Project context in Chinese"],
            ground_truth={"language": "Chinese", "project": "alice_projects", "understanding": "project_contents"}
        ))
        
        # Test 2: Mixed language query
        tests.append(MultiUserTestCase(
            id="multilingual_mixed_bob_1", 
            category=MultiUserTestCategory.MULTILINGUAL,
            user_query="Show me the 实验结果 for optimization",  # "Show me the experimental results"
            language="Mixed",
            project_context=self.base_project_contexts["bob"],
            expected_content="Bob's optimization experimental results",
            expected_insights=["Mixed language handling", "Technical terms understood"],
            ground_truth={"language": "Mixed", "technical_terms": ["实验结果", "optimization"]}
        ))
        
        return tests
    
    def generate_permission_control_tests(self) -> List[MultiUserTestCase]:
        """Generate test cases for permission control"""
        tests = []
        
        # Test 1: Owner permissions
        tests.append(MultiUserTestCase(
            id="permission_owner_modify_1",
            category=MultiUserTestCategory.PERMISSION_CONTROL,
            user_query="Create a new experiment folder",
            language="English",
            project_context=ProjectContext("project_alice_projects", "alice", "owner"),
            expected_content="New experiment folder created",
            expected_insights=["Owner can create folders", "Write permissions working"],
            ground_truth={"permission_level": "owner", "action": "create", "allowed": True}
        ))
        
        # Test 2: Shared user limitations
        tests.append(MultiUserTestCase(
            id="permission_shared_limit_1",
            category=MultiUserTestCategory.PERMISSION_CONTROL, 
            user_query="Delete this project",
            language="English",
            project_context=ProjectContext("project_shared_protocols", "temp_user", "shared"),
            expected_content="Permission denied - shared users cannot delete projects",
            expected_insights=["Permission boundaries respected", "Clear error messaging"],
            ground_truth={"permission_level": "shared", "action": "delete", "allowed": False}
        ))
        
        return tests
    
    def generate_all_multiuser_tests(self) -> List[MultiUserTestCase]:
        """Generate comprehensive multi-user test suite"""
        all_tests = []
        
        all_tests.extend(self.generate_project_isolation_tests())
        all_tests.extend(self.generate_session_management_tests()) 
        all_tests.extend(self.generate_multilingual_multiuser_tests())
        all_tests.extend(self.generate_permission_control_tests())
        
        return all_tests
    
    def save_test_cases(self, test_cases: List[MultiUserTestCase], filepath: str):
        """Save test cases to JSON file"""
        test_data = {
            "metadata": {
                "total_tests": len(test_cases),
                "categories": list(set(tc.category.value for tc in test_cases)),
                "languages": list(set(tc.language for tc in test_cases)),
                "projects": list(set(tc.project_context.project_id for tc in test_cases if tc.project_context)),
                "generated_at": str(Path(filepath).resolve()),
                "test_format": "multiuser_v1"
            },
            "test_cases": [asdict(tc) for tc in test_cases]
        }
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, indent=2, ensure_ascii=False, default=str)
    
    @classmethod
    def load_test_cases(cls, filepath: str) -> List[MultiUserTestCase]:
        """Load test cases from JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        test_cases = []
        for tc_data in data.get("test_cases", []):
            # Handle ProjectContext
            if tc_data.get("project_context"):
                pc_data = tc_data["project_context"]
                tc_data["project_context"] = ProjectContext(**pc_data)
            
            # Handle enum conversion
            tc_data["category"] = MultiUserTestCategory(tc_data["category"])
            
            test_cases.append(MultiUserTestCase(**tc_data))
        
        return test_cases

# Convenience functions for backward compatibility
def convert_legacy_test_suite(legacy_test_file: str, output_file: str):
    """Convert legacy test suite to multi-user format"""
    # Load legacy test cases
    with open(legacy_test_file, 'r') as f:
        data = json.load(f)
    
    converted_tests = []
    for tc_data in data.get("test_cases", []):
        # Create legacy TestCase first
        legacy_case = TestCase(
            id=tc_data["id"],
            category=TestCategory(tc_data["category"]),
            user_query=tc_data["user_query"],
            language=tc_data["language"],
            current_folder=tc_data.get("current_folder"),
            selected_files=tc_data.get("selected_files"),
            expected_content=tc_data["expected_content"],
            expected_insights=tc_data["expected_insights"],
            ground_truth=tc_data["ground_truth"]
        )
        
        # Convert to MultiUserTestCase
        multiuser_case = MultiUserTestCase.from_legacy_test_case(legacy_case)
        converted_tests.append(multiuser_case)
    
    # Save converted tests
    generator = MultiUserTestGenerator()
    generator.save_test_cases(converted_tests, output_file)

def load_legacy_tests_as_multiuser(filepath: str) -> List[MultiUserTestCase]:
    """Load legacy tests and convert them to multi-user format on the fly"""
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    converted_tests = []
    for tc_data in data.get("test_cases", []):
        try:
            legacy_case = TestCase(
                id=tc_data["id"],
                category=TestCategory(tc_data["category"]), 
                user_query=tc_data["user_query"],
                language=tc_data["language"],
                current_folder=tc_data.get("current_folder"),
                selected_files=tc_data.get("selected_files"),
                expected_content=tc_data["expected_content"],
                expected_insights=tc_data["expected_insights"],
                ground_truth=tc_data["ground_truth"]
            )
            
            multiuser_case = MultiUserTestCase.from_legacy_test_case(legacy_case)
            converted_tests.append(multiuser_case)
        except Exception as e:
            print(f"Warning: Failed to convert test case {tc_data.get('id', 'unknown')}: {e}")
            continue
    
    return converted_tests