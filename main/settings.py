import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# =============================================================================
# SECURITY
# =============================================================================
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-change-me-in-production')
DEBUG = os.getenv('DJANGO_DEBUG', 'False').lower() == 'true'

env_hosts = os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
if DEBUG:
    if 'localhost' not in env_hosts:
        env_hosts.append('localhost')
    if '127.0.0.1' not in env_hosts:
        env_hosts.append('127.0.0.1')

ALLOWED_HOSTS = env_hosts

# =============================================================================
# APPS
# =============================================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'videos',
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

ROOT_URLCONF = 'main.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'main.wsgi.application'

# =============================================================================
# DATABASE
# =============================================================================
DEBUG_MODE = os.getenv('DJANGO_DEBUG', 'False').lower() == 'true'
print(f"🔍 DEBUG_MODE = {DEBUG_MODE}")

if not DEBUG_MODE:
    DB_PATH = '/data/db.sqlite3'
    MEDIA_ROOT = '/data/media'
else:
    DB_PATH = BASE_DIR / 'db.sqlite3'
    MEDIA_ROOT = BASE_DIR / 'media'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DB_PATH,
    }
}

# =============================================================================
# PASSWORD VALIDATION
# =============================================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# =============================================================================
# INTERNATIONALIZATION
# =============================================================================
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# =============================================================================
# STATIC & MEDIA
# =============================================================================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = MEDIA_ROOT

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =============================================================================
# CSRF & SESSION
# =============================================================================
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = False
CSRF_TRUSTED_ORIGINS = [
    f"https://{host}" for host in ALLOWED_HOSTS if host not in ['localhost', '127.0.0.1']
] + [
    f"http://{host}" for host in ALLOWED_HOSTS if host not in ['localhost', '127.0.0.1']
]

SESSION_COOKIE_AGE = 86400
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = False

# =============================================================================
# SECURITY FOR PRODUCTION
# =============================================================================
X_FRAME_OPTIONS = 'SAMEORIGIN'
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SECURE_REFERRER_POLICY = None

# =============================================================================
# LOGGING
# =============================================================================
if os.getenv('AMVERA_DEPLOYMENT', 'false').lower() == 'true':
    LOG_FILE = '/data/django.log'
else:
    LOG_FILE = BASE_DIR / 'django.log'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': str(LOG_FILE),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# =============================================================================
# VIDEO UPLOAD SETTINGS
# =============================================================================
VIDEO_UPLOAD_MAX_MEMORY_SIZE = 500 * 1024 * 1024  # 500MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 500 * 1024 * 1024  # 500MB

ALLOWED_VIDEO_EXTENSIONS = ['mp4', 'webm', 'mov', 'avi', 'mkv']
MAX_VIDEO_SIZE_MB = 500