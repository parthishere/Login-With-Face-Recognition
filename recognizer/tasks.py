from celery import shared_task
from time import sleep
from .models import ChangeWebsiteCount, TeacherProfileModel, LectrueModel

@shared_task
def after_create(teacher_username, lecture):
    sleep(20)
    teacher = TeacherProfileModel.objects.get(user__username=teacher_username)
    lecture_obj = LectrueModel.objects.get(lecture_name=lecture, teacher=teacher)
    print("before creating")
    if ChangeWebsiteCount.objects.filter(teacher=teacher, lecture=lecture_obj).count() % 2 == 0:
        c = ChangeWebsiteCount.objects.create(teacher=teacher, lecture=lecture_obj)
        print("created")
    print("done")
    return None


