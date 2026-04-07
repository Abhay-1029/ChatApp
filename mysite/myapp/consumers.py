from channels.generic.websocket import AsyncWebsocketConsumer
from collections import defaultdict
import json
from .models import ChatMessage, ChatRoom
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async


ACTIVE_ROOM_USERS = defaultdict(lambda: defaultdict(int))
ACTIVE_TYPING_USERS = defaultdict(set)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        self.username = self.scope["user"].username if self.scope["user"].is_authenticated else None

        #Adding created room to channel layer
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()
        if self.username:
            await self.track_user_status(is_online=True)
        print(">>>Websocket connection accepted")

    async def disconnect(self):
        if self.username:
            await self.update_typing_status(is_typing=False)
            await self.track_user_status(is_online=False)
        await self.channel_layer.group_discard(self.channel_name, self.room_group_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        event_type = data.get('type', 'message')
        message = data.get('message')
        username = data.get('username')
        room = data.get('room')

        if event_type == 'typing':
            if username:
                await self.update_typing_status(is_typing=data.get('is_typing', False), username=username)
            return

        if event_type == 'read_receipt':
            message_ids = data.get('message_ids', [])
            if username and message_ids:
                seen_message_ids = await self.mark_messages_seen(message_ids, username)
                if seen_message_ids:
                    await self.channel_layer.group_send(self.room_group_name, {
                        'type': 'read_receipt_update',
                        'message_ids': seen_message_ids,
                        'seen_by': username,
                    })
            return

        if not message:
            return

        await self.update_typing_status(is_typing=False, username=username)

        saved_message = await self.saved_message(username, room, message)

        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'chat_message',
            'message_id': saved_message.id,
            'message': message,
            'username': username,
            'room': room,
            'is_seen': False,
            'attachment_url': saved_message.attachment.url if saved_message.attachment else '',
            'attachment_name': saved_message.attachment.name.split('/')[-1] if saved_message.attachment else '',
            'is_image': False,
        })

    async def chat_message(self, event):
        message_id = event['message_id']
        message = event['message']
        username = event['username']
        room = event['room']
        is_seen = event.get('is_seen', False)
        attachment_url = event.get('attachment_url', '')
        attachment_name = event.get('attachment_name', '')
        is_image = event.get('is_image', False)

        await self.send(text_data=json.dumps({
            'type': 'message',
            'message_id': message_id,
            'message': message,
            'username': username,
            'room': room,
            'is_seen': is_seen,
            'attachment_url': attachment_url,
            'attachment_name': attachment_name,
            'is_image': is_image,
        }))

    async def presence_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'presence',
            'online_users': event['online_users'],
            'online_count': event['online_count'],
        }))

    async def typing_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'typing_users': event['typing_users'],
        }))

    async def read_receipt_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'read_receipt',
            'message_ids': event['message_ids'],
            'seen_by': event['seen_by'],
        }))

    async def track_user_status(self, is_online):
        room_users = ACTIVE_ROOM_USERS[self.room_name]

        if is_online:
            room_users[self.username] += 1
        else:
            if self.username in room_users:
                room_users[self.username] -= 1
                if room_users[self.username] <= 0:
                    del room_users[self.username]

        if not room_users and self.room_name in ACTIVE_ROOM_USERS:
            del ACTIVE_ROOM_USERS[self.room_name]

        online_users = sorted(ACTIVE_ROOM_USERS.get(self.room_name, {}).keys())

        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'presence_update',
            'online_users': online_users,
            'online_count': len(online_users),
        })

    async def update_typing_status(self, is_typing, username=None):
        active_username = username or self.username
        if not active_username:
            return

        room_typing_users = ACTIVE_TYPING_USERS[self.room_name]

        if is_typing:
            room_typing_users.add(active_username)
        else:
            room_typing_users.discard(active_username)

        if not room_typing_users and self.room_name in ACTIVE_TYPING_USERS:
            del ACTIVE_TYPING_USERS[self.room_name]

        typing_users = sorted(ACTIVE_TYPING_USERS.get(self.room_name, set()))

        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'typing_update',
            'typing_users': typing_users,
        })

    @sync_to_async
    def saved_message(self, username, room, message):
        user = User.objects.get(username=username)
        room = ChatRoom.objects.get(slug=room)
 
        return ChatMessage.objects.create(user=user, room=room, message_content=message)

    @sync_to_async
    def mark_messages_seen(self, message_ids, username):
        updated_ids = []
        for message in ChatMessage.objects.filter(id__in=message_ids, is_seen=False).exclude(user__username=username):
            message.is_seen = True
            message.save(update_fields=['is_seen'])
            updated_ids.append(message.id)
        return updated_ids
