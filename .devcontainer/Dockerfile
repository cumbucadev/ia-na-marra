# Usar uma imagem oficial do Python como base
FROM mcr.microsoft.com/devcontainers/python:1-3.11-bullseye

# Instalar dependências adicionais do sistema se necessário
RUN rm -f /etc/apt/sources.list.d/yarn.list \
    && apt update && export DEBIAN_FRONTEND=noninteractive \
    && apt -y install --no-install-recommends git curl zstd \
    && curl -fsSL https://ollama.com/install.sh | sh \
    && apt clean && rm -rf /var/lib/apt/lists/*

# Definir o diretório de trabalho no container
WORKDIR /workspace

# Opcional: Instalar dependências prévias diretamente na montagem da imagem
COPY requirements.txt /tmp/pip-tmp/
RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \
   && rm -rf /tmp/pip-tmp
