"""Formulário para edição dos dados da empresa (Tenant) incluindo logo.

A logo só pode ser alterada pelo Administrador Global do SaaS (settings.SAAS_ADMIN_EMAILS).
Admins locais do subdomínio (mesmo com is_superuser=True) não têm essa permissão.
"""

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Field

from .models import Client
from .permissions import is_saas_admin


class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["name", "cnpj", "phone", "email", "address", "logo"]
        widgets = {
            "address": forms.Textarea(attrs={"rows": 3}),
            "logo": forms.FileInput(attrs={"class": "form-control", "accept": "image/*"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_enctype = "multipart/form-data"

        # ─── Restrição de Logo: apenas Admin Global do SaaS pode alterar ──────
        if is_saas_admin(user):
            layout = Layout(
                Row(
                    Column("name", css_class="col-md-8"),
                    Column("cnpj", css_class="col-md-4"),
                ),
                Row(
                    Column("phone", css_class="col-md-6"),
                    Column("email", css_class="col-md-6"),
                ),
                Field("address"),
                Field("logo"),
                Submit("submit", "Salvar Dados da Empresa", css_class="btn btn-primary mt-3"),
            )
        else:
            # Remove o campo do form — protege mesmo contra POST forjado com arquivo
            self.fields.pop("logo", None)
            layout = Layout(
                Row(
                    Column("name", css_class="col-md-8"),
                    Column("cnpj", css_class="col-md-4"),
                ),
                Row(
                    Column("phone", css_class="col-md-6"),
                    Column("email", css_class="col-md-6"),
                ),
                Field("address"),
                Submit("submit", "Salvar Dados da Empresa", css_class="btn btn-primary mt-3"),
            )

        self.helper.layout = layout
