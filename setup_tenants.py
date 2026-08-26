"""
============================================================
SETUP & DEMO SEED SCRIPT
============================================================
Este script demonstra a criação programática de tenants,
domínios e dados iniciais (Ji Jardinagem e Levi Piscinas).

Execução:
    python setup_tenants.py
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from django.contrib.auth import get_user_model
from django_tenants.utils import schema_context
from apps.tenants.models import Client, Domain

User = get_user_model()


def main():
    print("=" * 60)
    print("🚀 INICIALIZANDO SCHEMA PÚBLICO E TENANTS DE DEMONSTRAÇÃO")
    print("=" * 60)

    # 1. Tenant Público
    public_tenant, created = Client.objects.get_or_create(
        schema_name="public",
        defaults={"name": "SaaS Platform Principal", "is_active": True},
    )
    if created:
        print("✅ Schema 'public' cadastrado na tabela de tenants.")
        Domain.objects.create(
            domain="localhost",
            tenant=public_tenant,
            is_primary=True,
        )
        print("  └─ Domínio 'localhost' vinculado ao schema public.")

    # 2. Tenant 1: Ji Jardinagem
    ji_tenant, created = Client.objects.get_or_create(
        schema_name="ji_jardinagem",
        defaults={
            "name": "Ji Jardinagem & Paisagismo",
            "cnpj": "12.345.678/0001-90",
            "phone": "(11) 98765-4321",
            "email": "contato@jijardinagem.com.br",
            "address": "Av. das Flores, 500 - São Paulo/SP",
            "is_active": True,
        },
    )
    if created:
        print("\n✅ Schema 'ji_jardinagem' criado com sucesso no PostgreSQL.")
        Domain.objects.create(
            domain="ji.localhost",
            tenant=ji_tenant,
            is_primary=True,
        )
        print("  └─ Subdomínio 'ji.localhost' vinculado à Ji Jardinagem.")

        # Popula dados dentro do schema 'ji_jardinagem'
        with schema_context("ji_jardinagem"):
            # Criar Admin do Tenant
            if not User.objects.filter(username="admin").exists():
                User.objects.create_superuser("admin", "admin@jijardinagem.com", "admin123")
                print("  └─ Usuário admin (senha: admin123) criado em ji_jardinagem.")

            # Popula Clientes e Catálogo
            from apps.clientes.models import Cliente
            from apps.catalogo.models import Produto, Servico, UnidadeMedida
            from apps.propostas.models import Proposta, ItemProposta, StatusProposta, TipoItem

            c1 = Cliente.objects.create(
                nome="Condomínio Vila Verde",
                cpf_cnpj="98.765.432/0001-10",
                tipo="PJ",
                email="sindico@vilaverde.com.br",
                telefone="(11) 91111-2222",
                logradouro="Rua das Palmeiras",
                numero="100",
                cidade="São Paulo",
                estado="SP",
            )

            p1 = Produto.objects.create(
                nome="Grama Esmeralda (m²)",
                codigo="GRA-001",
                unidade=UnidadeMedida.METRO_QUADRADO,
                preco_custo=8.50,
                preco_venda=15.00,
                estoque_atual=500.00,
                estoque_minimo=50.00,
            )

            s1 = Servico.objects.create(
                nome="Poda de Árvores de Grande Porte",
                descricao="Corte e poda preventiva com equipamento de segurança.",
                preco_padrao=450.00,
            )

            prop = Proposta.objects.create(
                cliente=c1,
                titulo="Manutenção Geral e Paisagismo - Primavera",
                status=StatusProposta.PENDENTE,
                condicao_pagamento="50% na aprovação e 50% na entrega",
                observacoes="Validade da proposta de 15 dias.",
            )

            ItemProposta.objects.create(
                proposta=prop,
                tipo=TipoItem.SERVICO,
                servico=s1,
                descricao=s1.nome,
                quantidade=2,
                preco_unitario=450.00,
                ordem=1,
            )
            ItemProposta.objects.create(
                proposta=prop,
                tipo=TipoItem.PRODUTO,
                produto=p1,
                descricao="Fornecimento de Grama Esmeralda",
                quantidade=100,
                preco_unitario=15.00,
                ordem=2,
            )
            print("  └─ Cliente, produtos, serviços e proposta inicial populados.")

    # 3. Tenant 2: Levi Piscinas
    levi_tenant, created = Client.objects.get_or_create(
        schema_name="levi_piscinas",
        defaults={
            "name": "Levi Piscinas & Manutenção",
            "cnpj": "23.456.789/0001-11",
            "phone": "(11) 97777-8888",
            "email": "contato@levipiscinas.com.br",
            "address": "Rua do Sol, 250 - Campinas/SP",
            "is_active": True,
        },
    )
    if created:
        print("\n✅ Schema 'levi_piscinas' criado com sucesso no PostgreSQL.")
        Domain.objects.create(
            domain="levi.localhost",
            tenant=levi_tenant,
            is_primary=True,
        )
        print("  └─ Subdomínio 'levi.localhost' vinculado à Levi Piscinas.")

        with schema_context("levi_piscinas"):
            if not User.objects.filter(username="admin").exists():
                User.objects.create_superuser("admin", "admin@levipiscinas.com", "admin123")
                print("  └─ Usuário admin (senha: admin123) criado em levi_piscinas.")

            from apps.clientes.models import Cliente
            from apps.catalogo.models import Produto, Servico, UnidadeMedida

            Cliente.objects.create(
                nome="Clube Esportivo Campineiro",
                cpf_cnpj="45.678.901/0001-33",
                tipo="PJ",
                email="diretoria@clube.com.br",
                telefone="(19) 3232-4040",
            )

            Produto.objects.create(
                nome="Cloro Granulado 10kg",
                codigo="CLO-010",
                unidade=UnidadeMedida.CAIXA,
                preco_custo=120.00,
                preco_venda=190.00,
                estoque_atual=12.00,
                estoque_minimo=3.00,
            )

            Servico.objects.create(
                nome="Tratamento Químico e Aspiração de Piscina",
                descricao="Limpeza completa da água, correção de pH e cloração.",
                preco_padrao=280.00,
            )
            print("  └─ Cliente, produtos e serviços iniciais populados em levi_piscinas.")

    print("\n" + "=" * 60)
    print("✨ SETUP CONCLUÍDO COM SUCESSO!")
    print("=" * 60)
    print("Para testar o acesso multi-tenant em desenvolvimento:")
    print("1. Adicione ao seu arquivo /etc/hosts ou C:\\Windows\\System32\\drivers\\etc\\hosts:")
    print("   127.0.0.1  localhost")
    print("   127.0.0.1  ji.localhost")
    print("   127.0.0.1  levi.localhost")
    print("\n2. Acesse no navegador:")
    print("   • http://ji.localhost:8000/    (Empresa: Ji Jardinagem | User: admin / Senha: admin123)")
    print("   • http://levi.localhost:8000/  (Empresa: Levi Piscinas  | User: admin / Senha: admin123)")
    print("=" * 60)


if __name__ == "__main__":
    main()
