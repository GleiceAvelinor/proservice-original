"""
============================================================
APP: propostas — [TENANT APP]
============================================================
Motor de geração de Propostas Comerciais com:
  - Relacionamento com Cliente
  - Múltiplos itens (Produtos e/ou Serviços)
  - Cálculo automático de totais
  - Controle de status (Pendente → Aprovada / Recusada)
  - Exportação para PDF via WeasyPrint

Models:
  - Proposta: cabeçalho da proposta comercial
  - ItemProposta: itens da proposta (produto ou serviço)
"""

import uuid
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal

from apps.clientes.models import Cliente
from apps.catalogo.models import Produto, Servico


class StatusProposta(models.TextChoices):
    """Status possíveis de uma proposta comercial."""
    RASCUNHO = "RASCUNHO", "Rascunho"
    PENDENTE = "PENDENTE", "Pendente (Enviada ao cliente)"
    APROVADA = "APROVADA", "Aprovada"
    RECUSADA = "RECUSADA", "Recusada"
    EXPIRADA = "EXPIRADA", "Expirada"


class Proposta(models.Model):
    """
    Cabeçalho de uma Proposta Comercial.

    Relaciona um conjunto de itens (produtos/serviços) a um cliente,
    com controle de validade, status e totais calculados automaticamente.
    """

    # ─── Identificador Público e Numeração ─────────────────────────────────────
    token_publico = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        db_index=True,
        verbose_name="Token Público",
    )
    numero = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Número da Proposta",
        help_text="Ex: PROP-2024-001",
    )

    # ─── Relacionamento ───────────────────────────────────────────────────────
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name="propostas",
        verbose_name="Cliente",
    )

    # ─── Datas ────────────────────────────────────────────────────────────────
    data_emissao = models.DateField(
        default=timezone.now,
        verbose_name="Data de Emissão",
    )
    data_validade = models.DateField(
        null=True,
        blank=True,
        verbose_name="Válida até",
        help_text="Após esta data, a proposta é considerada expirada",
    )

    # ─── Status ───────────────────────────────────────────────────────────────
    status = models.CharField(
        max_length=20,
        choices=StatusProposta.choices,
        default=StatusProposta.RASCUNHO,
        verbose_name="Status",
    )

    # ─── Financeiro ───────────────────────────────────────────────────────────
    desconto = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Desconto (%)",
    )
    condicao_pagamento = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Condição de Pagamento",
        help_text="Ex: À vista com 5% de desconto, 30/60/90 dias",
    )

    # ─── Textos ───────────────────────────────────────────────────────────────
    titulo = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        verbose_name="Título da Proposta",
        help_text="Ex: Proposta de Manutenção de Jardim - Outubro 2024",
    )
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações / Termos",
        help_text="Condições gerais, garantias, etc.",
    )

    # ─── Auditoria ────────────────────────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Proposta Comercial"
        verbose_name_plural = "Propostas Comerciais"
        ordering = ["-data_emissao", "-created_at"]

    def __str__(self):
        return f"{self.numero} — {self.cliente.nome}"

    # ─── Cálculos automáticos ─────────────────────────────────────────────────

    @property
    def subtotal(self):
        """Soma de todos os itens sem desconto."""
        return sum(item.total for item in self.itens.all())

    @property
    def valor_desconto(self):
        """Valor monetário do desconto."""
        return (self.subtotal * self.desconto) / Decimal("100")

    @property
    def total(self):
        """Valor final após aplicar o desconto."""
        return self.subtotal - self.valor_desconto

    @property
    def esta_vencida(self):
        """Verifica se a proposta passou da data de validade."""
        if self.data_validade and timezone.now().date() > self.data_validade:
            return True
        return False

    def gerar_numero(self):
        """
        Gera um número sequencial para a proposta no formato PROP-AAAA-NNN.
        Chamado automaticamente no save() se o número ainda não foi definido.
        """
        ano = timezone.now().year
        ultimo = (
            Proposta.objects.filter(numero__startswith=f"PROP-{ano}-")
            .order_by("-numero")
            .first()
        )
        if ultimo:
            try:
                seq = int(ultimo.numero.split("-")[-1]) + 1
            except (ValueError, IndexError):
                seq = 1
        else:
            seq = 1
        return f"PROP-{ano}-{seq:03d}"

    def save(self, *args, **kwargs):
        """Gera o número automaticamente na primeira gravação."""
        if not self.numero:
            self.numero = self.gerar_numero()
        super().save(*args, **kwargs)

    def get_status_badge_class(self):
        """Retorna a classe Bootstrap para o badge de status."""
        classes = {
            StatusProposta.RASCUNHO: "secondary",
            StatusProposta.PENDENTE: "warning",
            StatusProposta.APROVADA: "success",
            StatusProposta.RECUSADA: "danger",
            StatusProposta.EXPIRADA: "dark",
        }
        return classes.get(self.status, "secondary")

    @property
    def mensagem_whatsapp(self):
        """Gera o texto formatado para envio da proposta via WhatsApp."""
        from django.db import connection
        try:
            tenant_nome = connection.tenant.name
        except Exception:
            tenant_nome = "Nossa Empresa"

        data_val = self.data_validade.strftime("%d/%m/%Y") if self.data_validade else "A combinar"
        total_fmt = f"{self.total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        msg = (
            f"Olá, {self.cliente.nome}! 👋\n\n"
            f"Aqui é da *{tenant_nome}*.\n"
            f"Segue o resumo da sua proposta comercial:\n\n"
            f"📄 *Proposta:* {self.numero}\n"
            f"📌 *Assunto:* {self.titulo or 'Orçamento de Serviços'}\n"
            f"💰 *Valor Total:* R$ {total_fmt}\n"
            f"📅 *Válida até:* {data_val}\n\n"
            f"Ficamos à disposição para quaisquer dúvidas!"
        )
        return msg

    @property
    def link_publico(self):
        """Retorna a URL pública relativa para aprovação da proposta pelo cliente."""
        from django.urls import reverse
        return reverse("propostas:publica-detalhe", kwargs={"token": self.token_publico})

    @property
    def whatsapp_link(self):
        """Retorna o link https://api.whatsapp.com/send pré-formatado."""
        import urllib.parse
        phone = self.cliente.telefone_whatsapp if self.cliente else ""
        text = urllib.parse.quote(self.mensagem_whatsapp)
        if phone:
            return f"https://api.whatsapp.com/send?phone={phone}&text={text}"
        return f"https://api.whatsapp.com/send?text={text}"


class TipoItem(models.TextChoices):
    """Define se o item é um produto ou serviço."""
    PRODUTO = "PRODUTO", "Produto"
    SERVICO = "SERVICO", "Serviço"


class ItemProposta(models.Model):
    """
    Um item (linha) de uma Proposta Comercial.

    Pode referenciar um Produto ou um Serviço do catálogo.
    O preço unitário pode ser ajustado para cada item individualmente,
    permitindo negociações específicas sem alterar o catálogo.
    """

    # ─── Relacionamento com a Proposta ────────────────────────────────────────
    proposta = models.ForeignKey(
        Proposta,
        on_delete=models.CASCADE,
        related_name="itens",
        verbose_name="Proposta",
    )

    # ─── Tipo do item ─────────────────────────────────────────────────────────
    tipo = models.CharField(
        max_length=10,
        choices=TipoItem.choices,
        verbose_name="Tipo",
    )

    # ─── Referência ao catálogo (opcional) ───────────────────────────────────
    produto = models.ForeignKey(
        Produto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Produto",
    )
    servico = models.ForeignKey(
        Servico,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Serviço",
    )

    # ─── Dados do Item (podem ser preenchidos manualmente) ────────────────────
    descricao = models.CharField(
        max_length=500,
        verbose_name="Descrição do Item",
        help_text="Preenchido automaticamente ao selecionar produto/serviço",
    )
    unidade = models.CharField(
        max_length=10,
        default="UN",
        verbose_name="Unidade",
    )

    # ─── Quantidades e Preços ─────────────────────────────────────────────────
    quantidade = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("1.00"),
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="Quantidade",
    )
    preco_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Preço Unitário (R$)",
    )

    # ─── Ordem de exibição ────────────────────────────────────────────────────
    ordem = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordem",
    )

    class Meta:
        verbose_name = "Item da Proposta"
        verbose_name_plural = "Itens da Proposta"
        ordering = ["ordem", "id"]

    def __str__(self):
        return f"{self.descricao} (x{self.quantidade})"

    @property
    def total(self):
        """Calcula o total deste item: quantidade × preço unitário."""
        return self.quantidade * self.preco_unitario
