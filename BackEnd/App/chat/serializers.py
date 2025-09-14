from rest_framework import serializers
from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for individual messages"""
    sender_name = serializers.CharField(
        source='sender.get_full_name', read_only=True)
    sender_email = serializers.CharField(source='sender.email', read_only=True)
    sender_role = serializers.CharField(source='sender.role', read_only=True)
    is_from_admin = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            'id', 'conversation', 'sender', 'sender_name', 'sender_email',
            'sender_role', 'content', 'message_type', 'attachment',
            'is_read', 'created_at', 'is_from_admin'
        ]
        read_only_fields = ['id', 'created_at', 'sender', 'conversation']

    def get_is_from_admin(self, obj):
        """Check if the message is from an admin"""
        return obj.sender.role == 'admin'

    def create(self, validated_data):
        """Override create to set the sender automatically"""
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for conversations"""
    user_name = serializers.CharField(
        source='user.get_full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    unread_count = serializers.IntegerField(read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'id', 'user', 'user_name', 'user_email', 'created_at',
            'last_message_at', 'is_active', 'unread_count', 'last_message'
        ]
        read_only_fields = ['id', 'created_at', 'last_message_at']

    def get_last_message(self, obj):
        """Get the last message in the conversation"""
        last_msg = obj.messages.last()
        if last_msg:
            return MessageSerializer(last_msg).data
        return None


class ConversationListSerializer(serializers.ModelSerializer):
    """Simplified serializer for conversation lists"""
    user_name = serializers.CharField(
        source='user.get_full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    unread_count = serializers.SerializerMethodField()
    last_message_preview = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'id', 'user', 'user_name', 'user_email', 'created_at',
            'last_message_at', 'is_active', 'unread_count', 'last_message_preview'
        ]

    def get_unread_count(self, obj):
        """Get unread count based on the requesting user's role"""
        request = self.context.get('request')
        if request and request.user.role == 'admin':
            return obj.admin_unread_count
        else:
            return obj.unread_count

    def get_last_message_preview(self, obj):
        """Get a preview of the last message"""
        last_msg = obj.messages.last()
        if last_msg:
            return {
                'content': last_msg.content[:100] + '...' if len(last_msg.content) > 100 else last_msg.content,
                'sender_role': last_msg.sender.role,
                'created_at': last_msg.created_at
            }
        return None


class MessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new messages"""

    class Meta:
        model = Message
        fields = ['content', 'message_type', 'attachment']

    def validate(self, data):
        """Validate message data"""
        if not data.get('content') and not data.get('attachment'):
            raise serializers.ValidationError(
                "Either content or attachment must be provided")
        return data


class MarkMessagesReadSerializer(serializers.Serializer):
    """Serializer for marking messages as read"""
    message_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
        help_text="List of message IDs to mark as read"
    )
