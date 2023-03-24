from dataclasses import field
from threading import Thread
from django import forms 
from .models import ChatMessage, Thread

class GroupForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = "__all__"
        
class ChatForm(forms.ModelForm):
    class Meta:
        model = ChatMessage
        fields = "__all__"
        
        