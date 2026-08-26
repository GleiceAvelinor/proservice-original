# 📖 Manual do Usuário — ProService SaaS

Bem-vindo ao **ProService SaaS**, a plataforma completa de gestão comercial, controle de estoque e emissão de propostas para prestadores de serviços.

Este manual orienta o passo a passo para cadastrar sua empresa, entender os 3 métodos de ativação do subdomínio pelo Administrador Master (WhatsApp, E-mail e Painel Admin), configurar sua identidade visual, gerenciar clientes, produtos e serviços, além de emitir e enviar propostas comerciais profissionais.

---

## 📌 Sumário
1. [Primeiros Passos, Cadastro e Ativação da Empresa](#1-primeiros-passos-cadastro-e-ativação-da-empresa)
   - [1.1 Formulário de Cadastro](#11-formulário-de-cadastro)
   - [1.2 Fluxo de Liberação e Os 3 Métodos de Envio pelo Admin Master](#12-fluxo-de-liberação-e-os-3-métodos-de-envio-pelo-admin-master)
   - [1.3 Desativação e Bloqueio de Acesso em Tempo Real](#13-desativação-e-bloqueio-de-acesso-em-tempo-real)
2. [Acesso ao Painel Exclusivo (Subdomínio) e Portal de Acesso](#2-acesso-ao-painel-exclusivo-subdomínio-e-portal-de-acesso)
3. [Configuração de Dados e Logomarca](#3-configuração-de-dados-e-logomarca)
4. [Gestão de Clientes](#4-gestão-de-clientes)
5. [Catálogo de Produtos e Serviços](#5-catálogo-de-produtos-e-serviços)
6. [Emissão, Envio e Gestão de Propostas Comerciais](#6-emissão-envio-e-gestão-de-propostas-comerciais)
7. [Aprovação Online pelo Cliente](#7-aprovação-online-pelo-cliente)
8. [Dashboard e Métricas Financeiras](#8-dashboard-e-métricas-financeiras)
9. [Painel do Administrador Master (Gestão de Tenants)](#9-painel-do-administrador-master-gestão-de-tenants)
10. [Perguntas Frequentes (FAQ)](#10-perguntas-frequentes-faq)

---

## 1. Primeiros Passos, Cadastro e Ativação da Empresa

### 1.1 Formulário de Cadastro
1. Na página inicial pública, clique no botão **"Cadastrar Empresa"** ou **"Bora Começar!"**.
2. Preencha os **Dados da Empresa**:
   - **Nome da Empresa**: Razão social ou nome fantasia da sua prestadora.
   - **Subdomínio Desejado**: Escolha um identificador único (ex: `jardinagem`, `piscinas`, `limpeza`).
   - **CNPJ**, **E-mail de Contato** e **Telefone/WhatsApp**.
3. Preencha os **Dados do Administrador**:
   - **Usuário**: Nome de usuário para login (ex: `admin`).
   - **E-mail**: E-mail pessoal ou corporativo do responsável.
   - **Senha**: Senha de acesso ao sistema.
4. Clique em **"Criar Ambiente da Empresa"**.

---

### 1.2 Fluxo de Liberação e Os 3 Métodos de Envio pelo Admin Master

Para garantir a segurança da plataforma contra cadastros indevidos, novas contas nascem desativadas (`is_active = False`) e aguardam autorização do **Administrador Master**.

O Administrador Master possui **3 formas práticas** para enviar o link de ativação ou aprovar o cadastro:

#### 🟢 Método 1: Envio Direto por WhatsApp em 1 Clique (Recomendado)
1. O Admin Master acessa o painel de administração: `http://localhost:8000/admin/tenants/client/`
2. Na tabela de empresas, na coluna **"WhatsApp Liberação"**, clica no botão verde **`[Enviar WhatsApp]`**.
3. O WhatsApp Web / App abre automaticamente com uma mensagem pré-formatada contendo o link oficial de ativação:
   > *"Olá! Suas credenciais da empresa 'Nome da Empresa' foram pré-cadastradas. Para liberar e ativar o seu acesso, clique no link oficial: http://localhost:8000/signup/ativar/<token>/"*
4. O Admin Master apenas clica em **Enviar** no WhatsApp!

#### ✉️ Método 2: Notificação Automática por E-mail
1. O sistema dispara um e-mail automático de notificação para o Admin Master no momento em que o cadastro é efetuado.
2. No corpo do e-mail consta o resumo da empresa e o link único de aprovação:
   `http://localhost:8000/signup/ativar/<token>/`
3. O Admin Master pode clicar no link para ativar ou encaminhar o e-mail diretamente para o responsável da empresa.

#### ⚡ Método 3: Ativação Direta no Painel Admin (Sem envio de mensagem)
1. No painel `http://localhost:8000/admin/tenants/client/`, na coluna **"Link Ativação"**, o Admin Master clica no botão azul **`[Ativar]`**.
2. Ou seleciona as empresas desejadas e aplica a ação em lote: *"🟢 Aprovar e Ativar Empresas Selecionadas"*.
3. O sistema ativa a conta instantaneamente e dispara um e-mail de boas-vindas para o e-mail da empresa com o link de login do subdomínio.

---

### 1.3 Desativação e Bloqueio de Acesso em Tempo Real
Caso uma empresa seja suspensa ou desativada no Painel Admin (`is_active = False`):
- O middleware de segurança (`TenantActiveMiddleware`) intercepta todas as tentativas de navegação e login no subdomínio daquela empresa.
- É exibida a tela de aviso **"Acesso Temporariamente Suspenso — Conta Desativada"**.
- A empresa é removida do Portal de Acesso público até que o Administrador Master reative o cadastro.

---

## 2. Acesso ao Painel Exclusivo (Subdomínio) e Portal de Acesso

Após a ativação pelo Administrador Master, sua empresa pode ser acessada de duas maneiras:

### Opção A: Acesso Direto pelo Subdomínio
Digite o endereço do seu subdomínio na barra do navegador:
```text
http://seu_subdominio.localhost:8000/accounts/login/
```

### Opção B: Portal de Acesso de Empresas
Acesse o **Portal de Acesso** (`/signup/acessar/`) para visualizar todas as empresas ativas cadastradas na plataforma. Utilize o campo de busca em tempo real para localizar sua empresa e clicar no botão **"Entrar no Painel"**.

---

## 3. Configuração de Dados e Logomarca

Ter a sua marca visível garante o profissionalismo das suas propostas comerciais.

### Como atualizar os dados e a logo da sua empresa:
1. No menu lateral ou no topo do painel, clique em **"Minha Empresa & Logo"** (ou acesse `Configurações da Empresa`).
2. Atualize o **Nome**, **CNPJ**, **Telefone**, **E-mail** e **Endereço Completo**.
3. No campo **Logo**, faça o upload do arquivo de imagem da sua marca (formatos aceitos: PNG, JPG ou WEBP).
4. Clique em **"Salvar Dados da Empresa"**.

> 🎨 **Onde a sua logo será exibida:**
> - No cabeçalho superior do painel (Navbar).
> - Na página de login da sua empresa.
> - Na visualização pública de propostas comerciais.
> - No arquivo **PDF impresso/anexado** de cada proposta.

---

## 4. Gestão de Clientes

Mantenha o cadastro atualizado de todos os seus clientes contratantes.

### Cadastrando um cliente:
1. No menu lateral, acesse **"Clientes"** e clique no botão **"Novo Cliente"**.
2. Preencha os campos:
   - **Nome / Razão Social** (obrigatório).
   - **CPF / CNPJ**, **E-mail**, **Telefone / WhatsApp**.
   - **Endereço Completo** (Rua, Número, Bairro, Cidade, Estado, CEP).
3. Clique em **"Salvar Cliente"**.

---

## 5. Catálogo de Produtos e Serviços

O catálogo centraliza tudo o que a sua empresa vende, facilitando a elaboração rápida de orçamentos.

### 5.1 Cadastrando Serviços
1. Acesse **"Serviços"** no menu e clique em **"Novo Serviço"**.
2. Informe o **Nome do Serviço** (ex: *Manutenção Mensal de Piscina*, *Poda de Árvores*).
3. Preencha a **Descrição detalhada** e o **Preço Padrão (R$)**.
4. Clique em **"Salvar Serviço"**.

### 5.2 Cadastrando Produtos e Insumos
1. Acesse **"Produtos"** no menu e clique em **"Novo Produto"**.
2. Preencha os dados:
   - **Nome do Produto** e **Código/SKU**.
   - **Unidade de Medida** (Unidade, Metro, Metro², Metro³, Litro, Quilograma, Caixa, Rolo, Saco).
   - **Estoque Atual** e **Estoque Mínimo** (para alertas automáticos).
   - **Preço de Custo (R$)** e **Preço de Venda (R$)**. O sistema calcula a **margem de lucro** automaticamente.
3. Clique em **"Salvar Produto"**.

> 🚨 **Alertas de Estoque Mínimo:** Quando o estoque atual de um produto atingir ou ficar abaixo do estoque mínimo cadastrado, o sistema emitirá um alerta no seu Dashboard principal.

---

## 6. Emissão, Envio e Gestão de Propostas Comerciais

As propostas comerciais são o coração da plataforma ProService.

### 6.1 Criando uma Nova Proposta
1. Clique em **"Nova Proposta"** no topo da tela ou no menu de propostas.
2. Selecione o **Cliente** na lista suspensa.
3. Defina a **Data de Validade** do orçamento e adicione **Observações / Condições Gerais**.
4. Adicione os itens (Produtos e/ou Serviços):
   - Escolha o item no catálogo.
   - Informe a quantidade e o preço unitário (o valor padrão do catálogo é carregado automaticamente, mas pode ser ajustado).
5. Clique em **"Salvar Proposta"**.

### 6.2 Status das Propostas
- 🟡 **Rascunho**: Proposta criada, em rascunho inicial.
- 🔵 **Pendente**: Proposta enviada ao cliente aguardando resposta.
- 🟢 **Aprovada**: Proposta aceita pelo cliente (soma no Faturamento Confirmado).
- 🔴 **Recusada**: Proposta declinada pelo cliente.
- ⚪ **Cancelada**: Proposta anulada.

---

## 7. Aprovação Online pelo Cliente

Após salvar a proposta comercial, você possui **4 formas de envio/compartilhamento**:

### 📄 1. Download do PDF Profissional
- Clique no botão **"Baixar PDF"** ou no ícone de PDF para gerar um arquivo formatado com cabeçalho, logomarca da empresa, tabela de itens, cálculo de totais e termos de execução.

### ✉️ 2. Envio por E-mail Automático
- Clique no botão **"Enviar por E-mail"**.
- O sistema dispara uma mensagem formatada em HTML para o e-mail do cliente com o **arquivo PDF anexado**.
- O status da proposta é atualizado automaticamente para **Pendente**.

### 💬 3. Envio por WhatsApp
- Clique no botão **"Enviar por WhatsApp"**.
- O sistema gera uma mensagem pronta formatada para o WhatsApp Web ou aplicativo com o link público da proposta.

### 🔗 4. Link Público de Aprovação Online
- Clique no botão **"Ver Link Público"**.
- Envie o link gerado para o seu cliente. Na página pública, o cliente pode visualizar todos os detalhes do orçamento e clicar diretamente nos botões:
  - 🟢 **"Aprovar Proposta"**
  - 🔴 **"Recusar Proposta"**
- A resposta do cliente atualiza o status no seu painel em tempo real!

---

## 8. Dashboard e Métricas Financeiras

O **Dashboard** é a sua central de controle executiva:

- **Faturamento Aprovado**: Soma total do valor de todas as propostas aprovadas no mês (clicável para filtrar).
- **Propostas Em Aberto**: Soma das propostas pendentes aguardando aprovação dos clientes (clicável para filtrar).
- **Clientes Ativos**: Total de clientes cadastrados no sistema (clicável).
- **Taxa de Conversão (%)**: Percentual de propostas aprovadas em relação ao total emitido.
- **Gráfico de Evolução do Faturamento**: Acompanhamento do histórico financeiro nos últimos 6 meses.
- **Alerta de Estoque Crítico**: Lista de produtos que precisam de reposição urgente.

---

## 9. Painel do Administrador Master (Gestão de Tenants)

Para o Administrador Global do SaaS (`/admin/` no schema público):

1. **Gestão de Empresas**: Acessar `Empresas (Tenants)` no Django Admin (`/admin/tenants/client/`).
2. **Envio de Link por WhatsApp**: Clicar no botão verde **`[Enviar WhatsApp]`** na tabela para abrir o aplicativo com a mensagem e o link de liberação.
3. **Ativação por E-mail**: Utilizar o link único gerado e notificado no e-mail master (`/signup/ativar/<token>/`).
4. **Ativação Direta**: Clicar no botão azul **`[Ativar]`** ou aplicar a ação em lote *"🟢 Aprovar e Ativar Empresas Selecionadas"*.
5. **Suspensão de Acesso**: Marcar `is_active = False` ou utilizar a ação em lote *"🔴 Suspender / Desativar Empresas Selecionadas"*.

---

## 10. Perguntas Frequentes (FAQ)

#### ❓ Como o Administrador Master envia o link de ativação para o cliente?
O Admin Master pode enviar clicando no botão **`[Enviar WhatsApp]`** no painel admin (que abre a mensagem pronta no WhatsApp com o link), encaminhando o e-mail de notificação recebido, ou ativando direto no botão **`[Ativar]`**.

#### ❓ Minha empresa se cadastrou. Por que ainda não consigo fazer login?
Por medida de segurança, novas contas entram em modo pendente até que o **Administrador Master** efetue a liberação via E-mail, WhatsApp ou Painel Admin.

#### ❓ Os meus clientes precisam criar login no sistema?
**Não.** Os seus clientes recebem o link público da proposta ou o arquivo PDF por e-mail/WhatsApp e conseguem visualizar e aprovar o orçamento sem necessidade de cadastro.

#### ❓ Posso alterar a logomarca da minha empresa a qualquer momento?
**Sim.** Basta ir em *Minha Empresa & Logo*, enviar a nova imagem e salvar. Todos os PDFs e visualizações públicas passarão a exibir a nova marca.

#### ❓ O que acontece quando o Administrador Master desativa uma empresa?
O acesso ao subdomínio da empresa é bloqueado imediatamente com a tela de aviso *"Acesso Temporariamente Suspenso"*, e a empresa é oculta do Portal de Acesso público até que seja reativada.

---

*ProService SaaS — Gestão Inteligente para Prestadores de Serviços.*
