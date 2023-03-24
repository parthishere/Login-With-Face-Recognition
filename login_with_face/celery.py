from __future__ import absolute_import, unicode_literals

from celery import Celery
import os

    
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'login_with_face.settings')


app = Celery("login_with_face.settings")


app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.beat_schedule = {
    
}
app.autodiscover_tasks()

# Celery beat settings
    

@app.task(bind=True)
def debug_task(self):
    print(f'{self.request}')