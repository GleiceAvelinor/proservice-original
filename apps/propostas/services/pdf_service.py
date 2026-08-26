"""
============================================================
PDF SERVICE — Geração de Propostas em PDF via ReportLab / WeasyPrint
============================================================
Gera PDFs profissionais de propostas comerciais de forma 100%
multiplataforma (sem depender de DLLs nativas GTK3 no Windows).

Uso:
    from apps.propostas.services.pdf_service import gerar_pdf_proposta

    response = gerar_pdf_proposta(proposta, request)
    return response  # HttpResponse com Content-Type: application/pdf
"""

import io
import os
from django.http import HttpResponse
from django.db import connection

# Tenta usar WeasyPrint se as bibliotecas C/GTK3 estiverem instaladas;
# caso contrário, usa ReportLab (100% Python puro, funciona perfeitamente no Windows).
WEASYPRINT_AVAILABLE = False
try:
    import contextlib
    import sys
    with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
        from weasyprint import HTML, CSS
        from weasyprint.text.fonts import FontConfiguration
        from django.template.loader import render_to_string
    WEASYPRINT_AVAILABLE = True
except Exception:
    WEASYPRINT_AVAILABLE = False

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image
)


def obter_pdf_bytes(proposta, request=None):
    """
    Retorna uma tupla (pdf_bytes, nome_arquivo) para uso no envio de e-mails.
    """
    if WEASYPRINT_AVAILABLE:
        try:
            return _obter_pdf_bytes_weasyprint(proposta, request)
        except Exception:
            pass  # Fallback para ReportLab

    return _obter_pdf_bytes_reportlab(proposta, request)


def _obter_pdf_bytes_weasyprint(proposta, request=None):
    try:
        tenant = connection.tenant
    except AttributeError:
        tenant = None

    context = {
        "proposta": proposta,
        "itens": proposta.itens.select_related("produto", "servico").order_by("ordem"),
        "tenant": tenant,
        "request": request,
    }

    html_string = render_to_string("propostas/proposta_pdf.html", context, request=request)
    font_config = FontConfiguration()
    pdf_buffer = io.BytesIO()

    base_url = request.build_absolute_uri("/") if request else "http://localhost:8000/"

    HTML(string=html_string, base_url=base_url).write_pdf(
        pdf_buffer,
        font_config=font_config,
    )

    pdf_buffer.seek(0)
    nome_arquivo = f"proposta_{proposta.numero}_{proposta.cliente.nome.replace(' ', '_')}.pdf"
    return pdf_buffer.getvalue(), nome_arquivo


def _obter_pdf_bytes_reportlab(proposta, request=None):
    try:
        tenant = connection.tenant
    except AttributeError:
        tenant = None

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        "CompanyTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#2563eb"),
    )
    subtitle_style = ParagraphStyle(
        "CompanySub",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#475569"),
    )
    prop_num_style = ParagraphStyle(
        "PropNum",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        alignment=2,
        textColor=colors.HexColor("#1e293b"),
    )
    section_title = ParagraphStyle(
        "SecTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#2563eb"),
        spaceAfter=4,
    )
    cell_style = ParagraphStyle(
        "Cell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=11,
    )
    cell_bold = ParagraphStyle(
        "CellBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11,
    )
    cell_right = ParagraphStyle(
        "CellRight",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=11,
        alignment=2,
    )
    cell_right_bold = ParagraphStyle(
        "CellRightBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11,
        alignment=2,
    )

    elements = []

    tenant_name = tenant.name if tenant else "Prestador de Serviços"
    tenant_cnpj = f"CNPJ: {tenant.cnpj}" if tenant and tenant.cnpj else ""
    tenant_contact = f"E-mail: {tenant.email or '-'} | Tel: {tenant.phone or '-'}" if tenant else ""
    tenant_addr = tenant.address if tenant and tenant.address else ""

    header_left = []
    if tenant and tenant.logo and hasattr(tenant.logo, "path") and os.path.exists(tenant.logo.path):
        try:
            img = Image(tenant.logo.path, width=4.5 * cm, height=1.6 * cm, kind="proportional")
            header_left.append(img)
            header_left.append(Spacer(1, 6))
        except Exception:
            pass

    header_left.extend([
        Paragraph(tenant_name, title_style),
        Paragraph(f"{tenant_cnpj}<br/>{tenant_contact}<br/>{tenant_addr}", subtitle_style),
    ])
    
    dt_emissao = proposta.data_emissao.strftime("%d/%m/%Y")
    dt_validade = proposta.data_validade.strftime("%d/%m/%Y") if proposta.data_validade else "Indefinida"

    header_right = [
        Paragraph(f"PROPOSTA {proposta.numero}", prop_num_style),
        Spacer(1, 4),
        Paragraph(f"<b>Data Emissão:</b> {dt_emissao}<br/><b>Válida até:</b> {dt_validade}", ParagraphStyle("RightSmall", parent=subtitle_style, alignment=2)),
    ]

    header_table = Table([[header_left, header_right]], colWidths=[11 * cm, 7 * cm])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563eb"), spaceAfter=15))

    cli = proposta.cliente
    cli_info = f"<b>{cli.nome}</b><br/>"
    if cli.cpf_cnpj:
        cli_info += f"CPF/CNPJ: {cli.cpf_cnpj}<br/>"
    if cli.email or cli.telefone:
        cli_info += f"E-mail: {cli.email or '-'} | Tel: {cli.telefone or '-'}<br/>"
    if cli.endereco_completo:
        cli_info += f"Endereço: {cli.endereco_completo}"

    cli_table = Table([[
        [Paragraph("CLIENTE / DESTINATÁRIO", section_title), Paragraph(cli_info, cell_style)]
    ]], colWidths=[18 * cm])
    cli_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("PADDING", (0, 0), (-1, -1), 10),
    ]))
    elements.append(cli_table)
    elements.append(Spacer(1, 15))

    table_data = [[
        Paragraph("<b>#</b>", cell_bold),
        Paragraph("<b>Descrição do Item / Serviço</b>", cell_bold),
        Paragraph("<b>Qtd</b>", cell_bold),
        Paragraph("<b>Unid</b>", cell_bold),
        Paragraph("<b>Preço Unit.</b>", cell_right_bold),
        Paragraph("<b>Total</b>", cell_right_bold),
    ]]

    itens = proposta.itens.all().order_by("ordem")
    for idx, item in enumerate(itens, 1):
        table_data.append([
            Paragraph(str(idx), cell_style),
            Paragraph(item.descricao, cell_bold if item.tipo == "SERVICO" else cell_style),
            Paragraph(str(item.quantidade), cell_style),
            Paragraph(item.unidade, cell_style),
            Paragraph(f"R$ {item.preco_unitario:,.2f}", cell_right),
            Paragraph(f"R$ {item.total:,.2f}", cell_right_bold),
        ])

    items_table = Table(table_data, colWidths=[1 * cm, 8.5 * cm, 1.8 * cm, 1.7 * cm, 2.5 * cm, 2.5 * cm])
    items_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eff6ff")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1d4ed8")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 15))

    subtotal_str = f"R$ {proposta.subtotal:,.2f}"
    desconto_str = f"- R$ {proposta.valor_desconto:,.2f}" if proposta.desconto > 0 else "R$ 0,00"
    total_str = f"R$ {proposta.total:,.2f}"

    totais_data = [
        [Paragraph("Subtotal:", cell_right), Paragraph(subtotal_str, cell_right)],
    ]
    if proposta.desconto > 0:
        totais_data.append([
            Paragraph(f"Desconto ({proposta.desconto}%):", cell_right),
            Paragraph(desconto_str, cell_right),
        ])
    totais_data.append([
        Paragraph("<b>VALOR TOTAL:</b>", ParagraphStyle("TotLbl", parent=cell_right_bold, textColor=colors.HexColor("#2563eb"))),
        Paragraph(f"<b>{total_str}</b>", ParagraphStyle("TotVal", parent=cell_right_bold, textColor=colors.HexColor("#2563eb"), fontSize=11)),
    ])

    totais_table = Table(totais_data, colWidths=[13 * cm, 5 * cm])
    totais_table.setStyle(TableStyle([
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(totais_table)
    elements.append(Spacer(1, 15))

    if proposta.condicao_pagamento or proposta.observacoes:
        obs_text = ""
        if proposta.condicao_pagamento:
            obs_text += f"<b>Condições de Pagamento:</b> {proposta.condicao_pagamento}<br/>"
        if proposta.observacoes:
            obs_text += f"<b>Observações:</b> {proposta.observacoes}"

        obs_table = Table([[
            [Paragraph("TERMOS E CONDIÇÕES", section_title), Paragraph(obs_text, cell_style)]
        ]], colWidths=[18 * cm])
        obs_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fffbebf5")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#fef3c7")),
            ("PADDING", (0, 0), (-1, -1), 10),
        ]))
        elements.append(obs_table)

    doc.build(elements)
    buffer.seek(0)
    nome_arquivo = f"proposta_{proposta.numero}_{proposta.cliente.nome.replace(' ', '_')}.pdf"
    return buffer.getvalue(), nome_arquivo


def gerar_pdf_proposta(proposta, request=None):
    """
    Gera o PDF de uma proposta comercial e retorna um HttpResponse.
    """
    pdf_bytes, nome_arquivo = obter_pdf_bytes(proposta, request=request)
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{nome_arquivo}"'
    return response



def _gerar_pdf_weasyprint(proposta, request=None):
    """Geração via WeasyPrint (HTML -> PDF)."""
    try:
        tenant = connection.tenant
    except AttributeError:
        tenant = None

    context = {
        "proposta": proposta,
        "itens": proposta.itens.select_related("produto", "servico").order_by("ordem"),
        "tenant": tenant,
        "request": request,
    }

    html_string = render_to_string("propostas/proposta_pdf.html", context, request=request)
    font_config = FontConfiguration()
    pdf_buffer = io.BytesIO()

    base_url = request.build_absolute_uri("/") if request else "http://localhost:8000/"

    HTML(string=html_string, base_url=base_url).write_pdf(
        pdf_buffer,
        font_config=font_config,
    )

    pdf_buffer.seek(0)
    nome_arquivo = f"proposta_{proposta.numero}_{proposta.cliente.nome.replace(' ', '_')}.pdf"

    response = HttpResponse(pdf_buffer.read(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{nome_arquivo}"'
    return response


def _gerar_pdf_reportlab(proposta, request=None):
    """Geração nativa via ReportLab (100% Python puro, sem DLLs externas)."""
    try:
        tenant = connection.tenant
    except AttributeError:
        tenant = None

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = getSampleStyleSheet()
    
    # Estilos customizados
    title_style = ParagraphStyle(
        "CompanyTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#2563eb"),
    )
    subtitle_style = ParagraphStyle(
        "CompanySub",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#475569"),
    )
    prop_num_style = ParagraphStyle(
        "PropNum",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        alignment=2, # Right
        textColor=colors.HexColor("#1e293b"),
    )
    section_title = ParagraphStyle(
        "SecTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#2563eb"),
        spaceAfter=4,
    )
    cell_style = ParagraphStyle(
        "Cell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=11,
    )
    cell_bold = ParagraphStyle(
        "CellBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11,
    )
    cell_right = ParagraphStyle(
        "CellRight",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=11,
        alignment=2,
    )
    cell_right_bold = ParagraphStyle(
        "CellRightBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11,
        alignment=2,
    )

    elements = []

    # 1. Cabeçalho (Tenant Info vs Número da Proposta)
    tenant_name = tenant.name if tenant else "Prestador de Serviços"
    tenant_cnpj = f"CNPJ: {tenant.cnpj}" if tenant and tenant.cnpj else ""
    tenant_contact = f"E-mail: {tenant.email or '-'} | Tel: {tenant.phone or '-'}" if tenant else ""
    tenant_addr = tenant.address if tenant and tenant.address else ""

    header_left = []
    if tenant and tenant.logo and hasattr(tenant.logo, "path") and os.path.exists(tenant.logo.path):
        try:
            img = Image(tenant.logo.path, width=4.5 * cm, height=1.6 * cm, kind="proportional")
            header_left.append(img)
            header_left.append(Spacer(1, 6))
        except Exception:
            pass

    header_left.extend([
        Paragraph(tenant_name, title_style),
        Paragraph(f"{tenant_cnpj}<br/>{tenant_contact}<br/>{tenant_addr}", subtitle_style),
    ])
    
    dt_emissao = proposta.data_emissao.strftime("%d/%m/%Y")
    dt_validade = proposta.data_validade.strftime("%d/%m/%Y") if proposta.data_validade else "Indefinida"

    header_right = [
        Paragraph(f"PROPOSTA {proposta.numero}", prop_num_style),
        Spacer(1, 4),
        Paragraph(f"<b>Data Emissão:</b> {dt_emissao}<br/><b>Válida até:</b> {dt_validade}", ParagraphStyle("RightSmall", parent=subtitle_style, alignment=2)),
    ]

    header_table = Table([[header_left, header_right]], colWidths=[11 * cm, 7 * cm])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563eb"), spaceAfter=15))

    # 2. Dados do Cliente
    cli = proposta.cliente
    cli_info = f"<b>{cli.nome}</b><br/>"
    if cli.cpf_cnpj:
        cli_info += f"CPF/CNPJ: {cli.cpf_cnpj}<br/>"
    if cli.email or cli.telefone:
        cli_info += f"E-mail: {cli.email or '-'} | Tel: {cli.telefone or '-'}<br/>"
    if cli.endereco_completo:
        cli_info += f"Endereço: {cli.endereco_completo}"

    cli_table = Table([[
        [Paragraph("CLIENTE / DESTINATÁRIO", section_title), Paragraph(cli_info, cell_style)]
    ]], colWidths=[18 * cm])
    cli_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("PADDING", (0, 0), (-1, -1), 10),
    ]))
    elements.append(cli_table)
    elements.append(Spacer(1, 15))

    # 3. Tabela de Itens
    table_data = [[
        Paragraph("<b>#</b>", cell_bold),
        Paragraph("<b>Descrição do Item / Serviço</b>", cell_bold),
        Paragraph("<b>Qtd</b>", cell_bold),
        Paragraph("<b>Unid</b>", cell_bold),
        Paragraph("<b>Preço Unit.</b>", cell_right_bold),
        Paragraph("<b>Total</b>", cell_right_bold),
    ]]

    itens = proposta.itens.all().order_by("ordem")
    for idx, item in enumerate(itens, 1):
        table_data.append([
            Paragraph(str(idx), cell_style),
            Paragraph(item.descricao, cell_bold if item.tipo == "SERVICO" else cell_style),
            Paragraph(str(item.quantidade), cell_style),
            Paragraph(item.unidade, cell_style),
            Paragraph(f"R$ {item.preco_unitario:,.2f}", cell_right),
            Paragraph(f"R$ {item.total:,.2f}", cell_right_bold),
        ])

    items_table = Table(table_data, colWidths=[1 * cm, 8.5 * cm, 1.8 * cm, 1.7 * cm, 2.5 * cm, 2.5 * cm])
    items_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eff6ff")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1d4ed8")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 15))

    # 4. Totais
    subtotal_str = f"R$ {proposta.subtotal:,.2f}"
    desconto_str = f"- R$ {proposta.valor_desconto:,.2f}" if proposta.desconto > 0 else "R$ 0,00"
    total_str = f"R$ {proposta.total:,.2f}"

    totais_data = [
        [Paragraph("Subtotal:", cell_right), Paragraph(subtotal_str, cell_right)],
    ]
    if proposta.desconto > 0:
        totais_data.append([
            Paragraph(f"Desconto ({proposta.desconto}%):", cell_right),
            Paragraph(desconto_str, cell_right),
        ])
    totais_data.append([
        Paragraph("<b>VALOR TOTAL:</b>", ParagraphStyle("TotLbl", parent=cell_right_bold, textColor=colors.HexColor("#2563eb"))),
        Paragraph(f"<b>{total_str}</b>", ParagraphStyle("TotVal", parent=cell_right_bold, textColor=colors.HexColor("#2563eb"), fontSize=11)),
    ])

    totais_table = Table(totais_data, colWidths=[13 * cm, 5 * cm])
    totais_table.setStyle(TableStyle([
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(totais_table)
    elements.append(Spacer(1, 15))

    # 5. Condições e Observações
    if proposta.condicao_pagamento or proposta.observacoes:
        obs_text = ""
        if proposta.condicao_pagamento:
            obs_text += f"<b>Condições de Pagamento:</b> {proposta.condicao_pagamento}<br/>"
        if proposta.observacoes:
            obs_text += f"<b>Observações:</b> {proposta.observacoes}"

        obs_table = Table([[
            [Paragraph("TERMOS E CONDIÇÕES", section_title), Paragraph(obs_text, cell_style)]
        ]], colWidths=[18 * cm])
        obs_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fffbebf5")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#fef3c7")),
            ("PADDING", (0, 0), (-1, -1), 10),
        ]))
        elements.append(obs_table)

    # Constrói o documento PDF
    doc.build(elements)
    buffer.seek(0)

    nome_arquivo = f"proposta_{proposta.numero}_{proposta.cliente.nome.replace(' ', '_')}.pdf"
    response = HttpResponse(buffer.read(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{nome_arquivo}"'
    return response
