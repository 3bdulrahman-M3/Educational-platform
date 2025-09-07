import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Notification


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.user = None
        self.room_name = None
        print("🔌 WebSocket connected (waiting for authentication)")

    async def disconnect(self, close_code):
        if self.room_name:
            await self.channel_layer.group_discard(self.room_name, self.channel_name)
            print(f"❌ WebSocket disconnected ({self.user.email if self.user else 'Unauthenticated'})")

    async def receive(self, text_data):
        """Handle incoming messages from WebSocket"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            # Handle authentication
            if message_type == 'auth' and not self.user:
                print(f"🔐 Received auth request")
                token = data.get('token')
                if token:
                    print(f"🔍 Token received, length: {len(token)}")
                    user = await self.get_user_from_token(token)
                    if user:
                        self.user = user
                        self.room_name = f"user_{self.user.id}"
                        await self.channel_layer.group_add(self.room_name, self.channel_name)
                        print(f"✅ Authenticated: {self.user.email}")
                        await self.send_json({
                            'type': 'auth_success',
                            'message': 'Successfully authenticated'
                        })
                    else:
                        print("❌ Authentication failed - invalid token")
                        await self.send_json({'type': 'auth_error', 'message': 'Invalid token'})
                        await self.close(code=1011)
                else:
                    print("❌ Authentication failed - no token provided")
                    await self.send_json({'type': 'auth_error', 'message': 'No token provided'})
                    await self.close(code=1011)

            # Handle marking notification as read
            elif message_type == 'mark_read' and self.user:
                notification_id = data.get('notification_id')
                if notification_id:
                    await self.mark_notification_read(notification_id)

        except json.JSONDecodeError:
            await self.send_json({'type': 'error', 'message': 'Invalid JSON'})

    async def notify(self, event):
        """Send notification to WebSocket"""
        if self.user:
            await self.send_json({
                'type': 'notification',
                'notification': event["data"]
            })

    async def send_json(self, content):
        await self.send(text_data=json.dumps(content))

    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        """Mark notification as read"""
        try:
            notification = Notification.objects.get(id=notification_id, receiver=self.user)
            notification.is_read = True
            notification.save()
        except Notification.DoesNotExist:
            pass

    @database_sync_to_async
    def get_user_from_token(self, token):
        """Get user from JWT token"""
        try:
            from rest_framework_simplejwt.tokens import AccessToken, TokenError
            from authentication.models import User
            import jwt
            from django.conf import settings
            
            print(f"🔍 Attempting to validate token: {token[:50]}...")
            
            # Try using SimpleJWT first
            try:
                access_token = AccessToken(token)
                user_id = access_token['user_id']
                print(f"🔍 Token valid via SimpleJWT, user_id: {user_id}")
            except TokenError as e:
                print(f"⚠️ SimpleJWT failed: {str(e)}, trying manual decode...")
                # Try manual JWT decode as fallback
                payload = jwt.decode(
                    token, 
                    settings.SECRET_KEY, 
                    algorithms=['HS256']
                )
                user_id = payload['user_id']
                print(f"🔍 Token valid via manual decode, user_id: {user_id}")
            
            user = User.objects.get(id=user_id)
            print(f"✅ User found: {user.email}")
            return user
            
        except jwt.ExpiredSignatureError:
            print("❌ Token expired")
            return None
        except jwt.InvalidTokenError as e:
            print(f"❌ Invalid token: {str(e)}")
            return None
        except User.DoesNotExist:
            print(f"❌ User with id {user_id} not found")
            return None
        except Exception as e:
            print(f"❌ Token validation failed: {str(e)}")
            return None
