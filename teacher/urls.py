import profile
from django.contrib import admin
from django.urls import path

from .views import (
    profile_view, 
    profile_list_view, 
    teacher_profile_list_view,
    teacher_profile_update_view,
    update_ips,
    lecture_list_view,
    add_lecture,
    delete_lecture,
    delete_attendance,
    update_lecture
    
)

app_name = 'teacher'


urlpatterns = [
    path('', profile_view, name='dashboard'),
    path('students/', profile_list_view, name='students-list'),
    path('teachers/', teacher_profile_list_view, name='teacher-list'),
    path('profile/update', teacher_profile_update_view, name='update-profile'),
    path('profile/update/ip', update_ips, name='ip-update'),
    path('lectures/', lecture_list_view, name='lec'),
    path('lectures/add', add_lecture, name='add-lec'),
    path('lectures/update/<int:pk>', update_lecture, name='lec-update'),
    path('lecture/delete/<int:pk>', delete_lecture, name='lec-delete'),
    path('attendance/delete/<int:pk>', delete_attendance, name='del-att'),
]    
