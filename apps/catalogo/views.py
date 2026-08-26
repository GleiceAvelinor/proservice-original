"""Views CRUD para Produtos e Serviços do catálogo."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db import models
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView
)

from .models import Produto, Servico
from .forms import ProdutoForm, ServicoForm


# ─── PRODUTO VIEWS ────────────────────────────────────────────────────────────

class ProdutoListView(LoginRequiredMixin, ListView):
    model = Produto
    template_name = "catalogo/produtos_lista.html"
    context_object_name = "produtos"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(nome__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "")
        ctx["baixo_estoque"] = Produto.objects.filter(
            ativo=True,
            estoque_minimo__gt=0,
            estoque_atual__lte=models.F("estoque_minimo")
        ).count() if hasattr(Produto, 'estoque_atual') else 0
        return ctx


class ProdutoCreateView(LoginRequiredMixin, CreateView):
    model = Produto
    form_class = ProdutoForm
    template_name = "catalogo/produto_form.html"
    success_url = reverse_lazy("catalogo:produtos")

    def form_valid(self, form):
        messages.success(self.request, "Produto cadastrado com sucesso!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titulo"] = "Novo Produto"
        return ctx


class ProdutoUpdateView(LoginRequiredMixin, UpdateView):
    model = Produto
    form_class = ProdutoForm
    template_name = "catalogo/produto_form.html"
    success_url = reverse_lazy("catalogo:produtos")

    def form_valid(self, form):
        messages.success(self.request, "Produto atualizado!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titulo"] = f"Editar: {self.object.nome}"
        return ctx


class ProdutoDeleteView(LoginRequiredMixin, DeleteView):
    model = Produto
    template_name = "catalogo/confirmar_exclusao.html"
    success_url = reverse_lazy("catalogo:produtos")


# ─── SERVIÇO VIEWS ────────────────────────────────────────────────────────────

class ServicoListView(LoginRequiredMixin, ListView):
    model = Servico
    template_name = "catalogo/servicos_lista.html"
    context_object_name = "servicos"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(nome__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "")
        return ctx


class ServicoCreateView(LoginRequiredMixin, CreateView):
    model = Servico
    form_class = ServicoForm
    template_name = "catalogo/servico_form.html"
    success_url = reverse_lazy("catalogo:servicos")

    def form_valid(self, form):
        messages.success(self.request, "Serviço cadastrado com sucesso!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titulo"] = "Novo Serviço"
        return ctx


class ServicoUpdateView(LoginRequiredMixin, UpdateView):
    model = Servico
    form_class = ServicoForm
    template_name = "catalogo/servico_form.html"
    success_url = reverse_lazy("catalogo:servicos")

    def form_valid(self, form):
        messages.success(self.request, "Serviço atualizado!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titulo"] = f"Editar: {self.object.nome}"
        return ctx


class ServicoDeleteView(LoginRequiredMixin, DeleteView):
    model = Servico
    template_name = "catalogo/confirmar_exclusao.html"
    success_url = reverse_lazy("catalogo:servicos")
