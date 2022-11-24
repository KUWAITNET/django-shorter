from django.conf import settings

DEFAULT_ALLOWED_URL_SCHEMES = ("http", "https", "ftp")
VALIDATION_ENABLED = False

try:
    VALIDATION_ENABLED = settings.VALIDATION_ENABLED
except:
    pass
