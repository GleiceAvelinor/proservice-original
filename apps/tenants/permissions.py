"""
Utilitários de permissão para controle de acesso por nível (SaaS Admin vs Tenant Admin).

Hierarquia de permissões:
  - SaaS Admin (Master do Produto): E-mail listado em settings.SAAS_ADMIN_EMAILS.
    Controla configurações globais: logomarca dos tenants, criação/remoção de tenants, etc.
  - Tenant Admin (Administrador do Subdomínio): is_superuser=True dentro do schema do tenant.
    Controla apenas os recursos dentro da sua própria empresa.
"""

from django.conf import settings


def is_saas_admin(user) -> bool:
    """
    Retorna True somente se o usuário for o Administrador Global do SaaS.

    A verificação é feita pelo e-mail cadastrado em settings.SAAS_ADMIN_EMAILS.
    Esta função NUNCA retorna True baseado apenas em is_superuser, pois admins
    locais de subdomínio também podem ter is_superuser=True dentro do seu schema.

    Quando SAAS_ADMIN_EMAILS estiver vazio (não configurado), a função retorna
    False para todos — negação por padrão (fail-safe).

    Configure no .env:
        SAAS_ADMIN_EMAILS=admin@saas.com,outro@admin.com

    Uso:
        from apps.tenants.permissions import is_saas_admin
        if is_saas_admin(request.user):
            ...
    """
    if not user or not user.is_authenticated:
        return False

    saas_emails = getattr(settings, "SAAS_ADMIN_EMAILS", [])

    # Lista vazia → ninguém tem a permissão (fail-safe).
    # Configure SAAS_ADMIN_EMAILS no .env para habilitar.
    if not saas_emails:
        return False

    return bool(user.email) and user.email in saas_emails
