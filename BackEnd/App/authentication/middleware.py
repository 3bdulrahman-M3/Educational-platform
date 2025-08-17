import json
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

User = get_user_model()


class JWTAuthMiddleware(BaseMiddleware):
    """
    JWT Authentication middleware for WebSocket connections
    """

    async def __call__(self, scope, receive, send):
        # Extract token from query parameters
        query_string = scope.get('query_string', b'').decode()
        token = None

        # Parse query string to get token
        if query_string:
            params = dict(param.split('=')
                          for param in query_string.split('&') if '=' in param)
            token = params.get('token')

        # If no token in query params, try headers
        if not token:
            headers = dict(scope.get('headers', []))
            auth_header = headers.get(b'authorization', b'').decode()
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        # Validate token and get user
        if token:
            try:
                user = await self.get_user_from_token(token)
                if user:
                    scope['user'] = user
                else:
                    scope['user'] = None
            except (InvalidToken, TokenError, jwt.InvalidTokenError):
                scope['user'] = None
        else:
            scope['user'] = None

        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def get_user_from_token(self, token):
        """
        Get user from JWT token
        """
        try:
            # Validate token
            token_obj = AccessToken(token)
            user_id = token_obj['user_id']

            # Get user from database
            user = User.objects.get(id=user_id, is_active=True)
            return user
        except (InvalidToken, TokenError, jwt.InvalidTokenError, User.DoesNotExist):
            return None


class RateLimitMiddleware(BaseMiddleware):
    """
    Rate limiting middleware for WebSocket connections
    """

    def __init__(self, app, rate_limit=100):
        super().__init__(app)
        self.rate_limit = rate_limit
        self.message_counts = {}

    async def __call__(self, scope, receive, send):
        # Add rate limiting to scope
        scope['rate_limit'] = self.rate_limit
        scope['message_counts'] = self.message_counts

        return await super().__call__(scope, receive, send)
