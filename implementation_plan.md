# SaaS Django Multi-Tenant para Prestadores de Serviços

## Visão Geral

Sistema SaaS completo em Django com isolamento total de dados por empresa (tenant) usando `django-tenants` + PostgreSQL multi-schema. Cada empresa (ex: Ji Jardinagem, Levi Piscinas) possui seu próprio schema isolado no banco de dados.

## Estrutura do Projeto

```
saas-servicos/
├── config/                        # Configurações do projeto Django
│   ├── settings/
│   │   ├── base.py                # Settings base compartilhados
│   │   ├── development.py         # Settings de desenvolvimento
│   │   └── production.py          # Settings de produção
│   ├── urls.py                    # URLs raiz (roteamento por tenant)
│   └── wsgi.py
├── apps/
│   ├── tenants/                   # [SHARED APP] Gestão de tenants/empresas
│   │   ├── models.py              # Client + Domain (TenantMixin, DomainMixin)
│   │   ├── admin.py
│   │   └── migrations/
│   ├── clientes/                  # [TENANT APP] Cadastro de clientes do tenant
│   │   ├── models.py              # Model Cliente
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── templates/
│   ├── catalogo/                  # [TENANT APP] Produtos e Serviços
│   │   ├── models.py              # Models Produto, Servico
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── templates/
│   ├── propostas/                 # [TENANT APP] Propostas Comerciais + PDF
│   │   ├── models.py              # Models Proposta, ItemProposta
│   │   ├── views.py               # CRUD + view de geração de PDF
│   │   ├── services/
│   │   │   └── pdf_service.py     # Serviço de geração de PDF (WeasyPrint)
│   │   ├── urls.py
│   │   └── templates/
│   └── dashboard/                 # [TENANT APP] Dashboard financeiro
│       ├── views.py
│       └── templates/
├── templates/                     # Templates globais (base.html, navbar, etc.)
├── static/                        # CSS, JS, imagens
├── requirements.txt
├── .env.example
└── manage.py
```

## Arquitetura Multi-Tenant

```
                        ┌─────────────────────────────┐
                        │        PostgreSQL DB          │
                        │                              │
┌──────────────┐        │  ┌──────────────────────┐   │
│  Requisição  │──────▶ │  │   Schema: public     │   │
│  ji.saas.com │        │  │  (shared_apps)       │   │
└──────────────┘        │  │  - tenants_client    │   │
                        │  │  - tenants_domain    │   │
┌──────────────┐        │  │  - django_migrations │   │
│  Requisição  │──────▶ │  └──────────────────────┘   │
│levi.saas.com │        │                              │
└──────────────┘        │  ┌──────────────────────┐   │
        │               │  │  Schema: ji_jardinagem│   │
        │               │  │  (tenant_apps)        │   │
        ▼               │  │  - clientes          │   │
  TenantMiddleware      │  │  - produtos          │   │
  (identifica tenant    │  │  - propostas         │   │
   pelo domínio)        │  └──────────────────────┘   │
                        │                              │
                        │  ┌──────────────────────┐   │
                        │  │  Schema: levi_piscinas│   │
                        │  │  (tenant_apps)        │   │
                        │  │  - clientes          │   │
                        │  │  - produtos          │   │
                        │  │  - propostas         │   │
                        │  └──────────────────────┘   │
                        └─────────────────────────────┘
```

## Proposed Changes

### Configuração do Projeto

#### [NEW] requirements.txt
#### [NEW] .env.example
#### [NEW] config/settings/base.py — Configuração completa com django-tenants
#### [NEW] config/urls.py — URLs com roteamento por schema

---

### App: tenants (Shared)

#### [NEW] apps/tenants/models.py — Client (TenantMixin) + Domain (DomainMixin)
#### [NEW] apps/tenants/admin.py

---

### App: clientes (Tenant)

#### [NEW] apps/clientes/models.py — Model Cliente com CPF/CNPJ
#### [NEW] apps/clientes/views.py — CRUD completo
#### [NEW] apps/clientes/urls.py
#### [NEW] apps/clientes/forms.py
#### [NEW] apps/clientes/templates/clientes/

---

### App: catalogo (Tenant)

#### [NEW] apps/catalogo/models.py — Models Produto e Servico
#### [NEW] apps/catalogo/views.py — CRUD completo
#### [NEW] apps/catalogo/urls.py
#### [NEW] apps/catalogo/forms.py

---

### App: propostas (Tenant)

#### [NEW] apps/propostas/models.py — Proposta + ItemProposta com cálculo automático
#### [NEW] apps/propostas/views.py — CRUD + exportação PDF
#### [NEW] apps/propostas/services/pdf_service.py — WeasyPrint PDF generation
#### [NEW] apps/propostas/templates/propostas/proposta_pdf.html — Template do PDF

---

### App: dashboard (Tenant)

#### [NEW] apps/dashboard/views.py — Métricas financeiras agregadas
#### [NEW] apps/dashboard/templates/dashboard/index.html

---

### Templates e Static

#### [NEW] templates/base.html — Layout base com Bootstrap 5
#### [NEW] templates/navbar.html — Navegação responsiva

## Verification Plan

### Comandos Essenciais
```bash
# 1. Criar schema público (shared)
python manage.py migrate_schemas --shared

# 2. Criar um novo tenant
python manage.py shell -c "
from apps.tenants.models import Client, Domain
tenant = Client(schema_name='ji_jardinagem', name='Ji Jardinagem')
tenant.save()
domain = Domain(domain='ji.localhost', tenant=tenant, is_primary=True)
domain.save()
"

# 3. Migrar todos os tenants existentes
python manage.py migrate_schemas

# 4. Rodar servidor de desenvolvimento
python manage.py runserver
```

### Manual Verification
- Acessar `ji.localhost:8000` → deve carregar painel da Ji Jardinagem
- Acessar `levi.localhost:8000` → deve carregar painel da Levi Piscinas (dados isolados)
- Criar proposta e fazer download do PDF
- Verificar dashboard com métricas do tenant correto
