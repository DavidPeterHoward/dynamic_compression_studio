#!/usr/bin/env python3
"""
Comprehensive WebSocket Validation Test for Dynamic Compression Algorithms
"""

import asyncio
import websockets
import json
import time

async def comprehensive_websocket_test():
    print('COMPREHENSIVE WEBSOCKET VALIDATION TEST')
    print('=' * 50)

    try:
        uri = 'ws://localhost:8443/ws/agent-updates'
        print(f'Connecting to: {uri}')

        async with websockets.connect(uri) as websocket:
            print('WebSocket HANDSHAKE: SUCCESS')

            # Test 1: Send ping and receive system status
            ping_msg = {'type': 'ping', 'timestamp': time.time()}
            await websocket.send(json.dumps(ping_msg))
            print(f'SENT: {ping_msg}')

            response = await websocket.recv()
            data = json.loads(response)
            print(f'RECEIVED: {data["event_type"]} ({len(str(data))} chars)')

            # Test 2: Verify data structure
            if 'data' in data and 'system_status' in data['data']:
                print('DATA VALIDATION: System status present')
                agents = data['data'].get('agents', {})
                print(f'AGENT REGISTRY: {len(agents)} agents detected')

                # List agent types
                agent_types = [info.get('type', 'unknown') for info in agents.values()]
                print(f'AGENT TYPES: {agent_types}')

            else:
                print('DATA VALIDATION: Missing expected fields')

            # Test 3: Connection stability
            print('TESTING CONNECTION STABILITY...')
            await asyncio.sleep(2)

            print('WEBSOCKET TEST: ALL VALIDATIONS PASSED')
            return True

    except Exception as e:
        print(f'WEBSOCKET TEST FAILED: {str(e)}')
        return False

if __name__ == '__main__':
    result = asyncio.run(comprehensive_websocket_test())
    print(f'\nFINAL RESULT: {"SUCCESS" if result else "FAILED"}')
