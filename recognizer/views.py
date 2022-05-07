from django.urls import reverse_lazy
from django.shortcuts import render, HttpResponseRedirect, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http.response import HttpResponse, StreamingHttpResponse, JsonResponse
import cv2
import os 
from django.conf import settings
from django.core.files.base import ContentFile

from .models import LectrueModel, TeacherProfileModel, UserProfile, User, ChangeWebsiteCount
from .forms import UserProfileForm, AuthenticationForm, LectureDetailsForm
from .recognizer import RecognizerClass, Recognizer 
from django.http import JsonResponse

from login_details.models import LoginDetails

from PIL import Image
from io import BytesIO

from django.contrib.auth import (
    login,
    authenticate,
    logout
)

import xlwt

def export_users_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="attendance.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Users')

    # Sheet header, first row
    row_num = 0

    header_font = xlwt.Font()
    header_font.name = 'Arial'
    header_font.bold = True
  
    header_style = xlwt.XFStyle()
    header_style.font = header_font
    
    body_font = xlwt.Font()
    body_font.name = 'Arial'
    body_font.bold = False
  
    body_style = xlwt.XFStyle()
    body_style.font = body_font
    
    
    format1 = 'D-MMM-YY'
    format2 = 'h:mm:ss AM/PM'

    columns = ['User', 'Authenticated user', 'Teacher', 'Lecture', 'Login date', 'Login time', "Authenticated Images"]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], header_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    teacher = TeacherProfileModel.objects.get(user=request.user)
    rows = list(LoginDetails.objects.filter(teacher=teacher).values_list('user', 'authenticated_user', 'teacher', 'lecture', 'login_date', 'login_time', 'processed_img'))
    print("rows")
    
    for row in rows:
        row = list(row)
        user = User.objects.get(id=row[0])
        row[0] = str(User.objects.get(id=row[0]).username) + ' ' + str(UserProfile.objects.get(user=user).unique_id) #user
        row[2] = str(TeacherProfileModel.objects.get(id=row[2]).user.username)
        row[3] = str(LectrueModel.objects.get(id=row[3]).lecture_name) + 'by' + str(LectrueModel.objects.get(id=row[3]).teacher.user.username)
        print(row[0])
        row_num += 1
        ws.row(row_num).height_mismatch = True

        
        
        for col_num in range(len(row)):
            if col_num == 4:
                #date
                style = xlwt.XFStyle()
                style.num_format_str = format1
                ws.write(row_num, col_num, row[col_num], style)

            elif col_num == 5:
                #time
                style = xlwt.XFStyle()
                style.num_format_str = format2
                ws.write(row_num, col_num, row[col_num], style)
                
            elif col_num == 6:
                #image 
                path = LoginDetails.objects.filter(teacher=teacher)[row_num-1].processed_img.path
                # path2 = os.path.abspath(path)
                print(path)
                img = Image.open(path)
                image_parts = img.split()
                r = image_parts[0]
                g = image_parts[1]
                b = image_parts[2]
                img = Image.merge("RGB", (r, g, b))
                fo = BytesIO()
                img.save(fo, format='bmp')
                ws.insert_bitmap_data(fo.getvalue(),row_num,col_num)
                img.close()

            else:      
                ws.write(row_num, col_num, row[col_num], body_style)
                
        
        
    # for row in rows:
    #     row_num += 1
    #     for col_num in range(len(row)):
    #         if col_num == 4:
    #             #date
    #             style = xlwt.XFStyle()
    #             style.num_format_str = format1
    #             ws.write(row_num, col_num, row[col_num], style)

    #         elif col_num == 5:
    #             #time
    #             style = xlwt.XFStyle()
    #             style.num_format_str = format2
    #             ws.write(row_num, col_num, row[col_num], style)

    #         else:      
    #             ws.write(row_num, col_num, row[col_num], header_style)

    wb.save(response)
    return response


def change_whole_site_by_clicking(request):
    
    context = {}
    if request.method == 'POST':
        if request.user.is_superuser or request.user in request.user.teacher_profile.all():
            teacher = request.user.teacher_profile.all().last()

            if ChangeWebsiteCount.objects.filter(teacher=teacher).count() % 2 == 0:
                c = ChangeWebsiteCount.objects.create(teacher=teacher)
                change_site_count = ChangeWebsiteCount.objects.filter(teacher=teacher).count()
                context['recognize'] = c.recognize
            else:
                c = ChangeWebsiteCount.objects.create(teacher=teacher)
                change_site_count = ChangeWebsiteCount.objects.filter(teacher=teacher).count()
                context['recognize'] = c.recognize
 
            return redirect('recognizer:home')
        else:
            return redirect('recongizer:home')
    return render(request, 'recognizer/home.html', context=context)
    

from .streamer import get_face_detect_data

def another_home_view(request):
    context = {}
    # login_details_form = LectureDetailsForm(request.POST or None)
    # context['login_details_form'] = login_details_form
    context['user'] = request.user
    if request.POST:

   

        image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAUAA…pqA7RSrmBjBRqPRU0/w+FrR/ktkf4YQAAAABJRU5ErkJggg=="
 
        try:
            image_data = get_face_detect_data(image)
            if image_data:
                return JsonResponse(status=200, data={'image': image_data, 'message': 'Face detected'})
        except Exception as e:
            pass
        return JsonResponse(status=400, data={'errors': {'error_message': 'No face detected'}})
    return render(request, 'recognizer/another-home.html', context=context)


# Create your views here.

allowedIps = ['129.0.0.1', '127.0.0.1']

def allow_by_ip(view_func):
    def authorize(request, *args, **kwargs):
        user_ip = request.META['REMOTE_ADDR']
        for ip in allowedIps:
            if ip==user_ip:
                return view_func(request, *args, **kwargs)
        return HttpResponse('Invalid Ip Access!')
    return authorize

# @allow_by_ip
@login_required(login_url='recognizer:login')
def home_view(request):
    
    context = {}
    context['change_site_count'] = 0
    context['recognize'] = False
    try:
        teacher = request.user.teacher_profile.all().last()
        change_site_count = teacher.change_website_objects.all().count()
        context['change_site_count'] = change_site_count
    except:
        pass
    
    context['data'] = 'Add your cool photo to your profile !'
    login_details_form = LectureDetailsForm(request.POST, request.FILES, user=request.user)
    context['login_details_form'] = login_details_form

    is_teacher=False
    teacher_user = None
    try:
        user = request.user
        try:
            teacher_user = TeacherProfileModel.objects.get(user=user)
            is_teacher = True
            user = UserProfile.objects.get(user=user)
        except:
            user = UserProfile.objects.get(user=user)
        
        context['user'] = user
        context['teacher'] = is_teacher
        context['teacher_user'] = teacher_user
        context['premium_data'] = LoginDetails.objects.filter(user=request.user)
    except:
        return redirect('recognizer:login')
    
    # this is new 
    
    if request.method == 'POST' and login_details_form.is_valid():
        print("request.POST  "+str(request.POST))
        print("request.FILES  "+str(request.FILES))
        print("form.cleaned_data  "+str(login_details_form.cleaned_data))
        file = request.FILES.get('image_file').read()  # src is the name of input attribute in your html file, this src value is set in javascript code
        teacher = request.POST['teacher']
        lecture = request.POST['lecture']
        teacher_user = TeacherProfileModel.objects.get(id=teacher)
        lecture_object = LectrueModel.objects.get(id=lecture)
        o = teacher_user.change_website_objects.all().count()
        if o == 0:
            print("no objects")
        c  = ChangeWebsiteCount.objects.filter(teacher=teacher_user).order_by('id').last()
        context['recognize'] = c.recognize

        
        if o%2==0:

            try:
                user = UserProfile.objects.get(user=request.user)
                
                gender = user.gender
                details = {
                'gender':gender,
                'username':user.user.username,
                'unique_id':user.unique_id,
                'user':user,
                }
                print(details)
            except:
                details = None
            
            frame, login_proceed, names, known_face_names = get_face_detect_data(file, username=user.user.username, unique_id=user.unique_id, superuser=False)
            ret, buf = cv2.imencode('.jpg', frame)
            image = ContentFile(buf.tobytes())
            

            if login_proceed:
                context['login_detail'] = True
                user.login_proceed = login_proceed
                
                instance = LoginDetails.objects.create(user=request.user, lecture=lecture_object, teacher=teacher_user)
                print("connected")
                instance.processed_img.save("output.jpg", image)
                user.save()
                
                context['login_details_form'] = LectureDetailsForm(request.POST, request.FILES or None)
                
                messages.success(request, 'now you canwatch premium content')
                url = reverse('recognizer:home')
                # return HttpResponseRedirect(reverse('recognizer:home'))
                return JsonResponse(status = 302 , data = {'success' : url })
            else:
                context['login_detail'] = False
                user.login_proceed = login_proceed
                user.save()
                
                context['login_details_form'] = LectureDetailsForm(request.POST, request.FILES or None)
            
                messages.error(request, 'get out of my website..')
                url = reverse('recognizer:home')
                return JsonResponse(status = 302 , data = {'success' : url })
        else:
            messages.error(request,"Can't take attendance")
            return HttpResponseRedirect(reverse('recognizer:home'))
    
    return render(request, 'recognizer/home.html', context=context)

#AJAX


def load_lectures(request):
    teacher_id = request.GET.get('teacher')
    lectures = LectrueModel.objects.filter(teacher_id=teacher_id).all()
    return render(request, 'recognizer/lecture_dropdown_list_option.html', {'lectures': lectures})

def succsess(request):
    return HttpResponse("success")


def login_view(request):
    login_form = AuthenticationForm(request.POST or None)
    context = {}
    context['form'] = login_form
    if request.POST:
        if login_form.is_valid():
            username = login_form.cleaned_data.get('username')
            email = login_form.cleaned_data.get('email')
            password= login_form.cleaned_data.get('password')
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user=user)
                messages.success(request, 'login sucsessful!')
                uqid = get_uqid(request)
                request.session['uqid'] = uqid
                
                request.session['user_pk'] = UserProfile.objects.get(user=user).pk
                
                login_form = AuthenticationForm(request.POST or None)
                context['form'] = login_form
                
                user_profile = UserProfile.objects.get(user=user)
                if user.teacher_profile:
                    if user_profile.image:
                        return redirect('recognizer:home')
                    else:
                        return redirect(reverse('recognizer:update-profile', kwargs={'pk': user_profile.pk}))
                    
                if user_profile.image:
                    return redirect('recognizer:home')
                else:
                    return redirect(reverse('recognizer:update-profile', kwargs={'pk': user_profile.pk}))
            else:
                messages.error(request, 'User not found signup first!')
                return render(request, 'recognizer/login.html', context=context)
            
    return render(request, 'recognizer/login.html', context=context)


def signup_view(request):
    signup_form = AuthenticationForm(request.POST or None)
    context = {
        
    }
    context['form'] = signup_form
    
    if request.POST:
        if signup_form.is_valid():
            username = signup_form.cleaned_data.get('username')
            email = signup_form.cleaned_data.get('email')
            password = signup_form.cleaned_data.get('password')
            
            user = authenticate(request, username=username, password=password)
            if user is None:
                user = User.objects.create(username=username, email=email, password=password)
                # user.set_password(password)
                user.save()
                login(request, user=user)
                
                signup_form = AuthenticationForm(request.POST or None)
                context['form'] = signup_form
                messages.success(request, "Sign up Sucsessful")
                
                user_profile = user.user_profile
                # uqid = get_uqid(request=request)
                # request.session['uqid'] = uqid
                return redirect(reverse('recognizer:update-profile', kwargs={'pk': user_profile.pk}))
            else:
                messages.error(request, 'User already exists!')
                context['form'] = signup_form
                return render(request, 'recognizer/signup.html', context=context)
                
    return render(request, 'recognizer/signup.html', context=context)


@login_required(login_url='recognizer:login')
def profile_view(request, pk=None):
    instance = None
    login_instance = None
    try:
        instance = UserProfile.objects.get(pk=pk)
    except:
        pass
    
    try:
        login_instance = LoginDetails.objects.filter(user=request.user)
    except: 
        pass
    
    context = {}
    # if request.user == instance.user or request.user.is_staff:
    context['object'] = instance
    context['teacher'] = False

    context['login_object'] = login_instance
    try:
        if User.objects.get(pk=pk).teacher_profile.all():
            context['teacher'] = True

        else:
            print('no')
    except:
        pass
    return render(request, 'recognizer/profile.html', context=context)


@login_required(login_url='recognizer:login')
def update_profile_view(request, pk=None):
    try: 
        instance = UserProfile.objects.get(pk=pk)
    except:
        instance = None
    edit_form = UserProfileForm(request.POST or None, instance=instance)
    context = {
            'form':edit_form,
        }
    if instance.user == request.user or request.user.is_superuser:
        if request.POST:
            if edit_form.is_valid:
                img = request.FILES.get('image')
                user = edit_form.save()
                instance.image = img
                instance.save()
                
                messages.success(request, "Profile Edited Sucsessfuly")
                request.session['uqid'] = user.unique_id
                context = {
                    'form':edit_form,
                }
                return HttpResponseRedirect(reverse("recognizer:profile", kwargs={'pk': pk}))
            else:
                context = {
                    'form':edit_form,
                }
                messages.error(request, "Somthing is wrong , i can feel it")

    return render(request, 'recognizer/profile_form.html', context=context)



@login_required(login_url='recognizer:login')
def logout_confirm_view(request):
    context = {}
    context['view'] = 'Logout'
    context['msg'] = 'Wanna Logout??'
    return render(request, 'recognizer/anything-confirm.html', context=context)


@login_required(login_url='recognizer:login')
def logout_view(request):
    user = UserProfile.objects.get(user=request.user)
    user.login_proceed = False
    user.save()
    logout(request)
    messages.success(request, "Logout Sucsessful")
    return redirect('recognizer:home')



def get_uqid(request):
    user = UserProfile.objects.get(user=request.user)
    return user.unique_id



################################################3
#################################################
####################################################33
#################################################333
###################################################3



@login_required(login_url = 'recognizer:login')
def login_with_face(request):
    

    context = {}

    if request.method == 'POST':
        print("teacher:"+str(request.POST.get('teacher')))
        print("lec:"+str(request.POST.get('lecture')))
        try:
            user = UserProfile.objects.get(user=request.user)
             
            gender = user.gender
            details = {
            'gender':gender,
            'username':user.user.username,
            'unique_id':user.unique_id,
            'user':user,
            }
            print(details)
        except:
            details = None
        
        names, known_lables, login_proceed = Recognizer(details, username=user.user.username, unique_id=user.unique_id)
        
        print(names, known_lables, login_proceed)
        print(request.user.username + user.unique_id)

        if str(request.user.username + user.unique_id) in names:
            context['login_detail'] = True
            user.login_proceed = login_proceed
            instance = LoginDetails.objects.create(user=request.user )
            instance.user=request.user
            instance.save()
            user.save()
            
            messages.success(request, 'now you canwatch premium content')
            return redirect('recognizer:home')
        else:
            context['login_detail'] = False
            user.login_proceed = login_proceed
            user.save()

            messages.error(request, 'stfu b** get your ass out of my website..')
            return redirect('recognizer:home')
    print(context)
    return render(request, 'recognizer/home.html', context)
        
        
 
        
        

    
    
from django import template

register = template.Library()

@register.simple_tag
def current_pk(user):
    return UserProfile.objects.get(user=user).pk  



def gen(camera):
    break_op = False
    while not break_op:
        names, known_face_names, proceed_login, frame, break_op = camera.get_frame()
                   
        
        # print(names, known_face_names, proceed_login)
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
	
def just_a_function(request):
    return render(request, 'recognizer/feed-stream.html', {})
	
def facecam_feed(request):
    user = UserProfile.objects.get(user=request.user)
                
    gender = user.gender
    details = {
    'gender':gender,
    'username':user.user.username,
    'unique_id':user.unique_id,
    'user':user,
    }
    # print(details)

    
    return StreamingHttpResponse(gen(RecognizerClass(details, username=user.user.username, unique_id=user.unique_id)),
                    content_type='multipart/x-mixed-replace; boundary=frame') 





# context = {}
# context['change_site_count'] = 0
# context['recognize'] = False
# try:
#     teacher = request.user.teacher_profile.all().last()
#     change_site_count = teacher.change_website_objects.all().count()
#     context['change_site_count'] = change_site_count
# except:
#     pass

# context['data'] = 'Add your cool photo to your profile !'
# login_details_form = LectureDetailsForm(request.POST or None)
# context['login_details_form'] = login_details_form

# teacher=False
# teacher_user = None
# try:
#     user = request.user
#     try:
#         teacher_user = TeacherProfileModel.objects.get(user=user)
#         teacher = True
#         user = UserProfile.objects.get(user=user)
#     except:
#         user = UserProfile.objects.get(user=user)
    
#     context['user'] = user
#     context['teacher'] = teacher
#     context['teacher_user'] = teacher_user
#     context['premium_data'] = LoginDetails.objects.filter(user=request.user)
# except:
#     return redirect('recognizer:login')

# # this is new 

# if request.method == 'POST' and login_details_form.is_valid():
    
#     teacher = login_details_form.cleaned_data.get('teacher')
#     o = teacher.change_website_objects.all().count()
#     c  = ChangeWebsiteCount.objects.filter(teacher=teacher).order_by('id').last()
#     context['recognize'] = c.recognize

    
#     if o%2==0:

#         try:
#             user = UserProfile.objects.get(user=request.user)
            
#             gender = user.gender
#             details = {
#             'gender':gender,
#             'username':user.user.username,
#             'unique_id':user.unique_id,
#             'user':user,
#             }
#             print(details)
#         except:
#             details = None
        
#         names, known_lables, login_proceed = Recognizer(details, username=user.user.username, unique_id=user.unique_id)
        
#         print(names, known_lables, login_proceed)
#         print(request.user.username + user.unique_id)

#         if login_proceed:
#             context['login_detail'] = True
#             user.login_proceed = login_proceed
#             instance = LoginDetails.objects.create(user=request.user, lecture=login_details_form.cleaned_data.get('lecture'), teacher=login_details_form.cleaned_data.get('teacher'))
#             # instance.user=request.user
#             instance.save()
#             user.save()
            
#             context['login_details_form'] = login_details_form
            
#             messages.success(request, 'now you canwatch premium content')
#             return redirect('recognizer:home')
#         else:
#             context['login_detail'] = False
#             user.login_proceed = login_proceed
#             user.save()
            
#             context['login_details_form'] = login_details_form
            
#             messages.error(request, 'get out of my website..')
#             return redirect('recognizer:home')
#     else:
#         messages.error(request,"Can't take attendance")