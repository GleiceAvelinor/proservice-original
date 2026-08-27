"""
============================================================
SETTINGS BASE — Configuração compartilhada entre todos os ambientes
============================================================
Este arquivo NÃO deve ser usado diretamente. Use development.py ou production.py.
As configurações críticas de django-tenants estão aqui.
"""

from pathlib import Path
from decouple import config

# ─── Diretórios base ───────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # raiz do projeto

# ─── Segurança ─────────────────────────────────────────────────────────────────
SECRET_KEY = config("SECRET_KEY", default="django-insecure-saas-multi-tenant-dev-key-change-in-production-123456789")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost").split(",")

# ─── django-tenants: DATABASE_ROUTERS ─────────────────────────────────────────
# Obrigatório para o roteamento multi-schema funcionar corretamente
DATABASE_ROUTERS = ("django_tenants.routers.TenantSyncRouter",)

# ─── SHARED APPS ───────────────────────────────────────────────────────────────
# Apps que vivem no schema "public" (compartilhado por todos os tenants).
# Inclui: gestão de tenants, autenticação global e admin do Django.
SHARED_APPS = [
    # django-tenants deve ser o PRIMEIRO da lista
    "django_tenants",

    # App de gerenciamento dos tenants (nosso Client e Domain)
    "apps.tenants",
    "apps.signup",

    # Apps Django padrão no schema público
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.admin",
    "django.contrib.staticfiles",

    # Third-party shared
    "crispy_forms",
    "crispy_bootstrap5",
    "django_celery_results",
]

# ─── TENANT APPS ───────────────────────────────────────────────────────────────
# Apps que vivem em schemas isolados de cada tenant.
# Cada empresa terá sua própria instância dessas tabelas.
TENANT_APPS = [
    # Django padrão replicado em cada schema de tenant
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.admin",

    # Nossas apps de negócio isoladas por tenant
    "apps.clientes",
    "apps.catalogo",
    "apps.propostas",
    "apps.dashboard",
    "apps.accounts",
]

# django-tenants exige que INSTALLED_APPS seja a união de SHARED + TENANT,
# sem duplicatas. O helper abaixo faz isso automaticamente.
INSTALLED_APPS = list(SHARED_APPS) + [
    app for app in TENANT_APPS if app not in SHARED_APPS
]

# ─── Model de Tenant ───────────────────────────────────────────────────────────
# Aponta para nosso model que herda de TenantMixin
TENANT_MODEL = "tenants.Client"

# ─── Model de Domínio ──────────────────────────────────────────────────────────
# Aponta para nosso model que herda de DomainMixin
TENANT_DOMAIN_MODEL = "tenants.Domain"

# ─── Middleware ────────────────────────────────────────────────────────────────
# TenantMainMiddleware DEVE ser o primeiro middleware da lista.
# Ele identifica o tenant pelo subdomínio da requisição e
# seta o schema correto no PostgreSQL para toda a requisição.
MIDDLEWARE = [
    "django_tenants.middleware.main.TenantMainMiddleware",  # ← PRIMEIRO!
    "apps.tenants.middleware.TenantActiveMiddleware",       # ← Bloqueia empresas com is_active=False!
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ─── URLs ──────────────────────────────────────────────────────────────────────
ROOT_URLCONF = "config.urls"

# ─── Templates ─────────────────────────────────────────────────────────────────
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # Contexto customizado para injetar dados do tenant nos templates
                "apps.tenants.context_processors.tenant_context",
            ],
        },
    },
]

# ─── WSGI / ASGI ───────────────────────────────────────────────────────────────
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ─── Banco de Dados ────────────────────────────────────────────────────────────
# django-tenants EXIGE que o ENGINE seja django_tenants.postgresql_backend
DATABASES = {
    "default": {
        "ENGINE": "django_tenants.postgresql_backend",
        "NAME": config("DB_NAME", default="postgres"),
        "USER": config("DB_USER", default="postgres"),
        "PASSWORD": config("DB_PASSWORD", default=""),
        "HOST": config("DB_HOST", default="aws-0-sa-east-1.supabase.com"),
        "PORT": config("DB_PORT", default="5432"),
        "OPTIONS": {
            "sslmode": config("DB_SSLMODE", default="require"),
        },
    }
}

# ─── Autenticação ──────────────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = "/accounts/login/"

# ─── Internacionalização ───────────────────────────────────────────────────────
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# ─── Arquivos Estáticos ────────────────────────────────────────────────────────
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# ─── Default primary key ───────────────────────────────────────────────────────
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ─── Crispy Forms ──────────────────────────────────────────────────────────────
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# ─── django-tenants: URLs públicas ─────────────────────────────────────────────
# URLs que serão servidas no schema público (tenant principal = public)
PUBLIC_SCHEMA_URLCONF = "config.urls_public"

# ─── Configurações de E-mail ───────────────────────────────────────────────────
EMAIL_BACKEND = config("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="propostas@saas.com")

# ─── Configurações do Celery & Redis ───────────────────────────────────────────
CELERY_BROKER_URL = config("CELERY_BROKER_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = config("CELERY_RESULT_BACKEND", default="django-db")
CELERY_CACHE_BACKEND = "django-cache"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60

# ─── Controle de Acesso Nível SaaS ────────────────────────────────────────────
# Lista de e-mails dos Administradores Globais do SaaS (Master do Produto).
# Somente esses usuários têm permissão para alterar a logomarca de qualquer tenant.
# Diferente de is_superuser=True que também pode ser concedido a admins locais de subdomínio.
# Formato no .env: SAAS_ADMIN_EMAILS=admin@saas.com,master@empresa.com
_saas_admin_emails_raw = config("SAAS_ADMIN_EMAILS", default="")
SAAS_ADMIN_EMAILS = [e.strip() for e in _saas_admin_emails_raw.split(",") if e.strip()]
