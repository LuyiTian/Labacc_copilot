#!/usr/bin/env python
"""
Test LLM-based file summarization with context
"""

import asyncio
import os
from pathlib import Path

from src.memory.file_summarizer import FileContextSummarizer
from src.memory.memory_tools import create_experiment


async def test_llm_summarization():
    """Test that LLM generates context-aware summaries."""
    
    print("🧪 Testing LLM-based File Summarization")
    print("=" * 60)
    
    # Check API key
    if not os.environ.get("OPENROUTER_API_KEY") and not os.environ.get("SILICONFLOW_API_KEY"):
        print("⚠️ Warning: No API keys found. Set OPENROUTER_API_KEY or SILICONFLOW_API_KEY")
        return
    
    # Create test experiment
    experiment_id = "exp_test_llm_summary"
    
    print(f"\n1️⃣ Creating test experiment: {experiment_id}")
    await create_experiment.ainvoke({
        "experiment_name": "PCR Optimization Study",
        "motivation": "Testing LLM summarization with context",
        "key_question": "What annealing temperature gives best yield?"
    })
    
    # Create test file
    test_file_path = Path(f"data/alice_projects/{experiment_id}/pcr_results.csv")
    test_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    test_content = """Sample,Temperature,Yield,260/280,Notes
Control,55,45,1.7,Standard conditions
Exp1,58,72,1.85,Increased temperature
Exp2,60,85,1.92,Optimal results
Exp3,62,61,1.88,Slight decrease
Exp4,65,23,1.65,Too hot, degradation
"""
    
    with open(test_file_path, 'w') as f:
        f.write(test_content)
    
    print(f"\n2️⃣ Created test file: pcr_results.csv")
    print("Content preview:")
    print(test_content[:200])
    
    # Test summarization WITH context
    print(f"\n3️⃣ Testing LLM summarization WITH experiment context...")
    summarizer = FileContextSummarizer()
    
    summary_with_context = await summarizer.summarize_with_context(
        str(test_file_path),
        experiment_id
    )
    
    print(f"Context-aware summary:\n{summary_with_context}")
    
    # Test summarization WITHOUT context
    print(f"\n4️⃣ Testing LLM summarization WITHOUT context...")
    summary_without_context = await summarizer.summarize_with_context(
        str(test_file_path),
        None  # No experiment context
    )
    
    print(f"Summary without context:\n{summary_without_context}")
    
    # Test TODO for image
    print(f"\n5️⃣ Testing TODO for image file...")
    image_path = test_file_path.parent / "gel_image.png"
    image_path.touch()  # Create empty file
    
    image_summary = await summarizer.summarize_with_context(
        str(image_path),
        experiment_id
    )
    
    print(f"Image summary:\n{image_summary}")
    
    # Clean up
    import shutil
    if test_file_path.parent.exists():
        shutil.rmtree(test_file_path.parent)
        print(f"\n🧹 Cleaned up test experiment")
    
    print("\n" + "=" * 60)
    print("✅ Summary Comparison:")
    print("- WITH context: Should mention PCR optimization and temperature")
    print("- WITHOUT context: Should be more generic")
    print("- Image: Should show TODO message")
    
    print("\n📊 Key Features:")
    print("1. Reads up to 10,000 characters")
    print("2. Uses fast LLM (GPT-OSS 120B)")
    print("3. Includes experiment README context")
    print("4. TODOs for images, PDFs, Excel")
    print("5. Context-aware interpretation")


if __name__ == "__main__":
    asyncio.run(test_llm_summarization())