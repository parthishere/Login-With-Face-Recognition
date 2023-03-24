import string
import random
from recognizer.models import UserProfile
from django.template.loader import render_to_string
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

from django.contrib.auth import get_user_model

User = get_user_model()


def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def unique_id_generator(username):
    """
    This is for a Django project and it assumes your instance
    has a model with a slug field and a title character (char) field.
        """
    new_id = random_string_generator(size=12)
    qs_exists = User.objects.filter(
        username=username).exists()
    if qs_exists:
        new_slug = "{}_{randstr}".format(
            username, randstr=random_string_generator(size=12)
        )
        return new_slug
    else:
        return username


@shared_task
def create_student(username, email, gender, teacher, enrollment_number):
    username = unique_id_generator(username)
    if not gender:
        gender = "M"
    password = email+gender+str(enrollment_number)
    us = User.objects.filter(email=email).first()
    if us:
        return
    else:
        user = User.objects.create(
            username=username, email=email, password=password)
        user.set_password(password)
        user.save()

        user_profile = UserProfile.objects.get(user=user)
        user_profile.enrollment_number = enrollment_number
        user_profile.gender = gender
        user_profile.college = teacher.college
        user_profile.branch = teacher.branch
        user_profile.save()

        if email:
            template = render_to_string('snippets/email_template.html', {'username': username, 'email': email,
                                        'enrollment_number': enrollment_number, 'college': user_profile.college, 'branch': user_profile.branch, 'password': password})

            subject = "Registred for FacIt !"
            message = template
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [email]
            send_mail(subject, message, email_from, recipient_list)

        return None
