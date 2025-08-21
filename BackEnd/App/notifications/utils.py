from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification


def send_notification(sender_id, receiver_id, notification_type, title, message, data=None):
    """Send and broadcast a notification"""

    notification = Notification.objects.create(
        sender_id=sender_id,
        receiver_id=receiver_id,
        notification_type=notification_type,
        title=title,
        message=message,
        data=data or {}
    )

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{receiver_id}",
        {
            "type": "notify",
            "data": {
                "id": notification.id,
                "sender": notification.sender_id,
                "sender_name": notification.sender.get_full_name() if notification.sender else "System",
                "receiver": notification.receiver_id,
                "receiver_name": notification.receiver.get_full_name(),
                "title": notification.title,
                "message": notification.message,
                "notification_type": notification.notification_type,
                "is_read": notification.is_read,
                "created_at": notification.created_at.isoformat(),
                "data": notification.data,
            },
        },
    )
    return notification
