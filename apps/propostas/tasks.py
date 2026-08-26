"""
============================================================
CELERY TASKS — Módulo de Propostas Comerciais
============================================================
Tarefas assíncronas executadas em background com isolamento
total por schema (multi-tenant) no PostgreSQL.
"""

from celery import shared_task
from django_tenants.utils import tenant_context
from apps.tenants.models import Client
from .models import Proposta, StatusProposta
from .services.email_service import enviar_proposta_email


@shared_task(name="propostas.enviar_proposta_email_async")
def enviar_proposta_email_async(proposta_id, schema_name, enviar_cliente=True, enviar_prestador=True):
    """
    Executa o envio de e-mail da proposta comercial em segundo plano,
    chaveando a conexão do PostgreSQL para o schema do tenant.

    Args:
        proposta_id (int): ID da proposta no banco de dados.
        schema_name (str): Nome do schema do tenant (ex: 'ji_jardinagem').
        enviar_cliente (bool): Se deve enviar para o cliente.
        enviar_prestador (bool): Se deve enviar cópia para o prestador.

    Returns:
        dict: Resultado com status de sucesso e log do disparo.
    """
    try:
        tenant = Client.objects.get(schema_name=schema_name)
    except Client.DoesNotExist:
        return {"sucesso": False, "erro": f"Tenant com schema '{schema_name}' não encontrado."}

    # Alterna a conexão do PostgreSQL para o schema isolado do tenant
    with tenant_context(tenant):
        try:
            proposta = Proposta.objects.select_related("cliente").prefetch_related("itens").get(id=proposta_id)
            
            sucesso, relatorio = enviar_proposta_email(
                proposta,
                enviar_cliente=enviar_cliente,
                enviar_prestador=enviar_prestador
            )

            # Atualiza o status para PENDENTE/ENVIADA se estava como RASCUNHO
            if sucesso and proposta.status == StatusProposta.RASCUNHO:
                proposta.status = StatusProposta.PENDENTE
                proposta.save(update_fields=["status"])

            return {
                "sucesso": sucesso,
                "proposta_numero": proposta.numero,
                "tenant": tenant.name,
                "relatorio": relatorio
            }
        except Proposta.DoesNotExist:
            return {"sucesso": False, "erro": f"Proposta ID {proposta_id} não encontrada no schema '{schema_name}'."}
        except Exception as e:
            return {"sucesso": False, "erro": str(e)}
