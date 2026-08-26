"""
============================================================
APP: tenants — [SHARED APP]
============================================================
Responsável por gerenciar os Tenants (empresas clientes do SaaS)
e seus Domínios. Vive no schema "public" do PostgreSQL.

Models:
  - Client: herda de TenantMixin — representa cada empresa cadastrada
  - Domain: herda de DomainMixin — mapeia subdomínios para empresas
"""

import uuid
from django_tenants.models import TenantMixin, DomainMixin
from django.db import models
from django.core.files.storage import FileSystemStorage

# Armazenamento no schema público
public_storage = FileSystemStorage(location="public")


class Client(TenantMixin):
    """
    Representa uma empresa (tenant) cadastrada no SaaS.

    Cada instância deste model cria automaticamente um schema isolado
    no PostgreSQL. O campo `schema_name` (herdado de TenantMixin) é
    usado como nome do schema — deve ser único e conter apenas letras
    minúsculas, números e underscores.

    Exemplo:
        schema_name = "ji_jardinagem" → schema PostgreSQL: ji_jardinagem
        schema_name = "levi_piscinas" → schema PostgreSQL: levi_piscinas
    """

    # Dados da empresa
    name = models.CharField(
        max_length=200,
        verbose_name="Nome da Empresa",
        help_text="Ex: Ji Jardinagem, Levi Piscinas",
    )
    cnpj = models.CharField(
        max_length=18,
        blank=True,
        null=True,
        verbose_name="CNPJ",
        help_text="Formato: XX.XXX.XXX/XXXX-XX",
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Telefone",
    )
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name="E-mail da Empresa",
    )
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name="Endereço",
    )
    logo = models.ImageField(
        upload_to="tenants/logos/",
        blank=True,
        null=True,
        verbose_name="Logo",
    )

    # Campos de auditoria e ativação por token / e-mail / WhatsApp
    created_on = models.DateField(auto_now_add=True, verbose_name="Cadastrado em")
    is_active = models.BooleanField(default=False, verbose_name="Ativo")
    activation_token = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        verbose_name="Token de Ativação",
    )

    # django-tenants: ao criar o tenant, cria o schema automaticamente
    # `auto_create_schema = True` é o padrão do TenantMixin
    auto_create_schema = True

    class Meta:
        verbose_name = "Empresa (Tenant)"
        verbose_name_plural = "Empresas (Tenants)"

    def __str__(self):
        return f"{self.name} ({self.schema_name})"


class Domain(DomainMixin):
    """
    Mapeia um domínio/subdomínio para um tenant específico.

    Cada Client pode ter múltiplos domínios (ex: domínio primário +
    aliases). O middleware do django-tenants usa esta tabela para
    identificar qual tenant deve ser ativado em cada requisição.

    Exemplo:
        domain = "ji.localhost"  → ativa o tenant "ji_jardinagem"
        domain = "levi.localhost" → ativa o tenant "levi_piscinas"
    """

    # domain e tenant são campos herdados de DomainMixin:
    # - domain: CharField com o hostname
    # - tenant: ForeignKey para o model TENANT_MODEL
    # - is_primary: BooleanField

    class Meta:
        verbose_name = "Domínio"
        verbose_name_plural = "Domínios"

    def __str__(self):
        return self.domain
