from django.urls import reverse
from django.db import models

from recognizer.models import LectrueModel, UserProfile
from django.conf import settings
import datetime, os

def processed_image_path(instance, filename):
    
    extension = "." + filename.split('.')[-1]
    t = datetime.datetime.now()
    name = ( instance.user.username + t.strftime("%d") + t.strftime("%m") + t.strftime("%Y") + t.strftime("%H:%M:%S"))
    filename = name + extension 
    
    path = 'Recognized_img/'
    return os.path.join(path , filename)


# Create your models here.
class LoginDetails(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='attandence', on_delete=models.CASCADE)
    login_date = models.DateField(auto_now_add=True)
    login_time = models.TimeField(auto_now_add=True)
    authenticated_user = models.BooleanField(default=False) 
    teacher = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='login_details_with_teacher', null=True, blank=True)
    lecture = models.ForeignKey(LectrueModel, on_delete=models.CASCADE, null=True, blank=True, related_name="lecture_login_details")
    enrollment_number = models.BigIntegerField(blank=True, null=True)
    processed_img = models.ImageField(upload_to=processed_image_path, null=True, blank=True)
      
    def __str__(self):
        login_date = str(self.login_date)
        login_time = str(self.login_time)
        user = str(self.user)
        return (user +'   '+ login_date +'  Time:  '+ login_time +" Lecture: "+ self.lecture.lecture_name)
    
    class Meta():
        ordering = ['-id']
        verbose_name = 'Login Detail'
        
        
    def get_delete_url(self):
        return reverse('teacher:del-att', kwargs={'pk':self.pk})