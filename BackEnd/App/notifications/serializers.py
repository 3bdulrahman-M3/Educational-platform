from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    receiver_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 
            'sender', 
            'sender_name',
            'receiver', 
            'receiver_name',
            'notification_type', 
            'title',
            'message', 
            'data', 
            'is_read', 
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'sender', 'receiver']
    
    def get_sender_name(self, obj):
        return obj.sender.get_full_name() if obj.sender else "System"
    
    def get_receiver_name(self, obj):
        return obj.receiver.get_full_name()
