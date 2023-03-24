from django.contrib import admin


# Register your models here.
from .models import DistrictCollege, CityCollegeModel, CollegeModel, CollegeBranchModel

admin.site.register(DistrictCollege)
admin.site.register(CityCollegeModel)
admin.site.register(CollegeModel)
admin.site.register(CollegeBranchModel)

