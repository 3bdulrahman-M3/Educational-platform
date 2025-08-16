import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Session, LiveParticipantState, SessionMessage

logger = logging.getLogger(__name__)
User = get_user_model()


class LiveSessionConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for live session communication"""

    async def connect(self):
        """Handle WebSocket connection"""
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.user = self.scope['user']
        self.room_group_name = f'session_{self.session_id}'

        # Check if user is authenticated
        if not self.user.is_authenticated:
            await self.close()
            return

        # Check if user can access this session
        can_access = await self.can_access_session()
        if not can_access:
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Update participant state
        await self.update_participant_state(is_connected=True)

        # Notify others that user joined
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'user_id': self.user.id,
                'user_name': f"{self.user.first_name} {self.user.last_name}",
                'user_role': self.user.role,
            }
        )

        logger.info(
            f"User {self.user.id} connected to session {self.session_id}")

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Update participant state
        await self.update_participant_state(is_connected=False)

        # Notify others that user left
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_left',
                'user_id': self.user.id,
                'user_name': f"{self.user.first_name} {self.user.last_name}",
            }
        )

        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        logger.info(
            f"User {self.user.id} disconnected from session {self.session_id}")

    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'webrtc_signal':
                await self.handle_webrtc_signal(data)
            elif message_type == 'chat_message':
                await self.handle_chat_message(data)
            elif message_type == 'participant_state':
                await self.handle_participant_state(data)
            elif message_type == 'hand_raise':
                await self.handle_hand_raise(data)
            elif message_type == 'screen_share':
                await self.handle_screen_share(data)
            else:
                logger.warning(f"Unknown message type: {message_type}")

        except json.JSONDecodeError:
            logger.error("Invalid JSON received")
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    async def handle_webrtc_signal(self, data):
        """Handle WebRTC signaling messages"""
        target_user_id = data.get('target_user_id')
        signal_data = data.get('signal')

        if target_user_id:
            # Send to specific user
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'webrtc_signal',
                    'from_user_id': self.user.id,
                    'target_user_id': target_user_id,
                    'signal': signal_data,
                }
            )
        else:
            # Broadcast to all users in session
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'webrtc_signal',
                    'from_user_id': self.user.id,
                    'signal': signal_data,
                }
            )

    async def handle_chat_message(self, data):
        """Handle chat messages"""
        message_text = data.get('message', '').strip()

        if not message_text:
            return

        # Save message to database
        await self.save_chat_message(message_text)

        # Broadcast to all users in session
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'user_id': self.user.id,
                'user_name': f"{self.user.first_name} {self.user.last_name}",
                'message': message_text,
                'timestamp': timezone.now().isoformat(),
            }
        )

    async def handle_participant_state(self, data):
        """Handle participant state updates (audio/video)"""
        audio_enabled = data.get('audio_enabled', False)
        video_enabled = data.get('video_enabled', False)

        # Update participant state in database
        await self.update_participant_media_state(audio_enabled, video_enabled)

        # Broadcast to all users in session
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'participant_state_update',
                'user_id': self.user.id,
                'user_name': f"{self.user.first_name} {self.user.last_name}",
                'audio_enabled': audio_enabled,
                'video_enabled': video_enabled,
            }
        )

    async def handle_hand_raise(self, data):
        """Handle hand raise events"""
        hand_raised = data.get('hand_raised', False)

        # Update participant state in database
        await self.update_hand_raise_state(hand_raised)

        # Broadcast to all users in session
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'hand_raise_update',
                'user_id': self.user.id,
                'user_name': f"{self.user.first_name} {self.user.last_name}",
                'hand_raised': hand_raised,
            }
        )

    async def handle_screen_share(self, data):
        """Handle screen sharing events"""
        screen_sharing = data.get('screen_sharing', False)

        # Update participant state in database
        await self.update_screen_share_state(screen_sharing)

        # Broadcast to all users in session
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'screen_share_update',
                'user_id': self.user.id,
                'user_name': f"{self.user.first_name} {self.user.last_name}",
                'screen_sharing': screen_sharing,
            }
        )

    # WebSocket event handlers
    async def webrtc_signal(self, event):
        """Send WebRTC signal to client"""
        await self.send(text_data=json.dumps({
            'type': 'webrtc_signal',
            'from_user_id': event['from_user_id'],
            'target_user_id': event.get('target_user_id'),
            'signal': event['signal'],
        }))

    async def chat_message(self, event):
        """Send chat message to client"""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'user_id': event['user_id'],
            'user_name': event['user_name'],
            'message': event['message'],
            'timestamp': event['timestamp'],
        }))

    async def participant_state_update(self, event):
        """Send participant state update to client"""
        await self.send(text_data=json.dumps({
            'type': 'participant_state_update',
            'user_id': event['user_id'],
            'user_name': event['user_name'],
            'audio_enabled': event['audio_enabled'],
            'video_enabled': event['video_enabled'],
        }))

    async def hand_raise_update(self, event):
        """Send hand raise update to client"""
        await self.send(text_data=json.dumps({
            'type': 'hand_raise_update',
            'user_id': event['user_id'],
            'user_name': event['user_name'],
            'hand_raised': event['hand_raised'],
        }))

    async def screen_share_update(self, event):
        """Send screen share update to client"""
        await self.send(text_data=json.dumps({
            'type': 'screen_share_update',
            'user_id': event['user_id'],
            'user_name': event['user_name'],
            'screen_sharing': event['screen_sharing'],
        }))

    async def user_joined(self, event):
        """Send user joined notification to client"""
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'user_id': event['user_id'],
            'user_name': event['user_name'],
            'user_role': event['user_role'],
        }))

    async def user_left(self, event):
        """Send user left notification to client"""
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'user_id': event['user_id'],
            'user_name': event['user_name'],
        }))

    # Database operations
    @database_sync_to_async
    def can_access_session(self):
        """Check if user can access this session"""
        try:
            session = Session.objects.get(id=self.session_id)

            # Creator can always access
            if session.creator == self.user:
                return True

            # Check if user is an approved participant
            return session.participants.filter(
                user=self.user,
                status='approved'
            ).exists()
        except Session.DoesNotExist:
            return False

    @database_sync_to_async
    def update_participant_state(self, is_connected=False, **kwargs):
        """Update participant state in database"""
        session = Session.objects.get(id=self.session_id)
        state, created = LiveParticipantState.objects.get_or_create(
            session=session,
            user=self.user,
            defaults={
                'is_connected': is_connected,
                'connection_id': self.channel_name,
            }
        )

        if not created:
            state.is_connected = is_connected
            state.connection_id = self.channel_name
            state.last_seen = timezone.now()
            state.save(update_fields=['is_connected',
                       'connection_id', 'last_seen'])

    @database_sync_to_async
    def update_participant_media_state(self, audio_enabled, video_enabled):
        """Update participant media state"""
        session = Session.objects.get(id=self.session_id)
        state, created = LiveParticipantState.objects.get_or_create(
            session=session,
            user=self.user,
            defaults={
                'audio_enabled': audio_enabled,
                'video_enabled': video_enabled,
            }
        )

        if not created:
            state.audio_enabled = audio_enabled
            state.video_enabled = video_enabled
            state.last_seen = timezone.now()
            state.save(update_fields=['audio_enabled',
                       'video_enabled', 'last_seen'])

    @database_sync_to_async
    def update_hand_raise_state(self, hand_raised):
        """Update hand raise state"""
        session = Session.objects.get(id=self.session_id)
        state, created = LiveParticipantState.objects.get_or_create(
            session=session,
            user=self.user,
            defaults={'hand_raised': hand_raised}
        )

        if not created:
            state.hand_raised = hand_raised
            state.last_seen = timezone.now()
            state.save(update_fields=['hand_raised', 'last_seen'])

    @database_sync_to_async
    def update_screen_share_state(self, screen_sharing):
        """Update screen sharing state"""
        session = Session.objects.get(id=self.session_id)
        state, created = LiveParticipantState.objects.get_or_create(
            session=session,
            user=self.user,
            defaults={'screen_sharing': screen_sharing}
        )

        if not created:
            state.screen_sharing = screen_sharing
            state.last_seen = timezone.now()
            state.save(update_fields=['screen_sharing', 'last_seen'])

    @database_sync_to_async
    def save_chat_message(self, message_text):
        """Save chat message to database"""
        session = Session.objects.get(id=self.session_id)
        SessionMessage.objects.create(
            session=session,
            sender=self.user,
            message=message_text,
            message_type='chat'
        )
