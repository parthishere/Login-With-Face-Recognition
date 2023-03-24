import datetime
from logging import lastResort
from django.shortcuts import render, HttpResponseRedirect, redirect, reverse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http.response import HttpResponse, StreamingHttpResponse, JsonResponse
import cv2
from django.core.files.base import ContentFile
from django.conf import settings
from botocore.client import Config
import boto3, urllib

from teacher.models import CityCollegeModel, CollegeBranchModel, CollegeModel

from recognizer.models import LectrueModel, UserProfile, SessionAttendanceModel
from django.contrib.auth import get_user_model  
  
User = get_user_model()  

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

from .tasks import add_user_to_accepted_user_session, after_setting_allow_attendance_to_true, remove_user_from_atendees_session, remove_user_from_requested_user_session

def check(request):
    user = request.user
    user_profile = request.user.user_profile
    
    return render(request, "base.html", {"user":user})

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
    teacher = UserProfile.objects.get(user=request.user)
    rows = list(LoginDetails.objects.filter(teacher=teacher).values_list('enrollment_number', 'user', 'authenticated_user', 'teacher', 'lecture', 'login_date', 'login_time', 'processed_img'))

    
    for row in rows:
        row = list(row)
        user = get_object_or_404(User, id=row[1])
        row[1] = str(get_object_or_404(User, id=row[1]).username) + ' ' + str(get_object_or_404(User, id=row[1]).unique_id) #user
        row[3] = str(UserProfile.objects.get(id=row[3]).user.username)
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

def set_name(teacher, lecture_name):
    lecture_obj = SessionAttendanceModel.objects.filter(lecture__lecture_name=lecture_name, teacher__user__username=teacher).count()
    return teacher.user.username + "'s :" + lecture_name +" no: "+ str(lecture_obj + 1) +" on date/time" + datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

def enable_disable_session_view(request):
    next_ = "recognizer:home"
    context = {}
    
    if request.method == 'POST':
        try:
            next_ = request.POST['next']
        except:
            next_ = "recognizer:home"
        all_in_one_user = request.user
        if all_in_one_user.is_staff or all_in_one_user.is_teacher:
    
            lecture_id = request.POST['lecture']
            lecture_obj = all_in_one_user.user_profile.lectures.get(pk=lecture_id)
            print(lecture_obj)
            print(lecture_obj.allow_recognize)
            
            if lecture_obj.allow_recognize:
                # these means the lecture was set to take attendance and in this fucntion we have to disable it and make new object
                # change allow_recognize to False
                print("1")
                lecture_obj.allow_recognize = False
                lecture_obj.save()
                print("ohk")
                context['allow_recognize'] = False
                print("2")
                return redirect(reverse(next_))
                
            else:
                # means already the lecture is disabled it self so we dont hahve to enable it for students
                #  and make new objcet
                print("mnot ohk")
                lecture_obj.allow_recognize = True
                lecture_obj.save()
                context['allow_recognize'] = True
                
                new_session_obj = SessionAttendanceModel.objects.create(teacher=all_in_one_user.user_profile, lecture=lecture_obj)
                print("here it goes to celery")
                after_setting_allow_attendance_to_true.s(teacher_username=all_in_one_user.username, lecture_id=lecture_id).apply_async(countdown=lecture_obj.time_to_expire_session*60)
                return redirect(reverse(next_))
                
    
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

    context['allow_attendance'] = False
    context['is_teacher'] = False
    context['user_ip'] = user_ip
    context['second_user_ip'] = second_user_ip
     
    all_in_one_user = request.user


    # print(user_user_profile_ip_lectures)
    # print(user_profile)
    # print(user_user_profile_ip_lectures.user_profile.lectures.all())
    # print(user_user_profile_ip_lectures.user_profile.ip_address.all())
    
    try:
        if all_in_one_user.is_teacher:
            lectures = all_in_one_user.user_profile.lectures.all()
            print(lectures)
            context['lectures_list'] = lectures
            context['is_teacher'] = True
    except Exception as e:
        print(e)
        pass
    
    lecture_details_form = LectureDetailsForm(request.POST, request.FILES, user_profile=all_in_one_user.user_profile)
    context['lecture_details_form'] = lecture_details_form

    
    try:
        user = all_in_one_user
        user_profile = all_in_one_user.user_profile
        
        context['request_user'] = user
        context['userprofile'] = user_profile
          
    except:
        return redirect('recognizer:login')
    
    # this is new 
    if request.method == 'POST' and lecture_details_form.is_valid():
        ifile = request.FILES.get('image_file').read()  # src is the name of input attribute in your html file, this src value is set in javascript code
        teacher = request.POST.get('teacher')
        lecture = request.POST.get('lecture')
        ip1, ip2 = None, None
        try:
            ip1 = request.POST['ip1'] 
            if ip1 == '':
                ip1 = None
        except:
            pass
        
        teacher_from_form = UserProfile.objects.select_related("user").prefetch_related("change_website_objects").get(id=teacher)

        if teacher_from_form.user.is_teacher:
            teacher_user = teacher_from_form
        else:
            return HttpResponse("nathi bhai koi aa naam nu teacher")
        
        if user_profile.user.pk == teacher_user.user.pk:
            teacher_user.ip_address1 = ip1
            teacher_user.save()
        
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
            context['allow_attendance'] = allow_attendance
        except:
            pass
         
        
        if not user_ip in allowed_ips:
            if (teacher_user.ip_address1 is None and teacher_user.ip_address1 is None):
                pass
            else:
                messages.error(request,"Your IP is not in same subnet IPs")
                url = reverse('recognizer:home')
                return JsonResponse(status = 302 , data = {'success' : url })
        
        if allow_attendance:

            try:
                
                gender = user_profile.gender
                details = {
                'gender':gender,
                'college':all_in_one_user.user_profile.college.college_name,
                'branch':all_in_one_user.user_profile.branch.branch_name,
                'username':user.username,
                'unique_id':user_profile.unique_id,
                'user':user_profile,
                'superuser':all_in_one_user.is_superuser,
                }

            except Exception as e:
                print(e)
                details = None
            
            frame, login_proceed = get_face_detect_data(ifile, details)
            _, buf = cv2.imencode('.jpg', frame)
            image = ContentFile(buf.tobytes())
            if login_proceed:
                context['face_recognized'] = True
                user_profile.login_proceed = login_proceed
                
                instance = LoginDetails.objects.create(user=user, lecture=lecture_object, teacher=teacher_user, enrollment_number=user_profile.enrollment_number)
                instance.processed_img.save("output.jpg", image)
                
                url = reverse('recognizer:home')
                context['lecture_details_form'] = lecture_details_form
                if instance in lecture_object.accepted_user.all():
                    if teacher_user.accept_with_request:
                        last_session.requested_users.add(instance)
                    else:
                        last_session.atendees.add(instance)
                    last_session.save()
                    user_profile.save()
                else:
                    messages.error(request, f"you are not accepted in lecture")
                    return JsonResponse(status = 302 , data = {'success' : url })
                
                
                messages.success(request, f'Your face was recognized as {user.username} - {user_profile.enrollment_number}')
                
                
                return JsonResponse(status = 302 , data = {'success' : url })
            else:
                context['face_recognized'] = False
                
                context['lecture_details_form'] = lecture_details_form
            
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

def load_cities(request):
    distric_id = request.GET.get('district')
    cities = CityCollegeModel.objects.filter(district_id=distric_id).all()
    return render(request, 'recognizer/load_cites.html', {'cities':cities})

def load_colleges(request):
    city_id = request.GET.get('city')
    colleges = CollegeModel.objects.filter(city_id=city_id).all()
    return render(request, 'recognizer/load_colleges.html', {'colleges':colleges})

def load_branches(request):
    college_id = request.GET.get('college')
    branches = CollegeBranchModel.objects.filter(college_id=college_id).all()
    return render(request, 'recognizer/load_branches.html', {'branches':branches})

def accept_user_from_session(request):
    next_ = "recognizer:home"
    if request.POST:
        next_ = request.POST.get("next")
        user_pk = request.POST['user_pk']
        session_pk = request.POST['session_pk']
        add_user_to_accepted_user_session(user_pk, request.user.username, session_pk)
    return redirect(next_)

def reject_request_to_session_view(request):
    next_ = "recognizer:home"
    if request.POST:
        next_ = request.POST.get("next")
        user_pk = request.POST['user_pk']
        session_pk = request.POST['session_pk']
        remove_user_from_requested_user_session(user_pk, request.user.username, session_pk)
    return redirect(next_)

def remove_from_atendees_view(request):
    next_ = "recognizer:home"
    if request.POST:
        next_ = request.POST.get("next")
        user_pk = request.POST['user_pk']
        session_pk = request.POST['session_pk']
        remove_user_from_atendees_session(user_pk, request.user.username, session_pk)
    return redirect(next_)

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
                
                user_profile = UserProfile.objects.select_related("user").get(user=user)

                    
                if user_profile.user.is_updated:
                    return redirect('recognizer:home')
                else:
                    return redirect(reverse('recognizer:update-profile', kwargs={'pk': user_profile.pk}))
            else:
                messages.error(request, 'User not found signup first!')
                return render(request, 'recognizer/login.html', context=context)
            
    return render(request, 'recognizer/login.html', context=context)


from teacher.tasks import create_student

def signup_view(request):
    signup_form = AuthenticationForm(request.POST or None)
    context = {
        
    }
    context['form'] = signup_form
    try:
        teacher_profile = request.user.teacher_profile
    except Exception as e:
        print(e)
        
    if request.POST :
        if signup_form.is_valid():
            username = signup_form.cleaned_data.get('username')
            email = signup_form.cleaned_data.get('email') 
            if not email:
                print("Email not found")
            password = signup_form.cleaned_data.get('password')
            gender = None
            enrollment_number = None
            
            
            user = authenticate(request, username=username, password=password)
            if user is None:
                
                create_student(username=username, email=email,
                               gender=gender, teacher=request.user.user_profile, enrollment_number=0)
                
                
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
        instance = UserProfile.objects.select_related("user").prefetch_related("user__attandence").get(pk=pk)
    except Exception as e:
        print(e)
        pass
    
    try:
        user= request.user
        if user.pk == instance.user.pk:
            login_instance = instance.user.attandance.all()
            # if request.user.is_staff:
            #     context['attendance'] = LoginDetails.objects.filter(user=request.user).count()
    except: 
        pass
    
    context = {}
    # if request.user == instance.user or request.user.is_staff:
    context['object'] = instance
    context['teacher'] = False
        
    context['login_object'] = login_instance
    try:
        if instance.user.is_teacher:
            context['teacher'] = True

        else:
            print('no')
    except:
        pass
    return render(request, 'recognizer/profile.html', context=context)



def lecture_details(request, pk=None):
    context={}
    
    user_profile = UserProfile.objects.select_related("user").prefetch_related("user__attandence").get(pk=pk)
    user = user_profile.user
    
    x_lables = []
    y_lables = []
    login = user_profile.user.attandence.all()
    for x in login:
        if f"{x.lecture.lecture_name}/{x.teacher.user.username}" in x_lables:
            pass
        else:
            x_lables.append(f"{x.lecture.lecture_name}/{x.teacher.user.username}")
    for i in x_lables:
        i = i.split('/')
        lecture = i[0]
        teacher = i[1]
        y_lables.append(user_profile.user.attandence.filter(lecture__lecture_name =lecture,teacher__user__username=teacher).count())
   
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
        instance = UserProfile.objects.select_related("user").get(pk=pk)
    except:
        instance = None
        
    
    if (not instance.user.is_updated) or instance.user.is_teacher:
        edit_form = FirstTimeUserProfileForm(request.POST or None, request.FILES or None, instance=instance)
    else:
        edit_form = SecondTimeUserProfileForm(request.POST or None, request.FILES or None, instance=instance)
    context = {
            'form':edit_form,
        }
    user = request.user
    if (instance.user == user) or user.is_teacher:
        print("hello")
        if request.POST:
            if edit_form.is_valid():
                user_profile = edit_form.save()
                user.is_updated = True
                user.save()
                messages.success(request, "Profile Edited Sucsessfuly")
                request.session['uqid'] = user_profile.unique_id
                context = {
                    'form':edit_form,
                }
                return redirect(reverse("recognizer:profile", kwargs={'pk': pk}))
            else:
                context = {
                    'form':edit_form,
                }
                messages.error(request, "Somthing is wrong , i can feel it")

    return render(request, 'recognizer/profile_form.html', context=context)



@user_passes_test(lambda u: u.is_staff)
def update_profile_image_view(request, pk=None):
    try: 
        instance = UserProfile.objects.select_related("user").get(pk=pk)
    except:
        instance = None
    edit_form = UserProfileImageForm(request.POST or None, request.FILES or None, instance=instance)
    context = {
            'form':edit_form,
        }
    user = request.user
    if user.is_teacher:
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
    
    if (request.user.is_teacher) and (request.user.is_staff != user_profile.user.is_staff):
        messages.error(request, "Is teacher cannot delete account!")
        return reverse("recognizer:home")
    if request.user.is_staff and user_profile.college.pk == teacher_profile.college.pk:
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
    user = request.user.user_profile
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
        
        
 
        
        

    
    
 

def get_teacher(request):
    var = request.user.user_profile
    return var if var.is_teacher else None

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

