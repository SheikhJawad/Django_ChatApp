from django.urls import path,re_path
from . import consumers

websocket_urlpatterns = [
   path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
  re_path(r'ws/dm/(?P<user_id>\d+)/$', consumers.DirectMessageConsumer.as_asgi()), 
   re_path(r'ws/game/(?P<game_id>\d+)/$', consumers.GameConsumer.as_asgi()),
  
  
   
]
