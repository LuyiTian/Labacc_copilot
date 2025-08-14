"""
Unit tests for file analysis functionality
Tests isolated file analyzer components without agent integration
"""

import pytest
from pathlib import Path
import pandas as pd
from unittest.mock import Mock, patch

from src.components.file_analyzer import FileAnalyzer


@pytest.mark.unit
@pytest.mark.tools
class TestFileAnalyzer:
    """Unit tests for FileAnalyzer class"""
    
    def test_file_analyzer_initialization(self):
        """Test FileAnalyzer initialization"""
        analyzer = FileAnalyzer()
        assert analyzer is not None
        assert hasattr(analyzer, 'analyze_file')
    
    def test_csv_file_analysis(self, temp_dir, sample_csv_content):
        """Test CSV file analysis"""
        # Create test CSV file
        csv_file = temp_dir / "test_data.csv"
        csv_file.write_text(sample_csv_content)
        
        analyzer = FileAnalyzer()
        result = analyzer.analyze_csv(str(csv_file))
        
        # Verify analysis results
        assert isinstance(result, dict)
        assert "columns" in result
        assert "rows" in result
        assert "summary" in result
        
        # Verify content parsing
        assert "cell_count" in str(result["columns"])
        assert "viability" in str(result["columns"])
        assert result["rows"] >= 3  # 3 data rows + header
    
    def test_text_file_analysis(self, temp_dir):
        """Test text file analysis"""
        # Create test text file
        text_content = """
        Experimental Protocol:
        1. Prepare cell suspension
        2. Add treatment compounds
        3. Incubate at 37°C for 24 hours
        4. Measure viability
        
        Results: Cell viability decreased by 30% in treated samples.
        """
        text_file = temp_dir / "protocol.txt"
        text_file.write_text(text_content)
        
        analyzer = FileAnalyzer()
        result = analyzer.analyze_text(str(text_file))
        
        assert isinstance(result, dict)
        assert "type" in result
        assert "content" in result
        assert "summary" in result
        
        # Verify key content extraction
        assert "protocol" in result["summary"].lower()
        assert "viability" in result["summary"].lower()
    
    def test_excel_file_analysis(self, temp_dir):
        """Test Excel file analysis"""
        # Create test Excel file
        data = {
            "Sample": ["Control", "Treated", "Stressed"],
            "Cell_Count": [50000, 35000, 15000],
            "Viability": [95.2, 88.7, 72.1]
        }
        df = pd.DataFrame(data)
        excel_file = temp_dir / "data.xlsx"
        df.to_excel(excel_file, index=False)
        
        analyzer = FileAnalyzer()
        result = analyzer.analyze_excel(str(excel_file))
        
        assert isinstance(result, dict)
        assert "sheets" in result
        assert "summary" in result
        
        # Verify data extraction
        assert "Cell_Count" in str(result)
        assert "Viability" in str(result)
    
    @patch('src.components.file_analyzer.Image')
    def test_image_file_analysis(self, mock_image, temp_dir):
        """Test image file analysis"""
        # Mock image analysis
        mock_image_instance = Mock()
        mock_image.open.return_value = mock_image_instance
        mock_image_instance.size = (800, 600)
        mock_image_instance.format = "PNG"
        
        # Create dummy image file
        image_file = temp_dir / "gel_image.png"
        image_file.write_bytes(b"dummy_image_data")
        
        analyzer = FileAnalyzer()
        result = analyzer.analyze_image(str(image_file))
        
        assert isinstance(result, dict)
        assert "type" in result
        assert "format" in result
        assert "size" in result
        
        # Verify image metadata
        assert result["format"] == "PNG"
        assert result["size"] == (800, 600)
    
    def test_file_type_detection(self, temp_dir):
        """Test automatic file type detection"""
        analyzer = FileAnalyzer()
        
        # Test different file extensions
        assert analyzer._detect_file_type("data.csv") == "csv"
        assert analyzer._detect_file_type("image.png") == "image"
        assert analyzer._detect_file_type("document.txt") == "text"
        assert analyzer._detect_file_type("spreadsheet.xlsx") == "excel"
        assert analyzer._detect_file_type("unknown.xyz") == "unknown"
    
    def test_analyze_file_dispatcher(self, temp_dir, sample_csv_content):
        """Test that analyze_file method dispatches to correct analyzer"""
        # Create CSV file
        csv_file = temp_dir / "test.csv"
        csv_file.write_text(sample_csv_content)
        
        analyzer = FileAnalyzer()
        result = analyzer.analyze_file(str(csv_file))
        
        # Should detect CSV and use CSV analyzer
        assert "columns" in result  # CSV-specific field
        assert "rows" in result     # CSV-specific field
    
    def test_error_handling_nonexistent_file(self):
        """Test error handling for non-existent files"""
        analyzer = FileAnalyzer()
        
        with pytest.raises(FileNotFoundError):
            analyzer.analyze_file("nonexistent_file.csv")
    
    def test_error_handling_corrupted_csv(self, temp_dir):
        """Test error handling for corrupted CSV files"""
        # Create corrupted CSV
        corrupted_csv = temp_dir / "corrupted.csv"
        corrupted_csv.write_text("not,a,valid\ncsv,content,here,extra,columns")
        
        analyzer = FileAnalyzer()
        result = analyzer.analyze_csv(str(corrupted_csv))
        
        # Should handle gracefully
        assert isinstance(result, dict)
        assert "error" in result or "columns" in result
    
    def test_large_file_handling(self, temp_dir):
        """Test handling of large files (sampling/truncation)"""
        # Create large CSV content
        large_content = "sample,value\n"
        for i in range(10000):  # 10k rows
            large_content += f"sample_{i},{i * 10}\n"
        
        large_csv = temp_dir / "large_data.csv"
        large_csv.write_text(large_content)
        
        analyzer = FileAnalyzer()
        result = analyzer.analyze_csv(str(large_csv))
        
        # Should still process successfully (may sample/truncate)
        assert isinstance(result, dict)
        assert "rows" in result
        assert result["rows"] >= 100  # Should detect substantial number of rows
    
    def test_multisheet_excel_analysis(self, temp_dir):
        """Test analysis of Excel files with multiple sheets"""
        # Create multi-sheet Excel file
        with pd.ExcelWriter(temp_dir / "multi_sheet.xlsx") as writer:
            df1 = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
            df2 = pd.DataFrame({"X": [7, 8, 9], "Y": [10, 11, 12]})
            df1.to_excel(writer, sheet_name="Sheet1", index=False)
            df2.to_excel(writer, sheet_name="Sheet2", index=False)
        
        analyzer = FileAnalyzer()
        result = analyzer.analyze_excel(str(temp_dir / "multi_sheet.xlsx"))
        
        assert "sheets" in result
        assert len(result["sheets"]) == 2
        assert "Sheet1" in str(result["sheets"])
        assert "Sheet2" in str(result["sheets"])
    
    def test_file_metadata_extraction(self, temp_dir, sample_csv_content):
        """Test extraction of file metadata"""
        csv_file = temp_dir / "metadata_test.csv"
        csv_file.write_text(sample_csv_content)
        
        analyzer = FileAnalyzer()
        result = analyzer.analyze_file(str(csv_file))
        
        # Should include metadata
        assert "file_size" in result or "size" in result
        assert "file_name" in result or "name" in result
        assert result.get("file_name", result.get("name")) == "metadata_test.csv"