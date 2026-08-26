"""Forms para o cadastro de clientes."""

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Field

from .models import Cliente


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            "nome", "tipo", "cpf_cnpj",
            "email", "telefone",
            "cep", "logradouro", "numero", "complemento",
            "bairro", "cidade", "estado",
            "observacoes", "ativo",
        ]
        widgets = {
            "observacoes": forms.Textarea(attrs={"rows": 3}),
            "tipo": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Row(
                Column("nome", css_class="col-md-8"),
                Column("tipo", css_class="col-md-4"),
            ),
            Row(
                Column("cpf_cnpj", css_class="col-md-6"),
                Column("telefone", css_class="col-md-3"),
                Column("email", css_class="col-md-3"),
            ),
            Row(
                Column("cep", css_class="col-md-3"),
                Column("logradouro", css_class="col-md-6"),
                Column("numero", css_class="col-md-3"),
            ),
            Row(
                Column("complemento", css_class="col-md-4"),
                Column("bairro", css_class="col-md-4"),
                Column("cidade", css_class="col-md-3"),
                Column("estado", css_class="col-md-1"),
            ),
            Field("observacoes"),
            Field("ativo"),
            Submit("submit", "Salvar Cliente", css_class="btn btn-primary mt-3"),
        )
