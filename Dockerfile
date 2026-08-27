FROM python:3.11-slim

# Evita que o Python gere arquivos .pyc e faça buffer de logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instala dependências do sistema necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    curl \
    gettext \
    python3-dev \
    python3-pip \
    python3-cffi \
    python3-brotli \
    libpango-1.0-0 \
    pango1.0-tools \
    libharfbuzz0b \
    libpangoft2-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala as dependências do Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# (Mantenha todo o seu bloco anterior de FROM, ENV, WORKDIR, apt-get e pip install)

COPY . /app/

# Porta padrão que o Render substitui via variável de ambiente do sistema
ENV PORT=10000
EXPOSE 10000

# Comando para iniciar a aplicação via Gunicorn usando a porta dinâmica do Render
CMD ["sh", "-c", "gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 3"]