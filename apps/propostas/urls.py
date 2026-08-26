"""URLs do módulo de Propostas Comerciais."""

from django.urls import path
from . import views

app_name = "propostas"

urlpatterns = [
    path("", views.PropostaListView.as_view(), name="lista"),
    path("nova/", views.PropostaCreateView.as_view(), name="criar"),
    path("<int:pk>/", views.PropostaDetailView.as_view(), name="detalhe"),
    path("<int:pk>/editar/", views.PropostaUpdateView.as_view(), name="editar"),
    path("<int:pk>/excluir/", views.PropostaDeleteView.as_view(), name="excluir"),

    # ─── Exportação PDF e E-mail ───────────────────────────────────────────────
    path("<int:pk>/pdf/", views.proposta_pdf_view, name="pdf"),
    path("<int:pk>/enviar-email/", views.proposta_enviar_email_view, name="enviar-email"),

    # ─── Ações rápidas de status ──────────────────────────────────────────────
    path("<int:pk>/status/<str:status>/", views.proposta_mudar_status, name="mudar-status"),

    # ─── Visualização e Aprovação Pública (Visão do Cliente Final) ─────────────
    path("p/<uuid:token>/", views.proposta_publica_detail, name="publica-detalhe"),
    path("p/<uuid:token>/aprovar/", views.proposta_publica_aprovar, name="publica-aprovar"),
    path("p/<uuid:token>/recusar/", views.proposta_publica_recusar, name="publica-recusar"),
]
