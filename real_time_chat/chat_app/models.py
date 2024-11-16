# chat_app/models.py
from django.db import models
from django.contrib.auth.models import User

class ChatRoom(models.Model):
    name = models.CharField(max_length=100, unique=True)
    members = models.ManyToManyField(User, related_name='chat_rooms')

    def __str__(self):
        return self.name

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username}: {self.content[:20]}'
from django.db import models
from django.contrib.auth.models import User

class PrivateMessage(models.Model):
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_messages", on_delete=models.CASCADE)
    content = models.TextField() 
    timestamp = models.DateTimeField(auto_now_add=True)
    attachment = models.FileField(upload_to='message_attachments/', null=True, blank=True)  # For file attachments

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver}"


class GameSession(models.Model):
    thinker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='games_as_thinker')
    is_active = models.BooleanField(default=True)
    secret_item = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Game by {self.thinker.username}"

class Question(models.Model):
    game_session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='questions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=500)
    answer = models.CharField(max_length=20, choices=[('Yes', 'Yes'), ('No', 'No'), ('I don\'t know', 'I don\'t know')], null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Question by {self.user.username}: {self.question_text}"
