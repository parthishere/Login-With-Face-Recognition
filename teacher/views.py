from django.shortcuts import render, redirect, HttpResponseRedirect, reverse
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from recognizer.models import User, UserProfile, TeacherProfileModel, LectrueModel
from login_details.models import LoginDetails
from recognizer.views import login_view
from .forms import IpAddress, TeacherUpdateForm

# Create your views here.
@user_passes_test(lambda u: u.is_superuser)
def profile_view(request):
    context={}
    try:
        teacher = TeacherProfileModel.objects.get(user=request.user)
        context['teacher'] = teacher
        context['user_profile'] = teacher.user.user_profile.all().first()
        change_site_count = teacher.change_website_objects.all().count()
        context['change_site_count'] = change_site_count
        print(teacher.user.user_profile)
        context['students_attended_teachers_lecture'] = LoginDetails.objects.filter(teacher__user=request.user).order_by('-login_date').order_by('-login_time')
    except:
        return redirect('recognizer:logout-cnf')
    
    return render(request, 'teacher/index.html', context=context)


@user_passes_test(lambda u: u.is_superuser)
def profile_list_view(request):
    context = {}
    try:
        teacher = TeacherProfileModel.objects.get(user=request.user)
        context['teacher'] = teacher
        context['user_profile'] = teacher.user.user_profile.all().first()
        print(teacher.user.user_profile)
        students = UserProfile.objects.filter(college=teacher.college).filter(branch=teacher.branch)
        context['objects'] = students
        context['is_student'] = "Student"
    except:
        return redirect('recognizer:logout-cnf')
    
    return render(request, 'teacher/students-list.html', context=context)

@user_passes_test(lambda u: u.is_superuser)
def teacher_profile_list_view(request):
    context = {}
    try:
        teacher = TeacherProfileModel.objects.get(user=request.user)
        context['teacher'] = teacher
        context['user_profile'] = teacher.user.user_profile.all().first()
        print(teacher.user.user_profile)
        teachers = TeacherProfileModel.objects.filter(college=teacher.college).values('user')
        context['is_teacher'] = "Teacher"
        context['objects'] = teachers
    except Exception as e:
        print(e)
        return redirect('recognizer:logout-cnf')
    
    return render(request, 'teacher/students-list.html', context=context)


@user_passes_test(lambda u: u.is_superuser)
def teacher_profile_update_view(request):
    edit_form = None
    instance = None
    try: 
        instance = TeacherProfileModel.objects.get(user=request.user)
    except:
        instance = None

    edit_form = TeacherUpdateForm(request.POST or None, instance=instance)
    
    context = {
            'form':edit_form,
        }
    if instance.user == request.user:
        if request.POST:
            if edit_form.is_valid:
                user = edit_form.save()

                
                messages.success(request, "Teacher Profile Edited Sucsessfuly")
                context = {
                    'form':edit_form,
                }
                return HttpResponseRedirect(reverse("teacher:dashboard"))
            else:
                context = {
                    'form':edit_form,
                }
                messages.error(request, "Somthing is wrong , i can feel it")

    return render(request, 'teacher/update-teacher-profile.html', context=context)



def update_ips(request):
    try:
        teacher = TeacherProfileModel.objects.get(user=request.user)
        if request.POST:
            ip1 = request.POST['ip1']
            teacher.ip1 = ip1
            teacher.save()
            messages.success(request, "IP Updated Sucsessfuly")
            return HttpResponseRedirect(reverse("recognizer:home"))
        
    except:
        return redirect("recognizer:login")
    
    
@user_passes_test(lambda u: u.is_superuser)
def lecture_list_view(request):
    context = {}
    try:
        teacher = TeacherProfileModel.objects.get(user=request.user)
        context['teacher'] = teacher
        context['user_profile'] = teacher.user.user_profile.all().first()
        print(teacher.user.user_profile)
        lectures = LectrueModel.objects.filter(teacher=teacher)
        context['objects'] = lectures

    except:
        return redirect('recognizer:logout-cnf')
    
    return render(request, 'teacher/lectures.html', context=context)


@user_passes_test(lambda u: u.is_superuser)
def add_lecture(request):
    context = {}
    try:
        teacher = TeacherProfileModel.objects.get(user=request.user)
        context['teacher'] = teacher
        context['user_profile'] = teacher.user.user_profile.all().first()
        print(teacher.user.user_profile)
        lectures = LectrueModel.objects.filter(teacher=teacher)
        context['objects'] = lectures

    except:
        return redirect('recognizer:logout-cnf')
    
    return render(request, 'teacher/lectures.html', context=context)