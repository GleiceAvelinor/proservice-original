"""
Settings de PRODUÇÃO — nunca use DEBUG=True em produção.
"""
from pathlib import Path
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

# Garante que o diretório de logs existe antes de configurar o logging para arquivo
LOGS_DIR = BASE_DIR / "logs"  # noqa: F405
LOGS_DIR.mkdir(exist_ok=True)

# Logging para arquivo em produção
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": LOGS_DIR / "django.log",
        },
    },
    "root": {
        "handlers": ["file"],
        "level": "WARNING",
    },
}
DATABASES["default"]["OPTIONS"] = {
    "sslmode": "require",
    "target_session_attrs": "read-write",
    "application_name": "django-tenants",
}