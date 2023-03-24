from celery import shared_task

from recognizer.views import User
from .models import SessionAttendanceModel, UserProfile, LectrueModel

@shared_task
def after_setting_allow_attendance_to_true(teacher_username, lecture_id):
    teacher = UserProfile.objects.select_related("user").prefetch_related("lectures", "change_website_objects").get(user__username=teacher_username)
    lecture_obj = teacher.lectures.get(id=lecture_id)
    print("before creating")
    if lecture_obj.allow_recognize:
        # these means the lecture was set to take attendance and in this fucntion we have to disable it and make new object
        # change allow_recognize to False
        lecture_obj.allow_recognize = False
        lecture_obj.save()
        print(f"changed allow attendance to false of lecture {lecture_obj.lecture_name}")
    else:
        print("allow_attendace was already false so nothing was done")
    print("done")
    
    return None

@shared_task
def add_user_to_accepted_user_session(user_pk, teacher_username, session_pk):
    user = User.objects.select_related("user_profile").get(id=user_pk)
    teacher = UserProfile.objects.select_realted("user").prefetch_related("change_website_objects").get(user__username=teacher_username)
    session = teacher.change_website_objects.prefetch_related("requested_user").get(pk=session_pk)
    
    if teacher.user.is_teacher and session.teacher == teacher:
        if user in session.requested_user.all():
            session.requested_users.remove(user)
            session.atendees.add(user)
            session.save()
    return None


@shared_task
def remove_user_from_requested_user_session(user_pk, teacher_username, session_pk):
    user = User.objects.select_related("user_profile").get(id=user_pk)
    teacher = UserProfile.objects.select_realted("user").prefetch_related("change_website_objects").get(user__username=teacher_username)
    session = teacher.change_website_objects.prefetch_related("requested_user").get(pk=session_pk)
    
    if teacher.user.is_teacher and session.teacher is teacher:
        if user in session.requested_user.all():
            session.requested_users.remove(user)
            session.save()
    return None


@shared_task
def remove_user_from_atendees_session(user_pk, teacher_username, session_pk):
    user = User.objects.select_related("user_profile").get(id=user_pk)
    teacher = UserProfile.objects.select_realted("user").prefetch_related("change_website_objects").get(user__username=teacher_username)
    session = teacher.change_website_objects.prefetch_related("atendees").get(pk=session_pk)
    
    if teacher.user.is_teacher and session.teacher is teacher:
        if user in session.atendees.all():
            session.atendees.remove(user)
            session.save()
    return None
