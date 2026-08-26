"""URLs do módulo de Tenants (Empresa)."""

from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = "tenants"

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="tenants:empresa-config", permanent=False)),
    path("configuracoes/", views.EmpresaConfigView.as_view(), name="empresa-config"),
]
