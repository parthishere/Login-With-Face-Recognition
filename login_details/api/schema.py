import graphene
from graphene_django import DjangoObjectType

from ..models import LoginDetails

class LoginDetailsType(DjangoObjectType):
    class Meta:
        model = LoginDetails
        fields = ("id", "user", "login_date", "login_time", "teacher", "lecture", "enrollment_number", "processed_img")
        
class Query(graphene.ObjectType):
    all_details = graphene.List(LoginDetailsType)
    
schema = graphene.Schema(query=Query)