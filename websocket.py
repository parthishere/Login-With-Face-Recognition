import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import socket
import os
import json
from ast import literal_eval

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'login_with_face.settings')
import django
django.setup()
from recognizer.models import User


class WSHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        self.user_id_ = self.get_secure_cookie("user")
        print("self.get_secure_cookie")
        print(self.user_id_)
        
        self.user_id = self.get_current_user()
        print("request")
        print(self.request)
        print ('new connection with tornado')
      
    def on_message(self, message):
        from recognizer.streamer import get_face_detect_data
        print(message)

        image_data = message
        # image_data , proceed_login, names, known_face_names = get_face_detect_data(message['message'], message['username'], message["unique_id"], False)
        print("recieved")
        
        if not image_data:
            image_data = message
        self.write_message(image_data)
        
 
    def on_close(self):
        print ('connection closed')
 
    def check_origin(self, origin):
        return True


application = tornado.web.Application([
    (r'/websocket', WSHandler),
], cookie_secret="L8LwECiNRxq2N0N2eGxx9MZlrpmuMEimlydNX/vt1LM=")
 
 
if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    myIP = socket.gethostbyname(socket.gethostname())
    print ('*** Websocket Server Started at %s***' % myIP)
    tornado.ioloop.IOLoop.instance().start()
    
    
    
# django celery beat
# redis
# celery
# eventlet
# celery -A login_with_face worker -l info -P eventlet