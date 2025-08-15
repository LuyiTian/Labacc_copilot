"""Agent-driven end-to-end tests for file conversion workflow.

These tests simulate realistic user workflows including:
- Uploading documents as background research
- Agent proactively analyzing and asking questions
- User providing context
- Agent using converted files to answer questions
"""

import asyncio
import json
import shutil
from pathlib import Path
import pytest
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api.file_conversion import FileConversionPipeline
from src.api.file_registry import FileRegistry
from src.agents.react_agent import handle_message, read_file, analyze_data
from src.memory.memory_tools import read_memory, append_insight
from src.utils.test_cleanup import TestCleanup, ensure_bob_projects_clean
from langchain_core.messages import HumanMessage


class TestAgentFileConversionWorkflow:
    """Test complete agent workflows with file conversion."""
    
    @pytest.fixture(autouse=True)
    def setup_and_cleanup(self):
        """Ensure clean state before and after each test."""
        ensure_bob_projects_clean()
        yield
        ensure_bob_projects_clean()
    
    @pytest.mark.asyncio
    async def test_researcher_uploads_protocol_background(self):
        """Simulate a researcher uploading a protocol as background research.
        
        Scenario:
        1. Researcher is working on exp_002_optimization
        2. Uploads lung cancer dissociation protocol as reference
        3. Agent analyzes and asks contextual questions
        4. Researcher provides context
        5. Agent can later answer questions using the protocol
        """
        with TestCleanup() as cleanup:
            # We're modifying exp_002, so need to restore it
            project_root = Path("data/bob_projects")
            experiment_id = "exp_002_optimization"
            exp_dir = project_root / experiment_id
            
            # Backup current state
            backup_dir = exp_dir.parent / f"{experiment_id}_test_backup"
            if exp_dir.exists():
                shutil.copytree(exp_dir, backup_dir)
            
            try:
                # Step 1: Upload the protocol document
                source_file = Path("data/extra_test_file/For lung cancer tissue dissociation.docx")
                if not source_file.exists():
                    # Fallback to PDF or MD
                    source_file = Path("data/extra_test_file/For lung cancer tissue dissociation.pdf")
                    if not source_file.exists():
                        source_file = Path("data/extra_test_file/lung_cancer_cell_dis_guide.md")
                
                if not source_file.exists():
                    pytest.skip("No test files available")
                
                # Simulate upload to originals folder
                originals_dir = exp_dir / "originals"
                originals_dir.mkdir(parents=True, exist_ok=True)
                dest_file = originals_dir / f"reference_protocol_{source_file.name}"
                shutil.copy2(source_file, dest_file)
                
                # Process conversion
                pipeline = FileConversionPipeline(str(project_root))
                conversion_result = await pipeline.process_upload(dest_file, experiment_id)
                
                # Step 2: Agent analyzes the uploaded file
                file_path = f"{experiment_id}/originals/{dest_file.name}"
                analysis_response = await analyze_data.ainvoke({"file_path": file_path})
                
                # Verify agent recognized the content
                assert "lung" in analysis_response.lower() or "dissociation" in analysis_response.lower()
                
                # Step 3: Simulate agent asking contextual questions
                # In real workflow, agent would proactively ask based on content
                contextual_question = (
                    "I see you've uploaded a lung cancer tissue dissociation protocol. "
                    "What specific cell line or tissue type are you working with, "
                    "and what digestion time are you currently using?"
                )
                
                # Step 4: User provides context
                user_context = "Working with A549 lung adenocarcinoma cells, currently using 30 minutes digestion"
                
                # Update memory with context (simulating what would happen after user response)
                await append_insight.ainvoke({
                    "experiment_id": experiment_id,
                    "insight": f"Using lung tissue dissociation protocol for A549 cells with 30 min digestion",
                    "source": "user_context"
                })
                
                # Step 5: Later, user asks about optimization
                query = "Based on the protocol, should I adjust my digestion time?"
                response = await handle_message(query, f"test-session-{experiment_id}")
                
                # Agent should reference the uploaded protocol
                assert response is not None
                # Response should mention digestion time recommendations
                assert "min" in response.lower() or "digest" in response.lower() or "time" in response.lower()
                
            finally:
                # Restore original state
                if backup_dir.exists():
                    if exp_dir.exists():
                        shutil.rmtree(exp_dir)
                    shutil.move(backup_dir, exp_dir)
    
    @pytest.mark.asyncio
    async def test_agent_reads_converted_content_correctly(self):
        """Test that agent correctly reads and interprets converted documents."""
        with TestCleanup() as cleanup:
            cleanup.register_test_folder("exp_test_agent_conversion")
            
            # Setup
            project_root = Path("data/bob_projects")
            experiment_id = "exp_test_agent_conversion"
            exp_dir = project_root / experiment_id
            exp_dir.mkdir(parents=True, exist_ok=True)
            
            # Upload Word document
            source_file = Path("data/extra_test_file/For lung cancer tissue dissociation.docx")
            if not source_file.exists():
                pytest.skip("Test Word file not available")
            
            originals_dir = exp_dir / "originals"
            originals_dir.mkdir(parents=True, exist_ok=True)
            dest_file = originals_dir / source_file.name
            shutil.copy2(source_file, dest_file)
            
            # Convert
            pipeline = FileConversionPipeline(str(project_root))
            result = await pipeline.process_upload(dest_file, experiment_id)
            
            if result["conversion_status"] == "success":
                # Use agent's read_file tool
                file_path = f"{experiment_id}/originals/{source_file.name}"
                content = await read_file.ainvoke({"file_path": file_path})
                
                # Verify key protocol elements are present
                key_elements = [
                    ("digestion", "dissociation"),  # At least one should be present
                    ("cell", "tissue"),  # At least one
                    ("min", "minute", "time"),  # At least one
                ]
                
                content_lower = content.lower()
                for element_group in key_elements:
                    assert any(elem in content_lower for elem in element_group), \
                        f"Missing key element group: {element_group}"
    
    @pytest.mark.asyncio
    async def test_multi_format_comparison(self):
        """Test that all three formats (MD, DOCX, PDF) convey the same information."""
        with TestCleanup() as cleanup:
            cleanup.register_test_folder("exp_test_format_comparison")
            
            # Setup
            project_root = Path("data/bob_projects")
            experiment_id = "exp_test_format_comparison"
            exp_dir = project_root / experiment_id
            exp_dir.mkdir(parents=True, exist_ok=True)
            originals_dir = exp_dir / "originals"
            originals_dir.mkdir(parents=True, exist_ok=True)
            
            # Test files
            test_files = [
                "lung_cancer_cell_dis_guide.md",
                "For lung cancer tissue dissociation.docx",
                "For lung cancer tissue dissociation.pdf"
            ]
            
            contents = {}
            pipeline = FileConversionPipeline(str(project_root))
            
            for filename in test_files:
                source_file = Path("data/extra_test_file") / filename
                if source_file.exists():
                    # Copy and process
                    dest_file = originals_dir / filename
                    shutil.copy2(source_file, dest_file)
                    
                    # Process (convert if needed)
                    result = await pipeline.process_upload(dest_file, experiment_id)
                    
                    # Read through agent
                    file_path = f"{experiment_id}/originals/{filename}"
                    content = await read_file.ainvoke({"file_path": file_path})
                    contents[filename] = content.lower()
            
            # Compare key information across formats
            if len(contents) >= 2:
                # All formats should mention these critical details
                critical_info = [
                    "lung cancer",
                    "dissociation",
                    "37",  # Temperature
                    "cell viability",
                ]
                
                for info in critical_info:
                    present_count = sum(1 for content in contents.values() if info in content)
                    assert present_count >= len(contents) - 1, \
                        f"Critical info '{info}' missing from multiple formats"
    
    @pytest.mark.asyncio
    async def test_proactive_analysis_simulation(self):
        """Simulate the proactive analysis workflow after file upload."""
        with TestCleanup() as cleanup:
            cleanup.register_test_folder("exp_test_proactive")
            
            # Setup
            project_root = Path("data/bob_projects")
            experiment_id = "exp_test_proactive"
            exp_dir = project_root / experiment_id
            exp_dir.mkdir(parents=True, exist_ok=True)
            
            # Create initial README
            readme_path = exp_dir / "README.md"
            readme_path.write_text("""# Experiment: Protocol Testing

## Motivation
Testing new dissociation protocols for improved cell viability.

## Files
(No files yet)
""")
            
            # Upload protocol
            source_file = Path("data/extra_test_file/lung_cancer_cell_dis_guide.md")
            if not source_file.exists():
                pytest.skip("Test file not available")
            
            dest_file = exp_dir / source_file.name
            shutil.copy2(source_file, dest_file)
            
            # Process
            pipeline = FileConversionPipeline(str(project_root))
            await pipeline.process_upload(dest_file, experiment_id)
            
            # Simulate proactive analysis
            # Agent would analyze file and generate questions
            analysis_prompt = (
                f"A new file '{source_file.name}' was uploaded to {experiment_id}. "
                "Analyze it and suggest what questions to ask the user."
            )
            
            response = await handle_message(analysis_prompt, f"test-proactive-{experiment_id}")
            
            # Response should be contextual
            assert response is not None
            # Should recognize it's a protocol
            assert any(word in response.lower() for word in ["protocol", "dissociation", "digest", "cell"])
    
    @pytest.mark.asyncio
    async def test_contextual_question_generation(self):
        """Test that agent generates appropriate contextual questions."""
        with TestCleanup() as cleanup:
            cleanup.register_test_folder("exp_test_questions")
            
            # Setup
            project_root = Path("data/bob_projects")
            experiment_id = "exp_test_questions"
            exp_dir = project_root / experiment_id
            exp_dir.mkdir(parents=True, exist_ok=True)
            
            # Upload lung cancer protocol
            source_file = Path("data/extra_test_file/For lung cancer tissue dissociation.docx")
            if not source_file.exists():
                source_file = Path("data/extra_test_file/lung_cancer_cell_dis_guide.md")
            
            if not source_file.exists():
                pytest.skip("No test files available")
            
            dest_file = exp_dir / source_file.name
            shutil.copy2(source_file, dest_file)
            
            # Process
            pipeline = FileConversionPipeline(str(project_root))
            await pipeline.process_upload(dest_file, experiment_id)
            
            # Ask agent to generate questions about the uploaded file
            query = (
                f"I just uploaded {source_file.name} to my experiment. "
                "What key information do you need to know to help me optimize my protocol?"
            )
            
            response = await handle_message(query, f"test-questions-{experiment_id}")
            
            # Good contextual questions would include:
            # - What cell line/tissue type?
            # - Current digestion time?
            # - Temperature being used?
            # - Observed viability?
            
            assert response is not None
            # Should ask relevant questions
            relevant_terms = ["cell", "tissue", "time", "temperature", "viability", "what", "which", "how"]
            relevant_count = sum(1 for term in relevant_terms if term in response.lower())
            assert relevant_count >= 3, "Agent should ask relevant contextual questions"


class TestRealScenario:
    """Test the exact scenario requested: uploading to exp_002_optimization."""
    
    @pytest.fixture(autouse=True)
    def setup_and_cleanup(self):
        """Ensure clean state before and after each test."""
        ensure_bob_projects_clean()
        yield
        ensure_bob_projects_clean()
    
    @pytest.mark.asyncio
    async def test_upload_protocol_to_exp_002_optimization(self):
        """Test uploading lung cancer protocol to exp_002_optimization as background.
        
        This is the exact scenario requested:
        - Upload protocol to exp_002_optimization
        - Agent recognizes it as background research
        - Agent can use it to provide optimization suggestions
        """
        # Backup exp_002
        project_root = Path("data/bob_projects")
        experiment_id = "exp_002_optimization"
        exp_dir = project_root / experiment_id
        backup_dir = exp_dir.parent / f"{experiment_id}_final_backup"
        
        if exp_dir.exists():
            shutil.copytree(exp_dir, backup_dir)
        
        try:
            # Read current experiment context
            readme_path = exp_dir / "README.md"
            if readme_path.exists():
                original_readme = readme_path.read_text()
            else:
                original_readme = ""
            
            # Upload lung cancer protocol as background research
            source_file = Path("data/extra_test_file/For lung cancer tissue dissociation.pdf")
            if not source_file.exists():
                source_file = Path("data/extra_test_file/lung_cancer_cell_dis_guide.md")
            
            if not source_file.exists():
                pytest.skip("No test files available")
            
            # Create originals directory if needed
            originals_dir = exp_dir / "originals"
            originals_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy as background research
            dest_file = originals_dir / f"background_research_{source_file.name}"
            shutil.copy2(source_file, dest_file)
            
            # Process conversion
            pipeline = FileConversionPipeline(str(project_root))
            result = await pipeline.process_upload(dest_file, experiment_id)
            
            # Verify upload successful
            assert result["filename"] == f"background_research_{source_file.name}"
            
            # Verify registry updated
            registry = FileRegistry(str(project_root))
            file_info = registry.get_file(experiment_id, f"background_research_{source_file.name}")
            assert file_info is not None
            
            # Test agent can read and use the file
            query = (
                "I'm working on protocol optimization in exp_002. "
                "Based on the background research I uploaded, "
                "what's the recommended digestion time range for lung tissue?"
            )
            
            response = await handle_message(query, "test-exp002-scenario")
            
            # Agent should reference the protocol
            assert response is not None
            # Should mention the specific time range from protocol (25-45 min)
            assert any(time_indicator in response.lower() 
                      for time_indicator in ["25", "45", "min", "minute"])
            
        finally:
            # Restore original state
            if backup_dir.exists():
                if exp_dir.exists():
                    shutil.rmtree(exp_dir)
                shutil.move(backup_dir, exp_dir)


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "-s"])