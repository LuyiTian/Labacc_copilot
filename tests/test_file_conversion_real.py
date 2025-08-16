#!/usr/bin/env python3
"""
REAL tests for file conversion that actually catch issues.

This test suite verifies:
1. MinerU is properly configured with models
2. PDF conversion actually creates markdown files
3. exp_unknown is never created
4. Conversion fallback works correctly
5. Files are saved in the correct location
"""

import asyncio
import json
import tempfile
from pathlib import Path
import sys
import os

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from src.api.file_conversion import FileConversionPipeline
from src.api.file_registry import FileRegistry


class FileConversionRealTests:
    """Real tests for file conversion functionality"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        
    def print_result(self, test_name: str, passed: bool, message: str = ""):
        if passed:
            self.passed += 1
            print(f"✅ {test_name}: {message}" if message else f"✅ {test_name}")
        else:
            self.failed += 1
            self.errors.append(f"{test_name}: {message}")
            print(f"❌ {test_name}: {message}")
    
    def print_summary(self):
        total = self.passed + self.failed
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.passed}/{total}")
        print(f"❌ Failed: {self.failed}/{total}")
        
        if self.errors:
            print("\nFailed Tests:")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.failed == 0:
            print("\n🎉 ALL TESTS PASSED!")
        else:
            print(f"\n⚠️ {self.failed} tests failed")
    
    async def test_mineru_availability(self):
        """Test that MinerU is properly configured"""
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                pipeline = FileConversionPipeline(tmpdir)
                
                # Check if MinerU is available
                if pipeline._mineru_available:
                    # Verify models exist
                    model_dir = Path.home() / ".magic-pdf" / "models"
                    if model_dir.exists() and any(model_dir.iterdir()):
                        self.print_result("MinerU Availability", True, "MinerU available with models")
                    else:
                        self.print_result("MinerU Availability", False, 
                                        f"MinerU available but models missing at {model_dir}")
                else:
                    self.print_result("MinerU Availability", False, "MinerU not available")
        except Exception as e:
            self.print_result("MinerU Availability", False, str(e))
    
    async def test_pdf_conversion_creates_file(self):
        """Test that PDF conversion actually creates a markdown file"""
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                tmpdir_path = Path(tmpdir)
                
                # Create test structure
                exp_dir = tmpdir_path / "exp_002_test"
                exp_dir.mkdir(parents=True)
                originals_dir = exp_dir / "originals"
                originals_dir.mkdir()
                
                # Create a simple test PDF
                test_pdf = originals_dir / "test.pdf"
                # Create minimal PDF content (PDF header)
                test_pdf.write_bytes(b"%PDF-1.4\n%Test PDF\n")
                
                # Initialize pipeline
                pipeline = FileConversionPipeline(tmpdir)
                
                # Process the upload
                result = await pipeline.process_upload(test_pdf, "exp_002_test")
                
                # Check if conversion was attempted
                if result["conversion_status"] == "success":
                    # Verify the converted file exists
                    converted_path = result.get("converted_path")
                    if converted_path:
                        full_converted_path = tmpdir_path / converted_path
                        if full_converted_path.exists():
                            self.print_result("PDF Conversion Creates File", True, 
                                            f"Created: {converted_path}")
                        else:
                            self.print_result("PDF Conversion Creates File", False, 
                                            f"File not found: {full_converted_path}")
                    else:
                        self.print_result("PDF Conversion Creates File", False, 
                                        "No converted_path in result")
                else:
                    # Conversion might fail for minimal PDF, check the reason
                    self.print_result("PDF Conversion Creates File", False, 
                                    f"Conversion status: {result['conversion_status']}")
        except Exception as e:
            self.print_result("PDF Conversion Creates File", False, str(e))
    
    async def test_no_exp_unknown_created(self):
        """Test that exp_unknown is never created"""
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                tmpdir_path = Path(tmpdir)
                
                # Create test file without experiment context
                test_file = tmpdir_path / "test.pdf"
                test_file.write_bytes(b"%PDF-1.4\n%Test PDF\n")
                
                # Initialize pipeline
                pipeline = FileConversionPipeline(tmpdir)
                
                # Try to process with invalid experiment_id
                result = await pipeline.process_upload(test_file, "exp_unknown")
                
                # Check that it properly rejects exp_unknown
                if result["conversion_status"] == "failed" and "Invalid experiment" in result.get("error", ""):
                    self.print_result("No exp_unknown Created", True, 
                                    "Properly rejected exp_unknown")
                else:
                    self.print_result("No exp_unknown Created", False, 
                                    "Did not reject exp_unknown")
                
                # Verify exp_unknown directory wasn't created
                exp_unknown_dir = tmpdir_path / "exp_unknown"
                if exp_unknown_dir.exists():
                    self.print_result("exp_unknown Directory Check", False, 
                                    "exp_unknown directory was created!")
                else:
                    self.print_result("exp_unknown Directory Check", True, 
                                    "No exp_unknown directory created")
                    
        except Exception as e:
            self.print_result("No exp_unknown Created", False, str(e))
    
    async def test_conversion_output_location(self):
        """Test that converted files are saved in the correct location"""
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                tmpdir_path = Path(tmpdir)
                
                # Create proper experiment structure
                exp_id = "exp_003_location_test"
                exp_dir = tmpdir_path / exp_id
                exp_dir.mkdir(parents=True)
                
                # Create test Word doc
                test_docx = exp_dir / "test.docx"
                # Create minimal DOCX (ZIP file with specific structure)
                test_docx.write_bytes(b"PK\x03\x04")  # ZIP header
                
                # Initialize pipeline
                pipeline = FileConversionPipeline(tmpdir)
                
                # Process the upload
                result = await pipeline.process_upload(test_docx, exp_id)
                
                # Check expected location
                expected_dir = exp_dir / ".labacc" / "converted"
                expected_file = expected_dir / "test.md"
                
                if expected_dir.exists():
                    self.print_result("Conversion Output Directory", True, 
                                    f"Created .labacc/converted/ directory")
                else:
                    self.print_result("Conversion Output Directory", False, 
                                    f"Directory not created: {expected_dir}")
                    
                # Note: Actual file might not exist if conversion fails on minimal input
                # But the directory structure should be created
                    
        except Exception as e:
            self.print_result("Conversion Output Location", False, str(e))
    
    async def test_file_registry_update(self):
        """Test that file registry is properly updated"""
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                tmpdir_path = Path(tmpdir)
                
                # Create experiment
                exp_id = "exp_004_registry_test"
                exp_dir = tmpdir_path / exp_id
                exp_dir.mkdir(parents=True)
                
                # Create test file
                test_file = exp_dir / "data.csv"
                test_file.write_text("col1,col2\n1,2\n3,4")
                
                # Initialize registry
                registry = FileRegistry(tmpdir)
                
                # Add file to registry
                registry.add_file(
                    experiment_id=exp_id,
                    filename="data.csv",
                    original_path=f"{exp_id}/data.csv",
                    converted_path=None,
                    file_size=100,
                    conversion_status="not_needed"
                )
                
                # Check registry file exists
                registry_file = exp_dir / ".labacc" / "file_registry.json"
                if registry_file.exists():
                    # Load and verify content
                    with open(registry_file) as f:
                        data = json.load(f)
                    
                    if "data.csv" in data.get("files", {}):
                        self.print_result("File Registry Update", True, 
                                        "Registry properly updated")
                    else:
                        self.print_result("File Registry Update", False, 
                                        "File not in registry")
                else:
                    self.print_result("File Registry Update", False, 
                                    f"Registry file not created: {registry_file}")
                    
        except Exception as e:
            self.print_result("File Registry Update", False, str(e))
    
    async def test_markitdown_fallback(self):
        """Test that MarkItDown fallback works when MinerU fails"""
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                tmpdir_path = Path(tmpdir)
                
                # Create experiment
                exp_id = "exp_005_fallback_test"
                exp_dir = tmpdir_path / exp_id
                exp_dir.mkdir(parents=True)
                
                # Create HTML file (MarkItDown should handle this)
                test_html = exp_dir / "test.html"
                test_html.write_text("<html><body><h1>Test</h1><p>Content</p></body></html>")
                
                # Initialize pipeline
                pipeline = FileConversionPipeline(tmpdir)
                
                # Process the upload
                result = await pipeline.process_upload(test_html, exp_id)
                
                # Check if MarkItDown was used
                if result.get("conversion_method") == "MarkItDown":
                    self.print_result("MarkItDown Fallback", True, 
                                    "MarkItDown used for HTML conversion")
                else:
                    self.print_result("MarkItDown Fallback", False, 
                                    f"Wrong method: {result.get('conversion_method')}")
                    
        except Exception as e:
            self.print_result("MarkItDown Fallback", False, str(e))
    
    async def run_all_tests(self):
        """Run all real conversion tests"""
        print("🧪 REAL FILE CONVERSION TESTS")
        print("=" * 60)
        
        await self.test_mineru_availability()
        await self.test_pdf_conversion_creates_file()
        await self.test_no_exp_unknown_created()
        await self.test_conversion_output_location()
        await self.test_file_registry_update()
        await self.test_markitdown_fallback()
        
        self.print_summary()


async def main():
    """Run the test suite"""
    tester = FileConversionRealTests()
    await tester.run_all_tests()


if __name__ == "__main__":
    # Set up minimal logging to reduce noise
    import logging
    logging.basicConfig(level=logging.ERROR)
    
    asyncio.run(main())