import ollama
import json
import logging
from typing import Dict, Any, Optional
from config import OLLAMA_MODEL, OLLAMA_HOST

logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(self, model: str = OLLAMA_MODEL, host: str = OLLAMA_HOST):
        self.model = model
        # O SDK oficial do Ollama usa a variável de ambiente OLLAMA_HOST para definir o endereço do host do Ollama
        import os
        os.environ["OLLAMA_HOST"] = host
        logger.info(f"OllamaClient inicializado com modelo: {self.model} no host: {host}")

    def generate_json_response(self, prompt: str, system_prompt: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Gera uma resposta em formato JSON a partir do Ollama com tratamento de erros."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = ollama.chat(
                model=self.model,
                messages=messages,
                format="json",  # Força o Ollama a responder estritamente como JSON
                options={
                    "temperature": 0.2, # Baixa temperatura para tarefas de classificação e filtragem estruturadas
                }
            )
            content = response.message.content
            # Converte string JSON em objeto Python
            return json.loads(content)
        except json.JSONDecodeError as je:
            logger.error(f"Erro ao decodificar JSON gerado pelo Ollama: {je}")
            logger.error(f"Conteúdo retornado bruto: {content if 'content' in locals() else 'Nenhum'}")
            return None
        except Exception as e:
            logger.error(f"Erro na chamada do Ollama client: {e}")
            return None

    def query(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Gera uma resposta de texto normal do Ollama."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = ollama.chat(
                model=self.model,
                messages=messages,
                options={
                    "temperature": 0.7, # Temperatura um pouco mais alta para escrita de textos criativos (newsletter)
                }
            )
            return response.message.content
        except Exception as e:
            logger.error(f"Erro na chamada do Ollama (texto): {e}")
            return f"Erro ao gerar conteúdo: {e}"
