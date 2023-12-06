from django.conf import settings

DEFAULT_ALLOWED_URL_SCHEMES = ("http", "https", "ftp")

try:
    TINYLINK_VALIDATION_ENABLED = settings.TINYLINK_VALIDATION_ENABLED
except AttributeError:
    TINYLINK_VALIDATION_ENABLED = False
