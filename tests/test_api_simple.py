#!/usr/bin/env python3
"""
Simple API tests for LabAcc Copilot multi-user system.
Tests basic functionality without complex fixtures.
"""

import httpx
import asyncio
import json
from pathlib import Path

API_BASE = "http://localhost:8002"

async def test_health_check():
    """Test the health check endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        print("✅ Health check passed")

async def test_authentication_flow():
    """Test basic authentication flow"""
    async with httpx.AsyncClient() as client:
        # Test login with test credentials
        login_data = {
            "username": "test_user",
            "password": "test_password"
        }
        
        response = await client.post(f"{API_BASE}/api/auth/login", json=login_data)
        print(f"Login response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("token")
            print(f"✅ Login successful, got token: {token[:20]}...")
            
            # Test token verification
            headers = {"Authorization": f"Bearer {token}"}
            verify_response = await client.get(f"{API_BASE}/api/auth/verify", headers=headers)
            
            if verify_response.status_code == 200:
                print("✅ Token verification passed")
            else:
                print(f"❌ Token verification failed: {verify_response.status_code}")
        else:
            print(f"⚠️ Login failed (might be expected): {response.status_code}")
            # Try without auth for project endpoints that don't require it

async def test_project_management():
    """Test project management endpoints"""
    async with httpx.AsyncClient() as client:
        # Test listing projects (should work without auth in temp mode)
        response = await client.get(f"{API_BASE}/api/projects/list")
        print(f"List projects response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Got {len(data['projects'])} projects")
            session_id = data.get("current_session")
            print(f"Session ID: {session_id}")
            
            # Test creating a demo project
            headers = {"X-Session-ID": session_id} if session_id else {}
            demo_response = await client.post(f"{API_BASE}/api/projects/create-demo", headers=headers)
            
            if demo_response.status_code == 200:
                demo_data = demo_response.json()
                project_id = demo_data["project_id"]
                print(f"✅ Created demo project: {project_id}")
                
                # Test selecting the project
                select_data = {"project_id": project_id}
                select_response = await client.post(
                    f"{API_BASE}/api/projects/select",
                    json=select_data,
                    headers=headers
                )
                
                if select_response.status_code == 200:
                    print(f"✅ Selected project: {project_id}")
                else:
                    print(f"❌ Failed to select project: {select_response.status_code}")
            else:
                print(f"❌ Failed to create demo project: {demo_response.status_code}")
        else:
            print(f"❌ Failed to list projects: {response.status_code}")

async def test_file_operations():
    """Test file operations"""
    async with httpx.AsyncClient() as client:
        # First get a session and project
        list_response = await client.get(f"{API_BASE}/api/projects/list")
        if list_response.status_code != 200:
            print("❌ Cannot test files without session")
            return
            
        session_id = list_response.json()["current_session"]
        headers = {"X-Session-ID": session_id}
        
        # Check if alice_projects exists
        projects = list_response.json()["projects"]
        alice_project = next((p for p in projects if "alice" in p["project_id"]), None)
        
        if alice_project:
            project_id = alice_project["project_id"]
            print(f"   Using existing project: {project_id}")
        else:
            # Create demo project
            demo_response = await client.post(f"{API_BASE}/api/projects/create-demo", headers=headers)
            if demo_response.status_code != 200:
                print("❌ Cannot create demo project")
                return
                
            project_id = demo_response.json()["project_id"]
            print(f"   Created demo project: {project_id}")
        
        # Select project - THIS IS CRITICAL FOR FILE OPS TO WORK
        select_response = await client.post(
            f"{API_BASE}/api/projects/select",
            json={"project_id": project_id},
            headers=headers
        )
        
        if select_response.status_code != 200:
            print(f"❌ Cannot select project: {select_response.text}")
            return
        
        print(f"   Selected project: {project_id}")
        
        # Now test file operations with the selected project
        # List files in root
        files_response = await client.get(
            f"{API_BASE}/api/files/list",
            params={"path": "/"},
            headers=headers
        )
        
        if files_response.status_code == 200:
            files = files_response.json()["files"]
            print(f"✅ Listed {len(files)} files in root")
        else:
            print(f"❌ Failed to list files: {files_response.status_code}")
        
        # Create a folder
        folder_data = {"path": "/", "folder_name": "test_folder"}
        folder_response = await client.post(
            f"{API_BASE}/api/files/folder",
            json=folder_data,
            headers=headers
        )
        
        if folder_response.status_code == 200:
            print("✅ Created test folder")
        else:
            print(f"❌ Failed to create folder: {folder_response.status_code}")

async def test_chat_functionality():
    """Test chat/agent functionality"""
    async with httpx.AsyncClient(timeout=30.0) as client:  # Increase timeout for AI response
        # Setup session and project first
        list_response = await client.get(f"{API_BASE}/api/projects/list")
        if list_response.status_code != 200:
            print("❌ Cannot test chat without session")
            return
            
        session_id = list_response.json()["current_session"]
        headers = {"X-Session-ID": session_id}
        
        # First select a project (required for chat to work)
        projects = list_response.json()["projects"]
        if projects:
            project_id = projects[0]["project_id"]
            select_response = await client.post(
                f"{API_BASE}/api/projects/select",
                json={"project_id": project_id},
                headers=headers
            )
            if select_response.status_code != 200:
                print(f"❌ Failed to select project for chat: {select_response.status_code}")
                return
            print(f"   Selected project: {project_id}")
        else:
            print("❌ No projects available for chat testing")
            return
        
        # Send a simple chat message using the correct endpoint
        chat_data = {
            "message": "Hello, what can you help me with?",
            "session_id": session_id
        }
        
        chat_response = await client.post(
            f"{API_BASE}/api/chat/message",  # Correct endpoint
            json=chat_data,
            headers=headers
        )
        
        if chat_response.status_code == 200:
            response_text = chat_response.json()["response"]
            print(f"✅ Chat response received: {response_text[:100]}...")
        else:
            print(f"❌ Chat failed: {chat_response.status_code}")
            if chat_response.text:
                print(f"   Error: {chat_response.text}")

async def main():
    """Run all simple tests"""
    print("🧪 Running Simple API Tests")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health_check),
        ("Authentication", test_authentication_flow),
        ("Project Management", test_project_management),
        ("File Operations", test_file_operations),
        ("Chat Functionality", test_chat_functionality),
    ]
    
    for test_name, test_func in tests:
        print(f"\n📋 Testing {test_name}...")
        try:
            await test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Simple tests completed")

if __name__ == "__main__":
    asyncio.run(main())