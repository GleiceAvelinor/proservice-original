"""Forms para Produtos e Serviços do catálogo."""

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Field

from .models import Produto, Servico


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = [
            "nome", "codigo", "descricao", "unidade",
            "preco_custo", "preco_venda",
            "estoque_atual", "estoque_minimo", "ativo",
        ]
        widgets = {
            "descricao": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Row(
                Column("nome", css_class="col-md-8"),
                Column("codigo", css_class="col-md-4"),
            ),
            Field("descricao"),
            Row(
                Column("unidade", css_class="col-md-4"),
                Column("estoque_atual", css_class="col-md-4"),
                Column("estoque_minimo", css_class="col-md-4"),
            ),
            Row(
                Column("preco_custo", css_class="col-md-6"),
                Column("preco_venda", css_class="col-md-6"),
            ),
            Field("ativo"),
            Submit("submit", "Salvar Produto", css_class="btn btn-primary mt-3"),
        )


class ServicoForm(forms.ModelForm):
    class Meta:
        model = Servico
        fields = ["nome", "descricao", "preco_padrao", "ativo"]
        widgets = {
            "descricao": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            "nome",
            Field("descricao"),
            Row(
                Column("preco_padrao", css_class="col-md-4"),
                Column("ativo", css_class="col-md-4 align-self-end"),
            ),
            Submit("submit", "Salvar Serviço", css_class="btn btn-primary mt-3"),
        )
