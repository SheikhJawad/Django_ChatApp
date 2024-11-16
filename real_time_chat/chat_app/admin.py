from django.contrib import admin
from .models import*
admin.site.register(ChatRoom)
admin.site.register(Message)
admin.site.register(PrivateMessage)
admin.site.register(GameSession)
admin.site.register(Question)

