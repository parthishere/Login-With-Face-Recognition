web: daphne login_with_face.asgi:application --port $PORT --bind 0.0.0.0 -v2
celery: celery -A login_with_face worker -l INFO -E
celerybeat: celery -A login_with_face beat -l INFO