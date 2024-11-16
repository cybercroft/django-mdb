"""
Django settings for mdb project.

Generated by 'django-admin startproject' using Django 3.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
INSECURE_KEY = 'django-insecure-&m4i)a4-akl69^-_sfkw#gp@#sy5cdzz%38_9q9!%2o6#txy#d'
SECRET_KEY = os.getenv("SECRET_KEY", default=INSECURE_KEY)


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = int(os.getenv("DEBUG", default=1))

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", default="127.0.0.1").split(",")


# Application definition

INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # My apps
    'inventory',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mdb.urls'

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

WSGI_APPLICATION = 'mdb.wsgi.application'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

MEDIA_URL = '/media/'
STATIC_URL = '/static/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
if not DEBUG:
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')
    
IMPORT_DIR = 'import'
EXPORT_DIR = 'export'

IMPORT_PATH = os.path.join(MEDIA_ROOT, IMPORT_DIR)
EXPORT_PATH = os.path.join(MEDIA_ROOT, EXPORT_DIR)


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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = os.getenv('TIME_ZONE', default='UTC')

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

# Get the active database versions from the environment (if any)
db_versions_active = os.getenv('DB_VERSIONS_ACTIVE', None)
DB_VERSIONS_ACTIVE = [] if db_versions_active is None else db_versions_active.split(',')

# Ensure the import_path exists (create if necessary)
import_path_obj = Path(IMPORT_PATH)
if not import_path_obj.exists():
    import_path_obj.mkdir(parents=True, exist_ok=True)

# Get a list of all subfolders (database versions) in the import folder
DB_VERSIONS = [f.name for f in import_path_obj.iterdir() if f.is_dir()]

# Common database settings
db_password = os.getenv('POSTGRES_PASSWORD', 'db_password')
db_user = os.getenv('POSTGRES_USER', 'db_user')
db_name = os.getenv('POSTGRES_DB', 'db_default')
db_engine = os.getenv('DB_ENGINE', 'django.db.backends.postgresql')
db_host = os.getenv('DB_HOST', 'localhost')
db_port = os.getenv('DB_PORT', '5432')

# Set the Main database (stuff not depending on version)
DATABASES = {
    'default': {
        'ENGINE': db_engine,
        'NAME': db_name,
        'USER': db_user,
        'PASSWORD': db_password,
        'HOST': db_host,
        'PORT': db_port,
    }
}

# Set other databases (stuff depending on version)
for version in DB_VERSIONS:
    DATABASES[version] = {
        'ENGINE': db_engine,
        'NAME': version,
        'USER': db_user,
        'PASSWORD': db_password,
        'HOST': db_host,
        'PORT': db_port,
    }

DATABASE_ROUTERS = ['inventory.db_router.VersionDatabaseRouter']
