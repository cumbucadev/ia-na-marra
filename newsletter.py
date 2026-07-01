import logging
from typing import List, Dict, Any
from datetime import datetime
from openai_client import OpenAIClient

logger = logging.getLogger(__name__)

class NewsletterGenerator:
    def __init__(self, openai_client: OpenAIClient):
        self.ai = openai_client

    def generate_content(self, articles: List[Dict[str, Any]]) -> str:
        """Instrui o Ollama a redigir o corpo e editorial da newsletter com base nos artigos selecionados."""
        if not articles:
            return "# Sem notícias relevantes hoje.\nInfelizmente, nenhum artigo atendeu aos critérios de relevância técnica hoje."

        # Monta a estrutura dos artigos para alimentar o prompt de escrita
        articles_context = ""
        for idx, art in enumerate(articles, 1):
            articles_context += f"""
---
[Artigo #{idx}]
Título Original: {art['title']}
Fonte Original: {art['source']}
URL: {art['link']}
Justificativa Técnica Editorial: {art['justificativa']}
Resumo Fonte: {art['summary']}
"""

        prompt = f"""
Você é o Editor-Chefe da "DevPulse HQ", uma newsletter técnica lida por milhares de engenheiros de software seniores, tech leads e CTOs exigentes que valorizam seu tempo.

Sua missão é escrever a edição de hoje da newsletter em PORTUGUÊS (PT-BR).
Você tem em mãos os {len(articles)} melhores artigos selecionados de forma algorítmica pelo nosso agente de recomendação.

Aqui está o conteúdo dos artigos selecionados com o contexto:
{articles_context}

INSTRUÇÕES DE ESCRITA:
1. Comece com um título chamativo, profissional e focado em desenvolvedores (ex: "DevPulse HQ: [Assunto do Artigo Principal] + [Outro Tema]").
2. Escreva uma breve introdução editorial cativante (2-3 parágrafos) sobre o panorama de tecnologia atual, novidades empolgantes ou dores de programadores no dia-a-dia de hoje.
3. Para CADA um dos artigos listados acima, crie uma seção contendo:
   - Um título traduzido ou otimizado que desperte interesse técnico (em Markdown `###`).
   - Um texto curto e dinâmico explicando do que se trata a novidade, por que ela é de altíssima relevância técnica e como ela afeta quem codifica. Mescle a justificativa editorial e o resumo com seu conhecimento de engenharia.
   - Um link bem formatado para leitura completa sob o texto: `[Leia o artigo completo]({{Link do Artigo}})` (use o link original fornecido).
4. Termine com uma conclusão inteligente e um encerramento animador (ex: "Bons códigos, e até a próxima edição!").
5. Escreva com tom técnico, polido, mas que não seja sem graça (pode ter toques leves de humor sutil sobre a vida de Dev).
6. Use formatação Markdown limpa e impecável. Não use placeholders como '[Insira data aqui]', use a data de hoje: {datetime.now().strftime('%d/%m/%Y')}.

Escreva toda a edição no formato Markdown final:
"""
        
        system_prompt = "Você é o redator sênior de uma newsletter técnica que valoriza tempo e densidade de informação."
        logger.info("Gerando texto da newsletter...");
        newsletter_markdown = self.ai.query(prompt, system_prompt=system_prompt)
        return newsletter_markdown

    def save_newsletter(self, content: str, filepath: str = "newsletter.md") -> None:
        """Salva a newsletter gerada em um arquivo local."""
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"Newsletter salva com sucesso em '{filepath}'!")
        except Exception as e:
            logger.error(f"Erro ao salvar arquivo de newsletter: {e}")
