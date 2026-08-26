"""URLs do módulo de Catálogo (Produtos e Serviços)."""

from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = "catalogo"

urlpatterns = [
    # Redireciona /catalogo/ para /catalogo/produtos/
    path("", RedirectView.as_view(pattern_name="catalogo:produtos", permanent=False)),

    # Produtos
    path("produtos/", views.ProdutoListView.as_view(), name="produtos"),
    path("produtos/novo/", views.ProdutoCreateView.as_view(), name="produto-criar"),
    path("produtos/<int:pk>/editar/", views.ProdutoUpdateView.as_view(), name="produto-editar"),
    path("produtos/<int:pk>/excluir/", views.ProdutoDeleteView.as_view(), name="produto-excluir"),

    # Serviços
    path("servicos/", views.ServicoListView.as_view(), name="servicos"),
    path("servicos/novo/", views.ServicoCreateView.as_view(), name="servico-criar"),
    path("servicos/<int:pk>/editar/", views.ServicoUpdateView.as_view(), name="servico-editar"),
    path("servicos/<int:pk>/excluir/", views.ServicoDeleteView.as_view(), name="servico-excluir"),
]
