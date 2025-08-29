from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, PasswordResetToken
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
import secrets


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'role', 'password', 'confirm_password')
        extra_kwargs = {
            'password': {'write_only': True},
            'confirm_password': {'write_only': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid email or password.')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError(
                'Must include email and password.')


class UserProfileSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(
        required=False, allow_null=True)  # <-- Writable!
    interests = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.interests.through.objects.all(),
        required=False
    )

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'role', 'date_joined', 'image', 'bio', 'interests')
        read_only_fields = ('id', 'date_joined')

    def get_image(self, obj):
        if obj.image:
            try:
                return obj.image.url
            except AttributeError:
                return obj.image
        return None


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            self.user = User.objects.get(email=value)
        except User.DoesNotExist:
            # Do not leak which emails exist; still accept but mark user as None
            self.user = None
        return value

    def create_token(self, user: User) -> PasswordResetToken:
        # 64-char URL-safe token
        token_value = secrets.token_urlsafe(48)[:64]
        expires_at = timezone.now() + timedelta(minutes=15)
        return PasswordResetToken.objects.create(
            user=user,
            token=token_value,
            expires_at=expires_at,
        )

    def save(self, **kwargs) -> PasswordResetToken | None:
        # If user exists, create a token; otherwise return None
        if self.user is None:
            return None
        # Invalidate old unused tokens for same user
        PasswordResetToken.objects.filter(
            user=self.user, is_used=False, expires_at__gt=timezone.now()).update(is_used=True)
        return self.create_token(self.user)


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords don't match.")
        # Enforce strong password rules
        pwd = attrs['new_password']
        errors = []
        if len(pwd) < 8:
            errors.append('Must be at least 8 characters long.')
        if not any(c.isupper() for c in pwd):
            errors.append('Must include at least one uppercase letter.')
        if not any(c.islower() for c in pwd):
            errors.append('Must include at least one lowercase letter.')
        if not any(c.isdigit() for c in pwd):
            errors.append('Must include at least one number.')
        if pwd.isalnum():
            errors.append('Must include at least one symbol.')
        if errors:
            raise serializers.ValidationError({'new_password': errors})
        try:
            validate_password(attrs['new_password'])
        except DjangoValidationError as e:
            raise serializers.ValidationError(
                {'new_password': list(e.messages)})
        try:
            self.reset_token = PasswordResetToken.objects.select_related(
                'user').get(token=attrs['token'])
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError({'token': 'Invalid token.'})
        if self.reset_token.is_used:
            raise serializers.ValidationError({'token': 'Token already used.'})
        if self.reset_token.expires_at < timezone.now():
            raise serializers.ValidationError({'token': 'Token expired.'})
        return attrs

    @transaction.atomic
    def save(self, **kwargs):
        user = self.reset_token.user
        new_password = self.validated_data['new_password']
        user.set_password(new_password)
        user.save(update_fields=['password'])
        self.reset_token.is_used = True
        self.reset_token.save(update_fields=['is_used'])
        return user
