# Procfile

web: gunicorn login_with_face.wsgi:application -b 0.0.0.0:8000
celery: celery -A login_with_face worker -l INFO -E
celerybeat: celery -A login_with_face beat -l INFO