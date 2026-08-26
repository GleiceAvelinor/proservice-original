"""Views para gerenciamento do perfil e logo da empresa."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.views.generic import UpdateView
from django.db import connection

from .models import Client
from .forms import EmpresaForm
from .permissions import is_saas_admin


class EmpresaConfigView(LoginRequiredMixin, UpdateView):
    """
    View para o tenant editar seus próprios dados e fazer upload da logo personalizada.

    Hierarquia de Permissão:
        - Dados gerais (nome, CNPJ, etc.): qualquer usuário autenticado do tenant pode alterar.
        - Upload / remoção da LOGO: EXCLUSIVO para o Admin Global do SaaS
          (e-mail cadastrado em settings.SAAS_ADMIN_EMAILS).
          Mesmo um admin do subdomínio com is_superuser=True é BLOQUEADO → HTTP 403 Forbidden.
    """
    model = Client
    form_class = EmpresaForm
    template_name = "tenants/empresa_form.html"
    success_url = reverse_lazy("tenants:empresa-config")

    def get_object(self, queryset=None):
        return connection.tenant

    def get_form_kwargs(self):
        """Injeta o usuário atual no EmpresaForm para controle da permissão de logo."""
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["user_is_saas_admin"] = is_saas_admin(self.request.user)
        return ctx

    def post(self, request, *args, **kwargs):
        """
        Intercepta qualquer tentativa de envio de arquivo de logo por usuários não autorizados.
        Retorna HTTP 403 Forbidden sem processar o formulário.
        """
        if "logo" in request.FILES and not is_saas_admin(request.user):
            raise PermissionDenied(
                "A alteração da logomarca é restrita exclusivamente ao Administrador Global do SaaS."
            )
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "✅ Dados da empresa atualizados com sucesso!")
        return super().form_valid(form)
