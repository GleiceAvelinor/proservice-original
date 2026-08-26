"""
Context processor para injetar dados do tenant atual em todos os templates.
"""

from django.db import connection


def tenant_context(request):
    """
    Disponibiliza o tenant atual para todos os templates.

    Uso no template:
        {{ current_tenant.name }}
        {{ current_tenant.logo.url }}
    """
    try:
        tenant = connection.tenant
    except AttributeError:
        tenant = None

    return {
        "current_tenant": tenant,
    }
