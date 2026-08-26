"""
============================================================
APP: dashboard — [TENANT APP]
============================================================
Visão geral de faturamento e métricas operacionais do tenant logado.
Os dados são calculados dinamicamente no schema do tenant ativo.
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.db.models import Sum, Count, F, Q
from decimal import Decimal
from django.utils import timezone

from apps.clientes.models import Cliente
from apps.catalogo.models import Produto, Servico
from apps.propostas.models import Proposta, StatusProposta, ItemProposta


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # ─── Indicadores principais (KPIs) ──────────────────────────────────
        # Total de propostas
        propostas_qs = Proposta.objects.all()
        total_propostas = propostas_qs.count()

        # Propostas Aprovadas (Faturamento Confirmado)
        propostas_aprovadas = propostas_qs.filter(status=StatusProposta.APROVADA)
        # Calcula faturamento total das aprovadas
        faturamento_total = sum(p.total for p in propostas_aprovadas)

        # Propostas Pendentes (Faturamento Potencial)
        propostas_pendentes = propostas_qs.filter(status=StatusProposta.PENDENTE)
        faturamento_pendente = sum(p.total for p in propostas_pendentes)

        # Total Clientes Ativos
        total_clientes = Cliente.objects.filter(ativo=True).count()

        # Taxa de Conversão
        if total_propostas > 0:
            taxa_conversao = round((propostas_aprovadas.count() / total_propostas) * 100, 1)
        else:
            taxa_conversao = Decimal("0.0")

        # ─── Checklist de Onboarding ──────────────────────────────────────────
        from django.db import connection
        try:
            tenant = connection.tenant
            has_logo = bool(tenant and (tenant.logo or tenant.cnpj))
        except Exception:
            has_logo = False

        has_clientes = total_clientes > 0
        has_catalogo = (Produto.objects.count() + Servico.objects.count()) > 0
        has_propostas = total_propostas > 0

        steps = [has_logo, has_clientes, has_catalogo, has_propostas]
        onboarding_progresso = int((sum(1 for s in steps if s) / len(steps)) * 100)
        onboarding_completo = onboarding_progresso == 100

        # ─── Listagens Recentes e Alertas ───────────────────────────────────
        # Últimas 5 propostas
        propostas_recentes = propostas_qs.select_related("cliente").order_by("-created_at")[:5]

        # Produtos com estoque baixo (apenas se houver estoque mínimo cadastrado > 0)
        produtos_estoque_baixo = Produto.objects.filter(
            ativo=True,
            estoque_minimo__gt=0,
            estoque_atual__lte=F("estoque_minimo")
        ).order_by("estoque_atual")[:5]

        # Distribuição de status de propostas
        status_counts = propostas_qs.values("status").annotate(count=Count("id"))
        status_dict = {item["status"]: item["count"] for item in status_counts}

        # ─── Dados para Gráficos Interativos (Chart.js) ─────────────────────
        import datetime
        import json

        hoje = timezone.now().date()
        meses_labels = []
        faturamento_mensal_data = []
        nomes_meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

        for i in range(5, -1, -1):
            # Recua mês a mês
            ano_ref = hoje.year
            mes_ref = hoje.month - i
            while mes_ref <= 0:
                mes_ref += 12
                ano_ref -= 1
            
            label = f"{nomes_meses[mes_ref - 1]}/{str(ano_ref)[2:]}"
            meses_labels.append(label)

            props_mes = propostas_aprovadas.filter(
                data_emissao__year=ano_ref,
                data_emissao__month=mes_ref
            )
            val_mes = sum(p.total for p in props_mes)
            faturamento_mensal_data.append(float(val_mes))

        chart_status_labels = ["Aprovadas", "Pendentes", "Recusadas", "Rascunhos"]
        chart_status_data = [
            status_dict.get(StatusProposta.APROVADA, 0),
            status_dict.get(StatusProposta.PENDENTE, 0),
            status_dict.get(StatusProposta.RECUSADA, 0),
            status_dict.get(StatusProposta.RASCUNHO, 0),
        ]

        # Contexto injetado na view
        ctx["faturamento_total"] = faturamento_total
        ctx["faturamento_pendente"] = faturamento_pendente
        ctx["total_clientes"] = total_clientes
        ctx["total_propostas"] = total_propostas
        ctx["taxa_conversao"] = taxa_conversao
        ctx["propostas_recentes"] = propostas_recentes
        ctx["produtos_estoque_baixo"] = produtos_estoque_baixo
        ctx["status_dict"] = status_dict
        ctx["hoje"] = hoje

        # Contexto de onboarding
        ctx["has_logo"] = has_logo
        ctx["has_clientes"] = has_clientes
        ctx["has_catalogo"] = has_catalogo
        ctx["has_propostas"] = has_propostas
        ctx["onboarding_progresso"] = onboarding_progresso
        ctx["onboarding_completo"] = onboarding_completo

        # JSON para os gráficos
        ctx["chart_meses_json"] = json.dumps(meses_labels)
        ctx["chart_faturamento_json"] = json.dumps(faturamento_mensal_data)
        ctx["chart_status_labels_json"] = json.dumps(chart_status_labels)
        ctx["chart_status_data_json"] = json.dumps(chart_status_data)

        return ctx
