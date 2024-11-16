import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path,re_path
from chat_app.consumers import *
from chat_app.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'real_time_chat.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("ws/chat/<str:room_name>/", ChatConsumer.as_asgi()),
          re_path(r'ws/dm/(?P<user_id>\d+)/$', DirectMessageConsumer.as_asgi()),  # Adjust regex as needed
           re_path(r'ws/game/(?P<game_id>\d+)/$', GameConsumer.as_asgi()),
  
        ])
    ),
})
