import cv2
import face_recognition
import os
import numpy as np
import socket
import struct
from io import BytesIO



def recognizer(details, username, unique_id):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 8080))
    
    known_face_encodings = []   # User uploaded image's encodings
    known_face_locations = []   # User uploaded image's locations
    known_face_lables = []      # User uploaded image's lables
    
    video_face_encodings = []   # video capture ma je malya e face nu encoding
    video_face_locations = []   # video capture ma je malya e face nu encoding
    
    je_video_ma_malya_enu_naam = []  # not repetative & return ready
    face_names = []  # repetative
    
    best_match_index = None
    
    proceed_login = False
    
    # ----------------------------------------------------------------------- #
    
    base_dir = os.path.dirname(os.path.abspath('__file__'))
	
    base_dir = os.getcwd() # ek pachal

    image_dir = os.path.join(base_dir,"{}\{}\{}".format('media','User_images',details['gender']))
    
        

    for root, dirs, files in os.walk(image_dir):
        for file in files:
            if file.endswith('jpg') or file.endswith('png'):
                path = os.path.join(root, file)  # file no path 
                img = face_recognition.load_image_file(path)
                
                known_lable = file[:len(file)-4]
                known_face_lables.append(known_lable)  # janita face na lable taiyar
                
                known_location = face_recognition.face_locations(img, model='hog')
                known_face_locations.append(known_location)
                
                known_encoding = face_recognition.face_encodings(img, known_location)
                if not len(known_encoding):
                    print(known_lable, "can't be encoded")
                    continue
                else:
                    known_face_encodings.append(known_encoding[0])  # janita face na encodings taiyar
    
    # ----------------------------------------------------------------------- #
                
    print('known_face_encodings')
    print(known_face_encodings)
    # video par kaam chalu
    # try:
    #     cap = cv2.VideoCapture(0)   #start the video camera
    # except:
    try:
        cap = cv2.VideoCapture(0)
    except: 
        return print("nothing  found")
    
    # width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    # height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    while True:
        
        ret, frame = cap.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        if ret:
            
            video_face_location = face_recognition.face_locations(frame)
            video_face_encoding = face_recognition.face_encodings(frame,
                                        video_face_location
                                    )
            if len(video_face_encoding) == 0:
                print("video_face_encoding can't be encoded")
                continue
            else:
                video_face_encoding = video_face_encoding
            
            print(video_face_encoding)
            for face_encoding in video_face_encoding:

                matches = face_recognition.compare_faces(known_face_encodings, np.array(face_encoding), tolerance = 0.6)

                face_distances = face_recognition.face_distance(known_face_encodings,face_encoding)	
                
                try:
                    matches = face_recognition.compare_faces(known_face_encodings, np.array(face_encoding), tolerance = 0.6)

                    face_distances = face_recognition.face_distance(known_face_encodings,face_encoding)
                    best_match_index = np.argmin(face_distances)

                    if matches[best_match_index]:
                        name = known_face_lables[best_match_index]
                        face_names.append(name)
                        if name not in je_video_ma_malya_enu_naam:
                            je_video_ma_malya_enu_naam.append(name)
                except:
                    pass
                
            # jo video ma thobdu malyu pan verified nathi to
            if len(face_names) == 0:
                for (top, right, bottom, left) in video_face_locations:
                    
                    # top*=2
                    # right*=2
                    # bottom*=2
                    # left*=2
                    
                    cv2.rectangle(frame, (left,top),(right,bottom), (0,0,255), 2)

                    # cv2.rectangle(frame, (left, bottom - 30), (right,bottom - 30), (0,255,0), -1)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(frame, 'Unknown', (left, top), font, 0.8, (255,255,255),1)
                    proceed_login = False
                    
            #jo video ma thobdu malyu ane verified 6e
            else:
                for (top, right, bottom, left), name in video_face_locations, je_video_ma_malya_enu_naam:
                    
                    # top*=2
                    # right*=2
                    # bottom*=2
                    # left*=2
                    cv2.rectangle(frame, (left,top),(right,bottom), (0,0,255), 2)

                    # cv2.rectangle(frame, (left, bottom - 30), (right,bottom - 30), (0,255,0), -1)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(frame, name , (left, top), font, 0.8, (255,255,255),1)
                    if (username+unique_id) in name:
                        proceed_login = True
                    else:
                        proceed_login = False
        
                    
                   
    # ----------------------------------------------------------------------- #
            
            # chalo have video batai do....
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            memfile = BytesIO()
            np.save(memfile, frame)
            memfile.seek(0)
            data = memfile.read()

            # Send form byte array: frame size + frame content
            client_socket.sendall(struct.pack("L", len(data)) + data)
            
            cv2.imshow("Face Recognition Panel", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    # stop everything and destroy all windows
    cap.release()
    cv2.destroyAllWindows()
    
    print(je_video_ma_malya_enu_naam, known_face_lables, proceed_login)
    return je_video_ma_malya_enu_naam, known_face_lables, proceed_login
    
# ----------------------------------------------------------------------- #
# ----------------------------------------------------------------------- #
# ----------------------------------------------------------------------- #
# ----------------------------------------------------------------------- #
# ----------------------------------------------------------------------- #
# ----------------------------------------------------------------------- #
# ----------------------------------------------------------------------- #
# ----------------------------------------------------------------------- #

def Recognizer(img, details, username, unique_id):
    threshold = 0
    threshold_for_unknown = 0
    def destroy_recognizer(self):
            cv2.destroyAllWindows()
    
    # javascript no video ahiya lavvano
    print("start")
    try:
        video = cv2.VideoCapture(0)
    except:
        try:
            video = cv2.VideoCapture(1)
        except:
            video = cv2.VideoCapture(2)
            
    print("cam start")
    known_face_encodings = []
    known_face_names = []


    cv2.imshow("image",img)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.getcwd()
    image_dir = os.path.join(base_dir,"{}\{}".format('media','User_images'))

    names = []
    proceed_login = False


    for root,dirs,files in os.walk(image_dir):
        for file in files:
            if file.endswith('jpeg') or file.endswith('png') or file.endswith('jpg'):
                path = os.path.join(root, file)
                img = face_recognition.load_image_file(path)
                label = file[:len(file)-4]
                img_encoding = face_recognition.face_encodings(img)[0]
                known_face_names.append(label)
                known_face_encodings.append(img_encoding)

    face_locations = []
    face_encodings = []

    
    try:
        while True:	

            check, frame = video.read()
            try:
                small_frame = cv2.resize(frame, (0,0), fx=0.5, fy= 0.5, interpolation=cv2.INTER_AREA)
            except:
                break
        
            rgb_small_frame = small_frame[:,:,::-1]

            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            face_names = []

            for face_encoding in face_encodings:

                matches = face_recognition.compare_faces(known_face_encodings, np.array(face_encoding), tolerance = 0.6)

                face_distances = face_recognition.face_distance(known_face_encodings,face_encoding)	
                
                try:
                    matches = face_recognition.compare_faces(known_face_encodings, np.array(face_encoding), tolerance = 0.6)

                    face_distances = face_recognition.face_distance(known_face_encodings,face_encoding)
                    best_match_index = np.argmin(face_distances)

                    if matches[best_match_index]:
                        name = known_face_names[best_match_index]
                        print("name:"+name)
                        face_names.append(name)
                        if name not in names:
                            names.append(name)
                            print("name array:"+names)
                except:
                    pass

            if len(face_names) == 0:
                for (top,right,bottom,left) in face_locations:
                    top*=2
                    right*=2
                    bottom*=2
                    left*=2

                    cv2.rectangle(frame, (left,top),(right,bottom), (0,0,255), 2)

                    # cv2.rectangle(frame, (left, bottom - 30), (right,bottom - 30), (0,255,0), -1)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(frame, 'Unknown', (left, top), font, 0.8, (255,255,255),1)
                    proceed_login = False
                    threshold_for_unknown += 10
                    if threshold_for_unknown >= 100:
                        raise StopIteration
            else:
                for (top,right,bottom,left), name in zip(face_locations, face_names):
                    top*=2
                    right*=2
                    bottom*=2
                    left*=2

                    cv2.rectangle(frame, (left,top),(right,bottom), (0,255,0), 2)

                    # cv2.rectangle(frame, (left, bottom - 30), (right,bottom - 30), (0,255,0), -1)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(frame, name, (left, top), font, 0.8, (255,255,255),1)
                    print(username+unique_id)
                    if str(username+unique_id) in name:
                        proceed_login = True
                        print('will break')
                        threshold += 2
                        if threshold >= 10:
                            raise StopIteration
                    else:
                        proceed_login = False
            
            cv2.imshow("Face Recognition Panel",frame)
            # ret, jpeg = cv2.imencode('.jpg', frame)

            if cv2.waitKey(1) == ord('q'):
                break
        
    except StopIteration:
        pass
    video.release()
    cv2.destroyAllWindows()
    print(names, known_face_names, proceed_login)
    # print(jpeg.tobytes())
    return (names, known_face_names, proceed_login) #jpeg.tobytes())

from imutils.video import VideoStream
from imutils.video import FPS
import imutils

class RecognizerClass(object):
    
    def __init__(self, details=None, username=None, unique_id=None):
        self.threshold = 0
        self.threshold_for_unknown = 0
        
        self.username = username
 
        self.unique_id = unique_id
        self.details = details
        self.proceed_login = False
        
        
        ###################################
        


        self.known_face_encodings = []
        self.known_face_names = []

        # base_dir = os.path.dirname(os.path.abspath(__file__))
        # image_dir = os.path.join(base_dir, "static")
        # image_dir = os.path.join(image_dir, "profile_pics")

        # base_dir = os.getcwd()
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # os.chdir("..")
        base_dir = os.getcwd()
        image_dir = os.path.join(base_dir,"{}\{}".format('media','User_images'))
        # print(image_dir)
        self.names = []
        self.proceed_login = False


        for root,dirs,files in os.walk(image_dir):
            for file in files:
                if file.endswith('jpeg') or file.endswith('jpg') or file.endswith('png'):
                    path = os.path.join(root, file)
                    img = face_recognition.load_image_file(path)
                    label = file[:len(file)-4]
                    img_encoding = face_recognition.face_encodings(img)[0]
                    self.known_face_names.append(label)
                    self.known_face_encodings.append(img_encoding)

        self.face_locations = []
        self.face_encodings = []
        
        self.video = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        self.vs = VideoStream(src=0).start()
        self.fps = FPS().start()
        
    def __del__(self):
        self.video.release()
        cv2.destroyAllWindows()
        # self.check_login_proceed()
        

    def get_frame(self):
        
        try:
            self.frame = self.vs.read()
            frame = cv2.flip(frame,1)
            # ret, self.frame = self.video.read()
            try:
                small_frame = cv2.resize(self.frame, (0,0), fx=0.5, fy= 0.5, interpolation=cv2.INTER_AREA)
            except:
                pass

            rgb_small_frame = small_frame[:,:,::-1]

            self.face_locations = face_recognition.face_locations(rgb_small_frame)
            self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)
            self.face_names = []


            for face_encoding in self.face_encodings:

                matches = face_recognition.compare_faces(self.known_face_encodings, np.array(face_encoding), tolerance = 0.6)

                face_distances = face_recognition.face_distance(self.known_face_encodings,face_encoding)	
                
                try:
                    matches = face_recognition.compare_faces(self.known_face_encodings, np.array(face_encoding), tolerance = 0.6)

                    face_distances = face_recognition.face_distance(self.known_face_encodings,face_encoding)
                    best_match_index = np.argmin(face_distances)

                    if matches[best_match_index]:
                        name = self.known_face_names[best_match_index]
                        self.face_names.append(name)
                        if name not in self.names:
                            self.names.append(name)
                except:
                    pass

            if len(self.face_names) == 0:
                for (top,right,bottom,left) in self.face_locations:
                    top*=2
                    right*=2
                    bottom*=2
                    left*=2

                    cv2.rectangle(self.frame, (left,top),(right,bottom), (0,0,255), 2)

                    # cv2.rectangle(frame, (left, bottom - 30), (right,bottom - 30), (0,255,0), -1)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(self.frame, 'Unknown', (left, top), font, 0.8, (255,255,255),1)
                    self.proceed_login = False
                    self.threshold_for_unknown += 1
                    print('will break')
                    if self.threshold_for_unknown >= 10:
                        raise StopIteration
            else:
                for (top,right,bottom,left), name in zip(self.face_locations, self.face_names):
                    top*=2
                    right*=2
                    bottom*=2
                    left*=2

                    cv2.rectangle(self.frame, (left,top),(right,bottom), (0,255,0), 2)

                    # cv2.rectangle(frame, (left, bottom - 30), (right,bottom - 30), (0,255,0), -1)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(self.frame, name, (left, top), font, 0.8, (255,255,255),1)
                    if (self.username+self.unique_id) in name:
                        self.proceed_login = True
                        print('will break')
                        self.threshold += 1
                        if self.threshold >= 5:
                            raise StopIteration
                    else:
                        self.proceed_login = False
                        
            
            # cv2.imshow('frame', self.frame)
            ret, jpeg = cv2.imencode('.jpg', self.frame)
            self.fps.update()
            # if cv2.waitKey(0) & 0xFF == ord('q'):
                
                
            
            return (self.names, self.known_face_names, self.proceed_login, jpeg.tobytes(), False)
        except:
            self.video.release()
            cv2.destroyAllWindows()
            return None, None, None, None, True

