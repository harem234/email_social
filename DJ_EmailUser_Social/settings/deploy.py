import os
import dj_database_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# ALLOWED_HOSTS = ['0.0.0.0', 'localhost', '127.0.0.1', 'django-moon.herokuapp.com']
# development
ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    # apps
    'flexart.apps.FlexartConfig',
    'ALSTAR.apps.AlstarConfig',
    'philosophy.apps.PhilosophyConfig',
    'user.apps.UserConfig',
    'social.apps.SocialConfig',
    'SocialGoogle.apps.SocialGoogleConfig',
    # django_compressor
    # 'compressor',

    # development
    # 'django_extensions',

    'whitenoise.runserver_nostatic',
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
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
]

ROOT_URLCONF = 'DJ_EmailUser_Social.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'DJ_EmailUser_Social.wsgi.application'

# Custom user model
AUTH_USER_MODEL = 'user.EmailUser'

# email backend
# EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
# EMAIL_FILE_PATH = os.path.join(BASE_DIR, "sent_emails")

# Email: Send grid
SENDGRID_API_KEY = os.environ['SENDGRID_API_KEY']
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = SENDGRID_API_KEY
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# db_from_env = dj_database_url.config(conn_max_age=600)
# DATABASES['default'].update(db_from_env)


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

# django.contrib.sites
SITE_ID = 1

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # django-compress
    # 'compressor.finders.CompressorFinder',
)

# # Extra places for collectstatic to find static files.
# STATICFILES_DIRS = (
#     os.path.join(BASE_DIR, 'static'),
# )

# whitenoise: Add compression and caching support
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
# STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# whitenoise and django-compressor
WHITENOISE_MAX_AGE = 31536000

# allow cross origin request for public static files
WHITENOISE_ALLOW_ALL_ORIGINS = True

# Stores only files with hashed names in STATIC_ROOT
WHITENOISE_KEEP_ONLY_HASHED_FILES = True

# Media URL
MEDIA_URL = '/media/'

# django-compress


# COMPRESS_ENABLED = True
# django-compressor: to work with whitenoise and better deployment's performance
# COMPRESS_OFFLINE = True


# COMPRESS_ROOT = STATIC_ROOT

# django-compress: css options
# COMPRESS_FILTERS = {
#     'css': ['compressor.filters.css_default.CssAbsoluteFilter', 'compressor.filters.cssmin.rCSSMinFilter'],
#     'js': ['compressor.filters.jsmin.JSMinFilter']}

# 'compressor.storage.GzipCompressorFileStorage', 'compressor.storage.BrotliCompressorFileStorage', 'compressor.storage.CompressorFileStorage'
# COMPRESS_STORAGE = 'compressor.storage.BrotliCompressorFileStorage'

# end django-compress


# social google
# GOOGLE_CLIENT_FILE_PATH = os.environ['GOOGLE_CLIENT_FILE_PATH']
GOOGLE_CLIENT_FILE_PATH = os.path.join(BASE_DIR, 'SocialGoogle', 'client_secret_104908188398-lovsjp717e2brlaqkao3tjc3kjpkn4o4.apps.googleusercontent.com.json')
GOOGLE_OPTIONS = {'prompt': 'consent'}

# django 3.2
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Security Settings

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# tell browser to redirect to https rather than http!
# SECURE_SSL_REDIRECT = True

# do not redirect URLS in regex format to https if SECURE_SSL_REDIRECT is True
# SECURE_REDIRECT_EXEMPT = [r'^flex/index/$', ]

# # tell browser to use this website over https only for the next seconds,
# # after browser see his header in response it is irreversible by the server!! since we (server!) tell the browser to do
# # HTTP header, Strict-Transport-Security
# SECURE_HSTS_SECONDS = 3
#
# # whitenoise use these only if HTTPS is available
# CSRF_COOKIE_SECURE = True
# SESSION_COOKIE_SECURE = True

# # heroku
# import django_heroku
#
# # logging=False
# # databases=False
# django_heroku.settings(locals(), staticfiles=False,)
