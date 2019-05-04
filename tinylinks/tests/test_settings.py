"""Settings that need to be set in order to run the tests."""
import os

DEBUG = True
USE_TZ = True
SITE_ID = 1

TINYLINK_LENGTH = 5
TINYLINK_CHECK_INTERVAL = 10
TINYLINK_CHECK_PERIOD = 300

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

CURRENT_DIR = os.path.dirname(__file__)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

ROOT_URLCONF = 'tinylinks.tests.urls'

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.admindocs',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django.contrib.sites',
    'rest_framework',
]

CUSTOM_APPS = [
    'tinylinks',
]

INSTALLED_APPS = DJANGO_APPS + CUSTOM_APPS

# JASMINE_TEST_DIRECTORY = os.path.join(CURRENT_DIR, 'jasmine_tests')
#
# COVERAGE_REPORT_HTML_OUTPUT_DIR = os.path.join(
#     CURRENT_DIR, 'coverage')
#
# COVERAGE_MODULE_EXCLUDES = [
#     'tests$', 'test_app$', 'settings$', 'urls$', 'locale$',
#     'migrations', 'fixtures', 'admin$', 'django_extensions', EXTERNAL_APPS
# ]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(os.path.join(CURRENT_DIR, "templates"))],
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

MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(CURRENT_DIR, '../../static/')

STATICFILES_DIRS = (
    os.path.join(CURRENT_DIR, 'test_static'),
)
