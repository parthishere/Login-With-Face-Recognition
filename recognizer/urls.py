from django.contrib import admin
from django.urls import path

from .views import (
    home_view,
    login_view,
    signup_view,
    update_profile_view,
    profile_view,
    logout_view,
    logout_confirm_view,
    login_with_face, # Login noramlly with my code # with normal function
    # login_with_face_part2, # login with recognizer Class
    # login_with_face_part3, # login with part 3 which consists of all the nessecity things inside on function!
    # test_frame
    export_users_xls
)

app_name = 'recognizer'

urlpatterns = [
    path('', home_view, name='home'),
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('logout/', logout_view, name='logout'),
    path('logout-confirm/', logout_confirm_view, name='logout-cnf'),
    path('profile/<int:pk>', profile_view, name='profile'),
    path('profile/<int:pk>/update', update_profile_view, name='update-profile'),
    path('login-with-face', login_with_face, name='login-with-face'),
    # path('login-with-face-2', login_with_face_part2, name='login-with-face-2'),
    # path('frame-check', test_frame, name='test-frame')
    
]