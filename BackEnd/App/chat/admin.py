from django.contrib import admin
from .models import Conversation, Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'last_message_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'last_message_at']
    ordering = ['-last_message_at']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'sender', 'message_type', 'created_at', 'is_read']
    list_filter = ['message_type', 'is_read', 'created_at']
    search_fields = ['content', 'conversation__user__email']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
