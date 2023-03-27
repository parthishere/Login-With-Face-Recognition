from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os
import dotenv

dotenv_file = os.path.join(settings.BASE_DIR, ".env")
if os.path.isfile(dotenv_file):
    dotenv.load_dotenv(dotenv_file)

User = get_user_model()


class Command(BaseCommand):

    def handle(self, *args, **options):
        if User.objects.filter(is_superuser=True).count() == 0:
            for user in settings.ADMINS:
                username = os.environ['ADMIN_NAME']
                email = os.environ['ADMIN_EMAIL']
                password = os.environ['ADMIN_PASSWORD']
                print('Creating account for %s (%s)' % (username, email))
                admin = User.objects.create_superuser(
                    email=email, username=username, password=password, is_active=True)
        else:
            print('Admin accounts can only be initialized if no Accounts exist')
