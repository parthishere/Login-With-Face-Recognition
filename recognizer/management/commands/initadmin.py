from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os
import dotenv
from recognizer.models import UserProfile, LectrueModel
from teacher.models import DistrictCollege, CityCollegeModel, CollegeModel, CollegeBranchModel

dotenv_file = os.path.join(settings.BASE_DIR, ".env")
if os.path.isfile(dotenv_file):
    dotenv.load_dotenv(dotenv_file)

User = get_user_model()


class Command(BaseCommand):

    def handle(self, *args, **options):
        if User.objects.filter(is_superuser=True).count() == 0:
            
            username = os.environ['ADMIN_NAME']
            email = os.environ['ADMIN_EMAIL']
            password = os.environ['ADMIN_PASSWORD']
            print('Creating account for %s (%s) with password %s' % (username, email, password))
            admin = User.objects.create_superuser(
                email=email, username=username, password=password, is_active=True, is_teacher=True)
            
            gujrat_state = DistrictCollege.objects.create(district_name="Gujrat")
            rajasthan_state = DistrictCollege.objects.create(district_name="Rajasthan")
            
            ahm = CityCollegeModel.objects.create(district=gujrat_state, city_name="Ahmedabad")
            rajkot = CityCollegeModel.objects.create(district=gujrat_state, city_name="Rajkot")
            ajmer = CityCollegeModel.objects.create(district=rajasthan_state, city_name="Ajmer")
            jaipur = CityCollegeModel.objects.create(district=rajasthan_state, city_name="Jaipur")
            
            ld = CollegeModel.objects.create(city=ahm, college_name="LD College of Engineering")
            gec = CollegeModel.objects.create(city=rajkot, college_name="GEC")
            
            ajmed_ld = CollegeModel.objects.create(city=ajmer, college_name="LD College of Engineering, Ajmer branch")
            jaipur_branch = CollegeModel.objects.create(city=jaipur, college_name="LD College of Engineering, Jaipur branch")
            
            
            ec_branch = CollegeBranchModel.objects.create(college=ld, branch_name="Electronics and Communication")
            computer_branch = CollegeBranchModel.objects.create(college=ld, branch_name="Comupter")
            
            print(admin)
            # admin_up = UserProfile.objects.get(user=admin)
            # admin_up.gender="M"
            # admin_up.college=ld
            # admin_up.city = ahm
            # admin_up.branch = ec_branch
            # admin_up.save()
                
                
                
                
                
        else:
            print('Admin accounts can only be initialized if no Accounts exist')
