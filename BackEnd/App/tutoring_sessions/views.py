from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db import models
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from datetime import datetime
import pytz
from .models import (
    Session, Participant, BookingRequest, SessionMaterial, Notification,
    LiveParticipantState, SessionMessage, SessionRecording
)
from .serializers import (
    SessionSerializer,
    SessionCreateSerializer,
    SessionUpdateSerializer,
    SessionListSerializer,
    ParticipantSerializer,
    BookingRequestSerializer,
    SessionMaterialSerializer,
    NotificationSerializer,
    LiveParticipantStateSerializer,
    SessionMessageSerializer,
    SessionRecordingSerializer
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

        # Filter by subject if provided
        subject_filter = self.request.query_params.get('subject', None)
        if subject_filter:
            queryset = queryset.filter(subject__icontains=subject_filter)

        # Filter by level if provided
        level_filter = self.request.query_params.get('level', None)
        if level_filter:
            queryset = queryset.filter(level=level_filter)

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
        """Create session with creator validation and timezone handling"""
        # Handle timezone conversion
        date_data = self.request.data.get('date')
        if date_data:
            # Frontend sends datetime with timezone offset
            # Convert to UTC before saving
            user_timezone = self.request.data.get('timezone_offset', 0)
            try:
                # Parse the datetime and adjust for timezone
                dt = datetime.fromisoformat(date_data.replace('Z', '+00:00'))
                utc_dt = dt.astimezone(pytz.UTC)
                serializer.save(creator=self.request.user, date=utc_dt)
            except ValueError:
                # Fallback to direct parsing if timezone info is missing
                serializer.save(creator=self.request.user)
        else:
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

        if session.creator != user:
            return Response(
                {'error': 'Only the creator can cancel this session'},
                status=status.HTTP_403_FORBIDDEN
            )

        if session.status in ['completed', 'cancelled']:
            return Response(
                {'error': 'Cannot cancel completed or cancelled sessions'},
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

        if session.creator != user:
            return Response(
                {'error': 'Only the creator can start this session'},
                status=status.HTTP_403_FORBIDDEN
            )

        if session.status not in ['approved', 'scheduled']:
            return Response(
                {'error': 'Session must be approved or scheduled to start'},
                status=status.HTTP_400_BAD_REQUEST
            )

        session.status = 'ongoing'
        session.started_at = timezone.now()
        session.save()

        serializer = SessionSerializer(session)
        return Response({
            'message': 'Session started successfully',
            'session': serializer.data
        })

    @action(detail=True, methods=['post'])
    def end(self, request, pk=None):
        """End a session (creator only)"""
        session = self.get_object()
        user = request.user

        if session.creator != user:
            return Response(
                {'error': 'Only the creator can end this session'},
                status=status.HTTP_403_FORBIDDEN
            )

        if session.status != 'ongoing':
            return Response(
                {'error': 'Session must be ongoing to end'},
                status=status.HTTP_400_BAD_REQUEST
            )

        session.status = 'completed'
        session.ended_at = timezone.now()
        session.save()

        serializer = SessionSerializer(session)
        return Response({
            'message': 'Session ended successfully',
            'session': serializer.data
        })

    @action(detail=True, methods=['get'])
    def live_participants(self, request, pk=None):
        """Get live participant states for a session"""
        session = self.get_object()

        # Check if user can access this session
        if not (session.creator == request.user or
                session.participants.filter(user=request.user, status='approved').exists()):
            return Response(
                {'error': 'You do not have permission to view this session'},
                status=status.HTTP_403_FORBIDDEN
            )

        participants = LiveParticipantState.objects.filter(session=session)
        serializer = LiveParticipantStateSerializer(participants, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get chat messages for a session"""
        session = self.get_object()

        # Check if user can access this session
        if not (session.creator == request.user or
                session.participants.filter(user=request.user, status='approved').exists()):
            return Response(
                {'error': 'You do not have permission to view this session'},
                status=status.HTTP_403_FORBIDDEN
            )

        messages = SessionMessage.objects.filter(session=session)
        serializer = SessionMessageSerializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def recordings(self, request, pk=None):
        """Get recordings for a session"""
        session = self.get_object()

        # Check if user can access this session
        if not (session.creator == request.user or
                session.participants.filter(user=request.user, status='approved').exists()):
            return Response(
                {'error': 'You do not have permission to view this session'},
                status=status.HTTP_403_FORBIDDEN
            )

        recordings = SessionRecording.objects.filter(session=session)
        serializer = SessionRecordingSerializer(recordings, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def create_recording(self, request, pk=None):
        """Create a new recording for a session (creator only)"""
        session = self.get_object()
        user = request.user

        if session.creator != user:
            return Response(
                {'error': 'Only the creator can create recordings'},
                status=status.HTTP_403_FORBIDDEN
            )

        recording_url = request.data.get('recording_url')
        duration = request.data.get('duration')
        file_size = request.data.get('file_size')

        if not recording_url:
            return Response(
                {'error': 'Recording URL is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        recording = SessionRecording.objects.create(
            session=session,
            recording_url=recording_url,
            duration=duration,
            file_size=file_size,
            created_by=user
        )

        serializer = SessionRecordingSerializer(recording)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.read = True
        notification.save()
        return Response({'message': 'Marked as read'})

    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        Notification.objects.filter(
            user=request.user, read=False).update(read=True)
        return Response({'message': 'All marked as read'})


class SessionMaterialViewSet(viewsets.ModelViewSet):
    serializer_class = SessionMaterialSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SessionMaterial.objects.filter(session_id=self.kwargs.get('session_pk'))

    def perform_create(self, serializer):
        session_id = self.kwargs.get('session_pk')
        session = Session.objects.get(id=session_id)

        if session.creator != self.request.user:
            raise PermissionDenied("Only session creator can upload materials")

        serializer.save(uploaded_by=self.request.user, session_id=session_id)


# Live Session Endpoints
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_session(request, session_id):
    """Start a live session (creators only)"""
    try:
        session = get_object_or_404(Session, id=session_id)

        # Check if user is the creator
        if session.creator != request.user:
            return Response(
                {'error': 'Only the session creator can start the session'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if session is in correct state
        if session.status != 'scheduled':
            return Response(
                {'error': 'Session must be scheduled to start'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Start the session
        session.status = 'ongoing'
        session.started_at = timezone.now()
        session.save()

        return Response({
            'message': 'Session started successfully',
            'session': {
                'id': session.id,
                'status': session.status,
                'started_at': session.started_at
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def end_session(request, session_id):
    """End a live session (creators only)"""
    try:
        session = get_object_or_404(Session, id=session_id)

        # Check if user is the creator
        if session.creator != request.user:
            return Response(
                {'error': 'Only the session creator can end the session'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if session is ongoing
        if session.status != 'ongoing':
            return Response(
                {'error': 'Session is not currently ongoing'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # End the session
        session.status = 'completed'
        session.ended_at = timezone.now()
        session.save()

        return Response({
            'message': 'Session ended successfully',
            'session': {
                'id': session.id,
                'status': session.status,
                'ended_at': session.ended_at
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_live_session(request, session_id):
    """Join a live session (participants only)"""
    try:
        session = get_object_or_404(Session, id=session_id)

        # Check if session is ongoing
        if session.status != 'ongoing':
            return Response(
                {'error': 'Session is not currently ongoing'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if user is approved participant
        if not session.participants.filter(user=request.user, status='approved').exists():
            return Response(
                {'error': 'You must be an approved participant to join'},
                status=status.HTTP_403_FORBIDDEN
            )

        return Response({
            'message': 'Joined live session successfully',
            'session': {
                'id': session.id,
                'status': session.status
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def leave_live_session(request, session_id):
    """Leave a live session"""
    try:
        session = get_object_or_404(Session, id=session_id)

        return Response({
            'message': 'Left live session successfully'
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
