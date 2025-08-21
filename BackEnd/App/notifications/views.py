from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from .serializers import NotificationSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(receiver=self.request.user)

    @action(detail=True, methods=['patch'])
    def mark_read(self, request, pk=None):
        """Mark a specific notification as read"""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'marked as read'})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        self.get_queryset().update(is_read=True)
        return Response({'status': 'all marked as read'})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications"""
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'unread_count': count})


# Utility function to send notifications
def send_notification(sender_id, receiver_id, notification_type, title, message, data=None):
    """
    Send a notification from sender to receiver

    Args:
        sender_id: ID of the user sending the notification (can be None for system notifications)
        receiver_id: ID of the user receiving the notification
        notification_type: Type of notification (from NOTIFICATION_TYPES)
        title: Notification title
        message: Notification message
        data: Additional data (optional)
    """
    from .models import Notification

    # Create notification in database
    notification = Notification.objects.create(
        sender_id=sender_id,
        receiver_id=receiver_id,
        notification_type=notification_type,
        title=title,
        message=message,
        data=data or {}
    )

    # Send via WebSocket
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
                "receiver_name": notification.receiver.get_full_name() if notification.receiver else "",
                "title": notification.title,
                "message": notification.message,
                "notification_type": notification.notification_type,
                "is_read": notification.is_read,
                "created_at": notification.created_at.isoformat(),
                "data": notification.data
            }
        }
    )

    return notification
