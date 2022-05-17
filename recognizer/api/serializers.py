from attr import field
from rest_framework import serializers
from recognizer.forms import LectureDetailsForm
from recognizer.models import UserProfile, User, TeacherProfileModel, LectrueModel, ChangeWebsiteCount, IPAddress 

class UserProfileSerializer(serializers.ModelSerializer):
    
    class Meta():
        model = UserProfile
        fields = "__all__"
        
    def create(self, validated_data):
        user = validated_data.get('user')
        if user.is_staff:
            image = validated_data.get('user')
            
    def update(self, instance, validated_data):
        pass
    
    
    
class TeacherProfileSerializer(serializers.ModelSerializer):
    
    class Meta():
        model = TeacherProfileModel
        fields = "__all__"
        
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class UserSeraializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = "__all__"
        
        def create(self, validated_data):
            pass
        
        def update(self, instance, valiated_Data):
            pass

class LectrueModelSerializer(serializers.ModelSerializer):
    
    class Meta():
        model = LectrueModel
        fields = "__all__"
        
    def create(self, validated_data):
        pass
    
    def update(self, instance, valiated_Data):
        pass  
    
class ChangeWebsiteCountSerailizer(serializers.ModelSerializer):
    
    class Meta():
        model = ChangeWebsiteCount
        fields = "__all__"
      
    def create(self, validated_data):
        pass
    
    def update(self, instance, valiated_Data):
        pass    
    