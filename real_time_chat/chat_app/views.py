
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import *
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import login
from .serializers import RegisterSerializer, LoginSerializer
from rest_framework.permissions import AllowAny
from django.contrib.auth.decorators import login_required 
from.forms import*
from django.db.models import Q
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt



@login_required 
def chat_home(request):
    rooms = ChatRoom.objects.all()  
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
@permission_classes([AllowAny]) 
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def login_page(request):
    return render(request, 'chat/login.html')

@api_view(['POST'])
@permission_classes([AllowAny])  
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        login(request, user) 
        return Response({"message": "Login successful"}, status=status.HTTP_200_OK)  
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def create_room_view(request):
    if request.method == 'POST':
        room_form = ChatRoomForm(request.POST)
        if room_form.is_valid():
            room = room_form.save()
            room.members.add(request.user)  
            return redirect('chat_home')  
    else:
        room_form = ChatRoomForm()

    # Get all users for the user list
    users = User.objects.all()
    # Get online users (you can modify this based on your user tracking method)
    online_users = [request.user.id]  # Currently logged in user will show as online

    context = {
        'room_form': room_form,
        'users': users,
        'online_users': online_users
    }
    return render(request, 'chat/create_room.html', context)
@login_required
def user_list_view(request):
    users = User.objects.exclude(id=request.user.id)  #
    return render(request, "dm.html", {"users": users, "selected_user": None})



def user_list_view(request):
    users = User.objects.exclude(id=request.user.id)  
    return render(request, "dm.html", {"users": users, "selected_user": None})




def is_user_online(user_id):
    """Check if the user is online based on cache the cache is comming from
    Redis."""
    return cache.get(f'user_status_{user_id}', False)

def direct_message_view(request, user_id=None):
    users = User.objects.exclude(id=request.user.id)  
  
    online_users = [user.id for user in users if is_user_online(user.id)]

    if user_id is None:
   
        return render(request, "chat/dm.html", {
            'messages': None,
            'selected_user': None,
            'users': users,
            'online_users': online_users,
        })
    

    receiver = get_object_or_404(User, id=user_id)
    

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
def get_user_status(request, user_id):
  
    status = cache.get(f'user_status_{user_id}', 'offline')
    return JsonResponse({'status': status})



@login_required
def start_game(request):
    if request.method == 'POST':
        secret_item = request.POST.get('secret_item')
        if secret_item:
            game_session = GameSession.objects.create(thinker=request.user, secret_item=secret_item)
            return redirect('game_detail', game_id=game_session.id)
    return render(request, 'chat/start_game.html')




@csrf_exempt
@login_required
def game_detail(request, game_id):
    game_session = get_object_or_404(GameSession, id=game_id)
    questions = Question.objects.filter(game_session=game_session).order_by('created_at')

    if request.method == 'POST':
        if 'ask_question' in request.POST:
            question_text = request.POST.get('question_text')
            if question_text and len(questions) < 20:
                Question.objects.create(game_session=game_session, user=request.user, question_text=question_text)
                return redirect('chat/game_detail', game_id=game_id)
        
        elif 'answer_question' in request.POST:
            question_id = request.POST.get('question_id')
            answer = request.POST.get('answer')
            question = get_object_or_404(Question, id=question_id)
            if question and game_session.thinker == request.user:
                question.answer = answer
                question.save()
                return redirect('chat/game_detail', game_id=game_id)

    context = {
        'game_session': game_session,
        'questions': questions,
        'user': request.user,
        'playing_user': game_session.thinker,  # Add this line to show the game player
    }
    return render(request, 'chat/game_detail.html', context)


from django.shortcuts import render
from .models import GameSession

def active_games(request):
    active_game_sessions = GameSession.objects.filter(is_active=True)
    context = {
        'active_game_sessions': active_game_sessions
    }
    return render(request, 'chat/active_game.html', context)
