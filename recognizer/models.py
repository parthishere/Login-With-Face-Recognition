from django.conf import settings

from ipaddress import ip_address
from django.db import models
from django.shortcuts import reverse
from django.db.models.signals import pre_save, post_save

from teacher.models import DistrictCollege, CityCollegeModel, CollegeModel, CollegeBranchModel
import os

from .utils import random_string_generator

def user_image_path(instance, filename):
    
    extension = "." + filename.split('.')[-1]
    name = ( instance.user.username + instance.unique_id )
    filename = name + extension 
    
    path = f"User_images/{instance.college}/{instance.branch}/{instance.gender}"
    return os.path.join(path , filename)
                    
                    
def unique_id_generator(instance):
    """
    This is for a Django project and it assumes your instance 
    has a model with a slug field and a title character (char) field.
        """
    new_id = random_string_generator(size=12)
    Klass = instance.__class__
    qs_exists = Klass.objects.filter(unique_id=new_id).exists()
    if qs_exists:
        new_slug = "{randstr}".format(
                    randstr=random_string_generator(size=12)
                )
        return new_slug
    else:
        return new_id





class UserProfile(models.Model):
    
    GENDER_CHOICES = (
        ('M','MALE'),
        ('F','FEMALE'),
        ('O', 'OTHER'),
    )

    
    SEMESTER_CHOICES = (
        ('1', '1st Semester'),
        ('2', '2nd Semester'),
        ('3', '3rd Semester'),
        ('4', '4th Semester'),
        ('5', '5th Semester'),
        ('6', '6th Semester'),
        ('7', "7th Semester"),
        ('8', "8th Semester"),
    )
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_profile')
    unique_id = models.CharField(null=True, blank=True, max_length=120) 
    image = models.ImageField(upload_to=user_image_path, null=True, blank=True)
    about = models.CharField(max_length=30, null=True, blank=True)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=2)
    district = models.ForeignKey(DistrictCollege, on_delete=models.CASCADE, null=True, blank=True)
    city = models.ForeignKey(CityCollegeModel, on_delete=models.CASCADE, null=True, blank=True)
    college = models.ForeignKey(CollegeModel, on_delete=models.CASCADE, null=True, blank=True)
    branch = models.ForeignKey(CollegeBranchModel, on_delete=models.CASCADE, null=True, blank=True)
    company = models.CharField(max_length=100,null=True, blank=True)
    semester = models.CharField(choices=SEMESTER_CHOICES, max_length=3, default='1')
    enrollment_number = models.BigIntegerField(null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    phone_number = models.BigIntegerField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    github_username = models.CharField(max_length=100, null=True, blank=True)
    twitter_handle = models.CharField(max_length=100, null=True, blank=True)
    instagram_username = models.CharField(max_length=100, null=True, blank=True)
    facebook_username = models.CharField(max_length=100, null=True, blank=True)
    login_proceed = models.BooleanField(default=False)
    ip_address1 = models.CharField(max_length=100, null=True, blank=True)
    ip_address2 = models.CharField(max_length=100, null=True, blank=True)
    accept_with_request = models.BooleanField(default=False)
    
    
    def __str__(self):
        name = self.user.username + str(self.pk)
        return "{} {}".format(self.user.username, self.pk)
    
    def save(self, *args, **kwargs):
        try:
            this = UserProfile.objects.get(id=self.id)
            if this.image != self.image:
                this.image.delete(save=False)
        except: pass
        super(UserProfile, self).save(*args, **kwargs)
        
    @property
    def get_absolute_url(self):
        return reverse("recognizer:profile", kwargs={"pk": self.pk})
    
    @property
    def get_delete_url(self):
        return reverse("recognizer:del-profile", kwargs={"pk": self.pk})
    
        

class IpAddress(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True, related_name="user_ip_address")
    ip = models.CharField(null=True, blank=True, max_length=15) 
    
    def __str__(self):
        return self.user.username + " " + self.ip
    

class LectureQueryset(models.QuerySet):
    def lectures_teacher(self, teacher_pk):
        return self.filter(teacher=UserProfile.objects.get(id=teacher_pk))


class LectureManager(models.Manager):
    
    def get_queryset(self):
        return LectureQueryset(self.model, using=self._db)
            
    def teacher_lectures(self, teacher_pk):
        return self.get_queryset().lectures_teacher(teacher_pk)
    


class LectrueModel(models.Model):

    
    SEMESTER_CHOICES = (
        ('1', '1st Semester'),
        ('2', '2nd Semester'),
        ('3', '3rd Semester'),
        ('4', '4th Semester'),
        ('5', '5th Semester'),
        ('6', '6th Semester'),
    )
    
    lecture_name = models.CharField(max_length=100)
    teacher = models.ForeignKey(UserProfile, related_name='lectures', on_delete=models.CASCADE, null=True, blank=True)
    semester = models.CharField(choices=SEMESTER_CHOICES, default='1', max_length=1)
    district = models.ForeignKey(DistrictCollege, on_delete=models.CASCADE, null=True, blank=True)
    city = models.ForeignKey(CityCollegeModel, on_delete=models.CASCADE, null=True, blank=True)
    college = models.ForeignKey(CollegeModel, on_delete=models.CASCADE, null=True, blank=True)
    branch = models.ForeignKey(CollegeBranchModel, on_delete=models.CASCADE, null=True, blank=True)
    requested_user = models.ManyToManyField(UserProfile, related_name='requested_lectures', blank=True)
    accepted_user = models.ManyToManyField(UserProfile, related_name='accepted_lectures', blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    time_to_expire_session = models.IntegerField(default=5) # In Minutes
    allow_recognize = models.BooleanField(default=False)
       
    def __str__(self):
        return self.lecture_name
    
    class Meta():
        unique_together = ('teacher', 'lecture_name')
        
    @property
    def get_absolute_url(self):
        return reverse("teacher:lec-detail", kwargs={"pk": self.pk})
    
    @property
    def get_delete_url(self):
        return reverse("teacher:lec-delete", kwargs={"pk": self.pk})

        
 
class SessionAttendanceQueryset(models.QuerySet):
    def teacher(self, teacher_pk):
        return self.filter(teacher=UserProfile.objects.get(id=teacher_pk))
 
 
class SessionAttendanceModelManager(models.Manager):

    def get_queryset(self):
        return SessionAttendanceQueryset(self.model, using=self._db)
    
    def teacher_session(self, teacher_pk):
        return self.get_queryset().teacher(teacher_pk=teacher_pk)
    
    def get_teacher_session_count(self, teacher_pk):
        return self.get_queryset().teacher(teacher_pk=teacher_pk).count()


 
 
 
import login_details.models 

  
class SessionAttendanceModel(models.Model):
    name = models.CharField(max_length=255, default="Special Lecture")
    timestamp = models.DateTimeField(auto_now_add=True)
    teacher = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True, related_name='change_website_objects')
    lecture = models.ForeignKey(LectrueModel, on_delete=models.CASCADE, null=True, blank=True, related_name='change_website_objects_lecture')
    atendees = models.ManyToManyField("login_details.LoginDetails", related_name='sessions', blank=True)
    closed = models.BooleanField(default=False)
    requested_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='requested_sessions', blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    
    
    class Meta():
        ordering = ['-id']
        
    def __str__(self):
        return self.name
    
    @property
    def get_absolute_url(self):
        return reverse("teacher:session-detail", kwargs={"pk": self.pk})
    
    
    



# class IPAddress(models.Model):
#     ipAddress1 = models.CharField(null=True, blank=True, max_length=100)
#     ipAddress2 = models.CharField(null=True, blank=True, max_length=100)
#     teacher = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    
    
#     def __str__(self):
#         return self.ipAddress1 + " " + self.ipAddress2 + " " + str(self.teacher.user.username) 
  
 
#__________________________________________________________________________________________________________ 
 
    
def user_post_save_receiver(sender, instance, *args, **kwargs):
    print()
    print()
    print()
    print()
    print(instance.email)
    print()
    print()
    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    obj = None
    try:
        obj = UserProfile.objects.get(user=instance)
    except:
        pass
        
    
    try:
        if obj is None:
            obj = UserProfile.objects.create(user=instance)
    except Exception as e:
        print(e)
        
        
    try:    
        if obj.unique_id is None:
            obj.unique_id = unique_id_generator(obj)
            obj.save()
        if obj.enrollment_number:
            if obj.enrollment_number:
                instance.enrollment_number = obj.enrollment_number
    except:
        pass

pre_save.connect(user_post_save_receiver, sender=settings.AUTH_USER_MODEL)


import datetime
def get_session_name(lecture, teacher):
    lecture_obj = SessionAttendanceModel.objects.filter(lecture=lecture, teacher=teacher).count()
    return str(str(teacher.user.username) + "'s lecture " + lecture.lecture_name +"'s session no : "+ str(lecture_obj + 1) +" on date-time : " + datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
 

def lecture_pre_save_reciver(sender, instance, *args, **kwargs):
    if not instance.teacher.user.is_teacher:
        raise Exception("selected user is not teacher")     
    if instance.pk is None:
        name = get_session_name(teacher=instance.teacher, lecture=instance)
        instance.name = name
        
        
pre_save.connect(lecture_pre_save_reciver, sender=LectrueModel)

# def user_post_save_receiver_for_teacher(sender, instance, *args, **kwargs):
#     if instance.is_staff and instance.is_teacher is False:
#         instance.is_teacher = True
#         instance.save()


# post_save.connect(user_post_save_receiver_for_teacher, sender=settings.AUTH_USER_MODEL)





