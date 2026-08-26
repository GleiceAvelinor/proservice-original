"""
============================================================
URLs PRINCIPAIS DO TENANT — servidas em cada subdomínio isolado
============================================================
Ex: ji.localhost:8000, levi.localhost:8000

django-tenants usa duas URLs distintas:
  - config/urls.py        → para todos os tenants (subdomínios)
  - config/urls_public.py → para o schema público (domínio raiz)
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin do Django (acessível em cada tenant)
    path("admin/", admin.site.urls),

    # Autenticação
    path("accounts/", include("apps.accounts.urls")),
    path("accounts/", include("django.contrib.auth.urls")),

    # Apps do tenant
    path("dashboard/", include("apps.dashboard.urls")),
    path("clientes/", include("apps.clientes.urls")),
    path("catalogo/", include("apps.catalogo.urls")),
    path("propostas/", include("apps.propostas.urls")),
    path("empresa/", include("apps.tenants.urls")),

    # Redireciona raiz para o dashboard
    path("", RedirectView.as_view(url="/dashboard/", permanent=False)),
]

# Servir arquivos de mídia em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
