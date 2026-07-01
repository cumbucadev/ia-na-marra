import argparse
import sys
import logging
from config import DEFAULT_FEEDS, OPENAI_MODEL, OPENAI_API_BASE
from rss_parser import RSSCollector
from openai_client import OpenAIClient
from agent import NewsletterAgent
from newsletter import NewsletterGenerator

# Configura o logger para imprimir no terminal de forma legível e amigável
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("NewsletterOrchestrator")

def run_agent(model_name: str, host: str, output_file: str, limit: int = None):
    logger.info("=== INICIANDO AGENTE DA NEWSLETTER ===")
    logger.info(f"Modelo LLM configurado: '{model_name}'")
    logger.info(f"Endereço da API (OpenAI/KoboldCpp): '{host}'")

    # Passo 1: Coletar artigos das 3 fontes via RSS
    logger.info("\n--- PASSO 1: Coleta RSS ---")
    collector = RSSCollector(DEFAULT_FEEDS)
    raw_articles = collector.fetch_articles()
    
    if not raw_articles:
        logger.error("Nenhum artigo pôde ser coletado das fontes RSS configuradas. Saindo.")
        sys.exit(1)

    # Passo 2: Remover duplicadas
    logger.info("\n--- PASSO 2: Remoção de Duplicadas ---")
    unique_articles = collector.deduplicate(raw_articles)
    
    if not unique_articles:
        logger.error("Todos os artigos coletados foram filtrados como duplicados. Saindo.")
        sys.exit(1)

    if limit and limit > 0:
        logger.info(f"Limitando o processamento para as top {limit} notícias do total de {len(unique_articles)} únicas para economizar tempo.")
        unique_articles = unique_articles[:limit]

    # Passo 3: Inicializar Cliente OpenAI/KoboldCpp e Agente Editorial
    logger.info("\n--- PASSO 3: Inicializando IA local (OpenAI/KoboldCpp) ---")
    openai_client = OpenAIClient(model=model_name, api_base=host)
    agent = NewsletterAgent(openai_client)

    # Passo 4, 5 e 6: Classificar, Filtrar Notícias Relevantes e Selecionar as 5 Melhores
    logger.info("\n--- PASSO 4: Classificação, Filtragem e Ordenação pelo Agente Editorial IA ---")
    logger.info("Este processo pode levar alguns instantes enquanto consultamos a IA local...")
    top_articles = agent.process_and_filter_articles(unique_articles)

    if not top_articles:
        logger.warning("Nenhum artigo atingiu as condições ideais de relevância.")
        logger.info("Tentando forçar a escolha das 5 melhores histórias gerais do grupo de coletados...")
        # Como o processo já enriqueceu, vamos apenas selecionar as que têm scores maiores de forma robusta sem fazer deepcopy
        if hasattr(agent, 'processed_articles') and agent.processed_articles:
            sorted_all = sorted(agent.processed_articles, key=lambda x: x.get("score_relevancia", 0), reverse=True)
            top_articles = sorted_all[:5]
        else:
            # Se não houver nada analisado, usa as primeiras de unique_articles com valores padrão como fallback
            top_articles = []
            for art in unique_articles[:5]:
                top_articles.append({
                    **art,
                    "classificacao": "Outro",
                    "score_relevancia": 0,
                    "justificativa": "Análise não disponível (fallback)."
                })

    # Exibe no console o resultado da curadoria para visibilidade clara
    logger.info("\n=== DETALHES DOS 5 ARTIGOS SELECIONADOS PELO AGENTE ===")
    for i, art in enumerate(top_articles, 1):
        print(f"\n[{i}] {art['title']}")
        print(f"    Fonte: {art['source']} | Categoria: {art['classificacao']} | Relevância: {art['score_relevancia']}/10")
        print(f"    Link: {art['link']}")
        print(f"    Justificativa Editorial: {art['justificativa']}")
    print("\n" + "="*50)

    # Passo 7: Gerar a newsletter com os selecionados usando o modelo via KoboldCpp (OpenAI API)
    logger.info("\n--- PASSO 5: Redigindo Newsletter Final via IA ---")
    generator = NewsletterGenerator(openai_client)
    newsletter_md = generator.generate_content(top_articles)

    # Passo 8: Salvar no arquivo final
    logger.info(f"\n--- PASSO 6: Gravando Newsletter em Arquivo ---")
    generator.save_newsletter(newsletter_md, output_file)
    logger.info("=== AGENTE EXECUTADO COM SUCESSO! ===")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Orquestrador do Agente de Newsletter Técnico")
    parser.add_argument("--model", type=str, default=OPENAI_MODEL, help="Nome do modelo local configurado no KoboldCpp (OpenAI API)")
    parser.add_argument("--host", type=str, default=OPENAI_API_BASE, help="URL base da API OpenAI do KoboldCpp")
    parser.add_argument("--output", type=str, default="newsletter.md", help="Caminho do arquivo Markdown gerador")
    parser.add_argument("--limit", type=int, default=3, help="Limite de artigos únicos a processar (útil para testes rápidos)")
    
    args = parser.parse_args()
    run_agent(args.model, args.host, args.output, limit=args.limit)
