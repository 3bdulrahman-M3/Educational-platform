#!/usr/bin/env python
"""
Simple script to start the ASGI server with WebSocket support
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'App.settings')

# Setup Django
django.setup()

if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting ASGI server with WebSocket support...")
    print("📍 Server will be available at: http://localhost:8000")
    print("🔌 WebSocket endpoint: ws://localhost:8000/ws/notifications/")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 60)

    try:
        uvicorn.run(
            "App.asgi:application",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        import traceback
        traceback.print_exc()
