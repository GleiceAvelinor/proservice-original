Viewed base.py:149-170
Edited apps.py
Edited apps.py
Edited apps.py
Edited __init__.py
Edited __init__.py
Edited __init__.py
Edited __init__.py
Edited apps.py
Edited views.py
Edited urls.py
Edited __init__.py
Edited apps.py
Edited views.py
Edited urls.py
Edited custom.css
Edited base.html
Edited navbar.html
Edited sidebar.html
Edited login.html
Edited landing.html
Edited index.html
Edited proposta_pdf.html
Edited lista.html
Edited form.html
Edited detalhe.html
Edited confirmar_exclusao.html
Edited lista.html
Edited form.html
Edited detalhe.html
Edited confirmar_exclusao.html
Edited produtos_lista.html
Edited produto_form.html
Edited servicos_lista.html
Edited servico_form.html
Edited confirmar_exclusao.html
Edited setup_tenants.py

Aqui está a arquitetura, o código base completo e o guia de execução do sistema **SaaS Multi-Tenant em Django** para prestadores de serviços.

---

### 🏛️ 1. Visão Geral da Arquitetura Multi-Tenant (`django-tenants`)

O projeto utiliza a arquitetura de **isolamento por Schemas do PostgreSQL** através da biblioteca `django-tenants`.
- **`public` (Schema Compartilhado):** Armazena os dados globais do SaaS — a tabela de empresas (`Client`), domínios (`Domain`) e páginas públicas.
- **`ji_jardinagem`, `levi_piscinas`, etc. (Schemas Isolados):** Cada empresa cadastrada ganha um schema isolado no PostgreSQL contendo suas próprias tabelas de `clientes`, `produtos`, `serviços`, `propostas` e `usuários`. Os dados são fisicamente separados no banco de dados.

---

### 📂 2. Estrutura Completa de Pastas

```
saas/
├── config/
│   ├── settings/
│   │   ├── base.py               # Settings com SHARED_APPS vs TENANT_APPS e TenantMiddleware
│   │   ├── development.py        # Logging de SQL e console backend
│   │   └── production.py         # Configurações de segurança para prod
│   ├── urls.py                   # Roteamento dos tenants (subdomínios)
│   ├── urls_public.py            # Roteamento do domínio raiz (schema público)
│   └── wsgi.py / asgi.py
├── apps/
│   ├── tenants/                  # [SHARED APP] Models Client + Domain (TenantMixin, DomainMixin)
│   ├── clientes/                 # [TENANT APP] Model Cliente com CPF/CNPJ e endereço
│   ├── catalogo/                 # [TENANT APP] Models Produto e Servico
│   ├── propostas/                # [TENANT APP] Proposta, ItemProposta e Serviço WeasyPrint PDF
│   ├── dashboard/                # [TENANT APP] Indicadores financeiros e métricas
│   └── accounts/                 # [TENANT APP] Autenticação por tenant
├── templates/                    # Layouts Bootstrap 5 responsivos e modernos
│   ├── base.html
│   ├── navbar.html
│   ├── components/sidebar.html
│   ├── propostas/proposta_pdf.html # Template estilizado para conversão em PDF
│   └── ...
├── static/css/custom.css         # Estilos customizados
├── requirements.txt              # Django 4.2, django-tenants, WeasyPrint, psycopg2-binary
├── .env.example
├── manage.py
└── setup_tenants.py              # Script de população automatizada dos tenants de demo
```

---

### ⚙️ 3. Destaques da Configuração (`config/settings/base.py`)

No `settings/base.py`, a separação entre apps públicas e isoladas é configurada assim:

```python
# Database Router do django-tenants (obrigatório)
DATABASE_ROUTERS = ("django_tenants.routers.TenantSyncRouter",)

# Middleware de identificação do tenant pelo subdomínio (DEVE SER O PRIMEIRA DA LISTA)
MIDDLEWARE = [
    "django_tenants.middleware.main.TenantMainMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    # ...
]

# Shared Apps (Schema 'public')
SHARED_APPS = [
    "django_tenants",
    "apps.tenants",
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.admin",
    "django.contrib.staticfiles",
    "crispy_forms",
    "crispy_bootstrap5",
]

# Tenant Apps (Schemas isolados por empresa)
TENANT_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.admin",
    "apps.clientes",
    "apps.catalogo",
    "apps.propostas",
    "apps.dashboard",
    "apps.accounts",
]

INSTALLED_APPS = list(SHARED_APPS) + [app for app in TENANT_APPS if app not in SHARED_APPS]

TENANT_MODEL = "tenants.Client"
TENANT_DOMAIN_MODEL = "tenants.Domain"
PUBLIC_SCHEMA_URLCONF = "config.urls_public"
```

---

### 🗄️ 4. Models Central e de Negócio

#### Central Shared (`apps/tenants/models.py`)
```python
from django_tenants.models import TenantMixin, DomainMixin
from django.db import models

class Client(TenantMixin):
    name = models.CharField(max_length=200, verbose_name="Nome da Empresa")
    cnpj = models.CharField(max_length=18, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to="tenants/logos/", blank=True, null=True)
    created_on = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    auto_create_schema = True  # Cria o schema PostgreSQL automaticamente no save()

class Domain(DomainMixin):
    pass
```

#### Tenant App Propostas (`apps/propostas/models.py`)
```python
class Proposta(models.Model):
    numero = models.CharField(max_length=20, unique=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name="propostas")
    data_emissao = models.DateField(default=timezone.now)
    data_validade = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=StatusProposta.choices, default=StatusProposta.RASCUNHO)
    desconto = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    condicao_pagamento = models.CharField(max_length=200, blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)

    @property
    def subtotal(self):
        return sum(item.total for item in self.itens.all())

    @property
    def valor_desconto(self):
        return (self.subtotal * self.desconto) / Decimal("100")

    @property
    def total(self):
        return self.subtotal - self.valor_desconto
```

---

### 📄 5. Geração de PDF de Propostas (`apps/propostas/services/pdf_service.py`)

A conversão do HTML da proposta comercial em PDF de alta qualidade via **WeasyPrint**:

```python
import io
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db import connection
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

def gerar_pdf_proposta(proposta, request=None):
    tenant = getattr(connection, "tenant", None)

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
```

---

### 🚀 6. Guia Prático de Execução

#### 1. Instalação das Dependências
```bash
pip install -r requirements.txt
```

#### 2. Criação do Banco de Dados no PostgreSQL
Crie um banco de dados PostgreSQL com o nome `saas_db` (ou conforme configurado no `.env`):
```sql
CREATE DATABASE saas_db;
```

#### 3. Mapeamento no arquivo `hosts` do Sistema Operacional
Para simular o acesso aos subdomínios localmente em desenvolvimento, edite o arquivo `hosts` (`C:\Windows\System32\drivers\etc\hosts` no Windows ou `/etc/hosts` no Linux/macOS) adicionando:
```text
127.0.0.1  localhost
127.0.0.1  ji.localhost
127.0.0.1  levi.localhost
```

#### 4. Executar Migrações do `django-tenants`

```bash
# Migra o schema público (Shared Apps)
python manage.py migrate_schemas --shared

# Popula o banco e cria os tenants de teste (Ji Jardinagem e Levi Piscinas)
python setup_tenants.py

# Inicia o servidor
python manage.py runserver
```

#### 5. Acessar os Tenants no Navegador

- **Ji Jardinagem:** `http://ji.localhost:8000/`
  - **Login:** `admin` | **Senha:** `admin123`
- **Levi Piscinas:** `http://levi.localhost:8000/`
  - **Login:** `admin` | **Senha:** `admin123`
- **Portal SaaS Público:** `http://localhost:8000/`