import profile
from django.contrib import admin
from django.urls import path

from .views import profile_view, profile_list_view, teacher_profile_list_view, teacher_profile_update_view, update_ips

app_name = 'teacher'


urlpatterns = [
    path('', profile_view, name='dashboard'),
    path('students/', profile_list_view, name='students-list'),
    path('teachers/', teacher_profile_list_view, name='teacher-list'),
    path('profile/update', teacher_profile_update_view, name='update-profile'),
    path('profile/update/ip', update_ips, name='ip-update'),
]    
