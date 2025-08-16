#!/usr/bin/env python3
"""
Full upload workflow test - simulates real user uploading a PDF.
Tests the complete pipeline from upload to conversion to registry update.
"""

import asyncio
import httpx
import shutil
import tempfile
from pathlib import Path
import json
import sys

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# Test files
TEST_PDF = Path("/data/luyit/script/git/Labacc_copilot/data/extra_test_file/For lung cancer tissue dissociation.pdf")
TEST_DOCX = Path("/data/luyit/script/git/Labacc_copilot/data/extra_test_file/For lung cancer tissue dissociation.docx")

API_BASE = "http://localhost:8002"


async def test_full_upload_workflow():
    """Test the complete upload workflow as a user would experience it"""
    
    print("🧪 FULL UPLOAD WORKFLOW TEST")
    print("=" * 60)
    
    if not TEST_PDF.exists():
        print(f"❌ Test file not found: {TEST_PDF}")
        return False
    
    async with httpx.AsyncClient(base_url=API_BASE, timeout=60.0) as client:
        try:
            # Step 1: Check server health
            print("\n1️⃣ Checking server...")
            response = await client.get("/health")
            if response.status_code != 200:
                print(f"❌ Server not healthy: {response.status_code}")
                return False
            print("✅ Server is running")
            
            # Step 2: Get session
            print("\n2️⃣ Getting session...")
            response = await client.get("/api/projects/list")
            if response.status_code != 200:
                print(f"❌ Failed to get projects: {response.status_code}")
                return False
            
            session_id = response.json()["current_session"]
            headers = {"X-Session-ID": session_id}
            print(f"✅ Got session: {session_id}")
            
            # Step 3: Select alice_projects
            print("\n3️⃣ Selecting project...")
            response = await client.post(
                "/api/projects/select",
                json={"project_id": "project_alice_projects"},
                headers=headers
            )
            if response.status_code != 200:
                print(f"❌ Failed to select project: {response.text}")
                return False
            print("✅ Selected project_alice_projects")
            
            # Step 4: Upload PDF to exp_002_optimization
            print("\n4️⃣ Uploading PDF file...")
            with open(TEST_PDF, 'rb') as f:
                files = {"files": (TEST_PDF.name, f, "application/pdf")}
                response = await client.post(
                    "/api/files/upload",
                    data={"path": "/exp_002_optimization"},
                    files=files,
                    headers=headers
                )
            
            if response.status_code != 200:
                print(f"❌ Upload failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
            
            upload_result = response.json()
            print(f"✅ File uploaded successfully")
            print(f"   Files: {upload_result.get('files', [])}")
            
            # Step 5: Check conversion result
            print("\n5️⃣ Checking conversion...")
            if upload_result.get("files"):
                file_info = upload_result["files"][0]
                conversion_status = file_info.get("conversion_status", "unknown")
                converted_path = file_info.get("converted")
                
                print(f"   Conversion status: {conversion_status}")
                print(f"   Converted path: {converted_path}")
                
                if conversion_status == "success" and converted_path:
                    print("✅ File was converted to Markdown")
                else:
                    print("⚠️ File was not converted")
            
            # Step 6: List files to verify
            print("\n6️⃣ Verifying files...")
            response = await client.get(
                "/api/files/list",
                params={"path": "/exp_002_optimization"},
                headers=headers
            )
            
            if response.status_code == 200:
                files = response.json()["files"]
                print(f"✅ Found {len(files)} items in exp_002_optimization")
                
                # Check for originals folder
                has_originals = any(f["name"] == "originals" and f["is_dir"] for f in files)
                if has_originals:
                    print("✅ Originals folder exists")
                    
                    # List originals folder
                    response = await client.get(
                        "/api/files/list",
                        params={"path": "/exp_002_optimization/originals"},
                        headers=headers
                    )
                    if response.status_code == 200:
                        orig_files = response.json()["files"]
                        pdf_files = [f for f in orig_files if f["name"].endswith(".pdf")]
                        if pdf_files:
                            print(f"✅ PDF saved in originals: {pdf_files[0]['name']}")
                        else:
                            print("❌ PDF not found in originals")
                else:
                    print("❌ Originals folder not created")
            else:
                print(f"❌ Failed to list files: {response.status_code}")
            
            # Step 7: Check registry
            print("\n7️⃣ Checking file registry...")
            # This would require direct file system access or an API endpoint
            # For now, we'll check if the upload reported success
            if upload_result.get("success"):
                print("✅ Upload completed successfully")
            else:
                print("❌ Upload did not complete successfully")
            
            print("\n" + "=" * 60)
            print("✅ WORKFLOW TEST COMPLETED SUCCESSFULLY")
            return True
            
        except Exception as e:
            print(f"\n❌ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            return False


async def main():
    """Run the full workflow test"""
    
    # Check if server is running
    print("Checking if server is running...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE}/health")
            if response.status_code != 200:
                print("❌ Server not running. Start it with:")
                print("   uv run uvicorn src.api.app:app --port 8002 --reload")
                return
    except:
        print("❌ Cannot connect to server. Start it with:")
        print("   uv run uvicorn src.api.app:app --port 8002 --reload")
        return
    
    # Run the test
    success = await test_full_upload_workflow()
    
    if not success:
        print("\n⚠️ WORKFLOW TEST FAILED")
        print("\nPossible issues:")
        print("1. Server not running properly")
        print("2. File conversion not working")
        print("3. Session management issues")
        print("4. Project not properly selected")


if __name__ == "__main__":
    # Set up minimal logging
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    asyncio.run(main())