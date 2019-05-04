"""
These settings are used by the ``manage.py`` command.

With normal tests we want to use the fastest possible way which is an
in-memory sqlite database but if you want to create South migrations you
need a persistant database.

Unfortunately there seems to be an issue with either South or syncdb so that
defining two routers ("default" and "south") does not work.

"""
from tinylinks.tests.test_settings import *  # NOQA


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite',
    }
}

SECRET_KEY = 'ts4u!_y8xp!yvyxtvmk3046fxaoz_ubh4n2&qtsm&*z(-d(b07'

PIWIK_ID = 1
PIWIK_URL = 'http://127.0.0.1/piwik/piwik.php'
PIWIK_TOKEN = '60a437e4e088521ca506fcfcf4f57522'

import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
GEOIP_PATH = os.path.join(BASE_DIR, 'geoip')
GEOIP_PATH = '/development/django-tinylinks/geoip'
