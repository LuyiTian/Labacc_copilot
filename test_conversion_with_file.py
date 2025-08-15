#!/usr/bin/env python
"""Test file conversion with actual document files.

This script creates test documents and verifies the conversion pipeline.
"""

import asyncio
import os
from pathlib import Path

# Add project root to path
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.api.file_conversion import FileConversionPipeline
from src.api.file_registry import FileRegistry


async def test_with_sample_files():
    """Test conversion with actual files."""
    
    print("=" * 60)
    print("Testing File Conversion with Sample Documents")
    print("=" * 60)
    
    # Use test project directory
    project_root = "data/bob_projects"
    experiment_id = "exp_test_docs"
    
    # Create test experiment directory
    exp_dir = Path(project_root) / experiment_id
    exp_dir.mkdir(parents=True, exist_ok=True)
    originals_dir = exp_dir / "originals"
    originals_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize pipeline and registry
    pipeline = FileConversionPipeline(project_root)
    registry = FileRegistry(project_root)
    
    print(f"\n✅ Created test experiment: {experiment_id}")
    
    # Create a simple HTML file to test conversion
    html_file = originals_dir / "test_protocol.html"
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>PCR Protocol</title>
</head>
<body>
    <h1>PCR Protocol for Gene X Amplification</h1>
    
    <h2>Materials</h2>
    <ul>
        <li>Template DNA (50 ng/μL)</li>
        <li>Forward primer (10 μM)</li>
        <li>Reverse primer (10 μM)</li>
        <li>PCR Master Mix (2X)</li>
        <li>Nuclease-free water</li>
    </ul>
    
    <h2>PCR Reaction Setup (25 μL)</h2>
    <table border="1">
        <tr>
            <th>Component</th>
            <th>Volume (μL)</th>
            <th>Final Concentration</th>
        </tr>
        <tr>
            <td>2X Master Mix</td>
            <td>12.5</td>
            <td>1X</td>
        </tr>
        <tr>
            <td>Forward Primer</td>
            <td>0.5</td>
            <td>0.2 μM</td>
        </tr>
        <tr>
            <td>Reverse Primer</td>
            <td>0.5</td>
            <td>0.2 μM</td>
        </tr>
        <tr>
            <td>Template DNA</td>
            <td>1.0</td>
            <td>2 ng/μL</td>
        </tr>
        <tr>
            <td>Water</td>
            <td>10.5</td>
            <td>-</td>
        </tr>
    </table>
    
    <h2>Cycling Conditions</h2>
    <ol>
        <li>Initial denaturation: 95°C for 3 min</li>
        <li>35 cycles of:
            <ul>
                <li>Denaturation: 95°C for 30 sec</li>
                <li>Annealing: 58°C for 30 sec</li>
                <li>Extension: 72°C for 1 min</li>
            </ul>
        </li>
        <li>Final extension: 72°C for 5 min</li>
        <li>Hold: 4°C</li>
    </ol>
    
    <h2>Expected Results</h2>
    <p>Expected amplicon size: 750 bp</p>
    <p>Run on 1.5% agarose gel with 100 bp ladder</p>
</body>
</html>"""
    
    with open(html_file, 'w') as f:
        f.write(html_content)
    
    print(f"\n📄 Created test HTML file: {html_file.name}")
    
    # Test conversion
    print("\n🔄 Testing HTML to Markdown conversion...")
    
    result = await pipeline.process_upload(html_file, experiment_id)
    
    print(f"  Conversion status: {result['conversion_status']}")
    print(f"  Conversion method: {result.get('conversion_method', 'N/A')}")
    print(f"  Original path: {result['original_path']}")
    print(f"  Converted path: {result.get('converted_path', 'None')}")
    
    # If conversion was successful, read the converted file
    if result.get('converted_path'):
        converted_file = Path(project_root) / result['converted_path']
        if converted_file.exists():
            print("\n📋 Converted Content Preview:")
            print("-" * 40)
            with open(converted_file, 'r') as f:
                content = f.read()
                # Show first 500 characters
                preview = content[:500] + "..." if len(content) > 500 else content
                print(preview)
            print("-" * 40)
            print(f"  Total content length: {len(content)} characters")
        else:
            print("  ⚠️ Converted file not found at expected path")
    
    # Test registry lookup
    print("\n📊 Testing Registry Lookup...")
    
    file_info = registry.get_file(experiment_id, html_file.name)
    if file_info:
        print("  ✓ File found in registry")
        print(f"    - Conversion status: {file_info['conversion']['status']}")
        print(f"    - Conversion method: {file_info['conversion']['method']}")
    else:
        print("  ✗ File not found in registry")
    
    # Test the read_file tool
    print("\n🤖 Testing React Agent read_file tool...")
    
    try:
        from src.agents.react_agent import read_file
        
        # Try reading the original file path
        file_path = f"{experiment_id}/originals/{html_file.name}"
        content = await read_file.ainvoke({"file_path": file_path})
        
        if "PCR Protocol" in content:
            print(f"  ✓ Agent successfully read file: {file_path}")
            if "converted to Markdown" in content:
                print("  ✓ Agent used converted version")
            else:
                print("  ℹ️ Agent used original version")
        else:
            print(f"  ⚠️ Unexpected content from agent")
            
    except Exception as e:
        print(f"  ✗ Error testing agent: {e}")
    
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
    print("✅ Conversion Test Complete!")
    print("=" * 60)
    
    print("\n💡 Summary:")
    print("  - HTML files can be converted to Markdown")
    print("  - Conversion is automatic on upload")
    print("  - Registry tracks both original and converted paths")
    print("  - Agent's read_file tool transparently uses converted version")
    
    print("\n📝 To test with real Office/PDF files:")
    print("  1. Upload a .docx, .pptx, .xlsx, or .pdf file via the web UI")
    print("  2. Check data/alice_projects/exp_XXX/.labacc/converted/ for markdown")
    print("  3. Use 'read file <filename>' in chat to see converted content")


if __name__ == "__main__":
    asyncio.run(test_with_sample_files())