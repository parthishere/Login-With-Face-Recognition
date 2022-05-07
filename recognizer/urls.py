from django.contrib import admin
from django.urls import path

from .views import (
    facecam_feed,
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
    export_users_xls,
    change_whole_site_by_clicking,
    load_lectures,
    just_a_function,
    update_profile_image_view,
    succsess,
)

app_name = 'recognizer'

urlpatterns = [
    path('', home_view, name='home'),
    path('ajax/lec/', load_lectures, name='data_lec_url'),
    path('accounts/login/', login_view, name='login'),
    path('accounts/signup/', signup_view, name='signup'),
    path('accounts/logout/', logout_view, name='logout'),
    path('logout-confirm/', logout_confirm_view, name='logout-cnf'),
    path('profile/<int:pk>', profile_view, name='profile'),
    path('profile/<int:pk>/update', update_profile_view, name='update-profile'),
    path('profile/image/<int:pk>/update', update_profile_image_view, name='update-img-profile'),
    path('login-with-face', login_with_face, name='login-with-face'),
    path('change-website', change_whole_site_by_clicking, name='change-website'),
    path('export-attendance', export_users_xls, name='export'),
    path("succsess/", succsess, name="sus"),
    # path('facecam-feed', facecam_feed, name='feed_stream'),
    # path('redirect-face', just_a_function, name='redirect_stream'),
    
]