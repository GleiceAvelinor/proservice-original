"""
============================================================
APP: clientes — [TENANT APP]
============================================================
Cadastro de clientes de cada empresa prestadora de serviços.
Cada tenant possui seus próprios clientes, totalmente isolados
no schema PostgreSQL daquela empresa.

Model: Cliente
"""

from django.db import models


class Cliente(models.Model):
    """
    Representa um cliente da empresa (tenant).

    Os dados ficam armazenados no schema isolado do tenant,
    garantindo que Ji Jardinagem nunca veja clientes de Levi Piscinas.
    """

    # ─── Dados Pessoais / Identificação ───────────────────────────────────────
    nome = models.CharField(
        max_length=200,
        verbose_name="Nome / Razão Social",
    )
    cpf_cnpj = models.CharField(
        max_length=18,
        blank=True,
        null=True,
        verbose_name="CPF / CNPJ",
        help_text="CPF: 000.000.000-00 | CNPJ: 00.000.000/0000-00",
    )
    tipo = models.CharField(
        max_length=10,
        choices=[("PF", "Pessoa Física"), ("PJ", "Pessoa Jurídica")],
        default="PF",
        verbose_name="Tipo",
    )

    # ─── Contato ──────────────────────────────────────────────────────────────
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name="E-mail",
    )
    telefone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Telefone / WhatsApp",
    )

    # ─── Endereço ─────────────────────────────────────────────────────────────
    cep = models.CharField(
        max_length=9,
        blank=True,
        null=True,
        verbose_name="CEP",
    )
    logradouro = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        verbose_name="Endereço",
    )
    numero = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="Número",
    )
    complemento = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Complemento",
    )
    bairro = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Bairro",
    )
    cidade = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Cidade",
    )
    estado = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        verbose_name="Estado (UF)",
    )

    # ─── Informações Adicionais ───────────────────────────────────────────────
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações",
    )

    # ─── Auditoria ────────────────────────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ["nome"]

    def __str__(self):
        return self.nome

    @property
    def endereco_completo(self):
        """Retorna o endereço formatado para exibição."""
        partes = filter(None, [
            self.logradouro,
            self.numero,
            self.complemento,
            self.bairro,
            f"{self.cidade}/{self.estado}" if self.cidade else None,
            self.cep,
        ])
        return ", ".join(partes)

    @property
    def telefone_whatsapp(self):
        """Retorna o telefone apenas com dígitos e código de país 55 para o WhatsApp."""
        if not self.telefone:
            return ""
        import re
        num = re.sub(r"\D", "", str(self.telefone))
        if len(num) in (10, 11) and not num.startswith("55"):
            num = "55" + num
        return num
