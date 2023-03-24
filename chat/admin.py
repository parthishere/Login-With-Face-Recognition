from django.contrib import admin

# Register your models here.
from .models import Thread, ChatMessage

admin.site.register(Thread)
admin.site.register(ChatMessage)
