from django.contrib import admin

from .models import UserProfile, LectrueModel, SessionAttendanceModel

class LectureModelAdmin(admin.ModelAdmin):
    list_display = (
        "__str__", "id"
        )
    
class SessionModelAdmin(admin.ModelAdmin):
    list_display= (
        "__str__", "id"
    )

admin.site.register(UserProfile)
admin.site.register(LectrueModel, LectureModelAdmin)
admin.site.register(SessionAttendanceModel, SessionModelAdmin)





