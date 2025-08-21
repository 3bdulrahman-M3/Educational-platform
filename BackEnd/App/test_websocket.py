#!/usr/bin/env python
"""
Simple test script to verify WebSocket connection
"""
import asyncio
import websockets
import json


async def test_websocket():
    uri = "ws://localhost:8000/ws/notifications/"

    try:
        print("🔌 Testing WebSocket connection...")
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connection established!")

            # Send a test message
            test_message = {
                "type": "auth",
                "token": "test_token"
            }

            await websocket.send(json.dumps(test_message))
            print("📤 Sent test message")

            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"📥 Received response: {response}")
            except asyncio.TimeoutError:
                print("⏰ No response received within 5 seconds")

    except ConnectionRefusedError:
        print("❌ WebSocket connection refused - server may not be running")
        print("💡 Make sure to run: python manage.py run_asgi")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
