from .settings_deploy import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# ALLOWED_HOSTS = ('django-moon.herokuapp.com',)
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]', 'django-moon.herokuapp.com']
# ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    # apps
    'flexart.apps.FlexartConfig',
    'ALSTAR.apps.AlstarConfig',
    'philosophy.apps.PhilosophyConfig',
    'user.apps.UserConfig',
    'social.apps.SocialConfig',
    'SocialGoogle.apps.SocialGoogleConfig',
    # django_compressor
    'compressor',

    'django_extensions',
]

# # heroku
# import django_heroku

# # logging=False
# # databases=False
# django_heroku.settings(locals(), staticfiles=False,)
