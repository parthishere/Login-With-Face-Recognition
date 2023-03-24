from django.urls import path

from .views import all_messages_page, chat_page, make_group, on_message, all_messages_page

app_name = "chat"

urlpatterns = [
    path('get-thread/<int:pk>/', on_message, name="on-msg"),
    path("home/", all_messages_page, name="home"),
    path('chat/<int:thread_pk>/', chat_page, name="chat-page"),
    path('make-grp/', make_group, name="make-grp"),
]
