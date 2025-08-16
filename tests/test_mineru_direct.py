#!/usr/bin/env python3
"""
Test MinerU directly using the CLI command approach.
Since MinerU v2.1.11 is installed, we'll use it via subprocess.
"""

import asyncio
import subprocess
import tempfile
import shutil
from pathlib import Path
import json

# Test file
TEST_PDF = Path("/data/luyit/script/git/Labacc_copilot/data/extra_test_file/For lung cancer tissue dissociation.pdf")


def test_mineru_cli():
    """Test MinerU via CLI"""
    print("🧪 Testing MinerU CLI")
    print("-" * 40)
    
    if not TEST_PDF.exists():
        print(f"❌ Test PDF not found: {TEST_PDF}")
        return False
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "output"
        output_dir.mkdir()
        
        # Run MinerU CLI
        cmd = [
            "mineru",
            "-p", str(TEST_PDF),
            "-o", str(output_dir),
            "-m", "auto",  # Auto-detect method
            "-b", "pipeline"  # Use pipeline backend
        ]
        
        print(f"Running: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            print(f"Return code: {result.returncode}")
            
            if result.stdout:
                print("STDOUT:")
                print(result.stdout[:500])
            
            if result.stderr:
                print("STDERR:")
                print(result.stderr[:500])
            
            # Check for output files
            md_files = list(output_dir.glob("**/*.md"))
            if md_files:
                print(f"✅ Found {len(md_files)} markdown files")
                for md_file in md_files[:3]:
                    print(f"   - {md_file.relative_to(output_dir)}")
                    content = md_file.read_text()[:200]
                    print(f"     Content preview: {content}...")
                return True
            else:
                print("❌ No markdown files generated")
                
                # Check what was generated
                all_files = list(output_dir.rglob("*"))
                if all_files:
                    print(f"Found {len(all_files)} other files:")
                    for f in all_files[:5]:
                        if f.is_file():
                            print(f"   - {f.relative_to(output_dir)}")
                
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ MinerU timed out")
            return False
        except Exception as e:
            print(f"❌ Error running MinerU: {e}")
            return False


async def test_mineru_python_api():
    """Test using MinerU Python API"""
    print("\n🧪 Testing MinerU Python API")
    print("-" * 40)
    
    try:
        # Try importing mineru modules
        try:
            from mineru.parse_pdf import parse_pdf
            print("✅ Found mineru.parse_pdf")
        except ImportError as e:
            print(f"❌ Cannot import parse_pdf: {e}")
        
        try:
            from mineru import Pipeline
            print("✅ Found mineru.Pipeline")
        except ImportError as e:
            print(f"❌ Cannot import Pipeline: {e}")
        
        try:
            from mineru.processor import PDFProcessor
            print("✅ Found mineru.processor.PDFProcessor")
        except ImportError as e:
            print(f"❌ Cannot import PDFProcessor: {e}")
        
        # Try to find the actual API
        import mineru
        print(f"MinerU module path: {mineru.__file__}")
        
        # List mineru attributes
        attrs = [a for a in dir(mineru) if not a.startswith('_')]
        print(f"MinerU attributes: {attrs[:10]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Python API: {e}")
        return False


async def test_mineru_via_subprocess():
    """Test MinerU using subprocess from Python (as file_conversion.py would)"""
    print("\n🧪 Testing MinerU via subprocess in Python")
    print("-" * 40)
    
    if not TEST_PDF.exists():
        print(f"❌ Test PDF not found: {TEST_PDF}")
        return False
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "mineru_output"
        output_dir.mkdir()
        
        # Copy PDF to temp location
        temp_pdf = Path(tmpdir) / TEST_PDF.name
        shutil.copy(TEST_PDF, temp_pdf)
        
        # Build command
        cmd = [
            "uv", "run", "mineru",
            "-p", str(temp_pdf),
            "-o", str(output_dir),
            "-m", "auto",
            "-b", "pipeline"
        ]
        
        print(f"Running: {' '.join(cmd)}")
        
        try:
            # Run asynchronously
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=60
            )
            
            print(f"Return code: {proc.returncode}")
            
            if stdout:
                print(f"STDOUT: {stdout.decode()[:500]}")
            if stderr:
                print(f"STDERR: {stderr.decode()[:500]}")
            
            # Check for markdown output
            md_files = list(output_dir.glob("**/*.md"))
            if md_files:
                print(f"✅ Generated {len(md_files)} markdown files")
                
                # Read the first markdown file
                md_content = md_files[0].read_text()
                print(f"   File: {md_files[0].name}")
                print(f"   Size: {len(md_content)} chars")
                print(f"   Preview: {md_content[:200]}...")
                
                return True
            else:
                print("❌ No markdown files generated")
                
                # List what was created
                all_files = list(output_dir.rglob("*"))
                print(f"Created {len(all_files)} files total")
                for f in all_files[:5]:
                    if f.is_file():
                        print(f"   - {f.relative_to(output_dir)}")
                
                return False
                
        except asyncio.TimeoutError:
            print("❌ MinerU subprocess timed out")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False


async def main():
    """Run all MinerU tests"""
    print("=" * 60)
    print("🔬 MINERU INTEGRATION TESTS")
    print("=" * 60)
    
    results = []
    
    # Test CLI directly
    results.append(("MinerU CLI", test_mineru_cli()))
    
    # Test Python API
    results.append(("MinerU Python API", await test_mineru_python_api()))
    
    # Test subprocess approach
    results.append(("MinerU Subprocess", await test_mineru_via_subprocess()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    passed = sum(1 for _, r in results if r)
    print(f"\nPassed: {passed}/{len(results)}")
    
    if passed == len(results):
        print("\n🎉 ALL TESTS PASSED!")
        print("\nMinerU is working! Now we need to update file_conversion.py to use it properly.")
    else:
        print("\n⚠️ Some tests failed")
        print("\nNext steps:")
        print("1. Check if MinerU models are downloaded")
        print("2. Update file_conversion.py to use subprocess approach")
        print("3. Or use the CLI directly via subprocess")


if __name__ == "__main__":
    asyncio.run(main())