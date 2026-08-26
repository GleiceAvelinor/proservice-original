from django import forms
from apps.tenants.models import Client


class EmpresaSignUpForm(forms.Form):
    # Dados da Empresa
    name = forms.CharField(max_length=200, label="Nome da Empresa / Condomínio")
    schema_name = forms.CharField(max_length=63, label="Subdomínio Desejado")
    cnpj = forms.CharField(max_length=18, required=False, label="CNPJ")
    email = forms.EmailField(label="E-mail de Contato")
    phone = forms.CharField(max_length=20, required=False, label="Telefone / WhatsApp")

    # Dados do Administrador Inicial
    admin_username = forms.CharField(max_length=150, label="Usuário Administrador")
    admin_email = forms.EmailField(label="E-mail do Administrador")
    admin_password = forms.CharField(label="Senha", widget=forms.PasswordInput)

    def clean_schema_name(self):
        schema_name = self.cleaned_data["schema_name"].lower().strip()
        
        # Evita palavras reservadas do sistema
        reserved_names = ["public", "admin", "static", "media", "api", "www"]
        if schema_name in reserved_names:
            raise forms.ValidationError("Este nome de subdomínio é reservado pelo sistema.")

        if Client.objects.filter(schema_name=schema_name).exists():
            raise forms.ValidationError("Este subdomínio já está em uso. Escolha outro.")
            
        return schema_name