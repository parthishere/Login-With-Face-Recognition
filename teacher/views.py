from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from recognizer.models import UserProfile, TeacherProfileModel, LectrueModel
from login_details.models import LoginDetails
from .forms import TeacherUpdateForm, LectureForm
from django.db.models import Q
from django.contrib.auth.decorators import login_required

# Create your views here.
@user_passes_test(lambda u: u.is_staff)
def profile_view(request):
    context={}
    try:
        teacher = TeacherProfileModel.objects.get(user=request.user)
        context['teacher'] = teacher
        context['user_profile'] = teacher.user.user_profile.all().first()
        change_site_count = teacher.change_website_objects.all().count()
        context['change_site_count'] = change_site_count
        
        context['students_attended_teachers_lecture'] = LoginDetails.objects.filter(teacher__user=request.user).order_by('-login_date').order_by('-login_time')
    except:
        return redirect('recognizer:logout-cnf')
    
    return render(request, 'teacher/index.html', context=context)


@user_passes_test(lambda u: u.is_staff)
def profile_list_view(request):
    context = {}
    try:
        teacher = TeacherProfileModel.objects.get(user=request.user)
        context['teacher'] = teacher
        context['user_profile'] = teacher.user.user_profile.all().first()
        
        # teachers_user_profiles = TeacherProfileModel.objects.all().values('user')
        students = UserProfile.objects.filter(college=teacher.college, branch=teacher.branch).exclude(user__is_staff=True)
        context['objects'] = students
        context['is_student'] = "Student"
    except:
        return redirect('recognizer:logout-cnf')
    
    return render(request, 'teacher/students-list.html', context=context)

@user_passes_test(lambda u: u.is_staff)
def teacher_profile_list_view(request):
    context = {}
    try:
        teacher = TeacherProfileModel.objects.get(user=request.user)
        context['teacher'] = teacher
        context['user_profile'] = teacher.user.user_profile.all().first()
       
        teachers = TeacherProfileModel.objects.filter(college=teacher.college).values('user')
        context['is_teacher'] = "Teacher"
        context['objects'] = teachers
    except Exception as e:
        print(e)
        return redirect('recognizer:logout-cnf')
    
    return render(request, 'teacher/teacher-list.html', context=context)


@user_passes_test(lambda u: u.is_staff)
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
                return redirect("teacher:dashboard")
            else:
                context = {
                    'form':edit_form,
                }
                messages.error(request, "Somthing is wrong ..")
                return redirect("teacher:dashboard")

    return render(request, 'teacher/update-teacher-profile.html', context=context)



def update_ips(request):
    try:
        teacher = TeacherProfileModel.objects.get(user=request.user)
        if request.POST:
            ip1 = request.POST['ip1']
            teacher.ip1 = ip1
            teacher.save()
            messages.success(request, "IP Updated Sucsessfuly")
            return redirect("recognizer:home")
        
    except:
        return redirect("recognizer:login")
    
    
@user_passes_test(lambda u: u.is_staff)
def lecture_list_view(request):
    context = {}
    try:
        teacher = TeacherProfileModel.objects.get(user=request.user)
        context['teacher'] = teacher
        context['user_profile'] = teacher.user.user_profile.all().first()
        
        lectures = LectrueModel.objects.filter(teacher=teacher)
        context['objects'] = lectures

    except:
        return redirect('recognizer:logout-cnf')
    
    return render(request, 'teacher/lectures.html', context=context)


@login_required(login_url='recognizer:login')
def lec_detail_view(request, pk=None):
    context = {}
    print(pk)
    lecture = LectrueModel.objects.get(pk=pk)
    print(lecture)
    context['lecture'] = lecture
    return render(request, 'teacher/lectures_detail.html', context=context) 

@user_passes_test(lambda u: u.is_staff)
def add_lecture(request):
    context = {}
    form = LectureForm(request.POST or None)
    context['form'] = form
    if request.POST and form.is_valid:
        teacher = TeacherProfileModel.objects.get(user=request.user)
        instance = form.save()
        instance.teacher = teacher
        instance.save()
        context['form'] = form
        messages.success(request, "Lecture Added Succsessfully")
        return redirect('teacher:lec')
    
    return render(request, 'teacher/update-teacher-profile.html', context=context)

@login_required(login_url='recognizer:login')
def search_student(request):
    context = {}
    query = request.GET['q']
    user_profile = request.user.user_profile.all().first()
    qs = UserProfile.objects.filter(
                Q(user__username__icontains=query) |
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(user__email__icontains=query) |
                Q(enrollment_number__icontains=query) |
                Q(phone_number__icontains=query)
            ).exclude(user__is_staff=True).filter(college=user_profile.college)
    context['is_student'] = "Student"
    context['objects'] = qs
    
    lec_qs = LectrueModel.objects.filter(
                Q(lecture_name__icontains=query) |
                Q(teacher__user__username__icontains=query)
            ).filter(teacher__college=user_profile.college)
    context['is_lecture'] = "lecture"
    context['lec_objcets'] = lec_qs
    return render(request, "teacher/students-list.html", context)

@user_passes_test(lambda u: u.is_staff)
def search_lectures(request):
    query = request.GET.get('q')
    return (request, "", {})

@user_passes_test(lambda u: u.is_staff)
def delete_lecture(request, pk=None):
    lecture = LectrueModel.objects.get(pk=pk)
    if request.user == lecture.teacher.user:
        lecture.delete()
    return redirect('teacher:lec')

@user_passes_test(lambda u: u.is_staff)
def delete_attendance(request, pk=None):
    att = LoginDetails.objects.get(pk=pk)
    if att.teacher.user == request.user:
        print('ok')
        att.delete()
    return redirect('teacher:dashboard')

@user_passes_test(lambda u: u.is_staff)
def update_lecture(request, pk=None):
    context = {}
    lec = LectrueModel.objects.get(pk=pk)
    form = LectureForm(request.POST or None, instance=lec)
    context['form'] = form

    if lec.teacher.user == request.user and form.is_valid():
        instance = form.save()
        messages.success(request, "Lecture Updated Succsessfully")
        return redirect("teacher:lec")
    return render(request, 'teacher/update-teacher-profile.html',context)


@user_passes_test(lambda u: u.is_staff)
def reset_confirm_view(request, pk=None):
    context = {}
    lecture = LectrueModel.objects.get(pk=pk)
    context['view'] = 'Reset Lecture'
    context['msg'] = f"Reset Lecture {lecture.lecture_name}??"
    context['lecture'] = lecture
    return render(request, 'teacher/reset-cnf.html', context=context)

@user_passes_test(lambda u: u.is_staff)
def reset_attendance_of_lecture(request, pk=None):
    lecture = LectrueModel.objects.get(pk=pk)
    teacher = request.user.teacher_profile.all().first()
    if lecture.teacher.user == request.user:
        LoginDetails.objects.filter(lecture=lecture, teacher=teacher).delete()
        return redirect("teacher:dashboard")
        
        
def lec_detail(request, pk=None):
    context = {}
    lec = LectrueModel.objects.get(pk=pk)
    
    context['lecture'] = lec
    return render(request, "teacher/lecture_detail.html", context)


def send_request(request, pk):
    lecture = LectrueModel.objects.get(pk=pk)
    user_p = request.user.user_profile.all().first()
    if not user_p.user.is_staff: 
        lecture.requested_user.add(user_p)
    return redirect("teacher:lec_detail", kwargs={'pk':lecture.pk})

@user_passes_test(lambda u: u.is_staff)
def accept_request(request, user_id ,lec_id):
    lecture = LectrueModel.objects.get(id=lec_id)
    user_p = UserProfile.objects.get(pk=user_id)
    teacher_profile = request.user.teacher_profile.all().first()
    if teacher_profile == lecture.teacher: 
        if user_p in lecture.accepted_user.all():
            if user_p in lecture.requested_user.all():
                lecture.requested_user.remove(user_p)
        else:
            lecture.accepted_user.add(user_p)
            lecture.requested_user.remove(user_p)
    return redirect(reverse("teacher:lec-detail", kwargs={'pk':lecture.pk}))

@user_passes_test(lambda u: u.is_staff)
def decline_request(request, user_id, lec_id):
    lecture = LectrueModel.objects.get(id=lec_id)
    user_p = UserProfile.objects.get(pk=user_id)
    teacher_profile = request.user.teacher_profile.all().first()
    if teacher_profile == lecture.teacher: 
        
        if user_p in lecture.accepted_user.all():
            lecture.accepted_user.remove(user_p)
            
        if user_p in lecture.requested_user.all():
            lecture.requested_user.remove(user_p)
            
    return redirect(reverse("teacher:lec-detail", kwargs={'pk':lecture.pk}))