import base64
import cv2
import numpy as np

def base64_decode(data):
    out=base64.decodestring(data.split(',')[1].encode())
    return out
     
def base64_encode(data):
    if data:
        return 'data:image/png;base64,' + data
    
def get_face_detect_data(file, details):
    img = cv2.imdecode(np.fromstring(file, np.uint8), cv2.IMREAD_UNCHANGED)
    image_data, proceed_login, names, known_face_names = detectImage(img, details)

    return image_data, proceed_login, names, known_face_names


import os
import face_recognition


def detectImage(frame, details):
    
    print("start")
    
    known_face_encodings = []
    known_face_names = []

    base_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.getcwd()
    image_dir = os.path.join(base_dir,"{}\{}\{}\{}".format('media','User_images', details['college'], details['branch'], details['gender']))

    names = []
    proceed_login = False

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
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

    # print(known_face_names)

    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)
    face_names = []
    
    
    for face_encoding in face_encodings:

        try:
            matches = face_recognition.compare_faces(known_face_encodings, np.array(face_encoding), tolerance = 0.6)

            face_distances = face_recognition.face_distance(known_face_encodings,face_encoding)
            best_match_index = np.argmin(face_distances)
            
            if matches[best_match_index]:
                name = known_face_names[best_match_index]
                face_names.append(name)
                if name not in names:
                    names.append(name)
                    # print("name array:"+names)
        except:
            pass

    if len(face_names) == 0:
        for (top,right,bottom,left) in face_locations:

            cv2.rectangle(frame, (left,top),(right,bottom), (0,0,255), 2)
            
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, 'Unknown', (left, top), font, 0.8, (255,255,255),1)
            proceed_login = False
    else:
        for (top,right,bottom,left), name in zip(face_locations, face_names):


            cv2.rectangle(frame, (left,top),(right,bottom), (0,255,0), 2)

            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left, top), font, 0.8, (255,255,255),1)
            if str(details['username']+details['unique_id']) in name or details['superuser']:
                proceed_login = True
            else:
                proceed_login = False
    
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    
    return frame, proceed_login, names, known_face_names



# def detectImageForSuperUser(frame, details):