from channels.consumer import AsyncConsumer
from concurrent.futures import thread
from .models import Thread
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db.models import Count, F, Value
from channels.db import database_sync_to_async
from .models import ChatMessage, Thread
from django.contrib.auth import get_user_model
from channels.exceptions import StopConsumer

User = get_user_model()


class ChatConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        print('connected', event)
        thread_id = self.scope['thread_id']
        chat_room_name = f'user_chatroom_{thread_id}'
        self.chat_room_name = chat_room_name
        await self.channel_layer.group_add(
            chat_room_name,
            self.channel_name
        )
        await self.send({
            'type': 'websocket.accept'
        })

    async def websocket_receive(self, event):
        print('receive', event)
        received_data = json.loads(event['text'])
        msg = received_data.get('message')
        sent_by_id = received_data.get('sent_by')
        send_to_id = received_data.get('send_to')
        thread_id = received_data.get('thread_id')

        if not msg:
            print('Error:: empty message')
            return False

        sent_by_user = await self.get_user_object(sent_by_id)
        send_to_user = await self.get_user_object(send_to_id)
        thread_obj = await self.get_thread(thread_id)
        if not sent_by_user:
            print('Error:: sent by user is incorrect')
        if not send_to_user:
            print('Error:: send to user is incorrect')
        if not thread_obj:
            print('Error:: Thread id is incorrect')

        await self.create_chat_message(thread_obj, sent_by_user, msg)

        response = {
            'message': msg,
            'sent_by': sent_by_id,
            'sent_to': send_to_id,
            'thread_id': thread_id
        }

        await self.channel_layer.group_send(
            self.chat_room,
            {
                'type': 'chat_message',
                'text': json.dumps(response)
            }
        )

    async def websocket_disconnect(self, event):
        print('disconnect', event)
        self.channel_layer.group_discard(
            self.chat_room_name,
            self.channel_name
        )
        raise StopConsumer()

    async def chat_message(self, event):
        print('chat_message', event)
        await self.send({
            'type': 'websocket.send',
            'text': event['text']
        })

    @database_sync_to_async
    def get_user_object(self, user_id):
        qs = User.objects.get(id=user_id)
        if qs.exists():
            obj = qs
        else:
            obj = None
        return obj

    @database_sync_to_async
    def get_thread(self, thread_id):
        qs = Thread.objects.get(id=thread_id)
        if qs.exists():
            obj = qs
        else:
            obj = None
        return obj

    @database_sync_to_async
    def create_chat_message(self, thread, user, msg):
        ChatMessage.objects.create(thread=thread, user=user, message=msg)


class notificationConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        user = self.scope['user']
        await self.send({
            'type': 'websocket.accept'
        })

    async def websocket_message(self, event):
        pass

    async def websocket_close(self, event):
        print("closed ", event)

# class ChatConsumer(AsyncWebsocketConsumer):

#     async def connect(self):
#         self.thread_id = self.scope['url_route']['kwargs']['thread_id']
#         self.room_group_name = "chat_%s"%self.thread_id
#         print(self.thread_id)
#         # thread = await self.get_thread(self.thread_id)
#         # print(thread)

#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )

#         await self.accept()


#     async def disconnect(self, code):
#         print(code)
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )


#     async def receive(self, text_data=None, bytes_data=None):
#         # text_data = json.loads(text_data)
#         print(text_data)
#         # text_data = json.dumps(text_data)
#         self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 "type":"chat_message",
#                 "message":text_data
#             }
#         )

#     async def chat_message(self, event):
#         message = event["message"]

#         await self.send(text_data=json.dumps({
#             "message":message
#         }))

#     @database_sync_to_async
#     def get_thread(self, id):
#         return Thread.objects.get(id=self.thread_id)
