from django.core.management.base import BaseCommand
from faker import Faker
import faker.providers



class Command(BaseCommand):
    help = "Command Information"
    
    def handle(self, *args, **kwargs):
        
        fake = Faker()
        print(fake.name())
        