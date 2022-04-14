from datetime import datetime
from django.shortcuts import render, HttpResponseRedirect, redirect, get_object_or_404, reverse, get_list_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http.response import HttpResponse, StreamingHttpResponse
from django.views.decorators import gzip

import cv2

from .models import LectrueModel, TeacherProfileModel, UserProfile, User, ChangeWebsiteCount
from .forms import UserProfileForm, AuthenticationForm, LectureDetailsForm
from .recognizer import RecognizerClass, recognizer, Recognizer, frame_check

from login_details.models import LoginDetails

from django.contrib.auth import (
    login,
    authenticate,
    get_user_model,
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

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['User', 'Authenticated user', 'Teacher', 'Lecture', 'Login date', 'Login time']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    rows = LoginDetails.objects.all().values_list('user', 'authenticated_user', 'teacher', 'lecture', 'login_date', 'login_time')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response


def change_whole_site_by_clicking(request):
    
    context = {}
    if request.method == 'POST':
        if request.user.is_superuser or request.user in request.user.teacher_profile.all():
            teacher = request.user.teacher_profile.all().last()
            print(teacher)
            if ChangeWebsiteCount.objects.filter(teacher=teacher).count() % 2 == 0:
                c = ChangeWebsiteCount.objects.create(teacher=teacher)
                change_site_count = ChangeWebsiteCount.objects.filter(teacher=teacher).count()
                context['recognize'] = c.recognize
            else:
                c = ChangeWebsiteCount.objects.create(teacher=teacher)
                change_site_count = ChangeWebsiteCount.objects.filter(teacher=teacher).count()
                context['recognize'] = c.recognize
 
            print(change_site_count)
            return redirect('recognizer:home')
        else:
            return redirect('recongizer:home')
    return render(request, 'recognizer/home.html', context=context)
    


# Create your views here.
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
    login_details_form = LectureDetailsForm(request.POST or None)
    context['login_details_form'] = login_details_form

    teacher=False
    teacher_user = None
    try:
        user = request.user
        try:
            teacher_user = TeacherProfileModel.objects.get(user=user)
            teacher = True
            user = UserProfile.objects.get(user=user)
        except:
            user = UserProfile.objects.get(user=user)
        
        context['user'] = user
        context['teacher'] = teacher
        context['teacher_user'] = teacher_user
        context['premium_data'] = LoginDetails.objects.filter(user=request.user)
    except:
        return redirect('recognizer:login')
    
    # this is new 
    
    if request.method == 'POST' and login_details_form.is_valid():
        
        teacher = login_details_form.cleaned_data.get('teacher')
        o = teacher.change_website_objects.all().count()
        c  = ChangeWebsiteCount.objects.filter(teacher=teacher).order_by('id').last()
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
            
            names, known_lables, login_proceed = Recognizer(details, username=user.user.username, unique_id=user.unique_id)
            
            print(names, known_lables, login_proceed)
            print(request.user.username + user.unique_id)

            if login_proceed:
                context['login_detail'] = True
                user.login_proceed = login_proceed
                instance = LoginDetails.objects.create(user=request.user, lecture=login_details_form.cleaned_data.get('lecture'), teacher=login_details_form.cleaned_data.get('teacher'))
                # instance.user=request.user
                instance.save()
                user.save()
                
                context['login_details_form'] = login_details_form
                
                messages.success(request, 'now you canwatch premium content')
                return redirect('recognizer:home')
            else:
                context['login_detail'] = False
                user.login_proceed = login_proceed
                user.save()
                
                context['login_details_form'] = login_details_form
                
                messages.error(request, 'get out of my website..')
                return redirect('recognizer:home')
        else:
            messages.error(request,"Can't take attendance")
    
    
    return render(request, 'recognizer/home.html', context=context)

#AJAX

def load_lectures(request):
    print(request)
    teacher_id = request.GET.get('teacher')
    print(teacher_id)
    lectures = LectrueModel.objects.filter(teacher_id=teacher_id).all()
    return render(request, 'recognizer/lecture_dropdown_list_option.html', {'lectures': lectures})




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
    print(instance)
    context['login_object'] = login_instance
    try:
        if User.objects.get(pk=pk).teacher_profile.all():
            context['teacher'] = True
            print('yes')
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
        
# from streamer import Streamer



# def gen():
#     streamer = Streamer('localhost', 8080)
#     streamer.start()

#     while True:
#         if streamer.streaming:
#             yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + streamer.get_jpeg() + b'\r\n\r\n')

# @app.route('/')
# def index():
#   return render_template('index.html')

# @app.route('/video_feed')
# def video_feed():
#   return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

        
 
        
        

    
    
from django import template

register = template.Library()

@register.simple_tag
def current_pk(user):
    return UserProfile.objects.get(user=user).pk  



def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
		
def facecam_feed(request):
    
	return StreamingHttpResponse(gen(RecognizerClass()),
					content_type='multipart/x-mixed-replace; boundary=frame') 


