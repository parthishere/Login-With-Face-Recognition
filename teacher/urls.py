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
    update_lecture,
    search_student,
    reset_confirm_view,
    reset_attendance_of_lecture,
    lec_detail,
    accept_request,
    decline_request,
    send_request,
    search_lectures,
    see_all_sessions,
    create_bulk_student,

    session_detail,
    delete_session,
    update_session,
    lecture_accepted_students_from_other_lecture,
    see_all_requests_of_session,



)


from recognizer.views import (
    accept_user_from_session,
    reject_request_to_session_view,
    remove_from_atendees_view,
)

app_name = 'teacher'


urlpatterns = [
    path('', profile_view, name='dashboard'),
    path('students/', profile_list_view, name='students-list'),
    path('teachers/', teacher_profile_list_view, name='teacher-list'),
    path('profile/update', teacher_profile_update_view, name='update-profile'),
    path('profile/update/ip', update_ips, name='ip-update'),
    path('lectures/', lecture_list_view, name='lec'),
    path('search/', search_student, name='search-stud'),
    path('search-lecture/', search_lectures, name='search-lec'),

    path('lectures/add', add_lecture, name='add-lec'),
    path('lectures/<int:pk>', lec_detail, name='lec-detail'),
    path('lectures/update/<int:pk>', update_lecture, name='lec-update'),
    path('lecture/delete/<int:pk>', delete_lecture, name='lec-delete'),
    path('attendance/delete/<int:pk>', delete_attendance, name='del-att'),
    path('reset-attendance/<int:pk>',
         reset_attendance_of_lecture, name='reset-attendance'),
    path('reset-confirm/<int:pk>', reset_confirm_view, name='reset-cnf'),

    path('lec/request/<int:pk>', send_request, name='send_request'),
    path('lec/accept/<int:user_id>/<int:lec_id>',
         accept_request, name='accept_req'),
    path('lec/decline/<int:user_id>/<int:lec_id>',
         decline_request, name='decline_req'),
    path("lec/copy/<int:from_pk>/<int:to_pk>/",
         lecture_accepted_students_from_other_lecture, name="copy-lec"),

    path("sessions-status/", see_all_sessions, name="sessions"),
    path("session/<int:pk>", session_detail, name='session-detail'),
    path("session/<int:pk>/delete", delete_session, name='session-delete'),
    path("session/<int:pk>/update", update_session, name='session-update'),
    path("sessions-requests/", see_all_requests_of_session, name='session-requests'),
    path("session/accept", accept_user_from_session, name='session-accept'),
    path("session/reject", reject_request_to_session_view, name='session-reject'),
    path("session/remove-from-accepted",
         remove_from_atendees_view, name='session-remove-accept'),


    path("create-bulk-student/", create_bulk_student, name="create-bulk-student")
]
