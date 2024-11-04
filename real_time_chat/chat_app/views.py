# chat/views.py
# from django.shortcuts import render, get_object_or_404
# from .models import ChatRoom, Message

# def chat_home(request):
#     rooms = ChatRoom.objects.all()  # Get all chat rooms from the database
#     return render(request, 'chat/home.html', {'rooms': rooms})

# def chat_room(request, room_name):
#     chat_room = get_object_or_404(ChatRoom, name=room_name)
#     messages = Message.objects.filter(room=chat_room).order_by('timestamp')
#     return render(request, 'chat/room.html', {
#         'room_name': room_name,
#         'messages': messages,
#     })
    
    
    
# # chat/views.py
# # chat/views.py
# from django.shortcuts import render, redirect
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from rest_framework import status
# from django.contrib.auth import login
# from .serializers import RegisterSerializer, LoginSerializer
# import requests
# from rest_framework.permissions import AllowAny
# from rest_framework.decorators import api_view, permission_classes
# from django.conf import settings

# def register_page(request):
#     # Render the registration form
#     return render(request, 'chat/register.html')
# @api_view(['POST'])
# @permission_classes([AllowAny])  # Allow unauthenticated access
# def register_view(request):
#     serializer = RegisterSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# def login_page(request):
#     # Render the login form
#     return render(request, 'chat/login.html')


# @api_view(['POST'])
# @permission_classes([AllowAny])  # Allow unauthenticated access
# def login_view(request):
#     serializer = LoginSerializer(data=request.data)
#     if serializer.is_valid():
#         user = serializer.validated_data['user']
#         login(request, user)
#         return render(request,'chat/home.html')  # Redirect to chat_home after login
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import login
from .serializers import RegisterSerializer, LoginSerializer
from rest_framework.permissions import AllowAny
from django.contrib.auth.decorators import login_required 
from.forms import*

@login_required 
def chat_home(request):
    rooms = ChatRoom.objects.all()  # Get all chat rooms from the database
    return render(request, 'chat/home.html', {'rooms': rooms})
@login_required 
def chat_room(request, room_name):
    chat_room = get_object_or_404(ChatRoom, name=room_name)
    messages = Message.objects.filter(room=chat_room).order_by('timestamp')
    return render(request, 'chat/room.html', {
        'room_name': room_name,
        'messages': messages,
    })

def register_page(request):
    return render(request, 'chat/register.html')

@api_view(['POST'])
@permission_classes([AllowAny])  # Allow unauthenticated access
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def login_page(request):
    return render(request, 'chat/login.html')

@api_view(['POST'])
@permission_classes([AllowAny])  # Allow unauthenticated access
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        login(request, user)  # Log the user in
        return Response({"message": "Login successful"}, status=status.HTTP_200_OK)  # Send a JSON response
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def create_room_view(request):
    if request.method == 'POST':
        room_form = ChatRoomForm(request.POST)
        if room_form.is_valid():
            room = room_form.save()
            room.members.add(request.user)  # Automatically add the creator as a member
            return redirect('chat_home')  # Redirect to the home page
    else:
        room_form = ChatRoomForm()

    context = {'room_form': room_form}
    return render(request, 'chat/create_room.html', context)
@login_required
def user_list_view(request):
    users = User.objects.exclude(id=request.user.id)  # Exclude the logged-in user
    return render(request, "dm.html", {"users": users, "selected_user": None})

from django.shortcuts import render, get_object_or_404
from .models import User, PrivateMessage  # Adjust import based on your project structure

def user_list_view(request):
    users = User.objects.exclude(id=request.user.id)  # Exclude the logged-in user
    return render(request, "dm.html", {"users": users, "selected_user": None})


# views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q

# @login_required
# def direct_message_view(request, user_id=None):
#     """
#     Handle both the DM index and individual conversations.
#     If user_id is None, show the user list with no selected conversation.
#     If user_id is provided, show the conversation with that user.
#     """
#     users = User.objects.exclude(id=request.user.id)  # Get all users except the logged-in user
    
#     if user_id is None:
#         # No user selected - just show the user list
#         return render(request, "chat/dm.html", {
#             'messages': None,
#             'selected_user': None,
#             'users': users,
#         })
    
#     # Get the selected user and their messages
#     receiver = get_object_or_404(User, id=user_id)
    
#     # Get messages between current user and receiver
#     messages = PrivateMessage.objects.filter(
#         Q(sender=request.user, receiver=receiver) |
#         Q(sender=receiver, receiver=request.user)
#     ).order_by("timestamp")
    
#     return render(request, "chat/dm.html", {
#         'messages': messages,
#         'selected_user': receiver,
#         'users': users,
#     })


from django.core.cache import cache
# def direct_message_view(request, user_id=None):
#     """
#     Handle both the DM index and individual conversations.
#     If user_id is None, show the user list with no selected conversation.
#     If user_id is provided, show the conversation with that user.
#     """
#     # Get all users except the logged-in user
#     users = User.objects.exclude(id=request.user.id)  
    
#     # Get online users from cache
#     online_users = [int(key.split('_')[-1]) for key in cache.keys('user_status_*') if cache.get(key)]

#     if user_id is None:
#         # No user selected - just show the user list
#         return render(request, "chat/dm.html", {
#             'messages': None,
#             'selected_user': None,
#             'users': users,
#             'online_users': online_users,
#         })
    
#     # Get the selected user and their messages
#     receiver = get_object_or_404(User, id=user_id)
    
#     # Get messages between current user and receiver
#     messages = PrivateMessage.objects.filter(
#         Q(sender=request.user, receiver=receiver) |
#         Q(sender=receiver, receiver=request.user)
#     ).order_by("timestamp")
    
#     return render(request, "chat/dm.html", {
#         'messages': messages,
#         'selected_user': receiver,
#         'users': users,
#         'online_users': online_users,
#     })
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.cache import cache

def is_user_online(user_id):
    """Check if the user is online based on cache."""
    return cache.get(f'user_status_{user_id}', False)

def direct_message_view(request, user_id=None):
    """
    Handle both the DM index and individual conversations.
    If user_id is None, show the user list with no selected conversation.
    If user_id is provided, show the conversation with that user.
    """
    # Get all users except the logged-in user
    users = User.objects.exclude(id=request.user.id)  
    
    # Prepare a list of online users
    online_users = [user.id for user in users if is_user_online(user.id)]

    if user_id is None:
        # No user selected - just show the user list
        return render(request, "chat/dm.html", {
            'messages': None,
            'selected_user': None,
            'users': users,
            'online_users': online_users,
        })
    
    # Get the selected user and their messages
    receiver = get_object_or_404(User, id=user_id)
    
    # Get messages between current user and receiver
    messages = PrivateMessage.objects.filter(
        Q(sender=request.user, receiver=receiver) |
        Q(sender=receiver, receiver=request.user)
    ).order_by("timestamp")
    
    return render(request, "chat/dm.html", {
        'messages': messages,
        'selected_user': receiver,
        'users': users,
        'online_users': online_users,
    })
