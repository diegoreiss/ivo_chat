import json
import urllib.parse

from django.core.cache import caches
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
                'uuid': str(custom_user.uuid),
                'pk': custom_user.pk, 
                'first_name': custom_user.first_name, 
                'last_name': custom_user.last_name,
                'username': custom_user.username,
            }

            default_cache.set(f'users_minimal_data:CustomUser_{self.room_name}', custom_user_fields, timeout=None)
            custom_user_cache = custom_user_fields
        
        custom_user_cache['room_name'] = self.room_name
        logged_users_cache_list = default_cache.get('user_activity:logged_users')
        logged_users_cache_list.append(custom_user_cache)
        logged_users_cache_list = list({u['uuid']: u for u in logged_users_cache_list}.values())

        default_cache.set('user_activity:logged_users', logged_users_cache_list, timeout=None)

        await self.channel_layer.group_send('group_logged_users_room', {
            'type': 'send_notification',
            'message': logged_users_cache_list
        })
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
    
    async def disconnect(self, code):
        query = urllib.parse.parse_qs(self.scope['query_string'])
        uuid = query.get(b'uuid')[0].decode('utf-8')

        default_cache = caches['default']
        new_list = []
        logged_users_cache_list = default_cache.get('user_activity:logged_users')

        if logged_users_cache_list and uuid == self.room_name:
            print(logged_users_cache_list)
            new_list = list(filter(lambda user: user['uuid'] != self.room_name, logged_users_cache_list[:]))
            print(f'new list >>>: {new_list}')

            default_cache.set('user_activity:logged_users', new_list, timeout=None)

            await self.channel_layer.group_send('group_logged_users_room', {
                'type': 'send_notification',
                'message': new_list
            })

        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        default_cache = caches['default']
        chat_history_cache = default_cache.get(f'chat_history:{self.room_name}')

        if not chat_history_cache:
            chat_history_cache = []
            default_cache.set(f'chat_history:{self.room_name}', chat_history_cache, timeout=259200)

        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        chat_history_cache.append(text_data_json)
        default_cache.set(f'chat_history:{self.room_name}', chat_history_cache, timeout=259200)

        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'chat_message',
            'message': text_data_json
        })
    
    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))


class UsersConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        default_cache = caches['default']
        self.room_name = 'logged_users_room'
        self.room_group_name = f'group_{self.room_name}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        users_logged_cache = default_cache.get('user_activity:logged_users', [])

        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'send_notification',
            'message': users_logged_cache
        })
    
    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
    
    async def send_notification(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message
        }))
    