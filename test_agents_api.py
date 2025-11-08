#!/usr/bin/env python3
"""
Test script to validate all agent API endpoints
"""

import requests
import json
import sys
from typing import Dict, Any

BASE_URL = "http://localhost:8441"

def test_endpoint(method: str, endpoint: str, data: Dict[Any, Any] = None) -> Dict[str, Any]:
    """Test an API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=5)
        else:
            return {"error": f"Unsupported method: {method}"}
        
        return {
            "status_code": response.status_code,
            "success": response.ok,
            "data": response.json() if response.ok else {"error": response.text}
        }
    except Exception as e:
        return {"error": str(e), "success": False}

def main():
    print("=" * 60)
    print("Agent API Endpoint Testing")
    print("=" * 60)
    
    results = []
    
    # Test 1: Root endpoint
    print("\n1. Testing GET /")
    result = test_endpoint("GET", "/")
    results.append(("GET /", result))
    print(f"   Status: {result.get('status_code', 'N/A')}")
    if result.get("success"):
        print(f"   Agents: {result.get('data', {}).get('agents', [])}")
    
    # Test 2: List agents
    print("\n2. Testing GET /agents")
    result = test_endpoint("GET", "/agents")
    results.append(("GET /agents", result))
    print(f"   Status: {result.get('status_code', 'N/A')}")
    if result.get("success"):
        agents = result.get('data', {}).get('agents', [])
        print(f"   Found {len(agents)} agents")
        for agent in agents:
            print(f"   - Agent {agent.get('id')}: {agent.get('type')}")
    
    # Test 3: System status
    print("\n3. Testing GET /system/status")
    result = test_endpoint("GET", "/system/status")
    results.append(("GET /system/status", result))
    print(f"   Status: {result.get('status_code', 'N/A')}")
    if result.get("success"):
        data = result.get('data', {})
        print(f"   System Status: {data.get('system_status', 'N/A')}")
        print(f"   Agents: {len(data.get('agents', {}))}")
    
    # Test 4: Individual agent status
    print("\n4. Testing GET /agents/{agent_id}/status")
    agent_ids = ["01", "02", "03", "04", "06"]
    for agent_id in agent_ids:
        result = test_endpoint("GET", f"/agents/{agent_id}/status")
        results.append((f"GET /agents/{agent_id}/status", result))
        if result.get("success"):
            data = result.get('data', {})
            print(f"   Agent {agent_id}: {data.get('status', 'N/A')} - {data.get('agent_type', 'N/A')}")
        else:
            print(f"   Agent {agent_id}: Not available")
    
    # Test 5: Agent health
    print("\n5. Testing GET /agents/{agent_id}/health")
    for agent_id in agent_ids:
        result = test_endpoint("GET", f"/agents/{agent_id}/health")
        results.append((f"GET /agents/{agent_id}/health", result))
        if result.get("success"):
            data = result.get('data', {})
            print(f"   Agent {agent_id}: {data.get('status', 'N/A')}")
    
    # Test 6: Task execution (test with infrastructure agent)
    print("\n6. Testing POST /agents/01/execute")
    task_data = {
        "operation": "health_check",
        "parameters": {"test": True},
        "priority": "normal",
        "timeout_seconds": 30
    }
    result = test_endpoint("POST", "/agents/01/execute", task_data)
    results.append(("POST /agents/01/execute", result))
    print(f"   Status: {result.get('status_code', 'N/A')}")
    if result.get("success"):
        data = result.get('data', {})
        print(f"   Task ID: {data.get('task_id', 'N/A')}")
        print(f"   Status: {data.get('status', 'N/A')}")
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    successful = sum(1 for _, r in results if r.get("success"))
    total = len(results)
    print(f"Successful: {successful}/{total}")
    
    failed = [name for name, r in results if not r.get("success")]
    if failed:
        print(f"\nFailed endpoints:")
        for name in failed:
            print(f"  - {name}")
    
    return successful == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
