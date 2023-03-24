# Procfile

web: daphne login_with_face.asgi:application -v2
celery: celery -A login_with_face worker -l INFO -E
celerybeat: celery -A login_with_face beat -l INFO