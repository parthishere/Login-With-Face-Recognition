from django.db import models
# from django.contrib.auth import get_user_model
from django.db.models import Q
from django.conf import settings
# User = get_user_model()

# Create your models here.

class ThreadManager(models.Manager):
    def by_user(self, **kwargs):
        user = kwargs.get('user')
        lookup = Q(first_person=user) | Q(second_person=user)
        qs = self.get_queryset().filter(lookup).distinct()
        return qs
    
    def get_or_create(self, first_person, second_person):
        lookup = (Q(first_person=first_person) & Q(second_person=second_person)) | (Q(first_person=second_person) & Q(second_person=first_person))
        qs = self.get_queryset().filter(lookup).distinct()
        print(qs)
        if qs.exists() and qs.count() == 1:
            return qs.first()
        elif qs.count() > 1:
            raise Exception("more than one thread found")
        elif qs.count() == 0:
            return self.model.objects.create(first_person=first_person, second_person=second_person)
            


class Thread(models.Model):
    first_person = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='thread_first_person')
    second_person = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True,
                                     related_name='thread_second_person')
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = ThreadManager()
    class Meta:
        unique_together = ['first_person', 'second_person']


class ChatMessage(models.Model):
    thread = models.ForeignKey(Thread, null=True, blank=True, on_delete=models.CASCADE, related_name='chatmessage_thread')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)