import logging
from typing import List, Dict, Any
from openai_client import OpenAIClient
from config import CLASSIFICATIONS

logger = logging.getLogger(__name__)

class NewsletterAgent:
    def __init__(self, openai_client: OpenAIClient):
        self.ai = openai_client

    def self_analyze_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Usa o Ollama para classificar e pontuar a relevância de um artigo individual."""
        prompt = f"""
Você é o Agente Editorial de uma newsletter altamente técnica para programadores e desenvolvedores de software.
Sua missão é ler o título e resumo deste artigo e tomar decisões editoriais precisas.

DADOS DO ARTIGO:
Título: {article['title']}
Fonte: {article['source']}
Resumo: {article['summary']}

INSTRUÇÕES:
1. Classifique o tipo do artigo estritamente em um de: {", ".join(CLASSIFICATIONS)}.
2. Atribua um score de relevância de 1 a 10 para desenvolvedores de software.
   - 10: Mudanças profundas em linguagens populares, frameworks líderes ou ferramentas essenciais do dia a dia (ex: novos recursos do Python, Rust, React vNext, Docker).
   - 7-9: Notícias tecnológicas importantes, novos lançamentos de ferramentas relevantes, conceitos de arquitetura de alta utilidade.
   - 4-6: Tutoriais e tópicos gerais que são úteis, mas não mudam o rumo do mercado.
   - 1-3: Notícias de negócios em geral, fofocas corporativas, promoções de cursos, marketing ou irrelevantes.
3. Forneça uma justificativa curta (1-2 frases) na perspectiva de um desenvolvedor.

ATENÇÃO: Você deve retornar APENAS o JSON que obedeça à estrutura abaixo. Não inclua Markdown envolto no JSON, apenas o próprio conteúdo do dicionário JSON bruto.

ESTRUTURA DE RETORNO (JSON):
{{
  "classificacao": "Uma das 4 categorias especificadas",
  "score_relevancia": 1,
  "justificativa": "Sua justificativa técnica e curta"
}}
"""
        system_prompt = "Você é um agente editorial de newsletter para desenvolvedores, focado em precisão técnica e brevidade."
        
        logger.info(f"Analisando artigo: '{article['title']}' via {self.ai.model}")
        result = self.ai.generate_json_response(prompt, system_prompt=system_prompt)
        
        # Se vier como uma lista, desembrulha o primeiro elemento
        if isinstance(result, list) and len(result) > 0:
            result = result[0]
        
        # Fallback caso dê erro de parsing ou timeout
        if not result or not isinstance(result, dict):
            logger.warning(f"Falha de resposta para o artigo '{article['title']}'. Utilizando classificação padrão (Outro/0).")
            return {
                "classificacao": "Outro",
                "score_relevancia": 0,
                "justificativa": "Não foi possível analisar este artigo detalhadamente."
            }

        # Sanitiza e valida valores retornados pelo LLM
        classificacao = result.get("classificacao", "Outro")
        if classificacao not in CLASSIFICATIONS:
            # Tenta encontrar a classificação correta por aproximação ou usa "Outro"
            classificacao = next((c for c in CLASSIFICATIONS if c.lower() in classificacao.lower()), "Outro")

        try:
            score = int(result.get("score_relevancia", 0))
        except (ValueError, TypeError):
            score = 0
            
        return {
            "classificacao": classificacao,
            "score_relevancia": max(0, min(10, score)), # Mantém entre 0 e 10
            "justificativa": result.get("justificativa", "Análise concluída com sucesso.").strip()
        }

    def process_and_filter_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Processa todos os artigos, classifica, filtra e ordena."""
        processed_articles = []

        total = len(articles)
        for idx, article in enumerate(articles, 1):
            logger.info(f"Processando artigo {idx}/{total}")
            analysis = self.self_analyze_article(article)
            
            # Mescla as informações
            enriched_article = {**article, **analysis}
            processed_articles.append(enriched_article)

        self.processed_articles = processed_articles

        # Filtragem: apenas notícias relevantes
        # Requisito: "Filtrar apenas notícias relevantes para desenvolvedores"
        # Mantém apenas os artigos classificados como "Notícia" e que tenham relevância técnica razoável (score >= 5, por exemplo)
        filtered_articles = [
            art for art in processed_articles
            if art["classificacao"] == "Notícia" and art["score_relevancia"] >= 5
        ]
        
        logger.info(f"Filtragem completa: {len(processed_articles)} analisados -> {len(filtered_articles)} classificados como notícias relevantes.")
        
        # Ordenação por relevância (score_relevancia decrescente)
        # Requisito: "Ordenar por relevância e impacto"
        sorted_articles = sorted(filtered_articles, key=lambda x: x["score_relevancia"], reverse=True)
        
        # Seleciona as 5 melhores
        # Requisito: "Selecionar as 5 melhores"
        top_articles = sorted_articles[:5]
        
        # Fallback de sobrevivência: se não encontrar notícias de alta relevância suficientes, avise ou pegue as melhores gerais
        if len(top_articles) < 3:
            logger.warning("Poucas notícias altamente relevantes encontradas! Incluindo os melhores tutoriais como fallback de relevância...")
            # Pega as melhores opções restantes que não sejam Notícias, mas de alto score
            other_good_articles = [
                art for art in processed_articles
                if art not in top_articles and art["classificacao"] in ["Notícia", "Tutorial"] and art["score_relevancia"] >= 4
            ]
            sorted_others = sorted(other_good_articles, key=lambda x: x["score_relevancia"], reverse=True)
            top_articles.extend(sorted_others[:(5 - len(top_articles))])
            
        logger.info(f"Seleção final pronta com {len(top_articles)} artigos selecionados.")
        return top_articles
