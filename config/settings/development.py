"""
Settings de DESENVOLVIMENTO — importa tudo do base e ativa extras de debug.
"""
from .base import *  # noqa: F401, F403

DEBUG = True

# Django Debug Toolbar (opcional, instale com: pip install django-debug-toolbar)
# INSTALLED_APPS += ["debug_toolbar"]
# MIDDLEWARE.insert(1, "debug_toolbar.middleware.DebugToolbarMiddleware")
# INTERNAL_IPS = ["127.0.0.1"]

# Email (lê do .env ou usa o backend SSL customizado)
EMAIL_BACKEND = config("EMAIL_BACKEND", default="config.email_backend.SSLEmailBackend")

# Celery síncrono em dev (dispara e-mails imediatamente sem precisar do worker rodando)
CELERY_TASK_ALWAYS_EAGER = config("CELERY_TASK_ALWAYS_EAGER", default=True, cast=bool)
CELERY_TASK_EAGER_PROPAGATES = True

# Logging detalhado das queries SQL
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django.db.backends": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
        "django_tenants": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
    },
}
