#!/bin/sh
set -e

echo "============================================================"
echo "🚀 INICIANDO CONTAINER SAAS MULTI-TENANT DJANGO"
echo "============================================================"

# Aguarda o banco de dados estar pronto
echo "⏳ Aguardando banco de dados PostgreSQL ($DB_HOST:$DB_PORT)..."
python << END
import sys, time, socket
host = "$DB_HOST"
port = int("$DB_PORT" or 5432)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
while True:
    try:
        s.connect((host, port))
        s.close()
        print("✅ Banco de dados PostgreSQL online!")
        break
    except socket.error:
        time.sleep(1)
END

# 1. Executa as migrações do schema público (Shared Apps)
echo "📦 Aplicando migrações do schema público..."
python manage.py migrate_schemas --shared --noinput

# 2. Executa o script de inicialização dos tenants de demonstração
echo "🌱 Inicializando/Verificando tenants de demonstração..."
python setup_tenants.py || true

# Executa o comando passado no CMD do Dockerfile ou docker-compose
echo "✨ Executando o servidor Django..."
exec "$@"
