# Importa a instância do Celery para que o decorador @shared_task o utilize sempre
from .celery import app as celery_app

__all__ = ("celery_app",)
