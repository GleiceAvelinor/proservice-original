"""
============================================================
CELERY APP — Instanciação e Configuração do Celery
============================================================
Configura a aplicação do Celery para processamento de tarefas
assíncronas no sistema SaaS Multi-Tenant.
"""

import os
from celery import Celery

# Define as configurações padrão do Django para o Celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("saas")

# Carrega as configurações com prefixo 'CELERY_' do settings.py
app.config_from_object("django.conf:settings", namespace="CELERY")

# Descobre automaticamente arquivos 'tasks.py' em todos os apps registrados
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
