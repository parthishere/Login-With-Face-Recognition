from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView, ListCreateAPIView
from django.http.response import JsonResponse
from django.core.files.base import ContentFile
import cv2
from rest_framework.permissions import BasePermission, SAFE_METHODS, IsAdminUser, IsAuthenticated, IsAuthenticatedOrReadOnly
from recognizer.streamer import get_face_detect_data
from login_details.models import LoginDetails
from django.contrib.auth import (
    login,
    authenticate,
    logout
)
from rest_framework.decorators import action, permission_classes
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
# from recognizer.tasks import after_create


from recognizer.models import SessionAttendanceModel, UserProfile, LectrueModel
from recognizer.tasks import add_user_to_accepted_user_session, after_setting_allow_attendance_to_true, remove_user_from_atendees_session, remove_user_from_requested_user_session
from teacher.models import CityCollegeModel

from .serializers import CityCollegeSerializer, LectrueModelSerializer, SecondTimeUserProfileUpdateSerializer, UpdateImageSerializer, UserProfileSerializer, OverAllUserProfileUpdateSerializer, SessionAttendanceModelSerailizer, UserSeraializer
from django_auto_prefetching import AutoPrefetchViewSetMixin
from django.db import connection, reset_queries
import datetime

class IsTeacherOnly():
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        else:
            try:
                return request.user.user_profile.is_teacher
            except:
                return False

 


class UserProfileListView(ListAPIView):
    queryset = UserProfile.objects.select_related("user", "branch", "college").all()
    serializer_class = UserProfileSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user__username', 'user__enrollment_number', 'branch', "college", "user__is_teacher"]
    search_fields = ['user__username', 'user__enrollment_number', 'branch__branch_name', "college__college_name"]
    ordering_fields = ['user__username', 'user__enrollment_number', 'branch__branch_name', "college__college_name"]
    permission_classes = [IsAuthenticated]
    
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        print("Queries counted: {}".format(len(connection.queries)))
        return response
    
    
class UserProfileDetailUpdateDelete(RetrieveUpdateDestroyAPIView):
    """
        Profile Detail Update Delete View
    """
    queryset = UserProfile.objects.select_related("user", "branch", "college").all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self, *args, **kwargs):
        user = self.request.user
        if user.is_teacher or not user.is_updated:
            return OverAllUserProfileUpdateSerializer
        else:
            return SecondTimeUserProfileUpdateSerializer
    
    def perform_destroy(self, instance):
        if self.request.user == instance.user:
            instance.delete()
            return Response({"message": "object deleted"})
        return Response({"message": "object is not deleted"})
    
    def perform_update(self, serializer):
        user = self.request.user
        if not user.is_updated or user.is_teacher:
            object = serializer.save()
            user.is_updated = True
            user.save()
            return object
        return Response({"message": "object is not updated"})
    
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        print("Queries counted: {}".format(len(connection.queries)))
        return response
 
 
@api_view(['POST'])
def enable_disable_session_api_view(request):
    """
        send Lecture ID as "lecture" parameter in POST request
        for example, posted json data will be \n
        { \n
           \t "lecture": 1;\n
        }\n
    """
    user = request.user
    if user.is_staff or user.is_teacher:

        lecture_id = request.POST['lecture']
        lecture_obj = user.user_profile.lectures.get(pk=lecture_id)
        print(lecture_obj)
        
        if lecture_obj.teacher is user.user_profile and user.is_teacher:
            if lecture_obj.allow_recognize:
                print("ohk")
                # these means the lecture was set to take attendance and in this fucntion we have to disable it and make new object
                # change allow_recognize to False
                lecture_obj.allow_recognize = False
                lecture_obj.save()
                print(len(connection.queries))
                return Response({"message": "old session closed"})
            else:
                # means already the lecture is disabled it self so we dont hahve to enable it for students
                #  and make new objcet
                print("mnot ohk")
                lecture_obj.allow_recognize = True
                lecture_obj.save()
                # 'allow_recognize' = True
                new_session_obj = SessionAttendanceModel.objects.create(teacher=user.user_profile, lecture=lecture_obj)
            
                after_setting_allow_attendance_to_true.s(teacher_username=user.username, lecture_id=lecture_id).apply_async(countdown=lecture_obj.time_to_expire_session*60)
                print(len(connection.queries))
                return Response({"message": "New session was created"})
        else:
            print(len(connection.queries))
            return Response({"message":"lecture not found by the teacher"})
       
    else:
        print(len(connection.queries))
        return Response({"message": "Something went wrong"})

    
@api_view(['POST'])
def main_form_submit_API_view(request):
    """
        Main form API view\n
        parameters: "image_file", "teacher", "lecture", "ip1"\n
        image_file : image file that been captured by webcam\n
        teacher: teacher's id\n
        lecture: lecture's id\n
        ip1: user's ip address\n
        
        for example \n
        {\n
            \t"image_file":\n
            \t"teacher": 1          ===> teacher's id which student want to attend the lecture of\n
            \t"lecture": 2          ===> lecture's id which stdent want to attend\n
            \t"ip1": "192.168.0.0"    ===> user's ip address   \n
        }\n
    """
    user = request.user
    user_profile = request.user.user_profile
    
    file = request.FILES.get('image_file').read()  # src is the name of input attribute in your html file, this src value is set in javascript code
    teacher = request.POST.get('teacher')
    lecture = request.POST.get('lecture')
    user_ip = request.POST.get('ip1')

    
    teacher_from_form = UserProfile.objects.select_related("user").prefetch_related("change_website_objects").get(id=teacher)

    if teacher_from_form.is_teacher:
        teacher_user = teacher_from_form
    else:
        return Response({"message": "teacher not found"})
    
    
    allowed_ips = []

    if teacher_user.ip_address1:
        allowed_ip_host = ".".join(teacher_user.ip_address1.split('.')[0:3])
        allowed_masks = (".{}".format(i) for i in range(256))
        for mask in allowed_masks:
            allowed_ips.append(str(allowed_ip_host)+str(mask))
        
    if teacher_user.ip_address2:   
        allowed_ip_host = ".".join(teacher_user.ip_address2.split('.')[0:3])
        allowed_masks = (".{}".format(i) for i in range(256)) 
        for mask in allowed_masks:
            allowed_ips.append(str(allowed_ip_host)+str(mask))

    
    lecture_object = get_object_or_404(LectrueModel, id=lecture)
    
    try:
        allow_attendance = lecture_object.allow_recognize

        last_session = teacher_from_form.change_website_objects.first()
        print(last_session.name)
    except:
        pass
        
    
    if not user_ip in allowed_ips:
        if (teacher_user.ip1 is None and teacher_user.ip2 is None):
            pass
        else:
            return Response({"message": f"Your IP is not in same subnet IPs"})
    
    if allow_attendance:

        try:
            
            gender = user.gender
            details = {
            'gender':gender,
            'college':user_profile.college.college_name,
            'branch':user_profile.branch.branch_name,
            'username':user.username,
            'unique_id':user_profile.unique_id,
            'user':user_profile,
            'superuser':user.is_superuser,
            }

        except Exception as e:
            details = None
        
        frame, login_proceed = get_face_detect_data(file, details)
        _, buf = cv2.imencode('.jpg', frame)
        image = ContentFile(buf.tobytes())
        if login_proceed:
            user_profile.login_proceed = login_proceed
            
            instance = LoginDetails.objects.create(user=user, lecture=lecture_object, teacher=teacher_user, enrollment_number=user_profile.enrollment_number)
            instance.processed_img.save("output.jpg", image)
            
            if instance in lecture_object.accepted_user.all():
                if teacher_user.accept_with_request:
                    last_session.requested_users.add(instance)
                else:
                    last_session.atendees.add(instance)
                last_session.save()
                user_profile.save()
            else:
                return Response({"message": f"you are not accepted in lecture"})
            
            return Response({"message": f"Face was recognized as {user.username} - {user_profile.enrollment_number}"})
        else:
            return Response({"message": "Face was not recognized"})
    else:
        return Response({"message": f"Session hasn't started by {teacher_user.user.username}, Can't take attendance"})
    
    
class LecturesListAPI(ListCreateAPIView):
    queryset = LectrueModel.objects.select_related("teacher").prefetch_related("branch", "college", "teacher__user").all()
    permission_classes = [IsAuthenticated]
    serializer_class = LectrueModelSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['teacher__user__username', "lecture_name", 'branch', "college", "city", "requested_user", "accepted_user", "semester"]
    search_fields = ['teacher__user__username', 'code', "lecture_name", 'branch', "college"]
    
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()).filter(college=request.user.user_profile.college)
        serializer = LectrueModelSerializer(queryset, many=True)
        return Response(serializer.data)
    
    
class LectureRetriveDestroyUpdateAPIView(RetrieveUpdateDestroyAPIView):
    queryset = LectrueModel.objects.select_related("teacher", "teacher__user").all()
    permission_classes = [IsAuthenticated]
    serializer_class = LectrueModelSerializer
    
    def perform_update(self, serializer):
        if self.request.user.user_profile == serializer.validated_data['teacher']: 
            return super().perform_update(serializer)
        else:
            return Response({"message": "Not teacher of requested lecture"})
        
    def perform_destroy(self, instance):
        if self.request.user.user_profile == instance.teacher: 
            return super().perform_destroy(instance)
        else:
            return Response({"message": "Not teacher of requested lecture"})

    
    

class SessionListAPI(ListAPIView):
    queryset = SessionAttendanceModel.objects.prefetch_related("teacher", "lecture", "attendees").all()
    permission_classes = [IsTeacherOnly]
    serializer_class = SessionAttendanceModelSerailizer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["atendees__in", 'teacher', 'lecture', 'timestamp', "requested_users"]
    search_fields = ["atendees", 'teacher', 'lecture', 'timestamp', "name"]
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()).filter(teacher=request.user.user_profile)
        serializer = LectrueModelSerializer(queryset, many=True)
        return Response(serializer.data)
    
    
    
class SessionDetailUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = SessionAttendanceModel.objects.prefetch_related("teacher", "lecture", "attendees").all()
    permission_classes = [IsTeacherOnly]
    serializer_class = SessionAttendanceModelSerailizer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["atendees__in", 'teacher', 'lecture', 'timestamp', "requested_users"]
    search_fields = ["atendees", 'teacher', 'lecture', 'timestamp', "name"]
    
    def get_object(self): 
        pk = self.kwargs['lookup_field']
        print(pk)
        obj = SessionAttendanceModel.objects.get(pk=pk)
        if self.request.user.user_profile == obj.teacher:
            serializer = LectrueModelSerializer(obj)
            return Response(serializer.data)
        else:
            return Response({"message": "error"})
        
    def perform_destroy(self, instance):
        if self.request.user.user_profile == instance.teacher:
            instance.delete()
            return Response({"message": "session deleted"})
        return Response({"message": "session is not deleted"})
    
    def perform_update(self, serializer):
        user = self.request.user
        if user.user_profile is serializer.validated_data['teacher']:
            object = serializer.save()
            user.is_updated = True
            user.save()
            return Response({"message": "session updated"})
        return Response({"message": "session is not updated.. something went wrong"})
    
    
class CitesListView(ListAPIView):
    queryset = CityCollegeModel.objects.all()
    serializer_class = CityCollegeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['city_name', 'district']
    search_fields = ['city_name', 'district']
    
class CollegesListView(ListAPIView):
    queryset = CityCollegeModel.objects.all()
    serializer_class = CityCollegeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['college_name', 'city']
    search_fields = ['college_name', 'city']
    
class BranchListView(ListAPIView):
    queryset = CityCollegeModel.objects.all()
    serializer_class = CityCollegeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['branch_name', 'college']
    search_fields = ['branch_name', 'college']
    
def overall_attandence_in_lecture(request, pk):
    user_profile = UserProfile.objects.select_related("user").prefetch_related("user__attandence").get(pk=pk)
    user = user_profile.user
  
@api_view(['POST'])
@permission_classes([IsTeacherOnly])  
def update_ips(request):
    """
    Update Userprofile IP view\n
    parameters: "ip1", "ip2"\n
    example: \n
    {\n
       \t"ip1":"127.0.0.1",\n
       \t"ip2":"192.168.0.0"\n 
    }\n
    """
    ip1 = request.data.get("ip1", None)
    ip2 = request.data.get("ip2", None)
    user = request.user.user_profile
    user.ip1 = ip1
    user.ip2 = ip2
    user.save()
    serializer = OverAllUserProfileUpdateSerializer
    return Response(serializer.data)


@api_view(['POST'])
def accept_user_from_session_api_view(request):
    """
    View for accepting session request of student who attended and recognized in session\n
    Only if the teacher's accept_with_request is set to true\n
    \n
    paramters "user_pk", "session_pk"\n
    for example:\n
    {\n
    \t"user_pk":1,\n
    \t"session_pk":9\n
    }\n
    """
    if request.POST:
        user_pk = request.POST['user_pk']
        session_pk = request.POST['session_pk']
        add_user_to_accepted_user_session(user_pk, request.user.username, session_pk)
        return Response({"message": "user accepted in session"})

@api_view(['POST'])
def reject_request_to_session_api_view(request):
    """
    View for rejecting session request of student who attended and recognized in session\n
    Only if the teacher's accept_with_request is set to true\n
    \n
    paramters "user_pk", "session_pk"\n
    for example:\n
    {\n
    \t"user_pk":1,\n
    \t"session_pk":9\n
    }\n
    """
    
    if request.POST:
        user_pk = request.POST['user_pk']
        session_pk = request.POST['session_pk']
        remove_user_from_requested_user_session(user_pk, request.user.username, session_pk)
        return Response({"message": "user removed from requested user in session"})

@api_view(['POST'])
def remove_from_atendees_api_view(request):
    """
    View for removing session request of student who attended and recognized in session\n
    Only if the teacher's accept_with_request is set to true\n
    \n
    paramters "user_pk", "session_pk"\n
    for example:\n
    {\n
    \t"user_pk":1,\n
    \t"session_pk":9\n
    }\n
    """
    if request.POST:
        user_pk = request.POST['user_pk']
        session_pk = request.POST['session_pk']
        remove_user_from_atendees_session(user_pk, request.user.username, session_pk)
        return Response({"message": "user removed from accepted atendees in session"})
    
@api_view(["GET"])  
def profile_view(request):
    user_profile = request.user.user_profile
    serializer = UserProfileSerializer(user_profile)
    return Response(serializer.data)

@api_view(['POST'])
def lecture_accepted_students_from_other_lecture(request, from_pk, to_pk):
    """
    copy other lectures accepted student to other lecture
    """
    user = request.user
    if user.is_teacher:
        user_profile = UserProfile.objects.select_related("user").prefect_related("lectures").get(user_id=user.pk)
        
        lecture = user_profile.lectures.get(pk=to_pk)
        from_copy_lecture  = user_profile.lectures.prefetch_related("accepted_user").get(pk=from_pk)
        
        lecture.accepted_user.set(from_copy_lecture.accepted_user.all())
        lecture.save()
        return Response({"message":"lecture accepted user copied !"})
    return Response({"message":"not teacher"})
    
    
def accept_request_of_lecture(request, lecture):
    return 
    



# class UserProfileViewset(viewsets.ModelViewSet):
#     serializer_class = OverAllUserProfileUpdateSerializer
#     queryset = UserProfile.objects.all()
#     filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
#     filterset_fields = ['user__username', 'enrollment_number', 'branch']
#     search_fields = ['user__username', 'enrollment_number', "branch"]
#     ordering_fields = ['user__username', 'enrollment_number', "branch"]
#     permission_classes = [IsAuthenticated]
    
    
#     def list(self, request):
#         user = request.user
#         print(self.action)
#         queryset = self.get_queryset().filter(college=user.user_profile.college)
#         serializer = UserProfileSerializer(queryset, many=True)
#         return Response(serializer.data)
        

#     def retrieve(self, request, pk=None):
#         user = UserProfile.objects.select_related("user").get(pk=pk)
#         serializer = UserProfileSerializer(user)
#         return Response(serializer.data)
    
#     def update(self, request, pk=None):
#         user_profile = self.get_object()


#     @action(detail=True, methods=['POST'], permission_classes=[IsTeacherOnly])
#     def update_image(self, request, pk=None):
#         user_profile = self.get_object()
#         serializer = UpdateImageSerializer(instance=user_profile, data=request.data)
#         if serializer.is_valid() and user_profile.is_teacher:
#             user_profile = serializer.save()
#             return Response({"message": "updated successfully"})
#         else:
#             return Response({"error": "Userprofile is not teacher or not valid data", "status":"401"})

    
#     def destroy(self, request, pk=None):
#         user = self.get_object()
#         if request.user.user_profile ==  user:
#             user.user.delete()
#             user.delete()
#             return Response({"message":"Deletetd sucessfully"})
        
#     def get_serializer_context(self):
#         context = super(UserProfileViewset, self).get_serializer_context()
#         context.update({"request": self.request})
#         return context
    
    
    # def get_permissions(self):
    #     if self.action == ["list", "retrive"]:
    #         permission_classes = [IsAuthenticated]
    #     else:
    #         permission_classes = [IsTeacherOnly]
            






# class UserProfileListCreateAPIView(ListCreateAPIView):
#     queryset = UserProfile.objects.all()
#     permission_classes = [IsAdminUser]


# class FormSubmit(APIView):
#     """
#     View to list all users in the system.

#     * Requires token authentication.
#     * Only admin users are able to access this view.
#     """
#     authentication_classes = [authentication.TokenAuthentication]
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request, format=None):
#         """
#         post request
#         """
        
#         file = request.data.get('image_file').read()  # src is the name of input attribute in your html file, this src value is set in javascript code
#         teacher = request.data.get('teacher')
#         lecture = request.data.get('lecture')
#         user_ip = request.data.get('client_ip')
        

#         teacher_from_form = UserProfile.objects.select_related("user").prefetch_related("change_website_objects").get(id=teacher)

#         if teacher_from_form.is_teacher:
#             teacher_user = teacher_from_form
#         else:
#             return HttpResponse("nathi bhai koi aa naam nu teacher")
        
#         if user_profile.user.pk == teacher_user.user.pk:
#             teacher_user.ip1 = ip1
#             teacher_user.save()
        
#         allowed_ips = []

#         if teacher_user.ip_address1:
#             allowed_ip_host = ".".join(teacher_user.ip_address1.split('.')[0:3])
#             allowed_masks = (".{}".format(i) for i in range(256))
#             for mask in allowed_masks:
#                 allowed_ips.append(str(allowed_ip_host)+str(mask))
         
#         if teacher_user.ip_address2:   
#             allowed_ip_host = ".".join(teacher_user.ip_address2.split('.')[0:3])
#             allowed_masks = (".{}".format(i) for i in range(256)) 
#             for mask in allowed_masks:
#                 allowed_ips.append(str(allowed_ip_host)+str(mask))

        
#         lecture_object = get_object_or_404(LectrueModel, id=lecture)
        
#         try:
#             allow_attendance = lecture_object.allow_recognize

#             last_session = teacher_from_form.change_website_objects.first()
#             print(last_session.name)
#             context['allow_attendance'] = allow_attendance
#         except:
#             pass
         
        
#         if not user_ip in allowed_ips:
#             if (teacher_user.ip1 is None and teacher_user.ip2 is None):
#                 pass
#             else:
#                 messages.error(request,"Your IP is not in same subnet IPs")
#                 url = reverse('recognizer:home')
#                 return JsonResponse(status = 302 , data = {'success' : url })
        
#         if allow_attendance:

#             try:
                
#                 gender = user.gender
#                 details = {
#                 'gender':gender,
#                 'college':all_in_one_user.user_profile.college.college_name,
#                 'branch':all_in_one_user.user_profile.branch.branch_name,
#                 'username':user.username,
#                 'unique_id':user_profile.unique_id,
#                 'user':user_profile,
#                 'superuser':user.is_superuser,
#                 }

#             except Exception as e:
#                 details = None
            
#             frame, login_proceed = get_face_detect_data(file, details)
#             _, buf = cv2.imencode('.jpg', frame)
#             image = ContentFile(buf.tobytes())
#             if login_proceed:
#                 context['face_recognized'] = True
#                 user_profile.login_proceed = login_proceed
                
#                 instance = LoginDetails.objects.create(user=user, lecture=lecture_object, teacher=teacher_user, enrollment_number=user_profile.enrollment_number)
#                 instance.processed_img.save("output.jpg", image)
                
#                 last_session.atendees.add(instance)
                
                
#                 last_session.save()
#                 user_profile.save()
                
#                 context['lecture_details_form'] = lecture_details_form
                
#                 messages.success(request, f'Your face was recognized as {user.username} - {user_profile.enrollment_number}')
#                 url = reverse('recognizer:home')
                
#                 return JsonResponse(status = 302 , data = {'success' : url })
#             else:
#                 context['face_recognized'] = False
                
#                 context['lecture_details_form'] = lecture_details_form
            
#                 messages.error(request, 'Face not recognized !')
#                 url = reverse('recognizer:home')
#                 return JsonResponse(status = 302 , data = {'success' : url })
#         else:
#             messages.error(request,f"Session hasn't started by {teacher_user.user.username}, Can't take attendance")
#             url = reverse('recognizer:home')
                
#             return JsonResponse(status = 302 , data = {'success' : url })
    



# class IsStaffOrReadOnly(BasePermission):
#     def has_permission(self, request, view):
#         if request.method in SAFE_METHODS:
#             return True
#         else:
#             return request.user.is_staff
    

# class SignUPView(APIView):
#     """
#     View to list all users in the system.

#     * Requires token authentication.
#     * Only admin users are able to access this view.
#     """
#     authentication_classes = [authentication.TokenAuthentication]
#     permission_classes = [IsStaffOrReadOnly]
    
#     def post(self, request, format=None):
#         username = request.data.get('username')
#         email = request.data.get('email') or None
#         password = request.data.get('password')
        
#         user = authenticate(request, username=username, password=password)
#         if user is None:
#             user = User.objects.create(username=username, email=email)
#             user.set_password(password)
#             user.save()
            
#             message = "Sign up Sucsessful"
#             data = {
#                 'message':message
#             }
#             user_profile = UserProfile.objects.get(user=user, data=data)
            
#             return JsonResponse(status=302, data=data)
#         else:
#             messages = 'User already exists!'
#             data = {
#                 'message':message
#             }
#             return JsonResponse(status=302, data=data)



# class LogInView(APIView):
#     """
#     View to list all users in the system.

#     * Requires token authentication.
#     * Only admin users are able to access this view.
#     """
    
#     def post(self, request, format=None):
#         username = request.data.get('username')
#         password= request.data.get('password')
        
#         user = authenticate(request, username=username, password=password)
        
#         if user is not None:
#             login(request, user=user)
#             message = 'login sucsessful!'
#             data = {
#                 'messgage':message,
#             }
#             uqid = get_uqid(request)
#             request.session['uqid'] = uqid
            
#             request.session['user_pk'] = UserProfile.objects.get(user=user).pk
            
            
#             user_profile = UserProfile.objects.get(user=user)

                
#             if user_profile.updated:
#                 url =  reverse('recognizer:home')
#                 data['url'] = url
#                 return JsonResponse(status=302, data=data)
#             else:
#                 url = reverse('recognizer:update-profile', kwargs={'pk': user_profile.pk})
#                 data['url'] = url
#                 return JsonResponse(status=302, data=data)


# def get_uqid(request):
#     user = UserProfile.objects.get(user=request.user)
#     return user.unique_id


# @api_view(['POST'])
# def change_whole_site_by_clicking(request):
#     if request.method == 'POST':
#         if request.user.is_staff or request.user in request.user.teacher_profile.all():
#             teacher = request.user.teacher_profile.all().last()

#             if ChangeWebsiteCount.objects.filter(teacher=teacher).count() % 2 == 0:
#                 c = ChangeWebsiteCount.objects.create(teacher=teacher)
#                 change_site_count = ChangeWebsiteCount.objects.filter(teacher=teacher).count()
                
#             else:
#                 c = ChangeWebsiteCount.objects.create(teacher=teacher)
#                 change_site_count = ChangeWebsiteCount.objects.filter(teacher=teacher).count()
                
                
#             return JsonResponse(status=302, data={})
#         else:
#             return JsonResponse(status=302, data={})
        
# @api_view("GET")    
# def load_lectures(request):
#     teacher_id = request.GET.get('teacher')
#     lectures = LectrueModel.objects.filter(teacher_id=teacher_id).all()
    
    
# def profile_view(request, pk=None):
#     instance = None
#     login_instance = None
#     try:
#         instance = UserProfile.objects.get(pk=pk)
#     except:
#         pass
    
#     try:
#         if request.user == instance.user:
#             login_instance = LoginDetails.objects.filter(user=request.user)
#             if request.user.is_staff:
#                 context['attendance'] = LoginDetails.objects.filter(user=request.user).count()
#     except: 
#         pass
    
#     context = {}
#     context['object'] = instance
#     context['teacher'] = False
        
#     context['login_object'] = login_instance
#     try:
#         if instance.user.teacher_profile.all().first():
#             context['teacher'] = True
#         else:
#             print('no')
#     except:
#         pass
    