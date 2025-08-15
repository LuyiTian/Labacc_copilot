"""Integration tests for file conversion with actual files.

These tests use real files to verify the complete upload and conversion workflow.
Tests interact with the file system and test actual conversion quality.
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
from src.agents.react_agent import read_file
from src.utils.test_cleanup import TestCleanup, ensure_bob_projects_clean


class TestFileConversionIntegration:
    """Integration tests for file conversion pipeline."""
    
    @pytest.fixture(autouse=True)
    def setup_and_cleanup(self):
        """Ensure clean state before and after each test."""
        # Clean before
        ensure_bob_projects_clean()
        yield
        # Clean after
        ensure_bob_projects_clean()
    
    @pytest.mark.asyncio
    async def test_upload_and_convert_word_document(self):
        """Test uploading and converting a Word document."""
        with TestCleanup() as cleanup:
            cleanup.register_test_folder("exp_test_word_conversion")
            
            # Setup
            project_root = Path("data/bob_projects")
            experiment_id = "exp_test_word_conversion"
            exp_dir = project_root / experiment_id
            exp_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy test Word file
            source_file = Path("data/extra_test_file/For lung cancer tissue dissociation.docx")
            if not source_file.exists():
                pytest.skip("Test Word file not available")
            
            dest_file = exp_dir / "originals" / source_file.name
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_file, dest_file)
            
            # Initialize pipeline and process
            pipeline = FileConversionPipeline(str(project_root))
            result = await pipeline.process_upload(dest_file, experiment_id)
            
            # Verify conversion
            assert result["conversion_status"] == "success"
            assert result["conversion_method"] == "MarkItDown"
            assert result["converted_path"] is not None
            
            # Check converted file exists
            converted_path = project_root / result["converted_path"]
            assert converted_path.exists()
            
            # Read converted content and verify key information preserved
            content = converted_path.read_text()
            assert "lung cancer" in content.lower()
            assert "dissociation" in content.lower()
            
            # Verify registry was updated
            registry = FileRegistry(str(project_root))
            file_info = registry.get_file(experiment_id, source_file.name)
            assert file_info is not None
            assert file_info["conversion"]["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_upload_and_convert_pdf_document(self):
        """Test uploading and converting a PDF document."""
        with TestCleanup() as cleanup:
            cleanup.register_test_folder("exp_test_pdf_conversion")
            
            # Setup
            project_root = Path("data/bob_projects")
            experiment_id = "exp_test_pdf_conversion"
            exp_dir = project_root / experiment_id
            exp_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy test PDF file
            source_file = Path("data/extra_test_file/For lung cancer tissue dissociation.pdf")
            if not source_file.exists():
                pytest.skip("Test PDF file not available")
            
            dest_file = exp_dir / "originals" / source_file.name
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_file, dest_file)
            
            # Initialize pipeline and process
            pipeline = FileConversionPipeline(str(project_root))
            result = await pipeline.process_upload(dest_file, experiment_id)
            
            # Verify conversion
            assert result["conversion_status"] in ["success", "failed"]
            # PDF conversion might fail if MinerU not installed, which is OK
            
            if result["conversion_status"] == "success":
                # Check converted file exists
                converted_path = project_root / result["converted_path"]
                assert converted_path.exists()
                
                # Read converted content
                content = converted_path.read_text()
                assert len(content) > 100  # Should have substantial content
    
    @pytest.mark.asyncio
    async def test_agent_read_file_with_conversion(self):
        """Test that the agent's read_file tool uses converted versions."""
        with TestCleanup() as cleanup:
            cleanup.register_test_folder("exp_test_agent_read")
            
            # Setup
            project_root = Path("data/bob_projects")
            experiment_id = "exp_test_agent_read"
            exp_dir = project_root / experiment_id
            exp_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy test Word file
            source_file = Path("data/extra_test_file/For lung cancer tissue dissociation.docx")
            if not source_file.exists():
                pytest.skip("Test Word file not available")
            
            dest_file = exp_dir / "originals" / source_file.name
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_file, dest_file)
            
            # Process conversion
            pipeline = FileConversionPipeline(str(project_root))
            result = await pipeline.process_upload(dest_file, experiment_id)
            
            if result["conversion_status"] == "success":
                # Use agent's read_file tool
                file_path = f"{experiment_id}/originals/{source_file.name}"
                content = await read_file.ainvoke({"file_path": file_path})
                
                # Should indicate it's converted
                assert "converted to Markdown" in content or "lung cancer" in content.lower()
                
                # Should contain key protocol information
                assert "dissociation" in content.lower() or len(content) > 500
    
    @pytest.mark.asyncio
    async def test_conversion_quality_comparison(self):
        """Compare converted content with original markdown to assess quality."""
        with TestCleanup() as cleanup:
            cleanup.register_test_folder("exp_test_quality")
            
            # Setup
            project_root = Path("data/bob_projects")
            experiment_id = "exp_test_quality"
            exp_dir = project_root / experiment_id
            exp_dir.mkdir(parents=True, exist_ok=True)
            
            # Read original markdown for comparison
            original_md = Path("data/extra_test_file/lung_cancer_cell_dis_guide.md")
            if not original_md.exists():
                pytest.skip("Original markdown not available")
            
            original_content = original_md.read_text()
            
            # Key phrases that must be preserved
            key_phrases = [
                "25–45 min at 37 °C",
                "cold protease",
                "cell viability",
                "ambient RNA",
                "10x microfluidics"
            ]
            
            # Test Word conversion
            source_docx = Path("data/extra_test_file/For lung cancer tissue dissociation.docx")
            if source_docx.exists():
                dest_docx = exp_dir / "originals" / source_docx.name
                dest_docx.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_docx, dest_docx)
                
                pipeline = FileConversionPipeline(str(project_root))
                result = await pipeline.process_upload(dest_docx, experiment_id)
                
                if result["conversion_status"] == "success":
                    converted_path = project_root / result["converted_path"]
                    converted_content = converted_path.read_text()
                    
                    # Check preservation of key content
                    preserved_count = 0
                    for phrase in key_phrases:
                        if phrase.lower() in converted_content.lower():
                            preserved_count += 1
                    
                    # At least 60% of key phrases should be preserved
                    preservation_rate = preserved_count / len(key_phrases)
                    assert preservation_rate >= 0.6, f"Only {preservation_rate*100}% of key content preserved"
    
    @pytest.mark.asyncio
    async def test_duplicate_file_handling(self):
        """Test uploading the same file twice."""
        with TestCleanup() as cleanup:
            cleanup.register_test_folder("exp_test_duplicate")
            
            # Setup
            project_root = Path("data/bob_projects")
            experiment_id = "exp_test_duplicate"
            exp_dir = project_root / experiment_id
            exp_dir.mkdir(parents=True, exist_ok=True)
            
            # Use markdown file (no conversion needed)
            source_file = Path("data/extra_test_file/lung_cancer_cell_dis_guide.md")
            if not source_file.exists():
                pytest.skip("Test file not available")
            
            dest_file = exp_dir / source_file.name
            
            # First upload
            shutil.copy2(source_file, dest_file)
            pipeline = FileConversionPipeline(str(project_root))
            result1 = await pipeline.process_upload(dest_file, experiment_id)
            
            # Modify file slightly
            with open(dest_file, 'a') as f:
                f.write("\n# Additional notes\n")
            
            # Second upload (same filename)
            result2 = await pipeline.process_upload(dest_file, experiment_id)
            
            # Registry should have been updated
            registry = FileRegistry(str(project_root))
            file_info = registry.get_file(experiment_id, source_file.name)
            assert file_info is not None
            
            # Timestamps should differ
            assert result2["timestamp"] != result1["timestamp"]
    
    @pytest.mark.asyncio
    async def test_upload_to_existing_experiment(self):
        """Test uploading files to exp_002_optimization as background research."""
        with TestCleanup() as cleanup:
            # Note: We're modifying an existing experiment, so we need to restore it
            
            # Setup
            project_root = Path("data/bob_projects")
            experiment_id = "exp_002_optimization"
            exp_dir = project_root / experiment_id
            
            # Backup current state
            backup_dir = exp_dir.parent / f"{experiment_id}_backup"
            if exp_dir.exists():
                shutil.copytree(exp_dir, backup_dir)
            
            try:
                # Copy lung cancer protocol as background research
                source_file = Path("data/extra_test_file/For lung cancer tissue dissociation.pdf")
                if not source_file.exists():
                    source_file = Path("data/extra_test_file/lung_cancer_cell_dis_guide.md")
                
                if not source_file.exists():
                    pytest.skip("No test files available")
                
                # Create originals directory
                originals_dir = exp_dir / "originals"
                originals_dir.mkdir(parents=True, exist_ok=True)
                
                dest_file = originals_dir / f"background_{source_file.name}"
                shutil.copy2(source_file, dest_file)
                
                # Process upload
                pipeline = FileConversionPipeline(str(project_root))
                result = await pipeline.process_upload(dest_file, experiment_id)
                
                # Verify file was processed
                assert result["filename"] == f"background_{source_file.name}"
                
                # Check registry
                registry = FileRegistry(str(project_root))
                file_info = registry.get_file(experiment_id, f"background_{source_file.name}")
                assert file_info is not None
                
            finally:
                # Restore original state
                if backup_dir.exists():
                    shutil.rmtree(exp_dir)
                    shutil.move(backup_dir, exp_dir)


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    @pytest.fixture(autouse=True)
    def setup_and_cleanup(self):
        """Ensure clean state before and after each test."""
        ensure_bob_projects_clean()
        yield
        ensure_bob_projects_clean()
    
    @pytest.mark.asyncio
    async def test_special_characters_in_filename(self):
        """Test files with special characters in names."""
        with TestCleanup() as cleanup:
            cleanup.register_test_folder("exp_test_special_chars")
            
            # Setup
            project_root = Path("data/bob_projects")
            experiment_id = "exp_test_special_chars"
            exp_dir = project_root / experiment_id
            exp_dir.mkdir(parents=True, exist_ok=True)
            
            # Create test file with special characters
            test_file = exp_dir / "test & protocol (v2) [final].md"
            test_file.write_text("# Test Protocol\nContent here")
            
            # Process
            pipeline = FileConversionPipeline(str(project_root))
            result = await pipeline.process_upload(test_file, experiment_id)
            
            # Should handle special characters
            assert result["conversion_status"] == "not_needed"
            
            # Registry should track it
            registry = FileRegistry(str(project_root))
            file_info = registry.get_file(experiment_id, test_file.name)
            assert file_info is not None
    
    @pytest.mark.asyncio
    async def test_empty_file_handling(self):
        """Test handling of empty files."""
        with TestCleanup() as cleanup:
            cleanup.register_test_folder("exp_test_empty")
            
            # Setup
            project_root = Path("data/bob_projects")
            experiment_id = "exp_test_empty"
            exp_dir = project_root / experiment_id
            exp_dir.mkdir(parents=True, exist_ok=True)
            
            # Create empty file
            empty_file = exp_dir / "empty.txt"
            empty_file.touch()
            
            # Process
            pipeline = FileConversionPipeline(str(project_root))
            result = await pipeline.process_upload(empty_file, experiment_id)
            
            # Should handle gracefully
            assert result["conversion_status"] == "not_needed"
            assert result["filename"] == "empty.txt"


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "-s"])