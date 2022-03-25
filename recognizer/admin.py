from django.contrib import admin


from .models import UserProfile, TeacherProfileModel, LectrueModel, ChangeWebsiteCount
# Register your models here.

admin.site.register(UserProfile)
admin.site.register(TeacherProfileModel)
admin.site.register(LectrueModel)
admin.site.register(ChangeWebsiteCount)