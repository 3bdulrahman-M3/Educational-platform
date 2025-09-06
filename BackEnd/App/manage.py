#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'App.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Check if this is a runserver command
    if len(sys.argv) > 1 and sys.argv[1] == 'runserver':
        # Use PORT from environment (Railway sets this), fallback to 8000
        port = os.environ.get('PORT', '8000')
        host = '0.0.0.0'

        print("🚀 Starting ASGI server (uvicorn) with WebSocket support...")
        print(f"📍 Server: http://{host}:{port}")
        print(f"🔌 WebSocket: ws://{host}:{port}/ws/notifications/")
        print("⏹️  Press Ctrl+C to stop the server")
        print("-" * 60)

        # Replace runserver with custom ASGI management command and pass host/port
        sys.argv = [sys.argv[0], 'run_asgi', '--host', host, '--port', port]
        execute_from_command_line(sys.argv)
    else:
        # For all other commands, run normally
        execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
