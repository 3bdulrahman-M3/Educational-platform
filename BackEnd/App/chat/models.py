from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Conversation(models.Model):
    """
    Represents a conversation between a user and admin.
    Each user has exactly one conversation with admin.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='conversation',
        help_text="The user participating in this conversation"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_message_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, help_text="Whether the conversation is active")
    
    class Meta:
        ordering = ['-last_message_at']
        db_table = 'chat_conversations'
    
    def __str__(self):
        return f"Conversation with {self.user.email}"
    
    @property
    def unread_count(self):
        """Count of unread messages for the user (messages from admin)"""
        return self.messages.filter(
            sender__role='admin',
            is_read=False
        ).count()
    
    @property
    def admin_unread_count(self):
        """Count of unread messages for admin (messages from user)"""
        return self.messages.filter(
            sender=self.user,
            is_read=False
        ).count()


class Message(models.Model):
    """
    Represents a message in a conversation between user and admin.
    """
    MESSAGE_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('file', 'File'),
        ('system', 'System'),
    ]
    
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    content = models.TextField(help_text="Message content")
    message_type = models.CharField(
        max_length=10,
        choices=MESSAGE_TYPES,
        default='text'
    )
    attachment = models.FileField(
        upload_to='chat_attachments/',
        blank=True,
        null=True,
        help_text="Optional file attachment"
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        db_table = 'chat_messages'
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
            models.Index(fields=['sender', 'created_at']),
            models.Index(fields=['is_read']),
        ]
    
    def __str__(self):
        return f"{self.sender.email}: {self.content[:50]}..."
    
    def save(self, *args, **kwargs):
        # Update conversation's last_message_at when a new message is created
        super().save(*args, **kwargs)
        self.conversation.last_message_at = timezone.now()
        self.conversation.save(update_fields=['last_message_at'])


class MessageReadStatus(models.Model):
    """
    Track read status for messages (for future enhancements like group chats)
    """
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='read_statuses')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_read_statuses')
    read_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['message', 'user']
        db_table = 'chat_message_read_status'
