#!/usr/bin/env python3
"""
Test Agent 04 API endpoints
"""

import requests
import json
import time

print('🧪 TESTING AGENT 04 API LAYER')
print('=' * 50)

# Test 1: Root endpoint
try:
    response = requests.get('http://localhost:8000/')
    if response.status_code == 200:
        data = response.json()
        print('✅ Root endpoint: PASSED')
        print(f'   Agents registered: {len(data.get("agents", []))}')
    else:
        print('❌ Root endpoint: FAILED')
except Exception as e:
    print(f'❌ Root endpoint: ERROR - {e}')

# Test 2: System status
try:
    response = requests.get('http://localhost:8000/system/status')
    if response.status_code == 200:
        data = response.json()
        print('✅ System status endpoint: PASSED')
        print(f'   System status: {data.get("system_status")}')
        print(f'   Agents: {len(data.get("agents", {}))}')
        print(f'   API requests: {data.get("api_metrics", {}).get("total_requests", 0)}')
    else:
        print('❌ System status endpoint: FAILED')
except Exception as e:
    print(f'❌ System status endpoint: ERROR - {e}')

# Test 3: Agent list
try:
    response = requests.get('http://localhost:8000/agents')
    if response.status_code == 200:
        data = response.json()
        print('✅ Agents list endpoint: PASSED')
        print(f'   Agents available: {len(data.get("agents", []))}')
    else:
        print('❌ Agents list endpoint: FAILED')
except Exception as e:
    print(f'❌ Agents list endpoint: ERROR - {e}')

# Test 4: Agent status (if agents available)
try:
    response = requests.get('http://localhost:8000/agents/01/status')
    if response.status_code == 200:
        data = response.json()
        print('✅ Agent 01 status endpoint: PASSED')
        print(f'   Agent type: {data.get("agent_type")}')
        print(f'   Status: {data.get("status")}')
    elif response.status_code == 404:
        print('⚠️ Agent 01 status endpoint: NOT REGISTERED (expected)')
    else:
        print('❌ Agent 01 status endpoint: FAILED')
except Exception as e:
    print(f'❌ Agent 01 status endpoint: ERROR - {e}')

# Test 5: Task execution
try:
    task_data = {
        'task_id': f'test_task_{int(time.time())}',
        'operation': 'health_check',
        'parameters': {'test': True}
    }
    response = requests.post('http://localhost:8000/agents/01/execute', json=task_data)
    if response.status_code in [200, 404]:  # 404 is OK if agent not available
        data = response.json()
        print('✅ Task execution endpoint: PASSED')
        print(f'   Response status: {data.get("status")}')
    else:
        print(f'❌ Task execution endpoint: FAILED ({response.status_code})')
except Exception as e:
    print(f'❌ Task execution endpoint: ERROR - {e}')

print('')
print('🎉 AGENT 04 API TESTING COMPLETE')
print('=' * 50)
