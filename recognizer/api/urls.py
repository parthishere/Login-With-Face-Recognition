from django.urls import path
from graphene_django.views import GraphQLView

from recognizer.api.schema import schema
from recognizer.api.views import (
    LecturesListAPI,
    UserProfileListView,
    UserProfileDetailUpdateDelete,
    enable_disable_session_api_view,
    main_form_submit_API_view,
    LecturesListAPI,
    LectureRetriveDestroyUpdateAPIView,
    SessionListAPI,
    SessionDetailUpdateDestroyAPIView,
    CitesListView,
    CollegesListView,
    BranchListView,
    update_ips,
    accept_user_from_session_api_view,
    reject_request_to_session_api_view,
    remove_from_atendees_api_view,
    lecture_accepted_students_from_other_lecture,
)
# from .views import UserProfileViewset
# from rest_framework.routers import DefaultRouter

# router = DefaultRouter()
# router.register(r'users', UserProfileViewset, basename='userprofile')
urlpatterns = [
    path('user/list/', UserProfileListView.as_view()),
    path('user/<int:pk>/', UserProfileDetailUpdateDelete.as_view()),
    path('enable-disable-session/', enable_disable_session_api_view),
    path('lecture/list', LecturesListAPI.as_view()),
    path('lecture/<int:pk>', LectureRetriveDestroyUpdateAPIView.as_view()),
    path('session/list', SessionListAPI.as_view()),
    path('session/<int:pk>', SessionDetailUpdateDestroyAPIView.as_view()),
    path('cities/list', CitesListView.as_view()),
    path('colleges/list', CollegesListView.as_view()),
    path('branches/list', BranchListView.as_view()),
    path('update-ip/', update_ips),
    path('session/accept/attendee', accept_user_from_session_api_view),
    path('session/reject/attendee', reject_request_to_session_api_view),
    path('session/remove/request', remove_from_atendees_api_view),
    path("lecture/copy/<int:from_pk>/<int:to_pk>/", lecture_accepted_students_from_other_lecture),
]