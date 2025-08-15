#!/usr/bin/env python
"""Test script for file conversion and registry system.

This script tests the v3.0 file upload, conversion, and reading workflow.
"""

import asyncio
import json
import os
from pathlib import Path
import tempfile
from datetime import datetime

# Add project root to path
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.api.file_conversion import FileConversionPipeline
from src.api.file_registry import FileRegistry, get_file_registry


async def test_conversion_pipeline():
    """Test the file conversion pipeline with different file types."""
    
    print("=" * 60)
    print("Testing File Conversion Pipeline v3.0")
    print("=" * 60)
    
    # Use test project directory
    project_root = "data/bob_projects"
    experiment_id = "exp_test_conversion"
    
    # Create test experiment directory
    exp_dir = Path(project_root) / experiment_id
    exp_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize pipeline and registry
    pipeline = FileConversionPipeline(project_root)
    registry = FileRegistry(project_root)
    
    print(f"\n✅ Created test experiment: {experiment_id}")
    
    # Test 1: Check conversion detection
    print("\n📋 Test 1: Checking conversion detection...")
    test_files = [
        ("document.pdf", True),
        ("presentation.pptx", True),
        ("spreadsheet.xlsx", True),
        ("report.docx", True),
        ("data.csv", False),
        ("script.py", False),
        ("image.png", False),
        ("readme.md", False)
    ]
    
    for filename, should_convert in test_files:
        needs_conversion = pipeline.needs_conversion(filename)
        status = "✓" if needs_conversion == should_convert else "✗"
        print(f"  {status} {filename}: needs_conversion={needs_conversion} (expected={should_convert})")
    
    # Test 2: Create a simple text file to test conversion
    print("\n📋 Test 2: Testing actual file conversion...")
    
    # Create a test markdown file (no conversion needed)
    test_md_file = exp_dir / "test_notes.md"
    test_md_content = """# Test Notes

## Overview
This is a test markdown file for the conversion pipeline.

## Data
- Sample 1: 95% efficiency
- Sample 2: 87% efficiency
- Sample 3: 91% efficiency

## Conclusion
The results show consistent performance.
"""
    
    with open(test_md_file, 'w') as f:
        f.write(test_md_content)
    
    print(f"  Created test file: {test_md_file.name}")
    
    # Process the markdown file (should not convert)
    result = await pipeline.process_upload(test_md_file, experiment_id)
    print(f"  Conversion status: {result['conversion_status']}")
    print(f"  Converted path: {result.get('converted_path', 'None')}")
    
    # Test 3: Test file registry
    print("\n📋 Test 3: Testing file registry...")
    
    # Add file to registry
    file_entry = registry.add_file(
        experiment_id=experiment_id,
        filename=test_md_file.name,
        original_path=str(test_md_file.relative_to(Path(project_root))),
        file_size=test_md_file.stat().st_size,
        conversion_status="not_needed"
    )
    print(f"  Added to registry: {test_md_file.name}")
    
    # Load and verify registry
    loaded_registry = registry.load_registry(experiment_id)
    print(f"  Registry version: {loaded_registry['version']}")
    print(f"  Total files tracked: {loaded_registry['total_files']}")
    
    # Test 4: Test file lookup
    print("\n📋 Test 4: Testing file lookup...")
    
    file_info = registry.get_file(experiment_id, test_md_file.name)
    if file_info:
        print(f"  ✓ Found file in registry: {test_md_file.name}")
        print(f"    - Original path: {file_info['original_path']}")
        print(f"    - File size: {file_info['file_size']} bytes")
        print(f"    - Conversion status: {file_info['conversion']['status']}")
    else:
        print(f"  ✗ File not found in registry")
    
    # Test 5: Test readable path resolution
    print("\n📋 Test 5: Testing readable path resolution...")
    
    readable_path = registry.get_readable_path(experiment_id, str(test_md_file.relative_to(Path(project_root))))
    print(f"  Original path: {test_md_file.relative_to(Path(project_root))}")
    print(f"  Readable path: {readable_path}")
    print(f"  Same path (no conversion): {readable_path == str(test_md_file.relative_to(Path(project_root)))}")
    
    # Test 6: Simulate Office/PDF conversion (if libraries are available)
    print("\n📋 Test 6: Testing conversion libraries...")
    
    try:
        markitdown = pipeline._get_markitdown()
        print("  ✓ MarkItDown is available")
    except Exception as e:
        print(f"  ✗ MarkItDown not available: {e}")
    
    if pipeline._mineru_available:
        print("  ✓ MinerU is available")
    else:
        print("  ✗ MinerU not available (install with: pip install magic-pdf[full])")
    
    # Test 7: Check registry file structure
    print("\n📋 Test 7: Checking file structure...")
    
    labacc_dir = exp_dir / ".labacc"
    registry_file = labacc_dir / "file_registry.json"
    converted_dir = labacc_dir / "converted"
    
    print(f"  .labacc directory exists: {labacc_dir.exists()}")
    print(f"  Registry file exists: {registry_file.exists()}")
    print(f"  Converted directory exists: {converted_dir.exists()}")
    
    if registry_file.exists():
        with open(registry_file, 'r') as f:
            registry_content = json.load(f)
            print(f"  Registry contains {len(registry_content.get('files', {}))} files")
    
    # Cleanup - ALWAYS remove test folders
    print("\n🧹 Cleanup...")
    print(f"  Removing test directory: {exp_dir}")
    
    try:
        import shutil
        if exp_dir.exists():
            shutil.rmtree(exp_dir)
            print("  ✅ Test directory cleaned up")
    except Exception as e:
        print(f"  ⚠️ Warning: Could not clean up test directory: {e}")
    
    print("\n" + "=" * 60)
    print("✅ File Conversion Pipeline Tests Complete!")
    print("=" * 60)
    
    return True


async def test_react_agent_integration():
    """Test that the React agent can read converted files."""
    
    print("\n" + "=" * 60)
    print("Testing React Agent Integration")
    print("=" * 60)
    
    try:
        from src.agents.react_agent import read_file
        
        # Test reading a file through the agent's read_file tool
        test_file = "exp_test_conversion/test_notes.md"
        
        print(f"\n📋 Testing read_file tool...")
        print(f"  Reading: {test_file}")
        
        content = await read_file.ainvoke({"file_path": test_file})
        
        if "Test Notes" in content:
            print("  ✓ Successfully read file content through agent tool")
            print(f"  Content preview: {content[:100]}...")
        else:
            print("  ✗ Failed to read file content")
            print(f"  Result: {content}")
            
    except Exception as e:
        print(f"  ✗ Error testing agent integration: {e}")
    
    print("\n" + "=" * 60)
    print("✅ React Agent Integration Test Complete!")
    print("=" * 60)


async def main():
    """Run all tests."""
    # Test conversion pipeline
    await test_conversion_pipeline()
    
    # Test React agent integration
    await test_react_agent_integration()
    
    print("\n🎉 All tests completed!")
    print("\nNext steps:")
    print("1. Install MarkItDown: pip install markitdown")
    print("2. Install MinerU (optional): pip install magic-pdf[full]")
    print("3. Upload a PDF or Office file through the web interface")
    print("4. Check that it's automatically converted to Markdown")
    print("5. Use the read_file tool to read the converted content")


if __name__ == "__main__":
    asyncio.run(main())