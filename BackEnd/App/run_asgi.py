#!/usr/bin/env python
"""
Simple script to run the ASGI server with proper Django settings
"""
from App.asgi import application
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'App.settings')

# Setup Django
django.setup()

# Import and run the ASGI application

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "run_asgi:application",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
