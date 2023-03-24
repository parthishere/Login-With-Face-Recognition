from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models

# Create your models here.


class CustomUserManager(UserManager):
    def get(self, *args, **kwargs):
        return super().select_related("user_profile").select_related("user_profile__college").get(*args, **kwargs)
    def get_a_user_with_everything(self, *args, **kwargs):
        return self.select_related("user_profile", "user_profile__college", "user_profile__branch").prefetch_related("user_profile__lectures", "user_profile__change_website_objects", "attandence").get(*args, **kwargs)
    def filter_with_everything(self, *args, **kwargs):
        return self.select_related("user_profile", "user_profile__college", "user_profile__branch").prefetch_related("user_profile__lectures", "user_profile__change_website_objects", "attandence").filter(*args, **kwargs)


class CustomUser(AbstractUser):
    is_teacher = models.BooleanField(default=False)
    is_updated = models.BooleanField(default=False)
    enrollment_number = models.IntegerField(default=100)
    objects = CustomUserManager()    



    