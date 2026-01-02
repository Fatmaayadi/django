import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
DEBUG = os.getenv('DEBUG', '1') == '1'
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    # Jazzmin provides a modern, friendly admin UI (install `django-jazzmin` first)
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'corsheaders',
    'events',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'events' / 'templates'],
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

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'events' / 'static']
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'events.User'

# Redirect users to the events list after logout
LOGOUT_REDIRECT_URL = '/events/'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}

CORS_ALLOW_ALL_ORIGINS = True

# Optional Jazzmin settings (branding)
JAZZMIN_SETTINGS = {
    "site_title": "Plateforme Events Admin",
    "site_header": "Plateforme Events",
    "site_brand": "Plateforme Events",
    "welcome_sign": "Bienvenue dans l'administration",
    "copyright": "Plateforme Events",
}
LOGOUT_REDIRECT_URL = '/accounts/login/'
# Add a BI quick link in Jazzmin top menu
JAZZMIN_SETTINGS.setdefault('topmenu_links', [])
JAZZMIN_SETTINGS['topmenu_links'].insert(0, {
    'name': 'BI',
    'url': '/admin/bi/',
    'new_window': False,
})

# Pour TESTER (affiche les emails dans la console) :
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Pour PRODUCTION avec votre email :
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'ayadifatma418@gmail.com'
EMAIL_HOST_PASSWORD = 'votre_mot_de_passe_d_application'  # IMPORTANT !
DEFAULT_FROM_EMAIL = 'ayadifatma418@gmail.com'
