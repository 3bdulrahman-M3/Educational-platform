from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth import get_user_model

from .models import Conversation, Message
from .serializers import (
    MessageSerializer, ConversationSerializer, ConversationListSerializer,
    MessageCreateSerializer, MarkMessagesReadSerializer
)

User = get_user_model()


class MessagePagination(PageNumberPagination):
    """Custom pagination for messages"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ConversationPagination(PageNumberPagination):
    """Custom pagination for conversations"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def conversation_view(request):
    """
    GET: Get or create user's conversation with admin
    POST: Create a new conversation (for users)
    """
    user = request.user
    
    if request.method == 'GET':
        # Get or create conversation for the user
        conversation, created = Conversation.objects.get_or_create(
            user=user,
            defaults={'is_active': True}
        )
        serializer = ConversationSerializer(conversation, context={'request': request})
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Only allow users (not admins) to create conversations
        if user.role == 'admin':
            return Response(
                {'error': 'Admins cannot create conversations'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if conversation already exists
        if hasattr(user, 'conversation'):
            return Response(
                {'error': 'Conversation already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        conversation = Conversation.objects.create(user=user, is_active=True)
        serializer = ConversationSerializer(conversation, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def conversations_list(request):
    """
    Get list of all conversations (admin only)
    """
    if request.user.role != 'admin':
        return Response(
            {'error': 'Only admins can view all conversations'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    conversations = Conversation.objects.filter(is_active=True).order_by('-last_message_at')
    
    # Search functionality
    search = request.query_params.get('search', None)
    if search:
        conversations = conversations.filter(
            Q(user__email__icontains=search) |
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search)
        )
    
    # Filter by unread messages
    unread_only = request.query_params.get('unread_only', None)
    if unread_only == 'true':
        conversations = conversations.filter(
            messages__sender__role='student',
            messages__is_read=False
        ).distinct()
    
    paginator = ConversationPagination()
    page = paginator.paginate_queryset(conversations, request)
    
    if page is not None:
        serializer = ConversationListSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)
    
    serializer = ConversationListSerializer(conversations, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def conversation_detail(request, conversation_id):
    """
    Get specific conversation details
    """
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # Users can only see their own conversation, admins can see all
    if request.user.role != 'admin' and conversation.user != request.user:
        return Response(
            {'error': 'You can only view your own conversation'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = ConversationSerializer(conversation, context={'request': request})
    return Response(serializer.data)


class MessageListCreateView(generics.ListCreateAPIView):
    """
    List messages for a conversation and create new messages
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = MessagePagination
    
    def get_queryset(self):
        conversation_id = self.kwargs.get('conversation_id')
        conversation = get_object_or_404(Conversation, id=conversation_id)
        
        # Users can only see their own conversation, admins can see all
        if self.request.user.role != 'admin' and conversation.user != self.request.user:
            return Message.objects.none()
        
        return Message.objects.filter(conversation=conversation).order_by('created_at')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MessageCreateSerializer
        return MessageSerializer
    
    def perform_create(self, serializer):
        conversation_id = self.kwargs.get('conversation_id')
        conversation = get_object_or_404(Conversation, id=conversation_id)
        
        # Users can only send messages to their own conversation, admins can reply to any
        if self.request.user.role != 'admin' and conversation.user != self.request.user:
            raise PermissionError("You can only send messages to your own conversation")
        
        serializer.save(conversation=conversation, sender=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_messages_read(request):
    """
    Mark specific messages as read
    """
    serializer = MarkMessagesReadSerializer(data=request.data)
    if serializer.is_valid():
        message_ids = serializer.validated_data['message_ids']
        user = request.user
        
        # Get messages that belong to user's conversations
        if user.role == 'admin':
            # Admin can mark any messages as read
            messages = Message.objects.filter(id__in=message_ids)
        else:
            # Users can only mark messages from their own conversation as read
            messages = Message.objects.filter(
                id__in=message_ids,
                conversation__user=user
            )
        
        # Mark messages as read
        updated_count = messages.update(is_read=True)
        
        return Response({
            'message': f'{updated_count} messages marked as read',
            'updated_count': updated_count
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_conversation_read(request, conversation_id):
    """
    Mark all messages in a conversation as read
    """
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # Users can only mark their own conversation, admins can mark any
    if request.user.role != 'admin' and conversation.user != request.user:
        return Response(
            {'error': 'You can only mark your own conversation as read'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Mark appropriate messages as read based on user role
    if request.user.role == 'admin':
        # Admin marks user messages as read
        updated_count = conversation.messages.filter(
            sender=conversation.user,
            is_read=False
        ).update(is_read=True)
    else:
        # User marks admin messages as read
        updated_count = conversation.messages.filter(
            sender__role='admin',
            is_read=False
        ).update(is_read=True)
    
    return Response({
        'message': f'{updated_count} messages marked as read',
        'updated_count': updated_count
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def unread_count(request):
    """
    Get unread message count for current user
    """
    user = request.user
    
    if user.role == 'admin':
        # Admin gets count of unread messages from all users
        count = Message.objects.filter(
            sender__role__in=['student', 'instructor'],
            is_read=False
        ).count()
    else:
        # User gets count of unread messages from admin
        if hasattr(user, 'conversation'):
            count = user.conversation.unread_count
        else:
            count = 0
    
    return Response({'unread_count': count})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def conversation_unread_count(request, conversation_id):
    """
    Get unread message count for a specific conversation
    """
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # Users can only check their own conversation, admins can check any
    if request.user.role != 'admin' and conversation.user != request.user:
        return Response(
            {'error': 'You can only check your own conversation'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if request.user.role == 'admin':
        count = conversation.admin_unread_count
    else:
        count = conversation.unread_count
    
    return Response({'unread_count': count})

