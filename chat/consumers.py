import json

from django.core.cache import caches
from django.core.serializers import serialize
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from api.models import CustomUser


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        default_cache = caches['default']
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_u_{self.room_name}'
        logged_users = default_cache.get('user_activity:logged_users')

        if not logged_users:
            default_cache.set('user_activity:logged_users', [], timeout=None)

        custom_user_cache = default_cache.get(f'users_minimal_data:CustomUser_{self.room_name}')

        if not custom_user_cache:
            custom_user = await sync_to_async(CustomUser.objects.get, thread_sensitive=True)(uuid=self.room_name)
            custom_user_fields = {
                'uuid': custom_user.uuid,
                'pk': custom_user.pk, 
                'first_name': custom_user.first_name, 
                'last_name': custom_user.last_name
            }
            default_cache.set(f'users_minimal_data:CustomUser_{self.room_name}', custom_user_fields, timeout=None)
            custom_user_cache = custom_user_fields
        
        logged_users_cache_list = default_cache.get('user_activity:logged_users')
        logged_users_cache_list.append(custom_user_cache)

        logged_users_cache_list = list({user['uuid']:user for user in logged_users_cache_list}.values())

        print(logged_users_cache_list)

        default_cache.set('user_activity:logged_users', logged_users_cache_list, timeout=None)

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
    
    async def disconnect(self, code):
        default_cache = caches['default']
        logged_users_cache_list = default_cache.get('user_activity:logged_users')
        logged_users_cache_list = list(filter(lambda user: str(user['uuid']) != self.room_name, logged_users_cache_list))

        default_cache.set('user_activity:logged_users', logged_users_cache_list, timeout=None)

        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'chat_message',
            'message': message
        })
    
    async def chat_message(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message
        }))
