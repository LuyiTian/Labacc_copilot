"""
Unit tests for README memory operations
Tests isolated ReadmeMemory functionality without agent integration
"""

import pytest
from pathlib import Path
from datetime import datetime

from src.memory.readme_memory import ReadmeMemory


@pytest.mark.unit
@pytest.mark.memory
class TestReadmeMemory:
    """Unit tests for ReadmeMemory class"""
    
    def test_readme_memory_initialization(self, temp_experiment_dir):
        """Test ReadmeMemory initialization"""
        memory = ReadmeMemory(str(temp_experiment_dir))
        
        assert memory.experiment_path == Path(temp_experiment_dir)
        assert memory.readme_path == temp_experiment_dir / "README.md"
        assert memory.readme_path.exists()
    
    def test_read_existing_memory(self, temp_experiment_dir):
        """Test reading existing README content"""
        memory = ReadmeMemory(str(temp_experiment_dir))
        content = memory.read_memory()
        
        assert "# Test Experiment" in content
        assert "## Status" in content
        assert "## Files" in content
        assert "## Insights" in content
        assert "## Change Log" in content
    
    def test_write_memory_section(self, temp_experiment_dir):
        """Test writing content to specific section"""
        memory = ReadmeMemory(str(temp_experiment_dir))
        
        # Write to a section
        test_content = "New protocol: PCR amplification at 95°C"
        memory.write_memory(test_content, "Protocol Details")
        
        # Verify content was written
        updated_content = memory.read_memory()
        assert "## Protocol Details" in updated_content
        assert test_content in updated_content
    
    def test_append_insight(self, temp_experiment_dir):
        """Test appending insights to README"""
        memory = ReadmeMemory(str(temp_experiment_dir))
        
        # Append insights
        insight1 = "Cell viability was lower than expected"
        insight2 = "Temperature may be too high"
        
        memory.append_insight(insight1)
        memory.append_insight(insight2)
        
        # Verify insights were added
        content = memory.read_memory()
        assert insight1 in content
        assert insight2 in content
        
        # Verify timestamp was added
        today = datetime.now().strftime("%Y-%m-%d")
        assert today in content
    
    def test_update_file_registry(self, temp_experiment_dir):
        """Test updating file registry in README"""
        memory = ReadmeMemory(str(temp_experiment_dir))
        
        # Update file registry
        file_info = {
            "filename": "results.csv",
            "type": "data",
            "description": "Experimental results with cell counts"
        }
        memory.update_file_registry(file_info)
        
        # Verify file was registered
        content = memory.read_memory()
        assert "results.csv" in content
        assert "cell counts" in content
    
    def test_get_memory_sections(self, temp_experiment_dir):
        """Test extracting specific sections from memory"""
        memory = ReadmeMemory(str(temp_experiment_dir))
        
        # Add some content to different sections
        memory.write_memory("Protocol content", "Protocol")
        memory.append_insight("Test insight")
        
        # Get specific sections
        content = memory.read_memory()
        sections = memory._extract_sections(content)
        
        assert "Protocol" in sections
        assert "Insights" in sections
        assert "Protocol content" in sections["Protocol"]
    
    def test_memory_persistence(self, temp_experiment_dir):
        """Test that memory changes persist across instances"""
        # First instance
        memory1 = ReadmeMemory(str(temp_experiment_dir))
        memory1.append_insight("Persistent insight")
        
        # Second instance (simulates new session)
        memory2 = ReadmeMemory(str(temp_experiment_dir))
        content = memory2.read_memory()
        
        assert "Persistent insight" in content
    
    def test_multiple_insights_ordering(self, temp_experiment_dir):
        """Test that multiple insights maintain chronological order"""
        memory = ReadmeMemory(str(temp_experiment_dir))
        
        insights = [
            "First observation",
            "Second observation", 
            "Third observation"
        ]
        
        for insight in insights:
            memory.append_insight(insight)
        
        content = memory.read_memory()
        
        # Verify all insights present and in order
        first_pos = content.find("First observation")
        second_pos = content.find("Second observation")
        third_pos = content.find("Third observation")
        
        assert first_pos < second_pos < third_pos
    
    def test_section_update_overwrites(self, temp_experiment_dir):
        """Test that updating a section overwrites previous content"""
        memory = ReadmeMemory(str(temp_experiment_dir))
        
        # Write initial content
        memory.write_memory("Initial protocol", "Protocol")
        
        # Update with new content
        memory.write_memory("Updated protocol", "Protocol")
        
        content = memory.read_memory()
        assert "Updated protocol" in content
        assert "Initial protocol" not in content
    
    def test_change_log_updates(self, temp_experiment_dir):
        """Test that change log is updated with modifications"""
        memory = ReadmeMemory(str(temp_experiment_dir))
        
        # Make some changes
        memory.append_insight("New insight")
        memory.write_memory("Protocol update", "Protocol")
        
        content = memory.read_memory()
        
        # Verify change log exists and has entries
        assert "## Change Log" in content
        # Should have timestamp entries
        today = datetime.now().strftime("%Y-%m-%d")
        assert content.count(today) >= 2  # At least 2 entries for today
    
    def test_empty_experiment_directory(self, temp_dir):
        """Test creating memory in empty directory"""
        empty_exp_dir = temp_dir / "empty_experiment"
        empty_exp_dir.mkdir()
        
        memory = ReadmeMemory(str(empty_exp_dir))
        
        # Should create README
        assert memory.readme_path.exists()
        
        content = memory.read_memory()
        assert "# Experiment" in content
        assert "## Status" in content