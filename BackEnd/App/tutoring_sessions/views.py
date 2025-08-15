from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db import models
from django.utils import timezone
from .models import Session, Participant
from .serializers import (
    SessionSerializer,
    SessionCreateSerializer,
    SessionUpdateSerializer,
    SessionListSerializer,
    ParticipantSerializer
)


class SessionPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = SessionPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return SessionCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return SessionUpdateSerializer
        elif self.action == 'list':
            return SessionListSerializer
        return SessionSerializer

    def get_queryset(self):
        """Filter queryset based on action and user permissions"""
        queryset = Session.objects.all()

        # Filter by status if provided
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Filter by date range if provided
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)

        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)

        # Filter by creator if provided
        creator_id = self.request.query_params.get('creator', None)
        if creator_id:
            queryset = queryset.filter(creator_id=creator_id)

        return queryset.select_related('creator').prefetch_related('participants__user')

    def perform_create(self, serializer):
        """Create session with creator validation"""
        serializer.save(creator=self.request.user)

    def perform_update(self, serializer):
        """Update session with creator validation"""
        session = self.get_object()
        if session.creator != self.request.user:
            raise PermissionError("Only the creator can update this session")

        # Check if session can be updated
        if session.status in ['completed', 'cancelled']:
            raise ValueError("Cannot update completed or cancelled sessions")

        serializer.save()

    def perform_destroy(self, instance):
        """Delete session with creator validation"""
        if instance.creator != self.request.user:
            raise PermissionError("Only the creator can delete this session")

        if instance.status in ['ongoing', 'completed']:
            raise ValueError("Cannot delete ongoing or completed sessions")

        instance.delete()

    @action(detail=False, methods=['get'])
    def my_sessions(self, request):
        """Get sessions where user is creator or participant"""
        user = request.user

        # Get sessions where user is creator
        created_sessions = Session.objects.filter(creator=user)

        # Get sessions where user is participant
        participated_sessions = Session.objects.filter(participants__user=user)

        # Combine and remove duplicates
        all_sessions = (created_sessions | participated_sessions).distinct()

        # Apply pagination
        page = self.paginate_queryset(all_sessions)
        if page is not None:
            serializer = SessionListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = SessionListSerializer(all_sessions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def created_sessions(self, request):
        """Get sessions created by the current user"""
        sessions = Session.objects.filter(creator=request.user)

        page = self.paginate_queryset(sessions)
        if page is not None:
            serializer = SessionListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = SessionListSerializer(sessions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def joined_sessions(self, request):
        """Get sessions where user is a participant"""
        sessions = Session.objects.filter(participants__user=request.user)

        page = self.paginate_queryset(sessions)
        if page is not None:
            serializer = SessionListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = SessionListSerializer(sessions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Join a session"""
        session = self.get_object()
        user = request.user

        # Check if already joined
        if Participant.objects.filter(session=session, user=user).exists():
            return Response(
                {'error': 'Already joined this session'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if session is full
        if session.is_full:
            return Response(
                {'error': 'Session is full'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if session can be joined
        if not session.can_join:
            return Response(
                {'error': 'Cannot join this session. It may be cancelled, completed, or already started'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create participant
        Participant.objects.create(
            session=session,
            user=user,
            role='student'
        )

        serializer = SessionSerializer(session)
        return Response({
            'message': 'Successfully joined the session',
            'session': serializer.data
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """Leave a session"""
        session = self.get_object()
        user = request.user

        try:
            participant = Participant.objects.get(session=session, user=user)

            # Check if session is ongoing or completed
            if session.status in ['ongoing', 'completed']:
                return Response(
                    {'error': 'Cannot leave an ongoing or completed session'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            participant.delete()

            serializer = SessionSerializer(session)
            return Response({
                'message': 'Successfully left the session',
                'session': serializer.data
            })
        except Participant.DoesNotExist:
            return Response(
                {'error': 'Not joined to this session'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a session (creator only)"""
        session = self.get_object()
        user = request.user

        # Check if user is creator
        if session.creator != user:
            return Response(
                {'error': 'Only the creator can cancel a session'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if session can be cancelled
        if not session.can_be_cancelled_by(user):
            return Response(
                {'error': 'Cannot cancel a completed or cancelled session'},
                status=status.HTTP_400_BAD_REQUEST
            )

        session.status = 'cancelled'
        session.save()

        serializer = SessionSerializer(session)
        return Response({
            'message': 'Session cancelled successfully',
            'session': serializer.data
        })

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Start a session (creator only)"""
        session = self.get_object()
        user = request.user

        # Check if user is creator
        if session.creator != user:
            return Response(
                {'error': 'Only the creator can start a session'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if session can be started
        if session.status != 'upcoming':
            return Response(
                {'error': 'Only upcoming sessions can be started'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if session.date > timezone.now():
            return Response(
                {'error': 'Cannot start session before scheduled time'},
                status=status.HTTP_400_BAD_REQUEST
            )

        session.status = 'ongoing'
        session.save()

        serializer = SessionSerializer(session)
        return Response({
            'message': 'Session started successfully',
            'session': serializer.data
        })

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete a session (creator only)"""
        session = self.get_object()
        user = request.user

        # Check if user is creator
        if session.creator != user:
            return Response(
                {'error': 'Only the creator can complete a session'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if session can be completed
        if session.status != 'ongoing':
            return Response(
                {'error': 'Only ongoing sessions can be completed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        session.status = 'completed'
        session.save()

        serializer = SessionSerializer(session)
        return Response({
            'message': 'Session completed successfully',
            'session': serializer.data
        })

    @action(detail=True, methods=['get'])
    def participants(self, request, pk=None):
        """Get session participants"""
        session = self.get_object()
        participants = session.participants.all()

        serializer = ParticipantSerializer(participants, many=True)
        return Response(serializer.data)
