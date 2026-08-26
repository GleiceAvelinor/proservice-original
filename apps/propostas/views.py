"""
Views do módulo de Propostas Comerciais.

Inclui CRUD completo, exportação para PDF, envio assíncrono via Celery e views públicas de aprovação.
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views import View
from django.db import transaction, connection

from .models import Proposta, StatusProposta
from .forms import PropostaForm, ItemPropostaFormSet
from .services.pdf_service import gerar_pdf_proposta


class PropostaListView(LoginRequiredMixin, ListView):
    model = Proposta
    template_name = "propostas/lista.html"
    context_object_name = "propostas"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related("cliente")

        # Filtros da barra de pesquisa
        status = self.request.GET.get("status")
        q = self.request.GET.get("q")

        if status:
            qs = qs.filter(status=status)
        if q:
            qs = qs.filter(cliente__nome__icontains=q) | qs.filter(numero__icontains=q)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["status_choices"] = StatusProposta.choices
        ctx["status_filtro"] = self.request.GET.get("status", "")
        ctx["q"] = self.request.GET.get("q", "")

        # Contadores por status (para os badges no topo)
        ctx["total_pendentes"] = Proposta.objects.filter(status=StatusProposta.PENDENTE).count()
        ctx["total_aprovadas"] = Proposta.objects.filter(status=StatusProposta.APROVADA).count()
        return ctx


class PropostaDetailView(LoginRequiredMixin, DetailView):
    model = Proposta
    template_name = "propostas/detalhe.html"
    context_object_name = "proposta"

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            "itens__produto", "itens__servico"
        ).select_related("cliente")


class PropostaCreateView(LoginRequiredMixin, CreateView):
    """
    View de criação de proposta com InlineFormSet para os itens.
    Usa transação atômica para garantir consistência dos dados.
    """
    model = Proposta
    form_class = PropostaForm
    template_name = "propostas/form.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titulo"] = "Nova Proposta Comercial"
        if self.request.POST:
            ctx["formset"] = ItemPropostaFormSet(self.request.POST)
        else:
            ctx["formset"] = ItemPropostaFormSet()
        return ctx

    @transaction.atomic
    def form_valid(self, form):
        ctx = self.get_context_data()
        formset = ctx["formset"]

        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            messages.success(self.request, f"Proposta {self.object.numero} criada com sucesso!")
            return redirect(self.get_success_url())
        else:
            messages.error(self.request, "Corrija os erros nos itens da proposta.")
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse("propostas:detalhe", kwargs={"pk": self.object.pk})


class PropostaUpdateView(LoginRequiredMixin, UpdateView):
    model = Proposta
    form_class = PropostaForm
    template_name = "propostas/form.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titulo"] = f"Editar Proposta {self.object.numero}"
        if self.request.POST:
            ctx["formset"] = ItemPropostaFormSet(self.request.POST, instance=self.object)
        else:
            ctx["formset"] = ItemPropostaFormSet(instance=self.object)
        return ctx

    @transaction.atomic
    def form_valid(self, form):
        ctx = self.get_context_data()
        formset = ctx["formset"]

        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            messages.success(self.request, "Proposta atualizada com sucesso!")
            return redirect(self.get_success_url())
        else:
            messages.error(self.request, "Corrija os erros nos itens.")
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse("propostas:detalhe", kwargs={"pk": self.object.pk})


class PropostaDeleteView(LoginRequiredMixin, DeleteView):
    model = Proposta
    template_name = "propostas/confirmar_exclusao.html"
    success_url = reverse_lazy("propostas:lista")

    def form_valid(self, form):
        messages.warning(self.request, "Proposta excluída.")
        return super().form_valid(form)


# ─── VIEW DE GERAÇÃO DE PDF ────────────────────────────────────────────────────

@login_required
def proposta_pdf_view(request, pk):
    """
    Gera e faz o download do PDF da proposta comercial.
    """
    proposta = get_object_or_404(
        Proposta.objects.select_related("cliente").prefetch_related(
            "itens__produto", "itens__servico"
        ),
        pk=pk,
    )
    return gerar_pdf_proposta(proposta, request=request)


# ─── VIEW DE MUDANÇA RÁPIDA DE STATUS ─────────────────────────────────────────

@login_required
def proposta_mudar_status(request, pk, status):
    """
    Muda o status de uma proposta comercial e atualiza o estoque dos produtos vinculados.
    """
    proposta = get_object_or_404(Proposta, pk=pk)
    status_validos = [s[0] for s in StatusProposta.choices]

    if status in status_validos:
        status_anterior = proposta.status

        if status_anterior != status:
            with transaction.atomic():
                proposta.status = status
                proposta.save(update_fields=["status"])

                if status == StatusProposta.APROVADA and status_anterior != StatusProposta.APROVADA:
                    itens_produtos = proposta.itens.filter(tipo="PRODUTO", produto__isnull=False).select_related("produto")
                    for item in itens_produtos:
                        item.produto.debitar_estoque(item.quantidade)
                    messages.success(
                        request,
                        f"Proposta {proposta.numero} APROVADA! Estoque dos produtos baixado com sucesso."
                    )

                elif status_anterior == StatusProposta.APROVADA and status != StatusProposta.APROVADA:
                    itens_produtos = proposta.itens.filter(tipo="PRODUTO", produto__isnull=False).select_related("produto")
                    for item in itens_produtos:
                        item.produto.creditar_estoque(item.quantidade)
                    messages.warning(
                        request,
                        f"Proposta {proposta.numero} alterada para {proposta.get_status_display()}. Estoque dos produtos devolvido."
                    )

                else:
                    messages.success(
                        request,
                        f"Proposta {proposta.numero} → {proposta.get_status_display()}"
                    )
    else:
        messages.error(request, "Status inválido.")

    return redirect(reverse("propostas:detalhe", kwargs={"pk": pk}))


# ─── VIEW DE ENVIO POR E-MAIL (CELERY + FALLBACK) ──────────────────────────────

@login_required
def proposta_enviar_email_view(request, pk):
    """
    Envia a proposta comercial por e-mail em segundo plano via Celery + Redis,
    com fallback síncrono automático.
    """
    from .tasks import enviar_proposta_email_async
    from .services.email_service import enviar_proposta_email

    proposta = get_object_or_404(
        Proposta.objects.select_related("cliente").prefetch_related("itens"),
        pk=pk
    )

    if not proposta.cliente.email:
        messages.error(
            request,
            f"Não foi possível enviar: o cliente '{proposta.cliente.nome}' não possui e-mail cadastrado no sistema."
        )
        return redirect(reverse("propostas:detalhe", kwargs={"pk": pk}))

    schema_name = getattr(connection, "schema_name", "public")

    try:
        enviar_proposta_email_async.delay(proposta.id, schema_name)
        messages.success(
            request,
            f"🚀 O envio da Proposta nº {proposta.numero} para '{proposta.cliente.email}' foi agendado em segundo plano!"
        )
    except Exception:
        sucesso, relatorio = enviar_proposta_email(proposta, request=request)
        if sucesso:
            messages.success(
                request,
                f"Proposta nº {proposta.numero} enviada com sucesso para: {', '.join(relatorio['enviados'])}!"
            )
        else:
            messages.error(request, f"Falha no envio da proposta: {' | '.join(relatorio['erros'])}")

    return redirect(reverse("propostas:detalhe", kwargs={"pk": pk}))


# ─── VIEWS PÚBLICAS (VISÃO DO CLIENTE FINAL) ──────────────────────────────────

def proposta_publica_detail(request, token):
    """
    Exibe a proposta comercial para o cliente final sem exigência de login.
    URL: /propostas/p/<token>/
    """
    proposta = get_object_or_404(
        Proposta.objects.select_related("cliente").prefetch_related(
            "itens__produto", "itens__servico"
        ),
        token_publico=token
    )
    ctx = {
        "proposta": proposta,
        "itens": proposta.itens.all().order_by("ordem"),
        "cliente": proposta.cliente,
    }
    return render(request, "propostas/publica_detalhe.html", ctx)


def proposta_publica_aprovar(request, token):
    """
    Permite ao cliente final aprovar a proposta comercial diretamente.
    """
    proposta = get_object_or_404(Proposta, token_publico=token)

    if proposta.status != StatusProposta.APROVADA:
        with transaction.atomic():
            proposta.status = StatusProposta.APROVADA
            proposta.save(update_fields=["status"])

            # Realiza baixa no estoque dos produtos da proposta
            itens_produtos = proposta.itens.filter(tipo="PRODUTO", produto__isnull=False).select_related("produto")
            for item in itens_produtos:
                item.produto.debitar_estoque(item.quantidade)

            messages.success(
                request,
                f"🎉 Proposta nº {proposta.numero} aprovada com sucesso! Muito obrigado pela parceria."
            )
    else:
        messages.info(request, "Esta proposta já consta como aprovada.")

    return redirect(reverse("propostas:publica-detalhe", kwargs={"token": token}))


def proposta_publica_recusar(request, token):
    """
    Permite ao cliente final recusar a proposta comercial ou solicitar ajustes.
    """
    proposta = get_object_or_404(Proposta, token_publico=token)

    if proposta.status != StatusProposta.RECUSADA:
        proposta.status = StatusProposta.RECUSADA
        proposta.save(update_fields=["status"])
        messages.warning(
            request,
            f"Proposta nº {proposta.numero} marcada como recusada. A equipe responsável foi notificada."
        )

    return redirect(reverse("propostas:publica-detalhe", kwargs={"token": token}))
