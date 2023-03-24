from difflib import context_diff
from .models import Thread, ChatMessage
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from .forms import GroupForm

User = get_user_model()

# Create your views here.
def on_message(request, pk=None):
    to_user = User.objects.get(pk=pk)
    from_user = request.user
    tobj = Thread.objects.get_or_create(first_person=to_user, second_person=from_user)
    
    return redirect(reverse("chat:chat-page", kwargs={'thread_pk':tobj.pk}))

@login_required
def all_messages_page(request):
    threads = Thread.objects.by_user(user=request.user).prefetch_related('chatmessage_thread').order_by('timestamp')
    context = {
        'Threads': threads
    }
    return render(request, 'chat/chat.html', context)


@login_required
def chat_page(request, thread_pk):
    context = {}
    thread = Thread.objects.prefetch_related('chatmessage_thread').order_by('timestamp').get(pk=thread_pk)
    context['thread'] = thread
    return render(request, "chat/chat-page.html", context)
  
  
  
def make_group(request):
    context = {}
    form = GroupForm(request.POST or None)
    context['form'] = form
    
    if request.POST and form.is_valid():
        obj = form.save()
        return redirect("chat:chat-page", kwargs={"thread_pk":obj.pk})
    

    
    