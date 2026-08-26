"""
============================================================
MIDDLEWARE: TenantActiveMiddleware
============================================================
Garante o bloqueio imediato de acesso a qualquer subdomínio
de empresa (tenant) cujo campo `is_active` esteja definido como False.
"""

from django.db import connection
from django.shortcuts import render


class TenantActiveMiddleware:
    """
    Verifica se a empresa (Tenant) associada à requisição atual está ativa.
    Caso `tenant.is_active` seja False, bloqueia o acesso e exibe a tela de suspensão.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tenant = getattr(request, "tenant", None) or getattr(connection, "tenant", None)

        if tenant and getattr(tenant, "schema_name", "public") != "public":
            if not getattr(tenant, "is_active", True):
                return render(
                    request,
                    "tenants/empresa_inativa.html",
                    {"tenant": tenant},
                    status=403,
                )

        return self.get_response(request)
