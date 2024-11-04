from django.urls import path
from . import views
from .views import *

# urlpatterns = [
#     path('', views.chat_home, name='chat_home'),
#     path('chat/<str:room_name>/', views.chat_room, name='chat_room'),
#     path('register/', views.register_page, name='register_page'),  # Renders registration form
#     path('register_user/', views.register_view, name='register'),  # Handles registration logic
#     path('login/', views.login_page, name='login_page'),  # Renders login form
#     path('login_user/', views.login_view, name='login'),  # Handles login logic
# ]
# urlpatterns = [
#     path('', login_page, name='login_page'),  # Adjust this to your desired landing page
#     path('register/', register_page, name='register_page'),
#     path('api/login/', login_view, name='login_view'),  # API endpoint for login
#     path('home/', chat_home, name='chat_home'),  # URL for chat home
#     path('room/<str:room_name>/', chat_room, name='chat_room'),  # Chat room URL
# ]
urlpatterns = [
    path('', login_page, name='login_page'),  # Adjust this to your desired landing page
    path('register/', register_page, name='register_page'),  # This serves the registration form
    path('api/register/', register_view, name='register_view'),  # New API endpoint for registration
    path('api/login/', login_view, name='login_view'),  # API endpoint for login
    path('home/', chat_home, name='chat_home'),  # URL for chat home
    path('room/<str:room_name>/', chat_room, name='chat_room'),  # Chat room URL
     path('create-room/', views.create_room_view, name='create_room'),
 path('dm/', views.direct_message_view, name='direct_message_index'),  # Base DM URL
    path('dm/<int:user_id>/', views.direct_message_view, name='direct_message'),  # DM with specific user
]
