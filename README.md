# 🚀 SaaS Multi-Tenant para Prestadores de Serviços

Sistema SaaS completo em **Django 5.1** para gestão comercial de micro e pequenos prestadores de serviços, com **isolamento total de dados por empresa (multi-schema)** via `django-tenants` + **PostgreSQL**, processamento assíncrono com **Celery + Redis** e geração de Propostas Comerciais em **PDF**.

---

## 📌 Sumário

- [Visão Geral & Funcionalidades](#-visão-geral--funcionalidades)
- [Arquitetura Multi-Tenant](#️-arquitetura-multi-tenant)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Requisitos & Instalação](#️-requisitos--instalação)
- [Configuração de Subdomínios Locais](#-configuração-de-subdomínios-locais)
- [Executando o Projeto](#-executando-o-projeto)
- [Credenciais de Acesso & Usuários](#-credenciais-de-acesso--usuários)
- [Mapa Completo de URLs & Rotas](#-mapa-completo-de-urls--rotas)
- [Hierarquia de Permissões](#-hierarquia-de-permissões)
- [Variáveis de Ambiente (.env)](#-variáveis-de-ambiente-env)
- [Celery & Redis — Tarefas Assíncronas](#-celery--redis--tarefas-assíncronas)
- [Licença](#-licença)

---

## 🌐 Visão Geral & Funcionalidades

Cada empresa cadastrada possui um **subdomínio próprio** (ex: `ji.localhost:8000`) e um **schema isolado no PostgreSQL**, garantindo total privacidade e segurança dos dados entre tenants.

| Funcionalidade | Descrição |
|---|---|
| **Landing Page & Signup** | Cadastro de novas empresas com status inativo (pendente de aprovação) e fluxo de liberação por E-mail / WhatsApp |
| **Aprovação do Admin Master** | Notificação automática com token UUID de ativação, botões de liberação direta e envio por WhatsApp no Django Admin |
| **Bloqueio por Middleware** | `TenantActiveMiddleware` que intercepta requisições em tempo real e bloqueia o acesso a subdomínios inativos (HTTP 403) |
| **Portal de Acesso** | Página pública (`/signup/acessar/`) com busca em tempo real e catálogo de empresas ativas cadastradas |
| **Manual do Usuário** | Guia completo passo a passo disponível no arquivo [`MANUAL_DO_USUARIO.md`](MANUAL_DO_USUARIO.md) |
| **Dashboard Financeiro** | KPIs de faturamento, propostas por status, taxa de conversão e gráficos mensais (Chart.js) |
| **Onboarding Guiado** | Checklist de primeiros passos no dashboard para novos tenants |
| **Gestão de Clientes** | CRUD completo com histórico de propostas por cliente |
| **Catálogo de Produtos & Serviços** | Controle de estoque, margem de lucro, preços e unidades de medida |
| **Propostas Comerciais** | Criação com itens dinâmicos, PDF profissional, envio automático por E-mail/WhatsApp e link público de aprovação pelo cliente |
| **Aprovação Pública pelo Cliente** | Link UUID único enviado ao cliente para aprovar/recusar proposta sem login |
| **Celery + Redis** | Fila de tarefas assíncronas com isolamento de schema por tenant e execução síncrona inteligente em dev |
| **Configurações da Empresa** | Dados cadastrais e logomarca (restrição de upload exclusiva ao Admin Global do SaaS) |

---

## 🏗️ Arquitetura Multi-Tenant

```
                                ┌─────────────────────────────┐
                                │        PostgreSQL DB        │
                                │                             │
┌──────────────┐                │  ┌──────────────────────┐   │
│  Requisição  │──────────────▶ │  │   Schema: public     │   │
│saas.localhost│                │  │  (shared_apps)       │   │
└──────────────┘                │  │  - tenants_client    │   │
                                │  │  - tenants_domain    │   │
┌──────────────┐                │  └──────────────────────┘   │
│  Requisição  │──────────────▶ │                             │
│ ji.localhost │                │  ┌──────────────────────┐   │
└──────────────┘                │  │  Schema:ji_jardinagem│   │
        │                       │  │  (tenant_apps)       │   │
        ▼                       │  │  - clientes          │   │
  TenantMiddleware              │  │  - propostas         │   │
 (roteia por domínio)           │  │  - catalogo          │   │
                                │  └──────────────────────┘   │
                                └─────────────────────────────┘
```

**Roteamento de URLs:**
- `config/urls_public.py` → Schema `public` (Landing Page, Signup, Admin Global)
- `config/urls.py` → Schemas de tenant (Dashboard, Propostas, Clientes etc.)

---

## 📁 Estrutura do Projeto

```
saas/
├── apps/
│   ├── accounts/          # Autenticação: login, logout, recuperação de senha
│   ├── catalogo/          # Produtos e Serviços (estoque, preços)
│   ├── clientes/          # Cadastro e gestão de clientes do tenant
│   ├── dashboard/         # KPIs, gráficos e onboarding guiado
│   ├── propostas/         # Propostas comerciais, PDF, aprovação pública, Celery
│   ├── signup/            # Onboarding e registro público de novos tenants
│   └── tenants/           # Client & Domain (django-tenants), configurações de empresa
├── config/
│   ├── settings/          # base.py, development.py, production.py
│   ├── celery.py          # Configuração do Celery App
│   ├── urls.py            # Roteador de URLs dos Tenants (subdomínios)
│   └── urls_public.py     # Roteador de URLs Públicas (schema public)
├── templates/             # HTML com Bootstrap 5 + Bootstrap Icons
├── static/                # CSS, JS e assets estáticos
├── media/                 # Logomarcas e uploads por tenant
├── Dockerfile             # Container do app Django (Python 3.11)
├── docker-compose.yml     # Orquestração: Django + PostgreSQL + Redis + Celery
├── setup_tenants.py       # Seed de dados: tenants de demonstração + dados iniciais
├── manage.py
└── requirements.txt
```

---

## 🛠️ Requisitos & Instalação

### Pré-requisitos

- **Docker Desktop** (recomendado) — inclui Python, PostgreSQL, Redis
- ou manualmente: **Python 3.11+**, **PostgreSQL 14+**, **Redis 7+**
- Dependências nativas do WeasyPrint: `cairo`, `pango`, `gdk-pixbuf` (Linux/macOS) ou via container

---

## 🌐 Configuração de Subdomínios Locais

Adicione as entradas abaixo ao seu arquivo de `hosts` para que os subdomínios sejam resolvidos localmente:

- **Windows:** `C:\Windows\System32\drivers\etc\hosts`
- **Linux/macOS:** `/etc/hosts`

```
127.0.0.1   localhost
127.0.0.1   saas.localhost
127.0.0.1   ji.localhost
127.0.0.1   levi.localhost
```

---

## 🚀 Executando o Projeto

### ✅ Opção 1: Docker Compose (Recomendado)

Sobe Django, PostgreSQL, Redis e Celery Worker de uma vez:

```bash
# 1. Clone o repositório
git clone <url-do-repo>
cd saas

# 2. Copie e configure o arquivo de ambiente
cp .env.example .env
# Edite o .env conforme necessário (veja seção de variáveis abaixo)

# 3. Suba todos os containers
docker-compose up --build -d

# 4. Crie os schemas e popule os dados de demonstração
docker-compose exec web python setup_tenants.py
```

> **Após isso, o sistema está acessível em:** `http://ji.localhost:8000/`

Para acompanhar os logs em tempo real:
```bash
docker-compose logs -f
```

---

### ⚙️ Opção 2: Execução Manual (Local)

```bash
# 1. Crie e ative o ambiente virtual
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Configure o .env com conexão ao PostgreSQL local

# 4. Execute as migrações (schema público e tenants)
python manage.py migrate_schemas

# 5. Popule os dados de demonstração
python setup_tenants.py

# 6. Terminal 1 — Servidor Django
python manage.py runserver 0.0.0.0:8000

# 7. Terminal 2 — Worker Celery (tarefas assíncronas)
celery -A config worker --loglevel=info
```

---

## 🛡️ Fluxo de Aprovação de Empresas & Bloqueio por Middleware

### 1. Liberação de Cadastro pelo Admin Master
- Ao se cadastrar via `/signup/`, a nova empresa é criada com **`is_active = False`** (acesso suspenso por padrão).
- O **Administrador Master** recebe uma notificação automática via E-mail contendo o resumo do cadastro e o **Link de Ativação Único** (`http://localhost:8000/signup/ativar/<token>/`).
- No Django Admin (`http://localhost:8000/admin/tenants/client/`), o Admin Master tem acesso a:
  - **Botão "Ativar"**: Liberação instantânea em 1 clique na tabela.
  - **Botão "Enviar WhatsApp"**: Disparo de mensagem formatada via WhatsApp Web para o gestor da empresa com o link de liberação.
  - **Ação em lote**: *"🟢 Aprovar e Ativar Empresas Selecionadas"*.

### 2. Bloqueio em Tempo Real (`TenantActiveMiddleware`)
- O middleware `TenantActiveMiddleware` valida o campo `is_active` em todas as requisições para subdomínios de empresas.
- Se `is_active == False` (conta pendente ou suspensa), qualquer tentativa de acesso/login é bloqueada imediatamente com status **HTTP 403 Forbidden** e a tela *"Acesso Temporariamente Suspenso — Conta Desativada"*.

---

## 🔑 Credenciais de Acesso & Usuários

> **Importante:** Os dados abaixo são para o ambiente de **desenvolvimento/demonstração** criados pelo `setup_tenants.py`. Nunca use essas senhas em produção.

### Admin Global do SaaS — Schema Público

| Campo | Valor |
|---|---|
| **URL de acesso** | `http://saas.localhost:8000/admin/` ou `http://localhost:8000/admin/` |
| **Username** | `admin` |
| **Senha** | *(criado manualmente — veja abaixo)* |
| **Tipo de usuário** | `is_superuser=True` no schema `public` |
| **Permissões exclusivas** | Alterar logomarca dos tenants, criar/remover tenants, gerenciar usuários globalmente |

Para criar o Admin Global do SaaS manualmente:
```bash
# Via Docker:
docker-compose exec web python manage.py createsuperuser

# Ou localmente:
python manage.py createsuperuser
```

> **Atenção:** Para habilitar a permissão de alterar a logomarca dos tenants em produção, adicione o e-mail deste usuário ao `.env`:
> ```
> SAAS_ADMIN_EMAILS=seuemail@saas.com
> ```

---

### Tenant Ji Jardinagem & Paisagismo

| Campo | Valor |
|---|---|
| **URL de acesso** | `http://ji.localhost:8000/` |
| **URL de login** | `http://ji.localhost:8000/accounts/login/` |
| **Username** | `admin` |
| **E-mail** | `admin@jijardinagem.com` |
| **Senha** | `admin123` |
| **Tipo** | `is_superuser=True` no schema `ji_jardinagem` (Admin local do tenant) |
| **Permissão de logo** | ❌ Bloqueado — apenas o Admin Global do SaaS pode alterar |
| **Dados de demo** | 1 cliente, 1 produto, 1 serviço, 1 proposta pendente |

---

### Tenant Levi Piscinas & Manutenção

| Campo | Valor |
|---|---|
| **URL de acesso** | `http://levi.localhost:8000/` |
| **URL de login** | `http://levi.localhost:8000/accounts/login/` |
| **Username** | `admin` |
| **E-mail** | `admin@levipiscinas.com` |
| **Senha** | `admin123` |
| **Tipo** | `is_superuser=True` no schema `levi_piscinas` (Admin local do tenant) |
| **Permissão de logo** | ❌ Bloqueado — apenas o Admin Global do SaaS pode alterar |
| **Dados de demo** | 1 cliente, 1 produto, 1 serviço |

---

## 📍 Mapa Completo de URLs & Rotas

### 🌍 Domínio Público (`localhost:8000` / `saas.localhost:8000`)

| URL | Função |
|---|---|
| `GET /` | Landing Page pública |
| `GET /signup/` | Cadastro de nova empresa (onboarding) |
| `GET /admin/` | Painel Admin Global do SaaS |

---

### 🏢 Subdomínio Tenant (`ji.localhost:8000` / `levi.localhost:8000`)

#### Autenticação (`/accounts/`)

| URL | Método | Função |
|---|---|---|
| `/accounts/login/` | GET / POST | Tela de login do tenant |
| `/accounts/logout/` | POST | Logout |
| `/accounts/password-reset/` | GET / POST | Solicitar redefinição de senha |
| `/accounts/password-reset/done/` | GET | Confirmação de envio do e-mail |
| `/accounts/reset/<uidb64>/<token>/` | GET / POST | Formulário de nova senha |
| `/accounts/reset/done/` | GET | Senha redefinida com sucesso |

#### Dashboard (`/dashboard/`)

| URL | Função |
|---|---|
| `/dashboard/` | KPIs, gráficos, propostas recentes e onboarding guiado |

#### Clientes (`/clientes/`)

| URL | Função |
|---|---|
| `/clientes/` | Listagem de clientes |
| `/clientes/novo/` | Criar novo cliente |
| `/clientes/<id>/` | Detalhes do cliente |
| `/clientes/<id>/editar/` | Editar cliente |
| `/clientes/<id>/excluir/` | Excluir cliente |

#### Catálogo (`/catalogo/`)

| URL | Função |
|---|---|
| `/catalogo/produtos/` | Listagem de produtos |
| `/catalogo/produtos/novo/` | Criar produto |
| `/catalogo/produtos/<id>/editar/` | Editar produto |
| `/catalogo/servicos/` | Listagem de serviços |
| `/catalogo/servicos/novo/` | Criar serviço |

#### Propostas (`/propostas/`)

| URL | Método | Função |
|---|---|---|
| `/propostas/` | GET | Listagem com filtros por status |
| `/propostas/nova/` | GET / POST | Criar proposta com itens dinâmicos |
| `/propostas/<id>/` | GET | Detalhes da proposta |
| `/propostas/<id>/editar/` | GET / POST | Editar proposta |
| `/propostas/<id>/excluir/` | GET / POST | Excluir proposta |
| `/propostas/<id>/pdf/` | GET | Download do PDF profissional |
| `/propostas/<id>/enviar-email/` | POST | Enviar proposta por e-mail (Celery) |
| `/propostas/<id>/status/<status>/` | POST | Mudar status (APROVADA, PENDENTE, etc.) |
| `/propostas/p/<uuid>/` | GET | **Aprovação pública pelo cliente (sem login)** |
| `/propostas/p/<uuid>/aprovar/` | POST | Cliente aprova proposta |
| `/propostas/p/<uuid>/recusar/` | POST | Cliente recusa proposta |

#### Empresa / Configurações (`/empresa/`)

| URL | Função | Permissão |
|---|---|---|
| `/empresa/configuracoes/` | Editar dados cadastrais da empresa | Qualquer usuário autenticado |
| `/empresa/configuracoes/` (campo logo) | Upload / troca de logomarca | **Exclusivo ao Admin Global do SaaS** |

---

## 🔐 Hierarquia de Permissões

```
┌─────────────────────────────────────────────────────────┐
│              Admin Global do SaaS                       │
│  (e-mail em SAAS_ADMIN_EMAILS + is_superuser=True)      │
│                                                         │
│  ✅ Acessar Django Admin global (/admin/)               │
│  ✅ Criar / remover tenants                             │
│  ✅ Alterar logomarca de qualquer tenant                │
│  ✅ Acessar admin de qualquer subdomínio                │
└────────────────────────┬────────────────────────────────┘
                         │ criado no schema public
                         ▼
┌─────────────────────────────────────────────────────────┐
│              Admin Local do Tenant                      │
│  (is_superuser=True no schema do subdomínio)            │
│                                                         │
│  ✅ Gerenciar clientes, produtos, propostas             │
│  ✅ Acessar Django Admin do seu subdomínio              │
│  ✅ Editar dados cadastrais da empresa                  │
│  ❌ Alterar logomarca (bloqueado → HTTP 403)            │
│  ❌ Ver dados de outros tenants                         │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              Cliente Final (sem login)                  │
│                                                         │
│  ✅ Acessar link público de proposta (/propostas/p/<uuid>/) │
│  ✅ Aprovar ou recusar proposta                         │
│  ✅ Baixar PDF da proposta                              │
│  ❌ Nenhum acesso ao painel                             │
└─────────────────────────────────────────────────────────┘
```

---

## ⚙️ Variáveis de Ambiente (.env)

```env
# ─── Django Core ────────────────────────────────────────
SECRET_KEY=<chave-secreta-forte-em-producao>
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,.localhost
DJANGO_SETTINGS_MODULE=config.settings.development
BASE_DOMAIN=localhost

# ─── PostgreSQL ─────────────────────────────────────────
DB_NAME=saas_db
DB_USER=postgres
DB_PASSWORD=<sua-senha>
DB_HOST=localhost           # ou 'db' dentro do Docker
DB_PORT=5432
DB_SSLMODE=prefer

# ─── E-mail ─────────────────────────────────────────────
# Desenvolvimento (exibe no terminal):
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
# Produção (SMTP):
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=exemple@email.com
# EMAIL_HOST_PASSWORD=xxxxxxxxxxx
# DEFAULT_FROM_EMAIL=exemple@email.com

# ─── Celery & Redis ──────────────────────────────────────
CELERY_BROKER_URL=redis://localhost:6379/0   # ou redis://redis:6379/0 no Docker
CELERY_RESULT_BACKEND=django-db

# ─── Controle de Acesso Nível SaaS ──────────────────────
# E-mails dos Admins Globais do SaaS que podem alterar logomarcas dos tenants.
# Deixe em branco em dev para que qualquer superuser tenha acesso.
SAAS_ADMIN_EMAILS=admin@saas.com,outro@admin.com
```

---

## 🔄 Celery & Redis — Tarefas Assíncronas

O sistema utiliza Celery para processar tarefas pesadas (ex: envio de e-mail com PDF) sem bloquear a resposta HTTP.

### Arquitetura de Isolamento por Tenant

Como o Celery Worker roda fora do contexto do request HTTP, ele não possui o middleware de roteamento de schema. Portanto, todas as tasks recebem o `schema_name` e usam `tenant_context`:

```python
# apps/propostas/tasks.py
from django_tenants.utils import tenant_context

@shared_task
def enviar_proposta_email_async(proposta_id, schema_name):
    tenant = Client.objects.get(schema_name=schema_name)
    with tenant_context(tenant):
        proposta = Proposta.objects.get(pk=proposta_id)
        enviar_proposta_email(proposta)
```

### Fallback Automático

Se o Redis/Celery estiver offline, o sistema executa o envio de forma **síncrona automática** — sem erro para o usuário.

### Monitoramento

```bash
# Ver tasks em execução / histórico:
docker-compose exec celery celery -A config inspect active

# Flower (UI de monitoramento do Celery):
pip install flower
celery -A config flower --port=5555
# Acesse: http://localhost:5555
```

---

## 📄 Licença

Este projeto é um software proprietário desenvolvido para a gestão de prestadores de serviços. Todos os direitos reservados.

Viewed base.py:120-160
Viewed .env:1-50

**Sim! A integração com o Supabase é 100% compatível e já está pronta no projeto.**

Como o **Supabase** é um banco de dados **PostgreSQL em nuvem completo**, o nosso sistema multi-tenant (`django-tenants`) consegue criar e isolar os schemas de cada empresa perfeitamente dentro do Supabase.

---

### 🚀 Como conectar o sistema ao Supabase:

No arquivo [`.env`](file:///c:/Users/ednar/OneDrive/Documentos/saas/.env), altere a seção de banco de dados comentando a opção local e ativando o Supabase:

#### 1. No arquivo [`.env`](file:///c:/Users/ednar/OneDrive/Documentos/saas/.env):
```env
# ─── Configuração do Supabase Cloud (Ativo) ───────────────────
DB_NAME=postgres
DB_USER=postgres.sua_id_do_projeto
DB_PASSWORD=sua_senha_do_supabase
DB_HOST=aws-0-sa-east-1.pooler.supabase.com # ou seu host do Supabase
DB_PORT=6543
DB_SSLMODE=require
```

---

### 📋 Passo a Passo para Inicializar no Supabase:

1. **Obter Credenciais no Supabase**:
   - Vá no painel do Supabase: `Project Settings` > `Database` > `Connection String` (Direct Connection ou Transaction Pooler).
   - Copie o **Host**, **User**, **Port** (geralmente `5432` ou `6543`) e **Password**.

2. **Aplicar Migrações e Schemas no Supabase**:
   No terminal do projeto (ou via Docker), rode o comando para migrar os schemas para a nuvem:
   ```bash
   python manage.py migrate_schemas
   ```

3. **Popular Dados Iniciais / Criar Admin**:
   ```bash
   # Popular tenants de demonstração:
   python manage.py runscript setup_tenants

   # Ou criar o Admin Global manualmente:
   python manage.py createsuperuser
   ```

---

### 💡 Vantagens de Conectar ao Supabase:
- ☁️ **Banco na Nuvem 24/7**: Não precisa manter o PostgreSQL rodando localmente.
- ⚡ **Desempenho**: Suporte nativo a Pooler de Conexões (PgBouncer).
- 🛡️ **Backups Automáticos**: O Supabase gerencia o backup de todas as empresas cadastradas.
- 📂 **Supabase Storage**: Pode ser integrado com `django-storages` para salvar as logomarcas das empresas na nuvem.