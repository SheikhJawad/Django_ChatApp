from django.urls import path
from . import views
from .views import *
urlpatterns = [
        path('', login_page, name='login_page'),  
        path('register/', register_page, name='register_page'),  # This serves the registration form
        path('api/register/', register_view, name='register_view'),  # New API endpoint for registration
        path('api/login/', login_view, name='login_view'),  # API endpoint for login
        path('home/', chat_home, name='chat_home'),  # URL for chat home
        path('room/<str:room_name>/', chat_room, name='chat_room'),  # Chat room URL
        path('create-room/', views.create_room_view, name='create_room'),
         path('dm/', views.direct_message_view, name='direct_message_index'),  # Base DM URL
        path('dm/<int:user_id>/', views.direct_message_view, name='direct_message'),  # DM with specific user
        path('user-status/<int:user_id>/', views.get_user_status, name='get_user_status'),
        path('start-game/', views.start_game, name='start_game'),
    path('game/<int:game_id>/', views.game_detail, name='game_detail'),
      path('active-games/', views.active_games, name='active_games'),
        
]

