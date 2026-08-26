"""
============================================================
APP: catalogo — [TENANT APP]
============================================================
Cadastro de Produtos e Serviços de cada empresa prestadora.

Models:
  - Produto: itens físicos com controle de estoque e preços
  - Servico: serviços prestados com preço padrão
"""

from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class UnidadeMedida(models.TextChoices):
    """Unidades de medida para produtos."""
    UNIDADE = "UN", "Unidade"
    METRO = "M", "Metro"
    METRO_QUADRADO = "M2", "Metro²"
    METRO_CUBICO = "M3", "Metro³"
    LITRO = "L", "Litro"
    QUILOGRAMA = "KG", "Quilograma"
    CAIXA = "CX", "Caixa"
    ROLO = "RL", "Rolo"
    SACO = "SC", "Saco"


class Produto(models.Model):
    """
    Representa um produto físico/material utilizado nos serviços.

    Exemplos: adubo (Ji Jardinagem), cloro (Levi Piscinas),
    bomba d'água, terra vegetal, etc.
    """

    # ─── Identificação ────────────────────────────────────────────────────────
    nome = models.CharField(
        max_length=200,
        verbose_name="Nome do Produto",
    )
    descricao = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descrição",
    )
    codigo = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True,
        verbose_name="Código / SKU",
    )

    # ─── Unidade e Estoque ────────────────────────────────────────────────────
    unidade = models.CharField(
        max_length=3,
        choices=UnidadeMedida.choices,
        default=UnidadeMedida.UNIDADE,
        verbose_name="Unidade de Medida",
    )
    estoque_atual = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Estoque Atual",
    )
    estoque_minimo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Estoque Mínimo",
        help_text="Alerta quando o estoque atingir este valor",
    )

    # ─── Preços ───────────────────────────────────────────────────────────────
    preco_custo = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Preço de Custo (R$)",
    )
    preco_venda = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Preço de Venda (R$)",
    )

    # ─── Auditoria ────────────────────────────────────────────────────────────
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ["nome"]

    def __str__(self):
        return f"{self.nome} ({self.get_unidade_display()})"

    @property
    def margem_lucro(self):
        """Calcula a margem de lucro em porcentagem."""
        if self.preco_custo and self.preco_custo > 0:
            return ((self.preco_venda - self.preco_custo) / self.preco_custo) * 100
        return Decimal("0.00")

    @property
    def estoque_baixo(self):
        """Retorna True se houver estoque mínimo cadastrado (> 0) e o estoque atual for <= mínimo."""
        if self.estoque_minimo > 0:
            return self.estoque_atual <= self.estoque_minimo
        return False

    @property
    def status_estoque_badge(self):
        """Retorna a classe do badge Bootstrap para o nível de estoque."""
        if self.estoque_atual <= 0:
            return "bg-danger text-white"
        elif self.estoque_minimo > 0 and self.estoque_atual <= self.estoque_minimo:
            return "bg-warning-subtle text-warning-emphasis"
        return "bg-success-subtle text-success"

    @property
    def status_estoque_texto(self):
        """Texto amigável do nível de estoque."""
        if self.estoque_atual <= 0:
            return "Sem Estoque"
        elif self.estoque_minimo > 0 and self.estoque_atual <= self.estoque_minimo:
            return "Estoque Crítico"
        return "Regular"

    def debitar_estoque(self, quantidade):
        """Baixa de estoque (subtrai a quantidade)."""
        if quantidade and Decimal(str(quantidade)) > 0:
            qtd = Decimal(str(quantidade))
            self.estoque_atual = max(Decimal("0.00"), self.estoque_atual - qtd)
            self.save(update_fields=["estoque_atual", "updated_at"])

    def creditar_estoque(self, quantidade):
        """Estorno/Devolução de estoque (soma a quantidade)."""
        if quantidade and Decimal(str(quantidade)) > 0:
            qtd = Decimal(str(quantidade))
            self.estoque_atual += qtd
            self.save(update_fields=["estoque_atual", "updated_at"])


class Servico(models.Model):
    """
    Representa um serviço prestado pela empresa.

    Exemplos: Poda de árvore, Limpeza de piscina, Paisagismo,
    Manutenção mensal, Instalação de equipamento, etc.
    """

    # ─── Identificação ────────────────────────────────────────────────────────
    nome = models.CharField(
        max_length=200,
        verbose_name="Nome do Serviço",
    )
    descricao = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descrição do Serviço",
        help_text="Detalhe o que está incluso neste serviço",
    )

    # ─── Preço ────────────────────────────────────────────────────────────────
    preco_padrao = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Preço Padrão (R$)",
        help_text="Pode ser ajustado individualmente em cada proposta",
    )

    # ─── Auditoria ────────────────────────────────────────────────────────────
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Serviço"
        verbose_name_plural = "Serviços"
        ordering = ["nome"]

    def __str__(self):
        return self.nome
