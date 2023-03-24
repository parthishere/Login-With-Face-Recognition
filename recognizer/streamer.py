import base64, cv2, io, boto3, urllib
import time
import numpy as np
from PIL import Image
from django.conf import settings
from botocore.client import Config


def stringToImage(base64_string):
    imgdata = base64.b64decode(base64_string)
    return Image.open(io.BytesIO(imgdata))
     
def base64_encode(data):
    if data:
        return 'data:image/png;base64,' + data
    
def get_face_detect_data(file, details):
    img = cv2.imdecode(np.fromstring(file, np.uint8), cv2.IMREAD_UNCHANGED)
    print(details)
    image_data, proceed_login = detectImageNew(img, details)
    return image_data, proceed_login


import os
import face_recognition

def detectImageNew(frame, details):
    print(details)
    s3_client = boto3.client('s3',
                         aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                         aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                         config=Config(signature_version='s3v4'),
                         region_name='ap-south-1'
                         )

    url = s3_client.generate_presigned_url(ClientMethod='get_object', Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': f"media/{details['user'].image.name}"}, ExpiresIn=3600)
    resp = urllib.request.urlopen(url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    

    known_face_encoding = face_recognition.face_encodings(image)[0]
    
    username = details['username']
    unique_id = details['unique_id']
    
    known_face_name = f"{username}{unique_id}"
    
    
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_location = face_recognition.face_locations(frame)
    face_encoding = face_recognition.face_encodings(frame, face_location)
    
    login_proceed = False
    try:
        match = face_recognition.compare_faces(known_face_encoding, np.array(face_encoding), tolerance = 0.6)
        face_distance = face_recognition.face_distance(known_face_encoding,face_encoding)
        
        if match[0] == True:
            login_proceed = True
        
    except Exception as e:
        print("Some exception happned while comparing faces")
        print(e)
        pass
    
    if login_proceed == False:
        for (top,right,bottom,left) in face_location:
        
            cv2.rectangle(frame, (left,top),(right,bottom), (0,0,255), 2)
            
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, 'Unknown', (left, top), font, 0.8, (255,255,255),1)
            login_proceed = False
    else:
        for (top,right,bottom,left) in face_location:
    

            cv2.rectangle(frame, (left,top),(right,bottom), (0,255,0), 2)

            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, known_face_name, (left, top), font, 0.8, (255,255,255),1)
            login_proceed = True
    
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    return frame, login_proceed



def detectImageOld(frame, details):

    print("start")
    
    known_face_encodings = []
    known_face_names = []

    base_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.getcwd()
    image_dir = os.path.join(base_dir,"{}/{}/{}/{}".format('media','User_images', details['college'], details['branch'], details['gender']))
    print("image directory for recognizing"+str(image_dir))
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

    print("Fnown face names from files in image dir"+str(known_face_names))

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
        except Exception as e:
            print("Some exception happned while comparing faces")
            print(e)
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
            print("valid !!")
            print(names)
            print(str(details['username']+details['unique_id']))
            print(str(details['username']+details['unique_id']) in names)
            if str(details['username']+details['unique_id']) in names or details['superuser']:
                proceed_login = True
            else:
                proceed_login = False
    
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    
    return frame, proceed_login

