from attr import field
from rest_framework import serializers
from recognizer.forms import LectureDetailsForm
from django.contrib.auth import get_user_model

from teacher.models import CityCollegeModel
User = get_user_model()
from recognizer.models import UserProfile, LectrueModel, SessionAttendanceModel 


class UserSerializer(serializers.ModelSerializer):
    class Meta():
        model = User
        exclude = ('last_login', "is_active")

class UserProfileSerializer(serializers.ModelSerializer):
    
    class Meta():
        model = UserProfile
        fields = "__all__"
    
    @staticmethod
    def setup_eager_loading(queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.select_related('user', "branch", "college").all()
        return queryset
       
class OverAllUserProfileUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = UserProfile
        fields = "__all__"
        read_only_fields = ('user', "unique_id", "is_updated", "ip_address1", "ip_address2", "login_proceed")
    
    @staticmethod
    def setup_eager_loading(queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.select_related('user', "branch", "college")
        return queryset

class SecondTimeUserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = "__all__"
        read_only_fields = ('user', "unique_id", "is_updated", "ip_address1", "ip_address2", "login_proceed", "city", "district", "image", "gender", "branch", "college")
    
    @staticmethod
    def setup_eager_loading(queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.select_related('user', "branch", "college")
        return queryset
        
class UpdateImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['image', 'branch', 'college', 'gender']
        
    @staticmethod
    def setup_eager_loading(queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.select_related('user', "branch", "college")
        return queryset
        
class IpAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('ip_address1', 'ip_address2')
        
    @staticmethod
    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.select_related('user', "branch", "college")
        return queryset
    
    

class UserSeraializer(serializers.ModelSerializer): 
    class Meta:
        model = User
        fields = "__all__"
        

class LectrueModelSerializer(serializers.ModelSerializer):
    
    class Meta():
        model = LectrueModel
        fields = "__all__"
        read_only_fields = ('teacher')

    
class SessionAttendanceModelSerailizer(serializers.ModelSerializer):
    
    class Meta():
        model = SessionAttendanceModel
        fields = "__all__"
        read_only_fields = ("timestamp", "teacher",)
    
    
class CityCollegeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CityCollegeModel
        field = "__all__"
        read_only_fields = "__all__"
        
class CityCollegeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CityCollegeModel
        field = "__all__"
        read_only_fields = "__all__"