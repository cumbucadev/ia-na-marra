from openai import OpenAI
import json
import logging
import re
from typing import Dict, Any, Optional
from config import OPENAI_MODEL, OPENAI_API_BASE, OPENAI_API_KEY

logger = logging.getLogger(__name__)

class OpenAIClient:
    def __init__(self, model: str = OPENAI_MODEL, api_base: str = OPENAI_API_BASE, api_key: str = OPENAI_API_KEY):
        self.model = model
        self.client = OpenAI(
            base_url=api_base,
            api_key=api_key
        )
        logger.info(f"OpenAIClient inicializado com modelo: {self.model} na base: {api_base}")

    def generate_json_response(self, prompt: str, system_prompt: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Gera uma resposta em formato JSON a partir do KoboldCpp (OpenAI API) com tratamento de erros."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={"type": "json_object"},  # Força resposta em JSON se o backend/modelo suportar
                temperature=0.2, # Baixa temperatura para tarefas estruturadas
            )
            content = response.choices[0].message.content
            logger.info(f"Resposta bruta recebida do LLM: {content}")
            
            # Limpa possíveis delimitadores markdown que alguns modelos insistem em retornar
            cleaned_content = content.strip()
            if cleaned_content.startswith("```json"):
                cleaned_content = cleaned_content[7:]
            elif cleaned_content.startswith("```"):
                cleaned_content = cleaned_content[3:]
            
            if cleaned_content.endswith("```"):
                cleaned_content = cleaned_content[:-3]
            
            cleaned_content = cleaned_content.strip()

            # Converte string JSON em objeto Python
            return json.loads(cleaned_content)
        except json.JSONDecodeError as je:
            logger.error(f"Erro ao decodificar JSON gerado pelo LLM: {je}")
            # Tenta extrair qualquer coisa entre chaves como último recurso de fallback
            try:
                match = re.search(r"(\{.*\})", content, re.DOTALL)
                if match:
                    return json.loads(match.group(1))
            except Exception as re_err:
                logger.error(f"Falha na extração de fallback via expressões regulares: {re_err}")
            return None
        except Exception as e:
            logger.error(f"Erro na chamada do OpenAI client: {e}")
            return None

    def query(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Gera uma resposta de texto normal do KoboldCpp (OpenAI API)."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7, # Maior criatividade na newsletter
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Erro na chamada do OpenAI (texto): {e}")
            return f"Erro ao gerar conteúdo: {e}"
