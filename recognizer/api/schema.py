from dataclasses import field
from lib2to3.pgen2 import grammar
import graphene
from graphene_django import DjangoObjectType, DjangoListField

from ..models import UserProfile, LectrueModel, SessionAttendanceModel
from django.contrib.auth import get_user_model

User = get_user_model()


class UserProfileType(DjangoObjectType):
    class Meta:
        model = UserProfile
        fields = "__all__"
        
class LectureModelType(DjangoObjectType):
    class Meta:
        model = LectrueModel
        fields = "__all__"
        
class SessionAttendanceModelType(DjangoObjectType):
    class Meta:
        model = SessionAttendanceModel
        fields = "__all__"
        
class UserModelType(DjangoObjectType):
    class Meta:
        model = User
        fields = "__all__"
        

class Query(graphene.ObjectType):
    
    all_users = DjangoListField(UserProfileType)
    user = graphene.Field(UserProfileType, id=graphene.Int())
    all_lectures = DjangoListField(LectureModelType, id=graphene.Int())
    
    def resolve_all_users(root, info):
        return UserProfile.objects.all()
    
    def resolve_all_lectures(root, info, id):
        return LectrueModel.objects.filter(teacher_id=id)
    
    def resolve_user(root, info, id):
        return UserProfile.objects.get(pk=id)
    
    

class UserMutation(graphene.Mutation):
    
    class Arguments:
        name = graphene.String(required=True)
        
    user = graphene.Field(UserProfileType)
    
    @classmethod
    def mutate(root, info, name):
        up = UserProfile(name=name)
        up.save()
        return UserMutation(user=up)
    

class Mutation(graphene.ObjectType):
    update_user = UserMutation.Field()
    
schema = graphene.Schema(query=Query, mutation=Mutation)