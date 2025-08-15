from rest_framework import serializers
from .models import Session, Participant
from authentication.serializers import UserProfileSerializer


class ParticipantSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    joined_at = serializers.ReadOnlyField()
    role = serializers.ReadOnlyField()

    class Meta:
        model = Participant
        fields = ['id', 'user', 'joined_at', 'role']


class SessionSerializer(serializers.ModelSerializer):
    creator = UserProfileSerializer(read_only=True)
    participants = ParticipantSerializer(many=True, read_only=True)
    is_full = serializers.ReadOnlyField()
    available_spots = serializers.ReadOnlyField()
    can_join = serializers.ReadOnlyField()
    status = serializers.ReadOnlyField()
    created_at = serializers.ReadOnlyField()
    updated_at = serializers.ReadOnlyField()

    class Meta:
        model = Session
        fields = [
            'id', 'title', 'description', 'date', 'max_participants',
            'creator', 'participants', 'status', 'created_at', 'updated_at',
            'is_full', 'available_spots', 'can_join'
        ]


class SessionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ['title', 'description', 'date', 'max_participants']

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
        if value > 20:
            raise serializers.ValidationError(
                "Maximum 20 participants allowed")
        return value

    def create(self, validated_data):
        """Set creator to current user"""
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)


class SessionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ['title', 'description', 'date', 'max_participants']

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
        if value > 20:
            raise serializers.ValidationError(
                "Maximum 20 participants allowed")

        # Check if reducing max_participants would kick out existing participants
        instance = self.instance
        if instance and value < instance.participants.count():
            raise serializers.ValidationError(
                f"Cannot reduce max participants below current participant count ({instance.participants.count()})"
            )
        return value


class SessionListSerializer(serializers.ModelSerializer):
    creator = UserProfileSerializer(read_only=True)
    participant_count = serializers.SerializerMethodField()
    is_full = serializers.ReadOnlyField()
    available_spots = serializers.ReadOnlyField()
    can_join = serializers.ReadOnlyField()

    class Meta:
        model = Session
        fields = [
            'id', 'title', 'description', 'date', 'max_participants',
            'creator', 'status', 'created_at', 'updated_at',
            'participant_count', 'is_full', 'available_spots', 'can_join'
        ]

    def get_participant_count(self, obj):
        """Get current number of participants"""
        return obj.participants.count()
