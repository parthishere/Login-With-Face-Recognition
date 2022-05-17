from rest_framework.views import APIView
from django.shortcuts import reverse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.http.response import JsonResponse
from django.core.files.base import ContentFile
import cv2
from sklearn import datasets
from recognizer.streamer import get_face_detect_data
from login_details.models import LoginDetails
from django.contrib.auth import (
    login,
    authenticate,
    logout
)


from recognizer.models import UserProfile, TeacherProfileModel, LectrueModel, ChangeWebsiteCount, User

from .serializers import UserProfileSerializer, TeacherProfileSerializer, ChangeWebsiteCountSerailizer, UserSeraializer


class FormSubmit(APIView):
    """
    View to list all users in the system.

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        """
        post request
        """
        
        file = request.data.get('image_file').read()  # src is the name of input attribute in your html file, this src value is set in javascript code
        teacher = request.data.get('teacher')
        lecture = request.data.get('lecture')
        user_ip = request.data.get('client_ip')
        

        teacher_user = TeacherProfileModel.objects.get(id=teacher)
            
        allowed_ips = []

        if teacher_user.ip1:
            allowed_ip_host = ".".join(teacher_user.ip1.split('.')[0:3])
            allowed_masks = (".{}".format(i) for i in range(256))
            for mask in allowed_masks:
                allowed_ips.append(str(allowed_ip_host)+str(mask))
         
        if teacher_user.ip2:   
            allowed_ip_host = ".".join(teacher_user.ip2.split('.')[0:3])
            allowed_masks = (".{}".format(i) for i in range(256)) 
            for mask in allowed_masks:
                allowed_ips.append(str(allowed_ip_host)+str(mask))

        
        lecture_object = LectrueModel.objects.get(id=lecture)
        
        try:
            o = teacher_user.change_website_objects.all().count()
            c  = ChangeWebsiteCount.objects.filter(teacher=teacher_user).order_by('id').last()

        except:
            o = 0
  
        if o == 0:
            print("no objects")
        
        if not user_ip in allowed_ips:
            if (teacher_user.ip1 is None and teacher_user.ip2 is None):
                pass
            else:
                data ={
                    'message' : "Your IP is not in same subnet IPs",
                    'login_proceed' : False
                }
                url = reverse('recognizer:home')
                return JsonResponse(status = 302 , data = {'success' : url, 'data' : data })
        
        if o%2==0:

            try:
                user = UserProfile.objects.get(user=request.user)
                
                gender = user.gender
                details = {
                'gender':gender,
                'college':user.college,
                'branch':user.branch,
                'username':user.user.username,
                'unique_id':user.unique_id,
                'user':user,
                'superuser':request.user.is_superuser,
                'image':user.image,
                }

            except Exception as e:
                details = None
            
            frame, login_proceed, names, known_face_names = get_face_detect_data(file, details)
            ret, buf = cv2.imencode('.jpg', frame)
            image = ContentFile(buf.tobytes())
            if login_proceed:
                data = {
                    'login_proceed' : True
                }
                user.login_proceed = login_proceed
                
                instance = LoginDetails.objects.create(user=request.user, lecture=lecture_object, teacher=teacher_user, enrollment_number=user.enrollment_number)
                instance.processed_img.save("output.jpg", image)
                
                user.save()
                
                
                data['message'] = f'Your face was recognized as {request.user.username} - {user.enrollment_number}'
                url = reverse('recognizer:home')
                
                return JsonResponse(status = 302 , data = {'success' : url })
            else:
                data = {
                    'login_proceed' : False
                }
                user.login_proceed = login_proceed
                user.save()
                

                data['message'] = 'Face not recognized !'
                url = reverse('recognizer:home')
                return JsonResponse(status = 302 , data = {'success' : url, 'data' : data })
        else:
            data = {
                    'login_proceed' : False,
                    'message': f"Session hasn't started by {teacher_user.user.username}, Can't take attendance"
            }
            url = reverse('recognizer:home')
                
            return JsonResponse(status = 302 , data = {'success' : url , 'data': data})




class SignUPView(APIView):
    """
    View to list all users in the system.

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsStaff]
    
    def post(self, request, format=None):
        username = request.data.get('username')
        email = request.data.get('email') or None
        password = request.data.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is None:
            user = User.objects.create(username=username, email=email)
            user.set_password(password)
            user.save()
            
            message = "Sign up Sucsessful"
            data = {
                'message':message
            }
            user_profile = UserProfile.objects.get(user=user, data=data)
            
            return JsonResponse(status=302)
        else:
            messages = 'User already exists!'
            data = {
                'message':message
            }
            return JsonResponse(status=302, data=data)



class LogInView(APIView):
    """
    View to list all users in the system.

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    
    def post(self, request, format=None):
        username = request.data.get('username')
        password= request.data.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user=user)
            message = 'login sucsessful!'
            data = {
                'messgage':message,
            }
            uqid = get_uqid(request)
            request.session['uqid'] = uqid
            
            request.session['user_pk'] = UserProfile.objects.get(user=user).pk
            
            
            user_profile = UserProfile.objects.get(user=user)

                
            if user_profile.updated:
                url =  reverse('recognizer:home')
                return JsonResponse(status=302, data=data)
            else:
                
                url = reverse('recognizer:update-profile', kwargs={'pk': user_profile.pk})
                return JsonResponse(status=302, data=data)


def get_uqid(request):
    user = UserProfile.objects.get(user=request.user)
    return user.unique_id


@api_view(['POST'])
def change_whole_site_by_clicking(request):
    if request.method == 'POST':
        if request.user.is_staff or request.user in request.user.teacher_profile.all():
            teacher = request.user.teacher_profile.all().last()

            if ChangeWebsiteCount.objects.filter(teacher=teacher).count() % 2 == 0:
                c = ChangeWebsiteCount.objects.create(teacher=teacher)
                change_site_count = ChangeWebsiteCount.objects.filter(teacher=teacher).count()
                
            else:
                c = ChangeWebsiteCount.objects.create(teacher=teacher)
                change_site_count = ChangeWebsiteCount.objects.filter(teacher=teacher).count()
                
                
            return JsonResponse(status=302, data={})
        else:
            return JsonResponse(status=302, data={})
        
        
def load_lectures(request):
    teacher_id = request.GET.get('teacher')
    lectures = LectrueModel.objects.filter(teacher_id=teacher_id).all()
    
    
def profile_view(request, pk=None):
    instance = None
    login_instance = None
    try:
        instance = UserProfile.objects.get(pk=pk)
    except:
        pass
    
    try:
        if request.user == instance.user:
            login_instance = LoginDetails.objects.filter(user=request.user)
            if request.user.is_staff:
                context['attendance'] = LoginDetails.objects.filter(user=request.user).count()
    except: 
        pass
    
    context = {}
    context['object'] = instance
    context['teacher'] = False
        
    context['login_object'] = login_instance
    try:
        if instance.user.teacher_profile.all().first():
            context['teacher'] = True
        else:
            print('no')
    except:
        pass
    