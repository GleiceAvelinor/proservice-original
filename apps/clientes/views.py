"""Views CRUD para o módulo de Clientes."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)

from .models import Cliente
from .forms import ClienteForm


class ClienteListView(LoginRequiredMixin, ListView):
    model = Cliente
    template_name = "clientes/lista.html"
    context_object_name = "clientes"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().filter(ativo=True)
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(nome__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "")
        ctx["total"] = Cliente.objects.filter(ativo=True).count()
        return ctx


class ClienteDetailView(LoginRequiredMixin, DetailView):
    model = Cliente
    template_name = "clientes/detalhe.html"
    context_object_name = "cliente"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        propostas = self.object.propostas.all()
        ctx["propostas"] = propostas.order_by("-data_emissao")[:10]
        ctx["total_propostas"] = propostas.count()
        ctx["total_faturado"] = sum(p.total for p in propostas.filter(status="APROVADA"))
        return ctx


class ClienteCreateView(LoginRequiredMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = "clientes/form.html"
    success_url = reverse_lazy("clientes:lista")

    def form_valid(self, form):
        messages.success(self.request, "Cliente cadastrado com sucesso!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titulo"] = "Novo Cliente"
        return ctx


class ClienteUpdateView(LoginRequiredMixin, UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = "clientes/form.html"
    success_url = reverse_lazy("clientes:lista")

    def form_valid(self, form):
        messages.success(self.request, "Cliente atualizado com sucesso!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titulo"] = f"Editar: {self.object.nome}"
        return ctx


class ClienteDeleteView(LoginRequiredMixin, DeleteView):
    model = Cliente
    template_name = "clientes/confirmar_exclusao.html"
    success_url = reverse_lazy("clientes:lista")

    def form_valid(self, form):
        messages.warning(self.request, "Cliente excluído.")
        return super().form_valid(form)
