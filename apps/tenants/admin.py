"""
Admin para os models de Tenant — apenas no schema público.
Permite gerenciar empresas e seus domínios pelo Django Admin.
"""

import urllib.parse
from django.contrib import admin
from django.utils.html import format_html
from django_tenants.admin import TenantAdminMixin

from .models import Client, Domain


class DomainInline(admin.TabularInline):
    """Gerencia domínios inline dentro do admin de Client."""
    model = Domain
    extra = 1
    fields = ("domain", "is_primary")


@admin.register(Client)
class ClientAdmin(TenantAdminMixin, admin.ModelAdmin):
    """
    Admin para o model Client (Tenant).
    Permite visualizar, ativar/aprovar empresas via ação em lote,
    link direto de ativação e envio de mensagem no WhatsApp.
    """
    list_display = ("name", "schema_name", "email", "phone", "is_active", "created_on", "link_ativacao", "whatsapp_ativacao")
    list_filter = ("is_active", "created_on")
    search_fields = ("name", "schema_name", "cnpj", "email", "phone")
    inlines = [DomainInline]
    readonly_fields = ("created_on", "activation_token", "link_ativacao_completo")
    actions = ["ativar_empresas_selecionadas", "desativar_empresas_selecionadas"]

    fieldsets = (
        ("Identificação", {
            "fields": ("name", "schema_name", "cnpj"),
        }),
        ("Contato", {
            "fields": ("email", "phone", "address"),
        }),
        ("Aparência", {
            "fields": ("logo",),
        }),
        ("Status e Ativação", {
            "fields": ("is_active", "activation_token", "link_ativacao_completo", "created_on"),
        }),
    )

    @admin.action(description="🟢 Aprovar e Ativar Empresas Selecionadas")
    def ativar_empresas_selecionadas(self, request, queryset):
        rows_updated = queryset.update(is_active=True)
        self.message_user(request, f"✅ {rows_updated} empresa(s) aprovada(s) e ativada(s) com sucesso!")

    @admin.action(description="🔴 Suspender / Desativar Empresas Selecionadas")
    def desativar_empresas_selecionadas(self, request, queryset):
        rows_updated = queryset.update(is_active=False)
        self.message_user(request, f"🔒 {rows_updated} empresa(s) suspensa(s) com sucesso!")

    @admin.display(description="Link Ativação")
    def link_ativacao(self, obj):
        if not obj.is_active:
            url = f"http://localhost:8000/signup/ativar/{obj.activation_token}/"
            return format_html(
                '<a href="{}" target="_blank" style="background-color: #2563eb; color: white; padding: 3px 8px; border-radius: 4px; text-decoration: none; font-size: 11px; font-weight: bold;">Ativar</a>',
                url
            )
        return format_html('<span style="color: green; font-weight: bold;">Ativo</span>')

    @admin.display(description="WhatsApp Liberação")
    def whatsapp_ativacao(self, obj):
        if obj.phone:
            num = "".join(filter(str.isdigit, str(obj.phone)))
            if num:
                url_ativacao = f"http://localhost:8000/signup/ativar/{obj.activation_token}/"
                texto = (
                    f"Olá! Suas credenciais da empresa '{obj.name}' foram pré-cadastradas.\n"
                    f"Para liberar e ativar o seu acesso, clique no link oficial:\n{url_ativacao}"
                )
                wa_url = f"https://wa.me/55{num}?text={urllib.parse.quote(texto)}"
                return format_html(
                    '<a href="{}" target="_blank" style="background-color: #25d366; color: white; padding: 3px 8px; border-radius: 4px; text-decoration: none; font-size: 11px; font-weight: bold;">Enviar WhatsApp</a>',
                    wa_url
                )
        return "-"

    @admin.display(description="Link de Ativação Completo")
    def link_ativacao_completo(self, obj):
        url = f"http://localhost:8000/signup/ativar/{obj.activation_token}/"
        return format_html('<a href="{}" target="_blank">{}</a>', url, url)


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ("domain", "tenant", "is_primary")
    list_filter = ("is_primary",)
    search_fields = ("domain",)
