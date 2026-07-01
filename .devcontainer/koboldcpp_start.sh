#!/bin/sh
MODEL_FILE="/models/Qwen3-8B.gguf"

echo "=== Iniciando serviço KoboldCpp ==="
if [ ! -f "$MODEL_FILE" ]; then
    echo "========================================================================="
    echo "AVISO: O arquivo de modelo '$MODEL_FILE' não foi encontrado!"
    echo "Por favor, baixe o seu modelo GGUF (Qwen3-8B) e coloque-o em:"
    echo "  ./models/Qwen3-8B.gguf"
    echo "========================================================================="
    echo "Aguardando o arquivo de modelo ser colocado... (verificando a cada 10s)"
    while [ ! -f "$MODEL_FILE" ]; do
        sleep 10
    done
    echo "Arquivo de modelo detectado! Prosseguindo com a inicialização..."
fi

echo "Iniciando o KoboldCpp com o modelo: $MODEL_FILE"
# Executa o koboldcpp substituindo o processo principal do container.
# Adiciona --port 5001 para expor a api, --host 0.0.0.0 para ser acessível na rede, e --nobrowser para devcontainers headless.
exec koboldcpp --model "$MODEL_FILE" --port 5001 --host 0.0.0.0
