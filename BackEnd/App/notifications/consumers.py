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
            print("❌ WebSocket disconnected")

    async def receive(self, text_data):
        """Handle incoming messages from WebSocket"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'auth' and not self.user:
                token = data.get('token')
                if token:
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
                        await self.send_json({'type': 'auth_error', 'message': 'Invalid token'})
                        await self.close()
                else:
                    await self.send_json({'type': 'auth_error', 'message': 'No token provided'})
                    await self.close()

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
    def get_user_from_token(self, token):
        """Get user from JWT token"""
        try:
            from rest_framework_simplejwt.tokens import AccessToken
            from authentication.models import User

            access_token = AccessToken(token)
            return User.objects.get(id=access_token['user_id'])
        except Exception:
            return None

    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        """Mark notification as read"""
        try:
            notification = Notification.objects.get(
                id=notification_id, receiver=self.user
            )
            notification.is_read = True
            notification.save()
        except Notification.DoesNotExist:
            pass
