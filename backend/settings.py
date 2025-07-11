

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-bpx_3t9hx9zsdr@pyjom77p$69lk3hff_0g4wkz2$qo&&=hnlc'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',  # for handling CORS
    'products',
    'cart',
    'users',
    'cloudinary',
    'cloudinary_storage',
]

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'dafuavxn8',
    'API_KEY': '316334353757638',
    'API_SECRET': 'N0DdalL8X4OZCjATbG83heh4ekE',
}


DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'


MIDDLEWARE = [
    'backend.middleware.firebase_auth.FirebaseAuthenticationMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
CORS_ALLOW_CREDENTIALS = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_HTTPONLY = False  # Required for JavaScript to access CSRF token
SESSION_COOKIE_HTTPONLY = True
CORS_ALLOWED_ORIGINS = [
    # "http://localhost:3000",
    'https://ecco-font.onrender.com',
    # "http://localhost:5173",  # React's default port
    # "http://127.0.0.1:5173",
    "https://web-production-2449.up.railway.app"

]
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    'https://ecco-font.onrender.com',
    'https://web-production-2449.up.railway.app',
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# Session will expire after 1 hour (3600 seconds)
SESSION_COOKIE_AGE = 60 * 60  # 1 hour

# Optional: Keep session alive as long as the browser is open
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Optional: Save session on every request (refreshes expiry time)
SESSION_SAVE_EVERY_REQUEST = True

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'
REST_FRAMEWORK = {
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',  # for FormData
        'rest_framework.parsers.FormParser',
    ],
        'DEFAULT_AUTHENTICATION_CLASSES': [
        'users.firebase_authentication.FirebaseAuthentication',
    ],

}



# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
import dj_database_url


DATABASES = {
    'default': dj_database_url.parse(
        "postgresql://neondb_owner:npg_6NCZlEQHn9AP@ep-plain-heart-a1mhav1m-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require",
        conn_max_age=600,
        ssl_require=True
    )
}



# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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


# AUTH_USER_MODEL = 'users.User'

# Password Reset Settings
FRONTEND_URL = 'http://localhost:5173'  # Your React app's URL
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'sandybanna1137@gmail.com'  # Your Gmail address
EMAIL_HOST_PASSWORD = 'yseu jyrs kutw ysuj'  # Your App Password
DEFAULT_FROM_EMAIL = 'sandybanna1137@gmail.com'  # Must match EMAIL_HOST_USER
SERVER_EMAIL = 'sandybanna1137@gmail.com'  # For error notifications
ADMIN_EMAIL = 'sandybanna1137@gmail.com'  # Where to send contact form emails



# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

import os
import dj_database_url

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Let Whitenoise serve static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Database for Render PostgreSQL
# DATABASES = {
#     'default': dj_database_url.config(default='sqlite:///db.sqlite3')
# }
# DEBUG = False

ALLOWED_HOSTS = ["ecco-back-4j3f.onrender.com", "*"]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
