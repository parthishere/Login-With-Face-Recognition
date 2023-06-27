import base64, cv2, io, boto3, urllib
import numpy as np
from PIL import Image
from django.conf import settings
from botocore.client import Config

import botocore
import botocore.session


def stringToImage(base64_string):
    imgdata = base64.b64decode(base64_string)
    return Image.open(io.BytesIO(imgdata))
     
def base64_encode(data):
    if data:
        return 'data:image/png;base64,' + data

import threading
import face_recognition
   
async def get_face_detect_data(file, details):
    img = cv2.imdecode(np.fromstring(file, np.uint8), cv2.IMREAD_UNCHANGED)
    print(details)
    # image_data, proceed_login = detectImageNew(img, details) # Execution time: 2.1410155296325684 seconds
    image_data, proceed_login = await detectImageNewThread(img, details) # 
    
    return image_data, proceed_login

def detectImageNew(frame, details):
    print(details)
    # s3_client = boto3.client('s3',
    #                      aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    #                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    #                      config=Config(signature_version='s3v4'),
    #                      region_name='ap-south-1'
    #                      )

    # url = s3_client.generate_presigned_url(ClientMethod='get_object', Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': f"media/{details['user'].image.name}"}, ExpiresIn=3600)
    # resp = urllib.request.urlopen(url)
    # image = np.asarray(bytearray(resp.read()), dtype="uint8")
    # image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    ####
    session = botocore.session.Session()

    s3_client = session.create_client(
        's3',
        region_name='ap-south-1',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        config=botocore.client.Config(signature_version='s3v4')
    )

    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    object_key = f"media/{details['user'].image.name}"
    image = None
    try:
        response = s3_client.get_object(
        Bucket=bucket_name,
        Key=object_key
        )
        image_data = response['Body'].read()

        # Decode image using OpenCV
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    except Exception as e:
        print(e)
    

    known_face_encoding = face_recognition.face_encodings(image)[0]
    
    username = details['username']
    unique_id = details['unique_id']
    
    known_face_name = f"{username}{unique_id}"
    
    
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(frame, model="hog")
    face_encodings = face_recognition.face_encodings(frame, face_locations, model="hog")
    
    login_proceed = False
    face_distances = None
    try:
        match = face_recognition.compare_faces(known_face_encoding, np.array(face_encodings), tolerance = 0.6)
        if match[0]:
            login_proceed = True

    except Exception as e:
        print("Some exception happened while comparing faces")
        print(e)
        pass

    for (top, right, bottom, left) in face_locations:
        # top *= 2  # Rescale face locations back to original frame size
        # right *= 2
        # bottom *= 2
        # left *= 2

        if login_proceed:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, known_face_name, (left, top), font, 0.8, (255, 255, 255), 1)
        else:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, 'Unknown', (left, top), font, 0.8, (255, 255, 255), 1)

    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    return frame, login_proceed

##########################################################################################################

async def detectImageNewThread(frame, details):
    print(details)
    session = botocore.session.Session()

    s3_client = session.create_client(
        's3',
        region_name='ap-south-1',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        config=botocore.client.Config(signature_version='s3v4')
    )

    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    object_key = f"media/{details['user'].image.name}"
    image = None
    try:
        response = s3_client.get_object(
        Bucket=bucket_name,
        Key=object_key
        )
        image_data = response['Body'].read()

        # Decode image using OpenCV
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

      
    except Exception as e:
        print(e)

    known_face_encoding = face_recognition.face_encodings(image)[0]
    
    username = details['username']
    unique_id = details['unique_id']
    
    known_face_name = f"{username}{unique_id}"
    
    
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)
    
    login_proceed = False
    face_distances = None

    def compare_faces_thread():
        nonlocal login_proceed, face_distances
        try:
            match = face_recognition.compare_faces(known_face_encoding, np.array(face_encodings), tolerance=0.6)
            if match[0]:
                login_proceed = True
            for (top, right, bottom, left) in face_locations:
                if login_proceed:
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(frame, known_face_name, (left, top), font, 0.8, (255, 255, 255), 1)
                else:
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(frame, 'Unknown', (left, top), font, 0.8, (255, 255, 255), 1)
        except Exception as e:
            print("Some exception happened while comparing faces")
            print(e)

    threads = []
    for _ in face_locations:
        t = threading.Thread(target=compare_faces_thread)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()


    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    return frame, login_proceed



        
     

