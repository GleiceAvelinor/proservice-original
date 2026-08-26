"""
============================================================
APP: signup — Views de Cadastro, Ativação e Portal de Acesso
============================================================
"""

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.views.generic import FormView, TemplateView, View
from django_tenants.utils import schema_context
import urllib.parse

from apps.tenants.models import Client, Domain
from .forms import EmpresaSignUpForm


class EmpresaSignUpView(FormView):
    """
    View pública para cadastro de uma nova empresa.
    Cadastra a empresa com STATUS INATIVO (is_active=False) e envia o link
    de ativação para autorização do Administrador Master via E-mail / WhatsApp.
    """
    template_name = "signup/signup.html"
    form_class = EmpresaSignUpForm

    def form_valid(self, form):
        data = form.cleaned_data
        schema_name = data["schema_name"]
        name = data["name"]
        cnpj = data.get("cnpj")
        email = data.get("email")
        phone = data.get("phone")

        admin_username = data["admin_username"]
        admin_email = data["admin_email"]
        admin_password = data["admin_password"]

        try:
            # 1. Cria a empresa desativada por padrão (is_active=False)
            tenant, created = Client.objects.get_or_create(
                schema_name=schema_name,
                defaults={
                    "name": name,
                    "cnpj": cnpj,
                    "email": email,
                    "phone": phone,
                    "is_active": False,
                }
            )
            if not created:
                tenant.name = name
                tenant.cnpj = cnpj
                tenant.email = email
                tenant.phone = phone
                tenant.is_active = False
                tenant.save()

            # 2. Mapeia o subdomínio (Domain)
            base_domain = getattr(settings, "BASE_DOMAIN", "localhost")
            domain_name = f"{schema_name}.{base_domain}"
            Domain.objects.get_or_create(
                domain=domain_name,
                defaults={
                    "tenant": tenant,
                    "is_primary": True,
                }
            )

            # 3. Cria ou atualiza o usuário Administrador Inicial dentro do schema do tenant
            with schema_context(schema_name):
                user = User.objects.filter(username=admin_username).first()
                if not user:
                    User.objects.create_superuser(
                        username=admin_username,
                        email=admin_email,
                        password=admin_password,
                    )
                else:
                    user.email = admin_email
                    user.set_password(admin_password)
                    user.is_staff = True
                    user.is_superuser = True
                    user.save()

            # 4. Gera o link de ativação
            activation_url = f"http://localhost:8000/signup/ativar/{tenant.activation_token}/"

            # 5. Envia notificação por e-mail para o Administrador Master e para o cliente
            master_email = getattr(settings, "DEFAULT_FROM_EMAIL", "admin@saas.com")
            subject_master = f"⚠️ [SaaS Master] Solicitação de Ativação de Empresa: {name}"
            message_master = (
                f"Uma nova empresa foi cadastrada no sistema e aguarda autorização:\n\n"
                f"Empresa: {name}\n"
                f"Subdomínio: {domain_name}\n"
                f"CNPJ: {cnpj or 'Não informado'}\n"
                f"E-mail: {email or 'Não informado'}\n"
                f"Telefone: {phone or 'Não informado'}\n\n"
                f"CLIQUE NO LINK ABAIXO PARA APROVAR E ATIVAR A EMPRESA:\n"
                f"{activation_url}\n"
            )
            try:
                send_mail(
                    subject=subject_master,
                    message=message_master,
                    from_email=master_email,
                    recipient_list=[master_email],
                    fail_silently=True,
                )

                if email:
                    subject_client = f"Cadastro Recebido — {name}"
                    message_client = (
                        f"Olá!\n\nSeu cadastro da empresa {name} foi recebido com sucesso.\n"
                        f"Por medida de segurança, o acesso ao seu subdomínio ({domain_name}) "
                        f"será liberado assim que o Administrador Master autorizar.\n\n"
                        f"Assim que ativado, você receberá a confirmação por e-mail."
                    )
                    send_mail(
                        subject=subject_client,
                        message=message_client,
                        from_email=master_email,
                        recipient_list=[email],
                        fail_silently=True,
                    )
            except Exception:
                pass

            return render(
                self.request,
                "signup/aguardando_ativacao.html",
                {
                    "tenant_name": name,
                    "domain_name": domain_name,
                    "activation_url": activation_url,
                }
            )

        except Exception as e:
            messages.error(
                self.request,
                f"Não foi possível concluir o cadastro da empresa: {str(e)}"
            )
            return self.form_invalid(form)


class EmpresaAtivarView(View):
    """
    View acionada quando o Administrador Master clica no link de ativação
    (enviado via E-mail ou WhatsApp). Ativa o tenant e libera o acesso ao subdomínio.
    """

    def get(self, request, token):
        tenant = Client.objects.filter(activation_token=token).first()
        if not tenant:
            messages.error(request, "Link de ativação inválido ou não encontrado.")
            return redirect("landing")

        tenant.is_active = True
        tenant.save(update_fields=["is_active"])

        primary_domain = tenant.domains.filter(is_primary=True).first() or tenant.domains.first()
        base_domain = getattr(settings, "BASE_DOMAIN", "localhost")
        domain_name = primary_domain.domain if primary_domain else f"{tenant.schema_name}.{base_domain}"

        # Envia e-mail de aviso ao cliente de que a conta foi liberada
        if tenant.email:
            try:
                send_mail(
                    subject=f"🎉 Sua empresa '{tenant.name}' foi ativada com sucesso!",
                    message=(
                        f"Olá!\n\nA empresa {tenant.name} foi aprovada e ativada pelo Administrador Master!\n\n"
                        f"Acesse seu painel exclusivo no link abaixo:\n"
                        f"http://{domain_name}:8000/accounts/login/\n"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[tenant.email],
                    fail_silently=True,
                )
            except Exception:
                pass

        messages.success(request, f"Empresa '{tenant.name}' ativada com sucesso pelo Administrador Master!")
        return render(
            request,
            "signup/empresa_ativada.html",
            {
                "tenant": tenant,
                "domain_name": domain_name,
            }
        )


class PortalAcessoView(TemplateView):
    """Portal de Acesso para listar empresas cadastradas e ativas."""
    template_name = "signup/portal_acesso.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tenants = Client.objects.filter(is_active=True).exclude(schema_name="public").prefetch_related("domains")
        ctx["tenants"] = tenants
        ctx["base_domain"] = getattr(settings, "BASE_DOMAIN", "localhost")
        return ctx