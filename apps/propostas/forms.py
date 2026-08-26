"""
Forms para Propostas Comerciais.

Inclui formulário principal da proposta + formset inline para os itens.
O formset permite adicionar/remover itens dinamicamente no front-end.
"""

from django import forms
from django.forms import inlineformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Field, Fieldset

from .models import Proposta, ItemProposta
from apps.clientes.models import Cliente
from apps.catalogo.models import Produto, Servico


class PropostaForm(forms.ModelForm):
    class Meta:
        model = Proposta
        fields = [
            "titulo", "cliente",
            "data_emissao", "data_validade",
            "status", "desconto",
            "condicao_pagamento", "observacoes",
        ]
        widgets = {
            "data_emissao": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "data_validade": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "observacoes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False  # O form tag é controlado no template
        self.helper.layout = Layout(
            Field("titulo"),
            Row(
                Column("cliente", css_class="col-md-8"),
                Column("status", css_class="col-md-4"),
            ),
            Row(
                Column("data_emissao", css_class="col-md-4"),
                Column("data_validade", css_class="col-md-4"),
                Column("desconto", css_class="col-md-4"),
            ),
            Field("condicao_pagamento"),
            Field("observacoes"),
        )


class ItemPropostaForm(forms.ModelForm):
    class Meta:
        model = ItemProposta
        fields = [
            "tipo", "produto", "servico",
            "descricao", "unidade",
            "quantidade", "preco_unitario", "ordem",
        ]
        widgets = {
            "descricao": forms.TextInput(attrs={"class": "form-control", "placeholder": "Descrição do item"}),
            "quantidade": forms.NumberInput(attrs={"step": "0.01", "class": "form-control quantidade-input"}),
            "preco_unitario": forms.NumberInput(attrs={"step": "0.01", "class": "form-control preco-input"}),
            "unidade": forms.TextInput(attrs={"class": "form-control"}),
            "ordem": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tipo"].required = False
        self.fields["descricao"].required = False
        self.fields["unidade"].required = False
        self.fields["preco_unitario"].required = False
        self.fields["ordem"].required = False
        if "quantidade" in self.fields:
            self.fields["quantidade"].initial = 1.0

    def has_changed(self):
        """
        Retorna True somente se o usuário preencheu algum dado relevante do item.
        Evita que linhas vazias em branco disparem a gravação de registros nulos no PostgreSQL.
        """
        if not self.instance.pk:
            has_data = any([
                self.data.get(self.add_prefix("produto")),
                self.data.get(self.add_prefix("servico")),
                self.data.get(self.add_prefix("descricao")),
                self.data.get(self.add_prefix("preco_unitario")),
            ])
            if not has_data:
                return False
        return super().has_changed()

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get("ordem") is None:
            cleaned_data["ordem"] = 0

        # Se o formulário foi marcado para deletar no formset, não valida mais nada
        if cleaned_data.get("DELETE"):
            return cleaned_data

        produto = cleaned_data.get("produto")
        servico = cleaned_data.get("servico")
        quantidade = cleaned_data.get("quantidade")
        preco_unitario = cleaned_data.get("preco_unitario")
        descricao = cleaned_data.get("descricao")
        tipo = cleaned_data.get("tipo")

        # Se nenhum item principal foi preenchido, tratamos como linha vazia para ignorar ou deletar
        if not produto and not servico and not preco_unitario and not descricao:
            if self.instance.pk:
                cleaned_data["DELETE"] = True
            return cleaned_data

        if produto:
            cleaned_data["tipo"] = "PRODUTO"
            if not descricao:
                cleaned_data["descricao"] = produto.nome
            if not cleaned_data.get("unidade"):
                cleaned_data["unidade"] = getattr(produto, "unidade", "UN")
            if preco_unitario is None:
                cleaned_data["preco_unitario"] = produto.preco_venda
        elif servico:
            cleaned_data["tipo"] = "SERVICO"
            if not descricao:
                cleaned_data["descricao"] = servico.nome
            if not cleaned_data.get("unidade"):
                cleaned_data["unidade"] = "UN"
            if preco_unitario is None:
                cleaned_data["preco_unitario"] = servico.preco_padrao
        elif descricao:
            if not tipo:
                cleaned_data["tipo"] = "SERVICO"
            if preco_unitario is None:
                cleaned_data["preco_unitario"] = 0
        else:
            raise forms.ValidationError("Selecione um Produto ou Serviço para o item.")

        return cleaned_data


# ─── InlineFormSet ─────────────────────────────────────────────────────────────
# Permite editar múltiplos itens na mesma view da proposta.
ItemPropostaFormSet = inlineformset_factory(
    Proposta,
    ItemProposta,
    form=ItemPropostaForm,
    extra=1,        # 1 linha em branco inicial
    can_delete=True,
    min_num=1,
    validate_min=True,
)
