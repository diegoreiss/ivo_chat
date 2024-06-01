from django.urls import re_path

from . import consumers


websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>[0-9(a-f|A-F)]{8}-[0-9(a-f|A-F)]{4}-4[0-9(a-f|A-F)]{3}-[89ab][0-9(a-f|A-F)]{3}-[0-9(a-f|A-F)]{12})/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/users/', consumers.UsersConsumer.as_asgi())
]
