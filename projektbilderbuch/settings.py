"""
Django settings for projektbilderbuch project.

Generated by 'django-admin startproject' using Django 3.2.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
from pathlib import Path
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/


# SECURITY WARNING: don't run with debug turned on in production!
# When we are deploying on render, there will be a RENDER environment variable
RENDER = 'RENDER' in os.environ

# If we are not on RENDER, we are in debug environment
DEBUG = False

# SECURITY WARNING: keep the secret key used in production secret!
if RENDER:
    SECRET_KEY = os.getenv('SECRET_KEY')
else:
    SECRET_KEY = 'django-insecure-4w!uv4akfp_edkdr!+3p85-2a^ak6deir=h$&w^-nzd7vwaf03'

ALLOWED_HOSTS = []

if RENDER:
    ALLOWED_HOSTS.append(os.environ.get('RENDER_EXTERNAL_HOSTNAME'))
else:
    ALLOWED_HOSTS.append('127.0.0.1')
    ALLOWED_HOSTS.append('localhost')

# Application definition

INSTALLED_APPS = [
    'administrator.apps.AdministratorConfig',
    'betreiber.apps.BetreiberConfig',
    'endnutzer.apps.EndnutzerConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'projektbilderbuch.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'projektbilderbuch.wsgi.application'

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

if RENDER:
    db_url = os.getenv('DATABASE_URL')
    DATABASES = {
        'default': dj_database_url.config(default=db_url)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'de-de'

TIME_ZONE = 'Europe/Berlin'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

if RENDER:
    PERSISTENT_STORAGE_ROOT = '/var/data'
    STATICFILES_DIRS = [Path(PERSISTENT_STORAGE_ROOT) / 'static']

    STATIC_ROOT = BASE_DIR / "staticfiles"
    STATIC_URL = '/static/'
else:
    PERSISTENT_STORAGE_ROOT = os.path.join('/Test')
    STATICFILES_DIRS = [Path(PERSISTENT_STORAGE_ROOT)]

    STATIC_ROOT = BASE_DIR / "staticfiles"
    STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Setting our custom User model for authorization
AUTH_USER_MODEL = 'betreiber.User'

# Setting up email backend for password emails
if os.getenv('GMAIL_PW') is None:
    EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
    EMAIL_FILE_PATH = 'tmp/app-messages'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_HOST_USER = 'projekt.bilderbuch@gmail.com'
    EMAIL_HOST_PASSWORD = os.getenv('GMAIL_PW')
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_USE_SSL = False
    DEFAULT_FROM_EMAIL = 'projekt.bilderbuch@gmail.com'

DATA_UPLOAD_MAX_NUMBER_FIELDS = None 

WHITENOISE_USE_FINDERS = True
