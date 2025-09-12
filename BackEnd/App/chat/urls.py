from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    # Conversation endpoints
    path('conversation/', views.conversation_view, name='conversation'),
    path('conversations/', views.conversations_list, name='conversations-list'),
    path('conversations/<int:conversation_id>/', views.conversation_detail, name='conversation-detail'),
    
    # Message endpoints
    path('conversations/<int:conversation_id>/messages/', 
         views.MessageListCreateView.as_view(), name='message-list-create'),
    
    # Read status endpoints
    path('messages/mark-read/', views.mark_messages_read, name='mark-messages-read'),
    path('conversations/<int:conversation_id>/mark-read/', 
         views.mark_conversation_read, name='mark-conversation-read'),
    
    # Unread count endpoints
    path('unread-count/', views.unread_count, name='unread-count'),
    path('conversations/<int:conversation_id>/unread-count/', 
         views.conversation_unread_count, name='conversation-unread-count'),
]
