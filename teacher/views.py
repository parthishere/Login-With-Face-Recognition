from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from recognizer.models import User, UserProfile, TeacherProfileModel
from login_details.models import LoginDetails
from recognizer.views import login_view

# Create your views here.
@login_required(login_url = 'recognizer:login')
def profile_view(request):
    context={}
    try:
        teacher = TeacherProfileModel.objects.get(user=request.user)
        context['teacher'] = teacher
        context['user_profile'] = teacher.user.user_profile.all().first()
        print(teacher.user.user_profile)
        context['students_attended_teachers_lecture'] = LoginDetails.objects.filter(teacher__user=request.user).order_by('-login_date').order_by('-login_time')
    except:
        return redirect('recognizer:logout-cnf')
    
    return render(request, 'teacher/index.html', context=context)

