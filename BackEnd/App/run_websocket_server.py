#!/usr/bin/env python
"""
Simple script to run the ASGI server with WebSocket support using daphne
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
    import asyncio
    from daphne.server import Server
    from daphne.endpoints import build_endpoint_description_strings
    
    # Import the ASGI application after Django is set up
    from App.asgi import application
    
    print("🚀 Starting ASGI server with WebSocket support...")
    print("📍 Server will be available at: http://localhost:8000")
    print("🔌 WebSocket endpoint: ws://localhost:8000/ws/notifications/")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 60)
    
    try:
        # Create the server with proper endpoint configuration
        server = Server(
            application=application,
            endpoints=[
                ("0.0.0.0", 8000, "http"),
                ("0.0.0.0", 8000, "websocket"),
            ],
            signal_handlers=True,
            action_logger=None,
            http_timeout=120,
            websocket_timeout=120,
            websocket_connect_timeout=20,
            verbosity=1,
        )
        
        # Run the server
        server.run()
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        import traceback
        traceback.print_exc()
