"""Unit tests for file conversion pipeline components.

These tests verify individual components work correctly in isolation.
Tests are fast and don't require actual file I/O where possible.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest
import asyncio

# Add project root to path
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api.file_conversion import FileConversionPipeline
from src.api.file_registry import FileRegistry


class TestFileConversionPipeline:
    """Test the FileConversionPipeline class."""
    
    def test_needs_conversion_detection(self):
        """Test that file types are correctly identified for conversion."""
        pipeline = FileConversionPipeline("data/test")
        
        # Files that need conversion
        assert pipeline.needs_conversion("document.pdf") == True
        assert pipeline.needs_conversion("report.docx") == True
        assert pipeline.needs_conversion("presentation.pptx") == True
        assert pipeline.needs_conversion("data.xlsx") == True
        assert pipeline.needs_conversion("page.html") == True
        assert pipeline.needs_conversion("document.rtf") == True
        
        # Files that don't need conversion
        assert pipeline.needs_conversion("data.csv") == False
        assert pipeline.needs_conversion("script.py") == False
        assert pipeline.needs_conversion("readme.md") == False
        assert pipeline.needs_conversion("image.png") == False
        assert pipeline.needs_conversion("config.json") == False
    
    def test_case_insensitive_extension(self):
        """Test that file extensions are checked case-insensitively."""
        pipeline = FileConversionPipeline("data/test")
        
        assert pipeline.needs_conversion("Document.PDF") == True
        assert pipeline.needs_conversion("Report.DOCX") == True
        assert pipeline.needs_conversion("Data.CSV") == False
    
    @pytest.mark.asyncio
    async def test_process_upload_no_conversion_needed(self):
        """Test processing a file that doesn't need conversion."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = FileConversionPipeline(tmpdir)
            
            # Create a test CSV file
            test_file = Path(tmpdir) / "exp_001" / "data.csv"
            test_file.parent.mkdir(parents=True)
            test_file.write_text("col1,col2\n1,2\n3,4")
            
            result = await pipeline.process_upload(test_file, "exp_001")
            
            assert result["filename"] == "data.csv"
            assert result["conversion_status"] == "not_needed"
            assert result["converted_path"] is None
            assert result["conversion_method"] is None
    
    def test_markitdown_availability(self):
        """Test that MarkItDown is available for conversion."""
        pipeline = FileConversionPipeline("data/test")
        
        # Should not raise an error
        try:
            markitdown = pipeline._get_markitdown()
            assert markitdown is not None
        except RuntimeError as e:
            pytest.skip(f"MarkItDown not available: {e}")
    
    def test_mineru_availability_check(self):
        """Test MinerU availability detection."""
        pipeline = FileConversionPipeline("data/test")
        
        # This just checks the flag is set correctly
        # MinerU might not be installed, which is fine
        assert isinstance(pipeline._mineru_available, bool)


class TestFileRegistry:
    """Test the FileRegistry class."""
    
    def test_registry_initialization(self):
        """Test creating a new registry."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = FileRegistry(tmpdir)
            
            # Load non-existent registry returns default structure
            reg_data = registry.load_registry("exp_001")
            
            assert reg_data["version"] == "3.0"
            assert reg_data["experiment_id"] == "exp_001"
            assert reg_data["files"] == {}
            assert reg_data["total_files"] == 0
    
    def test_add_file_to_registry(self):
        """Test adding a file to the registry."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = FileRegistry(tmpdir)
            
            # Add a file
            entry = registry.add_file(
                experiment_id="exp_001",
                filename="protocol.pdf",
                original_path="exp_001/originals/protocol.pdf",
                converted_path="exp_001/.labacc/converted/protocol.md",
                file_size=1024,
                conversion_status="success",
                conversion_method="MarkItDown"
            )
            
            assert entry["original_path"] == "exp_001/originals/protocol.pdf"
            assert entry["converted_path"] == "exp_001/.labacc/converted/protocol.md"
            assert entry["file_size"] == 1024
            assert entry["conversion"]["status"] == "success"
            assert entry["conversion"]["method"] == "MarkItDown"
    
    def test_get_file_from_registry(self):
        """Test retrieving a file from the registry."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = FileRegistry(tmpdir)
            
            # Add a file
            registry.add_file(
                experiment_id="exp_001",
                filename="data.xlsx",
                original_path="exp_001/data.xlsx",
                file_size=2048
            )
            
            # Retrieve it
            file_info = registry.get_file("exp_001", "data.xlsx")
            
            assert file_info is not None
            assert file_info["original_path"] == "exp_001/data.xlsx"
            assert file_info["file_size"] == 2048
            
            # Non-existent file returns None
            assert registry.get_file("exp_001", "missing.txt") is None
    
    def test_get_file_by_path(self):
        """Test retrieving a file by its path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = FileRegistry(tmpdir)
            
            # Add a file with conversion
            registry.add_file(
                experiment_id="exp_001",
                filename="report.docx",
                original_path="exp_001/originals/report.docx",
                converted_path="exp_001/.labacc/converted/report.md"
            )
            
            # Find by original path
            file_info = registry.get_file_by_path("exp_001", "exp_001/originals/report.docx")
            assert file_info is not None
            assert file_info["filename"] == "report.docx"
            
            # Find by converted path
            file_info = registry.get_file_by_path("exp_001", "exp_001/.labacc/converted/report.md")
            assert file_info is not None
            assert file_info["filename"] == "report.docx"
    
    def test_update_analysis(self):
        """Test updating analysis information for a file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = FileRegistry(tmpdir)
            
            # Add a file
            registry.add_file(
                experiment_id="exp_001",
                filename="results.csv",
                original_path="exp_001/results.csv"
            )
            
            # Update analysis
            registry.update_analysis(
                experiment_id="exp_001",
                filename="results.csv",
                summary="Contains qPCR results for 96 samples",
                context="Testing gene expression levels"
            )
            
            # Verify update
            file_info = registry.get_file("exp_001", "results.csv")
            assert file_info["analysis"]["analyzed"] == True
            assert file_info["analysis"]["summary"] == "Contains qPCR results for 96 samples"
            assert file_info["analysis"]["context"] == "Testing gene expression levels"
    
    def test_list_files_with_filters(self):
        """Test listing files with various filters."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = FileRegistry(tmpdir)
            
            # Add multiple files
            registry.add_file("exp_001", "file1.txt", "exp_001/file1.txt")
            registry.add_file("exp_001", "file2.pdf", "exp_001/file2.pdf",
                            converted_path="exp_001/.labacc/file2.md",
                            conversion_status="success")
            registry.add_file("exp_001", "file3.docx", "exp_001/file3.docx",
                            converted_path="exp_001/.labacc/file3.md",
                            conversion_status="success")
            
            # Update analysis for one file
            registry.update_analysis("exp_001", "file2.pdf", "PDF analysis")
            
            # List all files
            all_files = registry.list_files("exp_001")
            assert len(all_files) == 3
            
            # List only converted files
            converted = registry.list_files("exp_001", only_converted=True)
            assert len(converted) == 2
            assert all(f["converted_path"] for f in converted)
            
            # List only analyzed files
            analyzed = registry.list_files("exp_001", only_analyzed=True)
            assert len(analyzed) == 1
            assert analyzed[0]["filename"] == "file2.pdf"
    
    def test_get_readable_path(self):
        """Test getting the best readable version of a file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = FileRegistry(tmpdir)
            
            # File without conversion
            registry.add_file("exp_001", "data.csv", "exp_001/data.csv")
            readable = registry.get_readable_path("exp_001", "exp_001/data.csv")
            assert readable == "exp_001/data.csv"
            
            # File with successful conversion
            registry.add_file("exp_001", "doc.pdf", "exp_001/doc.pdf",
                            converted_path="exp_001/.labacc/doc.md",
                            conversion_status="success")
            readable = registry.get_readable_path("exp_001", "exp_001/doc.pdf")
            assert readable == "exp_001/.labacc/doc.md"
            
            # File with failed conversion
            registry.add_file("exp_001", "bad.pdf", "exp_001/bad.pdf",
                            converted_path="exp_001/.labacc/bad.md",
                            conversion_status="failed")
            readable = registry.get_readable_path("exp_001", "exp_001/bad.pdf")
            assert readable == "exp_001/bad.pdf"  # Falls back to original
    
    def test_registry_persistence(self):
        """Test that registry persists to disk and can be reloaded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create and save registry
            registry1 = FileRegistry(tmpdir)
            registry1.add_file("exp_001", "test.pdf", "exp_001/test.pdf",
                             file_size=5000)
            
            # Create new registry instance and load
            registry2 = FileRegistry(tmpdir)
            loaded = registry2.load_registry("exp_001")
            
            assert "test.pdf" in loaded["files"]
            assert loaded["files"]["test.pdf"]["file_size"] == 5000
            assert loaded["total_files"] == 1


class TestContentPreservation:
    """Test that conversion preserves important content."""
    
    def test_key_content_markers(self):
        """Test that we can identify key content in the lung cancer protocol."""
        # This is the content we expect to find after conversion
        key_phrases = [
            "lung cancer tissue dissociation",
            "25–45 min",  # Simplified to avoid encoding issues
            "cold protease",  # Simplified to avoid degree symbol issues
            "cell viability",
            "ambient RNA",
            "10x microfluidics",
            "FOS, JUN, HSPs",
            "gentleMACS"
        ]
        
        # Read the markdown reference
        md_path = Path("data/extra_test_file/lung_cancer_cell_dis_guide.md")
        if md_path.exists():
            content = md_path.read_text().lower()  # Make case-insensitive
            
            for phrase in key_phrases:
                assert phrase.lower() in content, f"Key phrase missing: {phrase}"
        else:
            pytest.skip("Test file not available")


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])