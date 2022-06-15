from celery import shared_task
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.auth.models import User

from django.template.loader import render_to_string

from recognizer.models import TeacherProfileModel

@shared_task
def create_student(username, password, gender, enrollment_number, teacher_id, email=None):
    user = User.objects.create(username=username, email=email)
    teacher = TeacherProfileModel.objects.get(id=teacher_id)
    user.set_password(password)
    user.save()
    
    user_profile = user.user_profile.all().first()
    user_profile.enrollment_number = enrollment_number
    user_profile.gender = gender
    user_profile.college = teacher.college
    user_profile.branch = teacher.branch
    user_profile.save()
    
    if email:
        template = render_to_string('snippets/email_template.html', {'username': username, 'email':email, 'enrollment_number':enrollment_number, 'college':user_profile.college, 'branch':user_profile.branch, 'password':password })

        subject = "Registred for FacIt !"
        message = template
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email]
        mail = EmailMessage(subject, message, email_from, recipient_list)
        mail.send()
    
    return None