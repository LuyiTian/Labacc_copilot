#!/usr/bin/env python3
"""
Admin functionality tests for LabAcc Copilot multi-user system.
Tests admin-specific features like user management and project oversight.
"""

import httpx
import asyncio
import json
from pathlib import Path

API_BASE = "http://localhost:8002"

async def get_admin_token():
    """Helper to get admin authentication token"""
    async with httpx.AsyncClient() as client:
        login_data = {"username": "admin", "password": "admin123"}
        response = await client.post(f"{API_BASE}/api/auth/login", json=login_data)
        if response.status_code == 200:
            return response.json()["token"]
        return None

async def test_admin_login():
    """Test admin user can login"""
    token = await get_admin_token()
    if token:
        print("✅ Admin login successful")
        return True
    else:
        print("❌ Admin login failed")
        return False

async def test_user_creation():
    """Test admin can create new users"""
    token = await get_admin_token()
    if not token:
        print("❌ Cannot test user creation without admin token")
        return False
    
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create a new user
        new_user_data = {
            "username": "test_user_001",
            "password": "test_password_001",
            "role": "user"
        }
        
        response = await client.post(
            f"{API_BASE}/api/auth/create-user",
            json=new_user_data,
            headers=headers
        )
        
        if response.status_code == 200:
            print(f"✅ Created new user: {new_user_data['username']}")
            
            # Try to login as the new user
            login_response = await client.post(
                f"{API_BASE}/api/auth/login",
                json={"username": new_user_data["username"], "password": new_user_data["password"]}
            )
            
            if login_response.status_code == 200:
                print("✅ New user can login successfully")
                return True
            else:
                print("❌ New user cannot login")
                return False
        else:
            print(f"❌ Failed to create user: {response.status_code}")
            if response.text:
                print(f"   Error: {response.text}")
            return False

async def test_user_listing():
    """Test admin can list all users"""
    token = await get_admin_token()
    if not token:
        print("❌ Cannot test user listing without admin token")
        return False
    
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}"}
        
        response = await client.get(f"{API_BASE}/api/auth/users", headers=headers)
        
        if response.status_code == 200:
            users = response.json()["users"]
            print(f"✅ Listed {len(users)} users")
            
            # Check if default users exist
            usernames = [u["username"] for u in users]
            expected_users = ["admin", "alice", "bob"]
            
            for expected in expected_users:
                if expected in usernames:
                    print(f"   ✅ Found user: {expected}")
                else:
                    print(f"   ❌ Missing user: {expected}")
            
            return all(u in usernames for u in expected_users)
        else:
            print(f"❌ Failed to list users: {response.status_code}")
            return False

async def test_project_access_control():
    """Test admin can access any project"""
    token = await get_admin_token()
    if not token:
        print("❌ Cannot test project access without admin token")
        return False
    
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}"}
        
        # List all projects (admin should see all)
        response = await client.get(f"{API_BASE}/api/projects/list", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            projects = data["projects"]
            session_id = data["current_session"]
            
            print(f"✅ Admin can see {len(projects)} projects")
            
            # Admin should be able to access any project
            if projects:
                # Try to select a project owned by another user
                alice_project = next((p for p in projects if "alice" in p["project_id"]), None)
                
                if alice_project:
                    headers["X-Session-ID"] = session_id
                    select_response = await client.post(
                        f"{API_BASE}/api/projects/select",
                        json={"project_id": alice_project["project_id"]},
                        headers=headers
                    )
                    
                    if select_response.status_code == 200:
                        print(f"✅ Admin can access alice's project: {alice_project['project_id']}")
                        return True
                    else:
                        print(f"❌ Admin cannot access alice's project")
                        return False
            
            return True
        else:
            print(f"❌ Failed to list projects: {response.status_code}")
            return False

async def test_non_admin_restrictions():
    """Test that non-admin users cannot perform admin actions"""
    # Login as alice (non-admin)
    async with httpx.AsyncClient() as client:
        login_data = {"username": "alice", "password": "alice123"}
        login_response = await client.post(f"{API_BASE}/api/auth/login", json=login_data)
        
        if login_response.status_code != 200:
            print("❌ Failed to login as alice")
            return False
        
        token = login_response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to create a user (should fail)
        new_user_data = {
            "username": "unauthorized_user",
            "password": "password123",
            "role": "user"
        }
        
        response = await client.post(
            f"{API_BASE}/api/auth/create-user",
            json=new_user_data,
            headers=headers
        )
        
        if response.status_code in [403, 401]:
            print("✅ Non-admin correctly denied user creation")
            
            # Try to list all users (should fail or return limited data)
            users_response = await client.get(f"{API_BASE}/api/auth/users", headers=headers)
            
            if users_response.status_code in [403, 401]:
                print("✅ Non-admin correctly denied user listing")
                return True
            else:
                print(f"⚠️ Non-admin got unexpected response for user listing: {users_response.status_code}")
                return False
        else:
            print(f"❌ Non-admin was allowed to create user: {response.status_code}")
            return False

async def test_project_sharing():
    """Test project sharing functionality"""
    # Login as alice
    async with httpx.AsyncClient() as client:
        alice_login = {"username": "alice", "password": "alice123"}
        alice_response = await client.post(f"{API_BASE}/api/auth/login", json=alice_login)
        
        if alice_response.status_code != 200:
            print("❌ Failed to login as alice")
            return False
        
        alice_token = alice_response.json()["token"]
        alice_headers = {"Authorization": f"Bearer {alice_token}"}
        
        # Get alice's projects
        projects_response = await client.get(f"{API_BASE}/api/projects/list", headers=alice_headers)
        if projects_response.status_code != 200:
            print("❌ Failed to get alice's projects")
            return False
        
        data = projects_response.json()
        alice_projects = [p for p in data["projects"] if p["owner"] == "alice"]
        
        if not alice_projects:
            # Create a project for alice first
            session_id = data["current_session"]
            alice_headers["X-Session-ID"] = session_id
            
            create_response = await client.post(
                f"{API_BASE}/api/projects/create-new",
                json={
                    "name": "alice_test_project",
                    "hypothesis": "Test project for validating sharing functionality",
                    "planned_experiments": ["sharing_test"],
                    "expected_outcomes": "Project can be shared with other users"
                },
                headers=alice_headers
            )
            
            if create_response.status_code == 200:
                project_id = create_response.json()["project_id"]
                print(f"✅ Created project for alice: {project_id}")
            else:
                print("❌ Failed to create project for alice")
                return False
        else:
            project_id = alice_projects[0]["project_id"]
        
        # Share project with bob
        share_data = {
            "project_id": project_id,
            "share_with": "bob",
            "permission": "shared"
        }
        
        share_response = await client.post(
            f"{API_BASE}/api/projects/share",
            json=share_data,
            headers=alice_headers
        )
        
        if share_response.status_code == 200:
            print(f"✅ Alice shared project with bob")
            
            # Login as bob and check if he can see the shared project
            bob_login = {"username": "bob", "password": "bob123"}
            bob_response = await client.post(f"{API_BASE}/api/auth/login", json=bob_login)
            
            if bob_response.status_code == 200:
                bob_token = bob_response.json()["token"]
                bob_headers = {"Authorization": f"Bearer {bob_token}"}
                
                bob_projects_response = await client.get(f"{API_BASE}/api/projects/list", headers=bob_headers)
                
                if bob_projects_response.status_code == 200:
                    bob_projects = bob_projects_response.json()["projects"]
                    shared_project = next((p for p in bob_projects if p["project_id"] == project_id), None)
                    
                    if shared_project:
                        print(f"✅ Bob can see the shared project with permission: {shared_project['permission']}")
                        return True
                    else:
                        print("❌ Bob cannot see the shared project")
                        return False
        else:
            print(f"❌ Failed to share project: {share_response.status_code}")
            return False

async def main():
    """Run all admin functionality tests"""
    print("🧪 Running Admin Functionality Tests")
    print("=" * 50)
    
    tests = [
        ("Admin Login", test_admin_login),
        ("User Creation", test_user_creation),
        ("User Listing", test_user_listing),
        ("Project Access Control", test_project_access_control),
        ("Non-Admin Restrictions", test_non_admin_restrictions),
        ("Project Sharing", test_project_sharing),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n📋 Testing {test_name}...")
        try:
            result = await test_func()
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All admin tests passed!")
        return 0
    else:
        print(f"\n⚠️ {failed} admin test(s) failed")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)