#!/usr/bin/env python3
"""
Simple WebSocket connection test for the Dynamic Compression Algorithms backend.
"""

import asyncio
import websockets
import json
import time

async def test_websocket():
    try:
        uri = 'ws://localhost:8443/ws/agent-updates'
        print(f'Connecting to {uri}...')
        async with websockets.connect(uri) as websocket:
            print('✅ WebSocket connected successfully!')

            # Send a ping message
            ping_msg = {'type': 'ping', 'data': {'timestamp': time.time()}}
            await websocket.send(json.dumps(ping_msg))
            print(f'📤 Sent: {ping_msg}')

            # Try to receive a response (with timeout)
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f'📥 Received: {response}')
            except asyncio.TimeoutError:
                print('⚠️  No response received (this is normal for ping)')

            print('✅ WebSocket test completed successfully!')

    except Exception as e:
        print(f'❌ WebSocket test failed: {str(e)}')

if __name__ == '__main__':
    asyncio.run(test_websocket())
