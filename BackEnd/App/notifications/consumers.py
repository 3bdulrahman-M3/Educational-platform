import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Notification


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            self.room_name = f"user_{self.user.id}"
            await self.channel_layer.group_add(self.room_name, self.channel_name)
            await self.accept()
            print(f"User {self.user.email} connected to notifications")
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_name'):
            await self.channel_layer.group_discard(self.room_name, self.channel_name)
            print(
                f"User {self.user.email if self.user.is_authenticated else 'Anonymous'} disconnected")

    async def notify(self, event):
        """Send notification to WebSocket"""
        await self.send(text_data=json.dumps(event["data"]))

    async def receive(self, text_data):
        """Handle incoming messages from WebSocket"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'message')

            if message_type == 'mark_read':
                notification_id = data.get('notification_id')
                if notification_id:
                    await self.mark_notification_read(notification_id)
        except json.JSONDecodeError:
            pass

    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        """Mark notification as read"""
        try:
            notification = Notification.objects.get(
                id=notification_id,
                recipient=self.user
            )
            notification.is_read = True
            notification.save()
        except Notification.DoesNotExist:
            pass
