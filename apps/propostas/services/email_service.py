"""
============================================================
EMAIL SERVICE — Envio de Propostas por E-mail (Cliente & Prestador)
============================================================
Envia e-mails formatados em HTML com PDF anexado para o cliente
e notificação para o prestador de serviços.
"""

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.db import connection
from django.conf import settings
from .pdf_service import obter_pdf_bytes


def enviar_proposta_email(proposta, enviar_cliente=True, enviar_prestador=True, request=None):
    """
    Envia o e-mail da proposta comercial para o cliente e/ou prestador com o PDF em anexo.

    Returns:
        tuple: (sucesso: bool, relatorio: dict)
    """
    try:
        tenant = connection.tenant
    except AttributeError:
        tenant = None

    pdf_bytes, filename = obter_pdf_bytes(proposta, request=request)
    
    enviados = []
    erros = []

    context = {
        "proposta": proposta,
        "cliente": proposta.cliente,
        "tenant": tenant,
        "itens": proposta.itens.all(),
        "total": proposta.total,
    }

    from_email = settings.DEFAULT_FROM_EMAIL

    # 1. Envio para o Cliente
    if enviar_cliente:
        email_cliente = proposta.cliente.email
        if email_cliente:
            try:
                nome_empresa = tenant.name if tenant else "Nossa Empresa"
                subject = f"Proposta Comercial #{proposta.numero} — {nome_empresa}"
                html_content = render_to_string("propostas/email/proposta_cliente.html", context, request=request)
                text_content = strip_tags(html_content)

                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email=from_email,
                    to=[email_cliente],
                )
                msg.attach_alternative(html_content, "text/html")
                msg.attach(filename, pdf_bytes, "application/pdf")
                msg.send(fail_silently=False)
                enviados.append(f"Cliente ({email_cliente})")
            except Exception as e:
                erros.append(f"Falha ao enviar para o cliente ({email_cliente}): {str(e)}")
        else:
            erros.append("O cliente não possui e-mail cadastrado.")

    # 2. Envio para o Prestador (Empresa / Usuário Logado)
    if enviar_prestador:
        email_prestador = None
        if tenant and tenant.email:
            email_prestador = tenant.email
        elif request and hasattr(request, "user") and request.user.is_authenticated and request.user.email:
            email_prestador = request.user.email

        if email_prestador:
            try:
                subject = f"[Notificação] Proposta #{proposta.numero} enviada para {proposta.cliente.nome}"
                html_content = render_to_string("propostas/email/proposta_prestador.html", context, request=request)
                text_content = strip_tags(html_content)

                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email=from_email,
                    to=[email_prestador],
                )
                msg.attach_alternative(html_content, "text/html")
                msg.attach(filename, pdf_bytes, "application/pdf")
                msg.send(fail_silently=False)
                enviados.append(f"Prestador ({email_prestador})")
            except Exception as e:
                erros.append(f"Falha ao enviar para a empresa ({email_prestador}): {str(e)}")

    sucesso = len(enviados) > 0
    if sucesso:
        from ..models import StatusProposta
        if proposta.status == StatusProposta.RASCUNHO:
            proposta.status = StatusProposta.PENDENTE
            proposta.save(update_fields=["status"])

    return sucesso, {"enviados": enviados, "erros": erros}
