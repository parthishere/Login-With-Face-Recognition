from django.db import models

# Create your models here.
class DistrictCollege(models.Model):
    district_name = models.CharField(max_length=50, null=True, blank=True)
    
    def __str__(self):
        return self.district_name

class CityCollegeModel(models.Model):
    district = models.ForeignKey(DistrictCollege, on_delete=models.CASCADE, null=True, blank=True)
    city_name = models.CharField(max_length=50, null=True, blank=True)
    def __str__(self):
        return self.district.ditrict_name + " " + self.city_name 

class CollegeModel(models.Model):
    city = models.ForeignKey(CityCollegeModel, on_delete=models.CASCADE, null=True, blank=True)
    college_name = models.CharField(max_length=50, null=True, blank=True)
    
    def __str__(self):
        return self.district.ditrict_name + " " + self.city_name + " " + self.college_name
    
class CollegeBranchModel(models.Model):
    college = models.ForeignKey(CollegeModel, on_delete=models.CASCADE, null=True, blank=True)
    branch_name = models.CharField(max_length=50, null=True, blank=True)
    
    def __str__(self):
        return self.college_name + " " + self.branch_name




