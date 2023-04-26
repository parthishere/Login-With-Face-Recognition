# Project Title

this decentralized attendance system uses facial recognition technology and Django framework. It's easy to use, accurate, and can be used in schools and industries. You only need a camera and internet connection to use it. The interface is customizable and provides real-time tracking, reporting, and analytics. It's scalable and easy to add new users, devices, and locations. It's a modern solution for attendance tracking!

you can see the dependancies in the requirements.txt file


## Documentation

### Attendance
Once the system is trained, it prompts the user to log in by showing them their live video feed on the screen. The system captures an image of the user's face from the video feed and uses it to compare against the encoding generated during the training phase.

### Face Recognition
The face recognition algorithm uses a pre-trained model to identify and recognize the face in the captured image. If the system recognizes the face, it logs the user into the system.

### User Management
Uses customizable user managment for flexibility in colleges and commercial use

### Flow of the code
The flow of the code starts by importing the required libraries, then it trains the system by loading the images from the 'images' directory and encoding them to create a facial recognition model. Once the system is trained, it initializes the camera and captures the live video feed. It then captures an image of the user's face from the video feed, encodes it, and compares it against the facial recognition model. If the user is authorized, the system logs them into the system. Otherwise, it prompts the user to try again or exits the system.

### Features
 
 0. local ip and gps detaction for the physical attendance
 1. Mass User creation with excel sheet
 2. Fully working teacher dashboard 
 3. Lecture and session Management, Sessions can be seen from dashboard
 4. Download overall attendace, session attendance, lecture attendance
 5. User profile page
 6. user can search the lectures send request to teache for joining the lecture
 7. teacher can enable and disable the lecture according to need and that will create another session for the lecture
 8. lectue,session management tools
 9. search teacher and lecture in the same college
 10. (working) send message to contact the student or teacher
 11. teacher can take attendance and also change the attendance
 

 ### Why it is full (fool) proof

 1. it uses local ip and gps to determine the location of the student
 2. Teacher can randomly start the  session and take attendace, also this session will automaticaly stop after some predefined time
 3. uses face recognition to check the student's avability
 4. student can't change the profile photo after updating it once / only teacher can change the photo


 ## API
 you can find apis for the code in /api route
## Run Locally with django

Install and run the project without docker with dango

```bash
  git clone https://github.com/parthishere/Login-With-Face-Recognition
```

Go to the project directory

```bash
  cd Login-With-Face-Recognition
```

Install dependencies and Start the server

```bash
  pip install -r requirements.txt
  
  python manage.py makemigrations
  python manage.py migrate
  python manage.py runserver 0.0.0.0:8000
```
install redis and start the worker
```bash
celery -A login_with_face worker -l info
```
## Run Locally with docker

Clone the project

```bash
  git clone https://github.com/parthishere/Login-With-Face-Recognition
```

Go to the project directory

```bash
  cd Login-With-Face-Recognition
```

Install dependencies and Start the server

```bash
  docker-compose up --build
```