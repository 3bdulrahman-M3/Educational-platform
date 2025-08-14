from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password',
                  'confirm_password', 'first_name', 'last_name', 'role']
        extra_kwargs = {
            'password': {'write_only': True},
            'confirm_password': {'write_only': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid email or password')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError(
                'Must include email and password')


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name',
                  'last_name', 'role', 'google_id', 'date_joined']
        read_only_fields = ['id', 'date_joined']

    def validate_role(self, value):
        valid_roles = ['student', 'instructor', 'admin']
        if value not in valid_roles:
            raise serializers.ValidationError(
                f"Role must be one of: {', '.join(valid_roles)}")
        return value


class RoleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['role']

    def validate_role(self, value):
        valid_roles = ['student', 'instructor', 'admin']
        if value not in valid_roles:
            raise serializers.ValidationError(
                f"Role must be one of: {', '.join(valid_roles)}")
        return value


class GoogleAuthSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate_token(self, value):
        if not value:
            raise serializers.ValidationError("Google token is required")
        return value


class GoogleCompleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'google_id', 'role']

    def validate(self, attrs):
        # Check if user exists with this email and google_id
        try:
            user = User.objects.get(
                email=attrs['email'], google_id=attrs['google_id'])
            if user.role != 'student':  # Only allow completion for users with default role
                raise serializers.ValidationError(
                    "User already has a role assigned")
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "User not found with provided email and Google ID")

        return attrs
