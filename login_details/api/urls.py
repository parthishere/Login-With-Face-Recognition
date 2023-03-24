from django.urls import path
from graphene_django.views import GraphQLView

from login_details.api.schema import schema

urlpatterns = [
    # ...
    path("", GraphQLView.as_view(graphiql=True, schema=schema)),
]