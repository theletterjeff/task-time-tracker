import dj_database_url

from .base import *

DEBUG = False

ALLOWED_HOSTS = [
    'task-time-tracker.herokuapp.com',
]

INSTALLED_APPS += [
    'whitenoise.runserver_nostatic',
]

MIDDLEWARE += [
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(db_from_env)