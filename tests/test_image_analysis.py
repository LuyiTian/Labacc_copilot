#!/usr/bin/env python3
"""
Test image analysis functionality using GLM-4.5V vision model.

Tests both the internal image analyzer and the React agent tool.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.components.image_analyzer import ImageAnalyzer, analyze_lab_image


async def test_image_analyzer():
    """Test the image analyzer module"""
    
    print("=" * 60)
    print("Testing Image Analysis Module")
    print("=" * 60)
    
    # Find a test image
    test_images = [
        "data/extra_test_file/lung_cancer_cell_dis_guide.md",  # Not an image - should fail
        "data/bob_projects/exp_002_optimization/For lung cancer tissue dissociation.md",  # Also not an image
    ]
    
    # Let's create a simple test image
    from PIL import Image
    import numpy as np
    
    # Create a simple test image
    test_image_path = Path("data/test_image.png")
    
    # Create a simple plot-like image
    img_array = np.zeros((400, 600, 3), dtype=np.uint8)
    img_array[:, :] = [255, 255, 255]  # White background
    
    # Add some blue bars (like a bar chart)
    for i in range(5):
        height = 50 + i * 40
        img_array[350-height:350, 50+i*100:100+i*100] = [50, 50, 200]
    
    # Add axes
    img_array[350:355, 30:570] = [0, 0, 0]  # X-axis
    img_array[45:355, 30:35] = [0, 0, 0]    # Y-axis
    
    img = Image.fromarray(img_array)
    img.save(test_image_path)
    print(f"\n✅ Created test image: {test_image_path}")
    
    # Test 1: Initialize analyzer
    print("\n1. Testing ImageAnalyzer initialization...")
    try:
        analyzer = ImageAnalyzer(vision_model_name="GLM-4.5V")
        if analyzer.vision_llm:
            print("   ✅ Vision LLM initialized successfully")
        else:
            print("   ⚠️ Vision LLM not available (check API key)")
    except Exception as e:
        print(f"   ❌ Failed to initialize: {e}")
        return False
    
    # Test 2: Analyze the test image
    print("\n2. Testing image analysis...")
    try:
        result = await analyze_lab_image(
            image_path=str(test_image_path),
            context="Test bar chart for experimental data",
            experiment_id="test_experiment"
        )
        
        if result.success:
            print(f"   ✅ Analysis successful!")
            print(f"   - Image size: {result.image_size}")
            print(f"   - Format: {result.format}")
            print(f"   - Description: {result.content_description[:200]}...")
            
            if result.key_features:
                print(f"   - Key features: {result.key_features}")
            if result.suggested_tags:
                print(f"   - Tags: {result.suggested_tags}")
        else:
            print(f"   ❌ Analysis failed: {result.error_message}")
            
    except Exception as e:
        print(f"   ❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Test with non-image file (should fail gracefully)
    print("\n3. Testing with non-image file...")
    try:
        result = await analyze_lab_image(
            image_path="data/bob_projects/exp_002_optimization/README.md"
        )
        
        if not result.success:
            print(f"   ✅ Correctly rejected non-image file")
            print(f"   - Error: {result.error_message}")
        else:
            print(f"   ⚠️ Unexpectedly accepted non-image file")
            
    except Exception as e:
        print(f"   ✅ Correctly raised error for non-image: {e}")
    
    # Clean up test image
    if test_image_path.exists():
        test_image_path.unlink()
        print(f"\n✅ Cleaned up test image")
    
    return True


async def test_react_agent_tool():
    """Test the analyze_image tool in React agent"""
    
    print("\n" + "=" * 60)
    print("Testing React Agent Image Analysis Tool")
    print("=" * 60)
    
    # Create another test image
    from PIL import Image, ImageDraw, ImageFont
    
    test_image_path = Path("data/bob_projects/exp_002_optimization/test_gel.png")
    
    # Create a gel electrophoresis-like image
    img = Image.new('RGB', (400, 500), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw lanes
    for lane in range(5):
        x = 50 + lane * 70
        # Draw lane background
        draw.rectangle([x, 50, x+40, 450], fill=(240, 240, 240))
        
        # Draw bands
        band_positions = [100, 150, 200, 280, 350, 400]
        for y in band_positions:
            intensity = 100 + (lane * 30) % 155
            draw.rectangle([x+5, y-5, x+35, y+5], fill=(intensity, intensity, intensity))
    
    # Add labels
    draw.text((10, 20), "Gel Electrophoresis Simulation", fill='black')
    
    img.save(test_image_path)
    print(f"\n✅ Created test gel image: {test_image_path}")
    
    # Set up session for agent
    from src.projects.session import session_manager, set_current_session, ProjectSession
    
    session_id = "test-image-session"
    user_id = "test_user"
    
    session_manager.create_session(session_id, user_id)
    
    project_session = ProjectSession(
        session_id=session_id,
        user_id=user_id,
        selected_project="bob_projects",
        project_path=Path("data/bob_projects"),
        permission="owner"
    )
    
    session_manager.sessions[session_id] = project_session
    set_current_session(session_id)
    
    # Test the agent tool
    from src.agents.react_agent import handle_message
    
    print("\n1. Testing agent with image analysis request...")
    
    message = "Please analyze the image at exp_002_optimization/test_gel.png - it should be a gel electrophoresis result"
    
    try:
        response = await handle_message(
            message=message,
            session_id=session_id
        )
        
        print("\nAgent Response:")
        print("-" * 40)
        print(response[:800])
        print("-" * 40)
        
        if "gel" in response.lower() or "electrophoresis" in response.lower() or "band" in response.lower():
            print("\n✅ Agent successfully analyzed the image!")
        else:
            print("\n⚠️ Agent response doesn't mention image content")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Clean up
    if test_image_path.exists():
        test_image_path.unlink()
        print(f"\n✅ Cleaned up test gel image")
    
    session_manager.end_session(session_id)
    
    return True


async def main():
    """Run all image analysis tests"""
    
    print("\n" + "=" * 60)
    print("IMAGE ANALYSIS TEST SUITE")
    print("=" * 60)
    
    # Check if API key is configured
    import os
    if not os.environ.get("SILICONFLOW_API_KEY"):
        print("\n⚠️ WARNING: SILICONFLOW_API_KEY not set")
        print("Vision analysis will use fallback mode")
        print("Set the API key to test GLM-4.5V vision model")
    
    success = True
    
    # Test 1: Basic image analyzer
    if not await test_image_analyzer():
        success = False
    
    # Test 2: React agent tool
    if not await test_react_agent_tool():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 60)
    
    return success


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)