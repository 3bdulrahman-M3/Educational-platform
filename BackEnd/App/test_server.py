#!/usr/bin/env python
"""
Simple test script to verify server is running with both HTTP and WebSocket support
"""
import requests
import websocket
import json
import time


def test_http():
    """Test HTTP endpoints"""
    try:
        response = requests.get('http://127.0.0.1:8000/api/courses/')
        print(f"✅ HTTP Server: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ HTTP Server: {e}")
        return False


def test_websocket():
    """Test WebSocket endpoint"""
    try:
        ws = websocket.create_connection(
            'ws://127.0.0.1:8000/ws/notifications/')
        print("✅ WebSocket: Connected")
        ws.close()
        return True
    except Exception as e:
        print(f"❌ WebSocket: {e}")
        return False


def main():
    print("🔍 Testing Server Status...")
    print("=" * 40)

    # Test HTTP
    http_ok = test_http()

    # Test WebSocket
    websocket_ok = test_websocket()

    print("=" * 40)
    if http_ok and websocket_ok:
        print("🎉 Server is running with full WebSocket support!")
        print("📍 HTTP: http://127.0.0.1:8000")
        print("🔌 WebSocket: ws://127.0.0.1:8000/ws/notifications/")
    else:
        print("⚠️  Server has issues:")
        if not http_ok:
            print("   - HTTP server not responding")
        if not websocket_ok:
            print("   - WebSocket not working")
        print("\n💡 Make sure to run: python manage.py runserver")


if __name__ == "__main__":
    main()
