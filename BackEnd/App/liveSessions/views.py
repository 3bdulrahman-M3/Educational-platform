from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import LiveSession
from .serializers import LiveSessionSerializer
import jwt
import datetime
import time
from datetime import datetime, timedelta
from pathlib import Path


JAAS_APP_ID = "vpaas-magic-cookie-8aca48389d514e87a3ac1a38dd3a7b68"
JAAS_ISS = "chat"
JAAS_AUD = "jitsi"

PRIVATE_KEY_PATH = Path(__file__).resolve().parent / "keys" / "Key 8_17_2025, 5_59_35 AM.pk"
with open(PRIVATE_KEY_PATH, "r") as f:
    JAAS_PRIVATE_KEY = f.read()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_session(request):
    serializer = LiveSessionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(created_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def list_sessions(request):
    sessions = LiveSession.objects.all().order_by('-created_at')
    serializer = LiveSessionSerializer(sessions, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def session_detail(request, pk):
    try:
        session = LiveSession.objects.get(pk=pk)
    except LiveSession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = LiveSessionSerializer(session)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_jaas_token(request):
    room_name = request.data.get('room_name')
    if not room_name:
        return Response({'error': 'room_name is required'}, status=status.HTTP_400_BAD_REQUEST)

    user = request.user
    now = datetime.utcnow()
    exp = now + timedelta(hours=4)  # Further extend to 4 hours
    nbf = now - timedelta(minutes=1)  # Allow 1-minute clock skew for nbf

    payload = {
        "aud": "jitsi",
        "iss": 'chat',  # Use JAAS_APP_ID as issuer, not hardcoded "chat"
        "sub": JAAS_APP_ID,  # Ensure this matches your Jitsi tenant's app ID
        "room": room_name,
        "exp": int(exp.timestamp()),
        "nbf": int(nbf.timestamp()),
        "context": {
            "user": {
                "name": user.get_full_name() or user.username,
                "email": user.email,
                "id": str(user.id),
            },
            "features": {
                "recording": True,
                "livestreaming": True,
                "transcription": True,
                "outbound-call": True,
                "sip-outbound-call": True,
            }
        }
    }

    # Ensure kid matches your Jitsi tenant's key ID
    token = jwt.encode(
        payload,
        JAAS_PRIVATE_KEY,
        algorithm="RS256",
        headers={"kid": "vpaas-magic-cookie-8aca48389d514e87a3ac1a38dd3a7b68/d8507d"}  # Replace with your tenant's key ID
    )
    return Response({"token": token})