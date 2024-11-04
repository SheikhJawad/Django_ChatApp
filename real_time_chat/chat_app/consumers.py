
# from channels.generic.websocket import AsyncWebsocketConsumer
# import json
# from .models import ChatRoom, Message
# from django.contrib.auth.models import User
# from asgiref.sync import sync_to_async
# from django.core.cache import cache  # Importing cache for Redis operations

# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         # Sanitize room name - replace spaces and special characters with underscores
#         original_room_name = self.scope['url_route']['kwargs']['room_name']
#         self.room_name = ''.join(c if c.isalnum() or c in '-_.' else '_' for c in original_room_name)
#         self.room_group_name = f"chat_{self.room_name}"

#         # Store both names for database queries
#         self.original_room_name = original_room_name  # Keep original for database queries

#         try:
#             # Join room group
#             await self.channel_layer.group_add(
#                 self.room_group_name,
#                 self.channel_name
#             )

#             # Send previous messages to the newly connected user
#             cached_messages = await self.get_cached_messages()
#             for msg in cached_messages:
#                 await self.send(text_data=json.dumps(msg))

#             await self.accept()
#         except Exception as e:
#             print(f"Error in connect: {e}")
#             await self.close()

#     async def disconnect(self, close_code):
#         try:
#             await self.channel_layer.group_discard(
#                 self.room_group_name,
#                 self.channel_name
#             )
#         except Exception as e:
#             print(f"Error in disconnect: {e}")

#     async def receive(self, text_data):
#         try:
#             data = json.loads(text_data)
#             message = data['message']
#             username = data['username']

#             # Save message to database and cache it in Redis
#             await self.save_message(username, message)

#             # Broadcast message to room group
#             await self.channel_layer.group_send(
#                 self.room_group_name,
#                 {
#                     'type': 'chat_message',
#                     'message': message,
#                     'username': username
#                 }
#             )
#         except Exception as e:
#             print(f"Error in receive: {e}")

#     async def chat_message(self, event):
#         try:
#             message = event['message']
#             username = event['username']

#             # Send message to WebSocket
#             await self.send(text_data=json.dumps({
#                 'message': message,
#                 'username': username
#             }))
#         except Exception as e:
#             print(f"Error in chat_message: {e}")

#     @sync_to_async
#     def save_message(self, username, message):
#         try:
#             print(f"Trying to save message: '{message}' from user: '{username}'")
            
#             # Use original room name for database queries
#             user = User.objects.get(username=username)
#             chat_room = ChatRoom.objects.get(name=self.original_room_name)
            
#             # Create message instance
#             new_message = Message.objects.create(
#                 user=user, 
#                 content=message, 
#                 room=chat_room
#             )
#             print(f"Message saved successfully: {new_message}")
            
#             # Save message to Redis
#             self.save_to_redis({'message': message, 'username': username})

#         except User.DoesNotExist:
#             print(f"User {username} does not exist.")
#         except ChatRoom.DoesNotExist:
#             print(f"Chat room {self.original_room_name} does not exist.")
#             # Optionally create the room if it doesn't exist
#             try:
#                 chat_room = ChatRoom.objects.create(name=self.original_room_name)
#                 print(f"Created new chat room: {chat_room}")
#                 # Try saving the message again
#                 user = User.objects.get(username=username)
#                 new_message = Message.objects.create(
#                     user=user, 
#                     content=message, 
#                     room=chat_room
#                 )
#                 # Save to Redis again
#                 self.save_to_redis({'message': message, 'username': username})
#             except Exception as e:
#                 print(f"Error creating chat room: {e}")
#         except Exception as e:
#             print(f"An error occurred while saving the message: {e}")

#     @sync_to_async
#     def get_cached_messages(self):
#         # Retrieve messages from Redis
#         messages = cache.get(self.room_group_name, [])
#         print(f"Retrieved messages from Redis for {self.room_group_name}: {messages}")
#         return messages

#     @sync_to_async
#     def save_to_redis(self, message):
#         # Append message to Redis list
#         current_messages = cache.get(self.room_group_name, [])
#         current_messages.append(message)
#         cache.set(self.room_group_name, current_messages)
#         print(f"Message saved to Redis for {self.room_group_name}: {message}")
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import ChatRoom, Message
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async
from django.core.cache import cache

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        original_room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_name = ''.join(c if c.isalnum() or c in '-_.' else '_' for c in original_room_name)
        self.room_group_name = f"chat_{self.room_name}"
        self.original_room_name = original_room_name

        try:
            # Accept connection before joining the room group
            await self.accept()

            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            # Retrieve and send both cached (recent) and older messages from the database
            await self.send_past_messages()

        except Exception as e:
            print(f"Error in connect: {e}")
            await self.close()


    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        except Exception as e:
            print(f"Error in disconnect: {e}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message = data['message']
            username = data['username']

            # Save message to database and cache it in Redis
            await self.save_message(username, message)

            # Broadcast message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': username
                }
            )
        except Exception as e:
            print(f"Error in receive: {e}")

    async def chat_message(self, event):
        try:
            message = event['message']
            username = event['username']

            # Send message to WebSocket
            await self.send(text_data=json.dumps({
                'message': message,
                'username': username
            }))
        except Exception as e:
            print(f"Error in chat_message: {e}")

    async def send_past_messages(self):
        cached_messages = await self.get_cached_messages()
        db_messages = await self.get_db_messages()
        
        for msg in db_messages + cached_messages:
            await self.send(text_data=json.dumps(msg))

    @sync_to_async
    def save_message(self, username, message):
        try:
            user = User.objects.get(username=username)
            chat_room, _ = ChatRoom.objects.get_or_create(name=self.original_room_name)
            new_message = Message.objects.create(user=user, content=message, room=chat_room)

            # Save message to Redis with limit (e.g., last 50 messages)
            self.save_to_redis({'message': message, 'username': username})
        except Exception as e:
            print(f"Error saving message: {e}")

    @sync_to_async
    def get_db_messages(self):
        try:
            # Fetch last 50 messages from the database for the room
            chat_room = ChatRoom.objects.get(name=self.original_room_name)
            messages = Message.objects.filter(room=chat_room).order_by('-timestamp')[:50]
            return [{'message': msg.content, 'username': msg.user.username} for msg in messages]
        except ChatRoom.DoesNotExist:
            return []

    @sync_to_async
    def get_cached_messages(self):
        # Retrieve messages from Redis
        messages = cache.get(self.room_group_name, [])
        return messages

    @sync_to_async
    def save_to_redis(self, message):
        # Append message to Redis list with a limit (e.g., 50 messages)
        current_messages = cache.get(self.room_group_name, [])
        if len(current_messages) >= 50:
            current_messages.pop(0)  # Remove the oldest message if over limit
        current_messages.append(message)
        cache.set(self.room_group_name, current_messages)

# from channels.generic.websocket import AsyncWebsocketConsumer
# import json
# from asgiref.sync import sync_to_async
# from django.core.cache import cache
# from django.utils import timezone
# from .models import PrivateMessage

# class DirectMessageConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.user_id = self.scope['user'].id  # Get the ID of the logged-in user
#         self.room_group_name = f'direct_message_{self.user_id}'

#         # Join the room group
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )

#         # Set the user as online
#         await sync_to_async(self.set_user_online)(self.user_id)

#         # Broadcast the user's online status to all connected clients
#         await self.channel_layer.group_send(
#             'user_status_group',
#             {
#                 'type': 'user_status',
#                 'user_id': self.user_id,
#                 'status': 'online'
#             }
#         )

#         await self.accept()

#         # Load messages from cache when connecting
#         messages = await sync_to_async(self.load_messages)(self.user_id)
#         for message in messages:
#             await self.send(text_data=json.dumps(message))

#     async def disconnect(self, close_code):
#         # Leave the room group
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )

#         # Set user as offline
#         await sync_to_async(self.set_user_offline)(self.user_id)

#         # Broadcast the user's offline status
#         await self.channel_layer.group_send(
#             'user_status_group',
#             {
#                 'type': 'user_status',
#                 'user_id': self.user_id,
#                 'status': 'offline'
#             }
#         )

#     async def receive(self, text_data):
#         data = json.loads(text_data)
#         message = data['message']
#         sender_id = self.scope['user'].id
#         receiver_id = data['receiver_id']

#         # Send message to room group
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': message,
#                 'sender_id': sender_id,
#                 'receiver_id': receiver_id,
#                 'sender': self.scope['user'].username,
#             }
#         )

#         # Save and cache the message
#         await sync_to_async(self.save_private_message)(sender_id, receiver_id, message)
#         await sync_to_async(self.cache_message)(sender_id, receiver_id, message)

#     async def chat_message(self, event):
#         message = event['message']
#         sender_id = event['sender_id']
#         receiver_id = event['receiver_id']
#         sender = event['sender']

#         # Send message to WebSocket
#         await self.send(text_data=json.dumps({
#             'message': message,
#             'sender_id': sender_id,
#             'receiver_id': receiver_id,
#             'sender': sender,
#             'timestamp': str(timezone.now()),
#         }))

#     async def user_status(self, event):
#         await self.send(text_data=json.dumps({
#             'user_id': event['user_id'],
#             'status': event['status'],
#         }))

#     def set_user_online(self, user_id):
#         cache.set(f'user_status_{user_id}', 'online', timeout=None)

#     def set_user_offline(self, user_id):
#         cache.delete(f'user_status_{user_id}')

#     def save_private_message(self, sender_id, receiver_id, content):
#         PrivateMessage.objects.create(
#             sender_id=sender_id,
#             receiver_id=receiver_id,
#             content=content
#         )

#     def cache_message(self, sender_id, receiver_id, content):
#         cache_key = f'direct_message_{sender_id}_{receiver_id}'
#         messages = cache.get(cache_key, [])
#         messages.append({
#             'sender_id': sender_id,
#             'receiver_id': receiver_id,
#             'content': content,
#             'timestamp': str(timezone.now()),
#         })
#         cache.set(cache_key, messages, timeout=3600)

#     def load_messages(self, user_id):
#         cache_key = f'direct_message_{user_id}_*'
#         messages = []
#         keys = cache.keys(cache_key)

#         for key in keys:
#             messages.extend(cache.get(key))

#         return messages
# consumers.py
# from channels.generic.websocket import AsyncWebsocketConsumer
# import json
# from asgiref.sync import sync_to_async
# from django.core.cache import cache
# from django.utils import timezone
# from .models import PrivateMessage

# class DirectMessageConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.receiver_id = self.scope['url_route']['kwargs']['user_id']  # Get receiver's ID from URL
#         self.user_id = self.scope['user'].id  # Get the ID of the logged-in user
#         self.room_group_name = f'direct_message_{self.receiver_id}'

#         # Join the room group
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )

#         # Set the user as online
#         await sync_to_async(self.set_user_online)(self.user_id)

#         # Broadcast the user's online status
#         await self.channel_layer.group_send(
#             'user_status_group',
#             {
#                 'type': 'user_status',
#                 'user_id': self.user_id,
#                 'status': 'online'
#             }
#         )

#         await self.accept()

#         # Load messages from cache when connecting
#         messages = await sync_to_async(self.load_messages)(self.receiver_id)
#         for message in messages:
#             await self.send(text_data=json.dumps(message))

#     async def disconnect(self, close_code):
#         # Leave the room group
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )

#         # Set user as offline
#         await sync_to_async(self.set_user_offline)(self.user_id)

#         # Broadcast the user's offline status
#         await self.channel_layer.group_send(
#             'user_status_group',
#             {
#                 'type': 'user_status',
#                 'user_id': self.user_id,
#                 'status': 'offline'
#             }
#         )

#     async def receive(self, text_data):
#         data = json.loads(text_data)
#         message = data['message']
#         sender_id = self.scope['user'].id
#         receiver_id = data['receiver_id']

#         # Send message to room group
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': message,
#                 'sender_id': sender_id,
#                 'receiver_id': receiver_id,
#                 'sender': self.scope['user'].username,
#                 'timestamp': str(timezone.now()),  # Add a timestamp
#             }
#         )

#         # Save and cache the message
#         await sync_to_async(self.save_private_message)(sender_id, receiver_id, message)
#         await sync_to_async(self.cache_message)(sender_id, receiver_id, message)

#     async def chat_message(self, event):
#         # Send message to WebSocket
#         await self.send(text_data=json.dumps({
#             'message': event['message'],
#             'sender_id': event['sender_id'],
#             'receiver_id': event['receiver_id'],
#             'sender': event['sender'],
#             'timestamp': event['timestamp'],  # Send the timestamp
#         }))

#     async def user_status(self, event):
#         await self.send(text_data=json.dumps({
#             'user_id': event['user_id'],
#             'status': event['status'],
#         }))

#     def set_user_online(self, user_id):
#         cache.set(f'user_status_{user_id}', 'online', timeout=None)

#     def set_user_offline(self, user_id):
#         cache.delete(f'user_status_{user_id}')

#     def save_private_message(self, sender_id, receiver_id, content):
#         PrivateMessage.objects.create(
#             sender_id=sender_id,
#             receiver_id=receiver_id,
#             content=content
#         )

#     def cache_message(self, sender_id, receiver_id, content):
#         cache_key = f'direct_message_{sender_id}_{receiver_id}'
#         messages = cache.get(cache_key, [])
#         messages.append({
#             'sender_id': sender_id,
#             'receiver_id': receiver_id,
#             'content': content,
#             'timestamp': str(timezone.now()),
#         })
#         cache.set(cache_key, messages, timeout=3600)

#     def load_messages(self, receiver_id):
#         cache_key = f'direct_message_*_{receiver_id}'
#         messages = []
#         keys = cache.keys(cache_key)

#         for key in keys:
#             messages.extend(cache.get(key))

#         return messages
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import sync_to_async
from django.core.cache import cache
from django.utils import timezone
from django.db import models
from django.contrib.auth import get_user_model
from .models import PrivateMessage

User = get_user_model()

class DirectMessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get the current user and receiver's ID
        self.user = self.scope['user']
        self.user_id = self.user.id
        self.receiver_id = int(self.scope['url_route']['kwargs']['user_id'])

        # Create a unique room name for this conversation
        # Ensure the room name is the same for both users by ordering the IDs
        user_ids = sorted([self.user_id, self.receiver_id])
        self.room_group_name = f'chat_{user_ids[0]}_{user_ids[1]}'

        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Also join a personal notification group
        await self.channel_layer.group_add(
            f'user_{self.user_id}',
            self.channel_name
        )

        # Set user as online
        await sync_to_async(self.set_user_online)(self.user_id)

        # Accept the connection
        await self.accept()

        # Load and send previous messages
        messages = await sync_to_async(self.load_messages)()
        if messages:
            for message in messages:
                await self.send(text_data=json.dumps(message))

    async def disconnect(self, close_code):
        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # Leave personal notification group
        await self.channel_layer.group_discard(
            f'user_{self.user_id}',
            self.channel_name
        )

        # Set user as offline
        await sync_to_async(self.set_user_offline)(self.user_id)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        
        # Create message data
        message_data = {
            'type': 'chat_message',
            'message': message,
            'sender_id': self.user_id,
            'receiver_id': self.receiver_id,
            'sender': self.user.username,
            'timestamp': str(timezone.now())
        }

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            message_data
        )

        # Save the message
        await sync_to_async(self.save_message)(message)

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_id': event['sender_id'],
            'receiver_id': event['receiver_id'],
            'sender': event['sender'],
            'timestamp': event['timestamp']
        }))

    def set_user_online(self, user_id):
        cache.set(f'user_status_{user_id}', 'online', timeout=None)

    def set_user_offline(self, user_id):
        cache.delete(f'user_status_{user_id}')

    def save_message(self, content):
        """Save message to database"""
        message = PrivateMessage.objects.create(
            sender_id=self.user_id,
            receiver_id=self.receiver_id,
            content=content
        )
        return message

    def load_messages(self):
        """Load recent messages for this conversation"""
        # Get messages between these two users
        messages = PrivateMessage.objects.filter(
            models.Q(sender_id=self.user_id, receiver_id=self.receiver_id) |
            models.Q(sender_id=self.receiver_id, receiver_id=self.user_id)
        ).order_by('-timestamp')[:50]

        # Convert messages to list of dicts
        message_list = []
        for message in messages:
            message_list.append({
                'message': message.content,
                'sender_id': message.sender_id,
                'receiver_id': message.receiver_id,
                'sender': User.objects.get(id=message.sender_id).username,
                'timestamp': str(message.timestamp)
            })

        return message_list[::-1]  # Reverse to show oldest first