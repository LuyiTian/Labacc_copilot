#!/bin/bash

# Test script for React frontend and API integration

echo "🧪 Testing LabAcc Copilot Frontend Integration"
echo "=============================================="

# Test API health
echo -e "\n1. Testing API health endpoint..."
curl -s http://localhost:8001/health | jq . || echo "❌ API not responding"

# Test file listing
echo -e "\n2. Testing file listing endpoint..."
curl -s "http://localhost:8001/api/files/list?path=/" | jq '.files[:3]' || echo "❌ File listing failed"

# Test project root
echo -e "\n3. Testing project root (should be data/alice_projects)..."
curl -s "http://localhost:8001/api/files/list?path=/alice_projects" | jq '.current_path' || echo "Note: alice_projects folder may not exist yet"

# Check React app
echo -e "\n4. Checking React app..."
if curl -s http://localhost:5173/ | grep -q "root"; then
    echo "✅ React app is running on http://localhost:5173"
else
    echo "❌ React app not responding"
fi

echo -e "\n=============================================="
echo "📊 Summary:"
echo "- API endpoint: http://localhost:8001"
echo "- React frontend: http://localhost:5173"
echo "- Project root: $LABACC_PROJECT_ROOT"
echo ""
echo "To test the full app:"
echo "1. Open http://localhost:5173 in your browser"
echo "2. You should see the file manager interface"
echo "3. Try browsing files, creating folders, and uploading files"