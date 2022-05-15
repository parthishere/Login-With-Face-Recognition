from attr import field
from rest_framework import serializers
from recognizer.models import UserProfile, User, TeacherProfileModel, LectrueModel, ChangeWebsiteCount, IPAddress 

class UserProfileSerializer(serializers.ModelSerializer):
    
    class Meta():
        model = UserProfile
        fields = "__all__"
        
    def create(self, validated_data):
        user = validated_data.get('user')
        if user.is_superuser:
            image = validated_data.get('user')