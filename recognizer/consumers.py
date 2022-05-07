import json
from channels.generic.websocket import AsyncWebsocketConsumer
from recognizer.streamer import get_face_detect_data


class AsyncStreamConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        await self.accept()
        print('new connection with websocket')
      
    async def receive(self, text_data): 
        message = text_data
        user = self.scope['user']
        # print(user.user_profile.all())
        image_data , proceed_login, names, known_face_names = get_face_detect_data(message, user.username, "pnfx2afegtr9", False)
        print("recieved data")
        # print(image_data)
        if not image_data:
            image_data = message
        print("sending  ")
        await self.send(json.dumps({
                "message":image_data}))
        await self.disconnect()

 
    async def disconnect(self):
        print ('connection closed')
        
        