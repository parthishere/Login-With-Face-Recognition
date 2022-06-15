from django.shortcuts import render, HttpResponseRedirect, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http.response import HttpResponse, StreamingHttpResponse, JsonResponse
import cv2
from django.core.files.base import ContentFile
from django.conf import settings
from botocore.client import Config
import boto3, urllib

import requests

from .models import LectrueModel, TeacherProfileModel, UserProfile, User, ChangeWebsiteCount
from .forms import FirstTimeUserProfileForm, SecondTimeUserProfileForm, AuthenticationForm, LectureDetailsForm, UserProfileImageForm
from .recognizer import RecognizerClass, Recognizer 

from login_details.models import LoginDetails

from PIL import Image
from io import BytesIO

from django.contrib.auth import (
    login,
    authenticate,
    logout
)

import xlwt

from django.contrib.auth.decorators import user_passes_test

from plotly.offline import plot
import plotly.graph_objs as go

from .streamer import get_face_detect_data

from .tasks import after_create

@user_passes_test(lambda u: u.is_staff)
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

    columns = ['Enrollment number', 'User', 'Authenticated user', 'Teacher', 'Lecture', 'Login date', 'Login time', "Authenticated Images"]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], header_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    teacher = TeacherProfileModel.objects.get(user=request.user)
    rows = list(LoginDetails.objects.filter(teacher=teacher).values_list('enrollment_number', 'user', 'authenticated_user', 'teacher', 'lecture', 'login_date', 'login_time', 'processed_img'))

    
    for row in rows:
        row = list(row)
        user = User.objects.get(id=row[1])
        row[1] = str(User.objects.get(id=row[1]).username) + ' ' + str(UserProfile.objects.get(user=user).unique_id) #user
        row[3] = str(TeacherProfileModel.objects.get(id=row[3]).user.username)
        row[4] = str(LectrueModel.objects.get(id=row[4]).lecture_name) + 'by' + str(LectrueModel.objects.get(id=row[4]).teacher.user.username)

        row_num += 1
        ws.row(row_num).height_mismatch = True
        
        
        for col_num in range(len(row)):
            if col_num == 5:
                #date
                style = xlwt.XFStyle()
                style.num_format_str = format1
                ws.write(row_num, col_num, row[col_num], style)

            elif col_num == 6:
                #time
                style = xlwt.XFStyle()
                style.num_format_str = format2
                ws.write(row_num, col_num, row[col_num], style)
                
            elif col_num == 7:
                #image 
                path = LoginDetails.objects.filter(teacher=teacher)[row_num-1].processed_img
                print(path)
                
                s3 = boto3.client('s3',
                         aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                         aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                         config=Config(signature_version='s3v4'),
                         region_name='ap-south-1'
                         )
                url=s3.generate_presigned_url('get_object', Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': f"media/{path}"})
                resp = urllib.request.urlopen(url)
                img = Image.open(resp)
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
                

    wb.save(response)
    return response


@user_passes_test(lambda u: u.is_staff)
def change_whole_site_by_clicking(request):
    next_ = "recognizer:home"
    context = {}
    
    if request.method == 'POST':
        try:
            next_ = request.POST['next']
        except:
            next_ = "recognizer:home"
        if request.user.is_staff or request.user in request.user.teacher_profile.all():
            teacher = get_teacher(request)
            lecture = request.POST['lecture']
            lecture_obj = LectrueModel.objects.get(lecture_name=lecture, teacher=teacher)
            c = ChangeWebsiteCount.objects.create(teacher=teacher, lecture=lecture_obj)
            change_site_count = ChangeWebsiteCount.objects.filter(teacher=teacher, lecture=lecture_obj).count()
            if change_site_count % 2 == 0:
                # even means recognition is enabled
                after_create.delay(teacher_username=teacher.user.username, lecture=lecture)

            context['recognize'] = c.recognize
                
            if next:
                return redirect(next_)
            else:
                return redirect('recognizer:home')
        else:
            return redirect('recongizer:home')
    return render(request, 'recognizer/home.html', context=context)
    





# Create your views here

# @allow_by_ip
@login_required(login_url='recognizer:login')
def home_view(request):
    
    try:
        user_ip = request.META['HTTP_X_FORWARDED_FOR']
    except:
        user_ip = request.META['REMOTE_ADDR']
    second_user_ip = request.META['REMOTE_ADDR']
    context = {}
    context['change_site_count'] = 0
    context['recognize'] = False
    context['user_ip'] = user_ip
    context['second_user_ip'] = second_user_ip
    is_teacher=False
    
    try:
        teacher = get_teacher(request)
        teacher_user = True
        lecture_counts = {}
        for lec in teacher.lectures.all():
            lecture_counts[lec] = lec.change_website_objects_lecture.all().count()
        change_site_count = teacher.change_website_objects.all().count()
        context['change_site_count'] = change_site_count
        context['lectures_with_count'] = lecture_counts
        print(lecture_counts)
    except Exception as e:
        print(e)
        pass
    
    context['data'] = 'Add your cool photo to your profile !'
    login_details_form = LectureDetailsForm(request.POST, request.FILES, user=request.user)
    context['login_details_form'] = login_details_form

    
    try:
        user = request.user
        
        user_profile = UserProfile.objects.get(user=user)
        
        context['user'] = user_profile
        context['teacher'] = is_teacher
        context['teacher_user'] = teacher
        context['premium_data'] = LoginDetails.objects.filter(user=user)
    except:
        return redirect('recognizer:login')
    
    # this is new 
    
    if request.method == 'POST' and login_details_form.is_valid():
        file = request.FILES.get('image_file').read()  # src is the name of input attribute in your html file, this src value is set in javascript code
        teacher = request.POST['teacher']
        lecture = request.POST['lecture']
        ip1, ip2 = None, None
        try:
            ip1 = request.POST['ip1'] 
            if ip1 == '':
                ip1 = None
        except:
            pass
        teacher_user = TeacherProfileModel.objects.get(id=teacher)
        if user == teacher_user.user:
            teacher_user.ip1 = ip1
            teacher_user.save()
            
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
            # o = teacher_user.change_website_objects.all().count()
            o = lecture_object.change_website_objects_lecture.all().count()
            c  = ChangeWebsiteCount.objects.filter(teacher=teacher_user, lecture=lecture_object).order_by('id').last()
            context['recognize'] = c.recognize
        except:
            o = 0
            context['recognize'] = False
            
        if o == 0:
            print("no objects")
        
        
        if not user_ip in allowed_ips:
            if (teacher_user.ip1 is None and teacher_user.ip2 is None):
                pass
            else:
                messages.error(request,"Your IP is not in same subnet IPs")
                url = reverse('recognizer:home')
                return JsonResponse(status = 302 , data = {'success' : url })
        
        if o%2==0:

            try:
                
                gender = user.gender
                details = {
                'gender':gender,
                'college':user_profile.college,
                'branch':user_profile.branch,
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
                context['login_detail'] = True
                user_profile.login_proceed = login_proceed
                
                instance = LoginDetails.objects.create(user=user, lecture=lecture_object, teacher=teacher_user, enrollment_number=user_profile.enrollment_number)
                instance.processed_img.save("output.jpg", image)
                
                user_profile.save()
                
                context['login_details_form'] = login_details_form
                
                messages.success(request, f'Your face was recognized as {user.username} - {user_profile.enrollment_number}')
                url = reverse('recognizer:home')
                
                return JsonResponse(status = 302 , data = {'success' : url })
            else:
                context['login_detail'] = False
                user_profile.login_proceed = login_proceed
                user_profile.save()
                
                context['login_details_form'] = login_details_form
            
                messages.error(request, 'Face not recognized !')
                url = reverse('recognizer:home')
                return JsonResponse(status = 302 , data = {'success' : url })
        else:
            messages.error(request,f"Session hasn't started by {teacher_user.user.username}, Can't take attendance")
            url = reverse('recognizer:home')
                
            return JsonResponse(status = 302 , data = {'success' : url })
    
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

                    
                if user_profile.updated:
                    return redirect('recognizer:home')
                else:
                    return redirect(reverse('recognizer:update-profile', kwargs={'pk': user_profile.pk}))
            else:
                messages.error(request, 'User not found signup first!')
                return render(request, 'recognizer/login.html', context=context)
            
    return render(request, 'recognizer/login.html', context=context)


from teacher.tasks import create_student

@user_passes_test(lambda u: u.is_staff)
def signup_view(request):
    signup_form = AuthenticationForm(request.POST or None)
    context = {
        
    }
    context['form'] = signup_form
    teacher_profile = request.user.teacher_profile.all().first()
    if request.POST :
        if signup_form.is_valid():
            username = signup_form.cleaned_data.get('username')
            email = signup_form.cleaned_data.get('email') or None
            password = signup_form.cleaned_data.get('password')
            gender = None
            enrollment_number = None
            
            
            user = authenticate(request, username=username, password=password)
            if user is None:
                
                create_student(username, password, email, gender, enrollment_number, teacher_profile, email)
                
                
                signup_form = AuthenticationForm(request.POST or None)
                context['form'] = signup_form

                return redirect(reverse('recognizer:signup'))
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
        if request.user == instance.user:
            login_instance = LoginDetails.objects.filter(user=request.user)
            if request.user.is_staff:
                context['attendance'] = LoginDetails.objects.filter(user=request.user).count()
    except: 
        pass
    
    context = {}
    # if request.user == instance.user or request.user.is_staff:
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
    return render(request, 'recognizer/profile.html', context=context)



def lecture_details(request, pk=None):
    context={}
    
    user_profile = UserProfile.objects.get(pk=pk)
    user = user_profile.user
    
    x_lables = []
    y_lables = []
    login = LoginDetails.objects.filter(user=user)
    for x in login:
        if f"{x.lecture.lecture_name}/{x.teacher.user.username}" in x_lables:
            pass
        else:
            x_lables.append(f"{x.lecture.lecture_name}/{x.teacher.user.username}")
    for i in x_lables:
        i = i.split('/')
        lecture = i[0]
        teacher = i[1]
        y_lables.append(LoginDetails.objects.filter(lecture__lecture_name =lecture,teacher__user__username=teacher).count())
   
    context['lectures_name'] = zip(x_lables, y_lables)

    fig = go.Figure()
    scatter = go.Bar(x=x_lables, y=y_lables,
                        name='test',
                        opacity=0.8, marker_color='green')
    fig.add_trace(scatter)
    plot_div = plot(fig ,  output_type='div', include_plotlyjs=False, show_link=False, link_text="")
    context['plot_div'] = plot_div

    return render(request, "recognizer/lectures-details.html", context)


@login_required(login_url='recognizer:login')
def update_profile_view(request, pk=None):
    edit_form = None
    try: 
        instance = UserProfile.objects.get(pk=pk)
    except:
        instance = None
    if not instance.updated or instance.user.is_staff:
        edit_form = FirstTimeUserProfileForm(request.POST, request.FILES, instance=instance)
    else:
        edit_form = SecondTimeUserProfileForm(request.POST, request.FILES, instance=instance)
    context = {
            'form':edit_form,
        }
    if instance.user == request.user or request.user.is_staff:
        if request.POST:
            if edit_form.is_valid():
                user = edit_form.save()
                instance.updated = True
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



@user_passes_test(lambda u: u.is_staff)
def update_profile_image_view(request, pk=None):
    try: 
        instance = UserProfile.objects.get(pk=pk)
    except:
        instance = None
    edit_form = UserProfileImageForm(request.POST, request.FILES, instance=instance)
    context = {
            'form':edit_form,
        }
    if instance.user == request.user or request.user.is_staff:
        if request.POST:
            if edit_form.is_valid():
                user = edit_form.save()
                instance.save()
                
                messages.success(request, "Profile Image Edited Sucsessfuly")
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


@user_passes_test(lambda u: u.is_staff)
def delete_profile(request, pk=None):
    try:   
        user_profile = UserProfile.objects.get(pk=pk)
        user = user_profile.user
        teacher_profile = request.user.teacher_profile.all().first()
    except:
        return reverse("recognizer:home")
    
    if (request.user.is_staff and user_profile.user.is_staff) and (request.user.is_staff != user_profile.user.is_staff):
        messages.error(request, "Is teacher cannot delete account!")
        return reverse("recognizer:home")
    if request.user.is_staff and user_profile.college == teacher_profile.college:
        user_profile.delete()
        user.delete()
        messages.success(request, "Account Deleted!")
    else:
        messages.error(request, "In not same college!")
        return reverse("recognizer:home")
    return reverse("recognizer:home")


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



#################################################
#################################################
#################################################
#################################################
#################################################



@login_required(login_url = 'recognizer:login')
def login_with_face(request):
    

    context = {}

    if request.method == 'POST':
        
        try:
            user = UserProfile.objects.get(user=request.user)
             
            gender = user.gender
            details = {
            'gender':gender,
            'username':user.user.username,
            'unique_id':user.unique_id,
            'user':user,
            }
        except:
            details = None
        
        names, known_lables, login_proceed = Recognizer(details, username=user.user.username, unique_id=user.unique_id)


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

    return render(request, 'recognizer/home.html', context)
        
        
 
        
        

    
    
from django import template

register = template.Library()

@register.simple_tag
def current_pk(user):
    return UserProfile.objects.get(user=user).pk  

def get_teacher(request):
    return request.user.teacher_profile.all().last()

def get_user_profile(request):
    return request.user.user_profile

def get_user(request):
    return request.user
    



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

