"""
============================================================
URLs PÚBLICAS — servidas no schema "public" (domínio raiz)
============================================================
Ex: saas.localhost:8000 ou localhost:8000

Aqui vivem páginas como: landing page, cadastro de novas empresas,
e o admin global do SaaS.
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin global (schema público)
    path("admin/", admin.site.urls),

    # Landing page pública
    path("", TemplateView.as_view(template_name="public/landing.html"), name="landing"),

    #Cadasro de novas empresas (futuro)
    path("signup/", include("apps.signup.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
