from rest_framework import serializers
from .models import (
    Session, Participant, BookingRequest, SessionMaterial, Notification,
    LiveParticipantState, SessionMessage, SessionRecording
)
from authentication.serializers import UserProfileSerializer


class ParticipantSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = Participant
        fields = '__all__'


class LiveParticipantStateSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = LiveParticipantState
        fields = '__all__'

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"


class SessionMessageSerializer(serializers.ModelSerializer):
    sender = UserProfileSerializer(read_only=True)
    sender_name = serializers.SerializerMethodField()

    class Meta:
        model = SessionMessage
        fields = '__all__'

    def get_sender_name(self, obj):
        return f"{obj.sender.first_name} {obj.sender.last_name}"


class SessionRecordingSerializer(serializers.ModelSerializer):
    created_by = UserProfileSerializer(read_only=True)

    class Meta:
        model = SessionRecording
        fields = '__all__'


class BookingRequestSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = BookingRequest
        fields = '__all__'


class SessionMaterialSerializer(serializers.ModelSerializer):
    uploaded_by = UserProfileSerializer(read_only=True)

    class Meta:
        model = SessionMaterial
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


class SessionSerializer(serializers.ModelSerializer):
    creator = UserProfileSerializer(read_only=True)
    participants = serializers.SerializerMethodField()
    materials = serializers.SerializerMethodField()
    booking_requests = serializers.SerializerMethodField()
    live_participants = serializers.SerializerMethodField()
    messages = serializers.SerializerMethodField()
    recordings = serializers.SerializerMethodField()
    is_full = serializers.ReadOnlyField()
    available_spots = serializers.ReadOnlyField()
    participant_count = serializers.ReadOnlyField()
    can_join = serializers.SerializerMethodField()

    class Meta:
        model = Session
        fields = '__all__'

    def get_participants(self, obj):
        return ParticipantSerializer(obj.participants.all(), many=True).data

    def get_materials(self, obj):
        return SessionMaterialSerializer(obj.materials.all(), many=True).data

    def get_booking_requests(self, obj):
        return BookingRequestSerializer(obj.booking_requests.all(), many=True).data

    def get_live_participants(self, obj):
        return LiveParticipantStateSerializer(obj.live_participants.all(), many=True).data

    def get_messages(self, obj):
        return SessionMessageSerializer(obj.messages.all(), many=True).data

    def get_recordings(self, obj):
        return SessionRecordingSerializer(obj.recordings.all(), many=True).data

    def get_can_join(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False

        # Check if user is already a participant
        if obj.participants.filter(user=request.user).exists():
            return False

        # Check if session is full
        if obj.is_full:
            return False

        # Check if session status allows joining
        return obj.status in ['scheduled', 'approved']


class SessionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ['title', 'description', 'subject', 'level', 'date', 'duration',
                  'max_participants', 'recording_enabled', 'chat_enabled', 'screen_sharing_enabled']

    def validate_date(self, value):
        """Validate that session date is in the future"""
        from django.utils import timezone
        if value <= timezone.now():
            raise serializers.ValidationError(
                "Session date must be in the future")
        return value

    def validate_max_participants(self, value):
        """Validate max participants range"""
        if value < 2:
            raise serializers.ValidationError(
                "Minimum 2 participants required")
        if value > 50:
            raise serializers.ValidationError(
                "Maximum 50 participants allowed")
        return value

    def create(self, validated_data):
        """Set creator to current user and generate room ID"""
        validated_data['creator'] = self.context['request'].user
        session = super().create(validated_data)
        session.generate_room_id()
        return session


class SessionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ['title', 'description', 'subject', 'level', 'date', 'duration', 'max_participants',
                  'status', 'recording_enabled', 'chat_enabled', 'screen_sharing_enabled']

    def validate_date(self, value):
        """Validate that session date is in the future"""
        from django.utils import timezone
        if value <= timezone.now():
            raise serializers.ValidationError(
                "Session date must be in the future")
        return value

    def validate_max_participants(self, value):
        """Validate max participants range and current participants"""
        if value < 2:
            raise serializers.ValidationError(
                "Minimum 2 participants required")
        if value > 50:
            raise serializers.ValidationError(
                "Maximum 50 participants allowed")

        # Check if reducing max_participants would kick out existing participants
        instance = self.instance
        if instance and value < instance.participants.filter(status='approved').count():
            raise serializers.ValidationError(
                f"Cannot reduce max participants below current participant count ({instance.participants.filter(status='approved').count()})"
            )
        return value


class SessionListSerializer(serializers.ModelSerializer):
    creator = UserProfileSerializer(read_only=True)
    participant_count = serializers.ReadOnlyField()
    is_full = serializers.ReadOnlyField()
    available_spots = serializers.ReadOnlyField()
    can_join = serializers.SerializerMethodField()

    class Meta:
        model = Session
        fields = [
            'id', 'title', 'description', 'subject', 'level', 'date', 'duration', 'max_participants',
            'creator', 'status', 'created_at', 'updated_at', 'room_id',
            'participant_count', 'is_full', 'available_spots', 'can_join'
        ]

    def get_can_join(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False

        # Check if user is already a participant
        if obj.participants.filter(user=request.user).exists():
            return False

        # Check if session is full
        if obj.is_full:
            return False

        # Check if session status allows joining
        return obj.status in ['scheduled', 'approved']
