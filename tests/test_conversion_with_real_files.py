#!/usr/bin/env python3
"""
Test file conversion with REAL PDF and DOCX files.
This will catch actual issues with MinerU and MarkItDown.
"""

import asyncio
import shutil
import tempfile
from pathlib import Path
import sys
import os

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from src.api.file_conversion import FileConversionPipeline
from src.api.file_registry import FileRegistry

# Real test files
TEST_PDF = Path("/data/luyit/script/git/Labacc_copilot/data/extra_test_file/For lung cancer tissue dissociation.pdf")
TEST_DOCX = Path("/data/luyit/script/git/Labacc_copilot/data/extra_test_file/For lung cancer tissue dissociation.docx")


async def test_real_pdf_conversion():
    """Test PDF conversion with a real PDF file"""
    print("\n📋 Testing Real PDF Conversion")
    print("-" * 40)
    
    if not TEST_PDF.exists():
        print(f"❌ Test PDF not found: {TEST_PDF}")
        return False
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Create experiment structure
        exp_id = "exp_002_optimization"
        exp_dir = tmpdir_path / exp_id
        exp_dir.mkdir(parents=True)
        originals_dir = exp_dir / "originals"
        originals_dir.mkdir()
        
        # Copy test PDF
        test_pdf_copy = originals_dir / TEST_PDF.name
        shutil.copy(TEST_PDF, test_pdf_copy)
        print(f"✓ Copied test PDF to: {test_pdf_copy}")
        
        # Initialize pipeline
        pipeline = FileConversionPipeline(tmpdir_path)
        
        # Check MinerU availability
        print(f"✓ MinerU available: {pipeline._mineru_available}")
        
        try:
            # Process the upload
            result = await pipeline.process_upload(test_pdf_copy, exp_id)
            
            print(f"Conversion status: {result['conversion_status']}")
            print(f"Conversion method: {result.get('conversion_method', 'N/A')}")
            
            if result['conversion_status'] == 'success':
                converted_path = result.get('converted_path')
                if converted_path:
                    full_path = tmpdir_path / converted_path
                    if full_path.exists():
                        content = full_path.read_text()[:200]
                        print(f"✅ PDF converted successfully")
                        print(f"   Output: {converted_path}")
                        print(f"   First 200 chars: {content}...")
                        return True
                    else:
                        print(f"❌ Converted file doesn't exist: {full_path}")
                else:
                    print(f"❌ No converted_path in result")
            else:
                print(f"❌ Conversion failed: {result}")
                if 'error' in result:
                    print(f"   Error: {result['error']}")
                    
        except Exception as e:
            print(f"❌ Exception during conversion: {e}")
            import traceback
            traceback.print_exc()
    
    return False


async def test_real_docx_conversion():
    """Test DOCX conversion with a real Word document"""
    print("\n📋 Testing Real DOCX Conversion")
    print("-" * 40)
    
    if not TEST_DOCX.exists():
        print(f"❌ Test DOCX not found: {TEST_DOCX}")
        return False
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Create experiment structure
        exp_id = "exp_003_test"
        exp_dir = tmpdir_path / exp_id
        exp_dir.mkdir(parents=True)
        
        # Copy test DOCX
        test_docx_copy = exp_dir / TEST_DOCX.name
        shutil.copy(TEST_DOCX, test_docx_copy)
        print(f"✓ Copied test DOCX to: {test_docx_copy}")
        
        # Initialize pipeline
        pipeline = FileConversionPipeline(tmpdir_path)
        
        try:
            # Process the upload
            result = await pipeline.process_upload(test_docx_copy, exp_id)
            
            print(f"Conversion status: {result['conversion_status']}")
            print(f"Conversion method: {result.get('conversion_method', 'N/A')}")
            
            if result['conversion_status'] == 'success':
                converted_path = result.get('converted_path')
                if converted_path:
                    full_path = tmpdir_path / converted_path
                    if full_path.exists():
                        content = full_path.read_text()[:200]
                        print(f"✅ DOCX converted successfully")
                        print(f"   Output: {converted_path}")
                        print(f"   First 200 chars: {content}...")
                        return True
                    else:
                        print(f"❌ Converted file doesn't exist: {full_path}")
                else:
                    print(f"❌ No converted_path in result")
            else:
                print(f"❌ Conversion failed: {result}")
                    
        except Exception as e:
            print(f"❌ Exception during conversion: {e}")
            import traceback
            traceback.print_exc()
    
    return False


async def test_mineru_models():
    """Check if MinerU models are properly installed"""
    print("\n📋 Checking MinerU Models")
    print("-" * 40)
    
    model_dir = Path.home() / ".magic-pdf" / "models"
    
    if not model_dir.exists():
        print(f"❌ Model directory doesn't exist: {model_dir}")
        print("   Run: magic-pdf download-models")
        return False
    
    # Check for model files
    model_files = list(model_dir.rglob("*.pth")) + list(model_dir.rglob("*.onnx"))
    
    if not model_files:
        print(f"❌ No model files found in {model_dir}")
        print("   Run: magic-pdf download-models")
        return False
    
    print(f"✅ Found {len(model_files)} model files:")
    for mf in model_files[:5]:  # Show first 5
        print(f"   - {mf.name}")
    
    return True


async def test_file_location_consistency():
    """Test that files are saved in correct locations"""
    print("\n📋 Testing File Location Consistency")
    print("-" * 40)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Create experiment
        exp_id = "exp_001_protocol_test"
        exp_dir = tmpdir_path / exp_id
        exp_dir.mkdir(parents=True)
        
        # Test with real DOCX
        if TEST_DOCX.exists():
            # Copy to originals folder
            originals_dir = exp_dir / "originals"
            originals_dir.mkdir()
            test_file = originals_dir / TEST_DOCX.name
            shutil.copy(TEST_DOCX, test_file)
            
            pipeline = FileConversionPipeline(tmpdir_path)
            result = await pipeline.process_upload(test_file, exp_id)
            
            # Check locations
            expected_converted = exp_dir / ".labacc" / "converted" / f"{TEST_DOCX.stem}.md"
            expected_registry = exp_dir / ".labacc" / "file_registry.json"
            
            checks = [
                (originals_dir.exists(), "Originals directory exists"),
                (test_file.exists(), "Original file in originals/"),
                ((exp_dir / ".labacc").exists(), ".labacc directory created"),
                ((exp_dir / ".labacc" / "converted").exists(), "converted/ directory created"),
                (expected_registry.exists(), "Registry file created"),
            ]
            
            all_good = True
            for check, desc in checks:
                if check:
                    print(f"✅ {desc}")
                else:
                    print(f"❌ {desc}")
                    all_good = False
            
            return all_good
    
    return False


async def main():
    """Run all tests with real files"""
    print("=" * 60)
    print("🧪 REAL FILE CONVERSION TESTS")
    print("=" * 60)
    
    # Set up minimal logging
    import logging
    logging.basicConfig(level=logging.WARNING)
    logging.getLogger('src.api.file_conversion').setLevel(logging.INFO)
    
    results = []
    
    # Run tests
    results.append(("MinerU Models Check", await test_mineru_models()))
    results.append(("Real PDF Conversion", await test_real_pdf_conversion()))
    results.append(("Real DOCX Conversion", await test_real_docx_conversion()))
    results.append(("File Location Consistency", await test_file_location_consistency()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print(f"\n⚠️ {total - passed} tests failed")
        print("\nTo fix MinerU issues:")
        print("1. Install MinerU: pip install magic-pdf[full]")
        print("2. Download models: magic-pdf download-models")
        print("3. Test CLI: magic-pdf -p /path/to/test.pdf")


if __name__ == "__main__":
    asyncio.run(main())