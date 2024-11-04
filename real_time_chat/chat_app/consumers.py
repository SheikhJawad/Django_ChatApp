

from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import ChatRoom, Message
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async
from django.core.cache import cache
from django.utils import timezone
from django.contrib.auth import get_user_model
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import sync_to_async
from django.core.cache import cache
from django.utils import timezone
from django.db import models
from django.contrib.auth import get_user_model
from .models import PrivateMessage

User = get_user_model()



class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        original_room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_name = ''.join(c if c.isalnum() or c in '-_.' else '_' for c in original_room_name)
        self.room_group_name = f"chat_{self.room_name}"
        self.original_room_name = original_room_name

        try:
           
            await self.accept()

           
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            
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

    
            await self.save_message(username, message)

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

           
            self.save_to_redis({'message': message, 'username': username})
        except Exception as e:
            print(f"Error saving message: {e}")

    @sync_to_async
    def get_db_messages(self):
        try:
           
            chat_room = ChatRoom.objects.get(name=self.original_room_name)
            messages = Message.objects.filter(room=chat_room).order_by('-timestamp')[:50]
            return [{'message': msg.content, 'username': msg.user.username} for msg in messages]
        except ChatRoom.DoesNotExist:
            return []

    @sync_to_async
    def get_cached_messages(self):
   
        messages = cache.get(self.room_group_name, [])
        return messages

    @sync_to_async
    def save_to_redis(self, message):
       
        current_messages = cache.get(self.room_group_name, [])
        if len(current_messages) >= 50:
            current_messages.pop(0)  
        current_messages.append(message)
        cache.set(self.room_group_name, current_messages)


# from channels.generic.websocket import AsyncWebsocketConsumer
# import json
# from asgiref.sync import sync_to_async
# from django.core.cache import cache
# from django.utils import timezone
# from django.db import models
# from django.contrib.auth import get_user_model
# from .models import PrivateMessage

# User = get_user_model()

class DirectMessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
    
        self.user = self.scope['user']
        self.user_id = self.user.id
        self.receiver_id = int(self.scope['url_route']['kwargs']['user_id'])


        user_ids = sorted([self.user_id, self.receiver_id])
        self.room_group_name = f'chat_{user_ids[0]}_{user_ids[1]}'


        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )


        await self.channel_layer.group_add(
            f'user_{self.user_id}',
            self.channel_name
        )


        await sync_to_async(self.set_user_online)(self.user_id)


        await self.accept()


        messages = await sync_to_async(self.load_messages)()
        if messages:
            for message in messages:
                await self.send(text_data=json.dumps(message))

    async def disconnect(self, close_code):
      
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        await self.channel_layer.group_discard(
            f'user_{self.user_id}',
            self.channel_name
        )


        await sync_to_async(self.set_user_offline)(self.user_id)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        

        message_data = {
            'type': 'chat_message',
            'message': message,
            'sender_id': self.user_id,
            'receiver_id': self.receiver_id,
            'sender': self.user.username,
            'timestamp': str(timezone.now())
        }

 
        await self.channel_layer.group_send(
            self.room_group_name,
            message_data
        )

    
        await sync_to_async(self.save_message)(message)

    async def chat_message(self, event):

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
        
        messages = PrivateMessage.objects.filter(
            models.Q(sender_id=self.user_id, receiver_id=self.receiver_id) |
            models.Q(sender_id=self.receiver_id, receiver_id=self.user_id)
        ).order_by('-timestamp')[:50]

        message_list = []
        for message in messages:
            message_list.append({
                'message': message.content,
                'sender_id': message.sender_id,
                'receiver_id': message.receiver_id,
                'sender': User.objects.get(id=message.sender_id).username,
                'timestamp': str(message.timestamp)
            })

        return message_list[::-1] 