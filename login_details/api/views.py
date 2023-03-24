from rest_framework.decorators import api_view

from login_details.models import LoginDetails
from .serializers import LoginDetailsSerializer
from rest_framework.generics import ListCreateAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.mixins import Auto

from django_auto_prefetching import AutoPrefetchViewSetMixin

class LoginDetailListCreateAPIView(AutoPrefetchViewSetMixin, ListCreateAPIView):
    queryset = LoginDetails.objects.all()
    serializer_class = LoginDetailsSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user__username', 'user__enrollment_number', 'teacher', "lecture", "login_date", "login_time"]
    search_fields = ['user__username', 'user__enrollment_number', 'teacher', "lecture", "login_date", "login_time"]
    ordering_fields = ['user__username', 'user__enrollment_number', 'teacher', "lecture", "login_date", "login_time"]
    permission_classes = [IsAuthenticated]
    

class LoginDetailsRetriveUpdateDestryAPIView(AutoPrefetchViewSetMixin, RetrieveUpdateDestroyAPIView):
    queryset = LoginDetails.objects.all()
    serializer_class = LoginDetailsSerializer
    
    def perform_update(self, serializer):
        if self.request.user.user_prpfile == serializer.validated_data['teacher']:
            obj = serializer.save()
        return Response(serializer.data)
    
    def perform_destroy(self, instance):
        if self.request.user.user_prpfile == instance.teacher:
            instance.delete()
        return Response({"message": "object Deleted"})
    
  