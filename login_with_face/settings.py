"""
Django settings for login_with_face project.

Generated by 'django-admin startproject' using Django 2.2.19.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import dotenv
from datetime import timedelta

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TAMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')
MEDIA_DIR = os.path.join(BASE_DIR, 'media')

dotenv_file = os.path.join(BASE_DIR, ".env")
if os.path.isfile(dotenv_file):
    dotenv.load_dotenv(dotenv_file)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',

    'daphne',

    'django.contrib.staticfiles',

    'channels',
    'storages',
    'import_export',
    "graphene_django",

    "customuser",
    'recognizer',
    'login_details',
    'teacher',
    "chat",


    'django_filters',
    'rest_framework',
    'rest_framework.authtoken',
    'dj_rest_auth',
    'django_cleanup.apps.CleanupConfig',

    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',

    "django_celery_results",
    "django_celery_beat",

    "corsheaders",
    # 'djcelery',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

]

ROOT_URLCONF = 'login_with_face.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TAMPLATE_DIR, ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


ASGI_APPLICATION = "login_with_face.asgi.application"
# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['DATABASE_NAME'],
        'HOST': os.environ['DATABASE_HOST'],
        'PORT': os.environ['DATABASE_PORT'],
        'USER': os.environ['DATABASE_USER'],
        'PASSWORD': os.environ['DATABASE_PASSWORD'],
    }
}

# DATABASES = {

#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }


# 'default': {
#     #     'ENGINE': 'django.db.backends.postgresql',
#     #     'NAME': os.environ['DATABASE_NAME'],
#     #     'HOST': os.environ['DATABASE_HOST'],
#     #     'PORT': 5432,
#     #     'USER': os.environ['DATABASE_USER'],
#     #     'PASSWORD': os.environ['DATABASE_PASSWORD'],
#     # }

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
AWS_DEFAULT_ACL = 'public-read'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400'
}
AWS_LOCATION = 'media'
AWS_QUERYSTRING_AUTH = False
AWS_HEADERS = {'Access-Control-Allow-Origin': '*'}
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'


MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
MEDIA_ROOT = MEDIA_DIR

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = os.path.join(BASE_DIR, 'static_media/')
STATICFILES_DIRS = (
    STATIC_DIR,
)


LOGIN_REDIRECT_URL = '/'
SIGNUP_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'


DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'


# celery broker and result
CELERY_BROKER_URL = os.environ["REDIS_URL"]
CELERY_RESULT_BACKEND = os.environ["REDIS_URL"]

# CELERY_BROKER_URL = 'redis://localhost:6379/0'
# CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Kolkata'

CELERY_RESULT_BACKEND = 'django-db'

CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False


if DEBUG:
    MIDDLEWARE += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )
    INSTALLED_APPS += (
        'debug_toolbar',
    )
    INTERNAL_IPS = ('127.0.0.1', )
    import mimetypes
    mimetypes.add_type("application/javascript", ".js", True)

    # DEBUG_TOOLBAR_PATCH_SETTINGS = False

    def show_toolbar(request):
        return True

    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
        "SHOW_TOOLBAR_CALLBACK": show_toolbar,
        'INSERT_BEFORE': '</head>',
        'INTERCEPT_REDIRECTS': False,
        'RENDER_PANELS': True,
    }

AUTH_USER_MODEL = 'customuser.CustomUser'
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

os.environ['DJANGO_SETTINGS_MODULE'] = 'login_with_face.settings'
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

# CHANNEL_LAYERS = {
#     "default": {
#         "BACKEND": "channels_redis.core.RedisChannelLayer",
#         "CONFIG": {
#             "hosts": [("redis", 6379)],
#         },
#     },
# }

LOGGING = {
'version': 1,
'disable_existing_loggers': False,
'filters': {
    'require_debug_false': {
        '()': 'django.utils.log.RequireDebugFalse',
    },
    'require_debug_true': {
        '()': 'django.utils.log.RequireDebugTrue',
    },
},
'formatters': {
    'django.server': {
        '()': 'django.utils.log.ServerFormatter',
        'format': '[%(server_time)s] %(message)s',
    }
},
'handlers': {
    'console': {
        'level': 'INFO',
        'filters': ['require_debug_true'],
        'class': 'logging.StreamHandler',
    },
    # Custom handler which we will use with logger 'django'.
    # We want errors/warnings to be logged when DEBUG=False
    'console_on_not_debug': {
        'level': 'WARNING',
        'filters': ['require_debug_false'],
        'class': 'logging.StreamHandler',
    },
    'django.server': {
        'level': 'INFO',
        'class': 'logging.StreamHandler',
        'formatter': 'django.server',
    },
    'mail_admins': {
        'level': 'ERROR',
        'filters': ['require_debug_false'],
        'class': 'django.utils.log.AdminEmailHandler'
    }
},
'loggers': {
    'django': {
        'handlers': ['console', 'mail_admins', 'console_on_not_debug'],
        'level': 'INFO',
    },
    'django.server': {
        'handlers': ['django.server'],
        'level': 'INFO',
        'propagate': False,
    },
}
}


CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [os.environ.get('REDIS_URL')],
        },
    },
}


REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
}


SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=45),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,

    'ALGORITHM': 'HS256',
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

FILE_UPLOAD_HANDLERS = ("django.core.files.uploadhandler.MemoryFileUploadHandler",
                        "django.core.files.uploadhandler.TemporaryFileUploadHandler",)
ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
    (os.environ.get("ADMIN_NAME"), os.environ.get("ADMIN_EMAIL")),
)
ADMIN_USERNAME = os.environ.get("ADMIN_NAME")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")
ADMIN_INITIAL_PASSWORD = os.environ.get("ADMIN_PASSWORD")
