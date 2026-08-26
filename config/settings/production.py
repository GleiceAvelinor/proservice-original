"""
Settings de PRODUÇÃO — nunca use DEBUG=True em produção.
"""
from .base import *  # noqa: F401, F403

DEBUG = False

# Segurança extra para produção
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Logging para arquivo em produção
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs" / "django.log",  # noqa: F405
        },
    },
    "root": {
        "handlers": ["file"],
        "level": "WARNING",
    },
}
