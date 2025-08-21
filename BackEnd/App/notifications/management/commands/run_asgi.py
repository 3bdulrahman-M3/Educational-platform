from django.core.management.base import BaseCommand
import uvicorn
import os
import sys


class Command(BaseCommand):
    help = 'Run the ASGI server with WebSocket support'

    def add_arguments(self, parser):
        parser.add_argument(
            '--host',
            type=str,
            default='0.0.0.0',
            help='Host to bind to (default: 0.0.0.0)'
        )
        parser.add_argument(
            '--port',
            type=int,
            default=8000,
            help='Port to bind to (default: 8000)'
        )

    def handle(self, *args, **options):
        host = options['host']
        port = options['port']

        self.stdout.write(
            self.style.SUCCESS(
                f'Starting ASGI server on {host}:{port} with WebSocket support...')
        )

        # Run uvicorn with the ASGI application
        uvicorn.run(
            "App.asgi:application",
            host=host,
            port=port,
            reload=True,
            log_level="info"
        )
