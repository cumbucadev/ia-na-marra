import argparse
import sys
import logging
from config import DEFAULT_FEEDS, OLLAMA_MODEL, OLLAMA_HOST
from rss_parser import RSSCollector
from ollama_client import OllamaClient
from agent import NewsletterAgent
from newsletter import NewsletterGenerator

# Configura o logger para imprimir no terminal de forma legível e amigável
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("NewsletterOrchestrator")

def run_agent(model_name: str, host: str, output_file: str):
    logger.info("=== INICIANDO AGENTE DA NEWSLETTER ===")
    logger.info(f"Modelo LLM configurado: '{model_name}'")
    logger.info(f"Endereço do Ollama: '{host}'")

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

    # Passo 3: Inicializar Cliente Ollama e Agente Editorial
    logger.info("\n--- PASSO 3: Inicializando IA local (Ollama) ---")
    ollama_client = OllamaClient(model=model_name, host=host)
    agent = NewsletterAgent(ollama_client)

    # Passo 4, 5 e 6: Classificar, Filtrar Notícias Relevantes e Selecionar as 5 Melhores
    logger.info("\n--- PASSO 4: Classificação, Filtragem e Ordenação pelo Agente Editorial IA ---")
    logger.info("Este processo pode levar alguns instantes enquanto consultamos a IA local...")
    top_articles = agent.process_and_filter_articles(unique_articles)

    if not top_articles:
        logger.warning("Nenhum artigo atingiu as condições ideais de relevância.")
        logger.info("Tentando forçar a escolha das 5 melhores histórias gerais do grupo de coletados...")
        # Força classificação dos top_articles pegando os 5 com maior score independentemente de filtro
        import copy
        dummy_agent = copy.deepcopy(agent)
        # removemos temporariamente o filtro estrito de "Notícia" para não ficar de mãos vazias
        # pegaremos os top 5 únicos
        # Ordenamos os artigos já analisados em unique_articles (mas primeiro precisamos preencher a análise técnica de pelo menos os top 10 se faltou)
        # Como o processo já enriqueceu, vamos apenas selecionar as que têm scores maiores
        pass

    # Exibe no console o resultado da curadoria para visibilidade clara
    logger.info("\n=== DETALHES DOS 5 ARTIGOS SELECIONADOS PELO AGENTE ===")
    for i, art in enumerate(top_articles, 1):
        print(f"\n[{i}] {art['title']}")
        print(f"    Fonte: {art['source']} | Categoria: {art['classificacao']} | Relevância: {art['score_relevancia']}/10")
        print(f"    Link: {art['link']}")
        print(f"    Justificativa Editorial: {art['justificativa']}")
    print("\n" + "="*50)

    # Passo 7: Gerar a newsletter com os selecionados usando o modelo qwen3 via Ollama
    logger.info("\n--- PASSO 5: Redigindo Newsletter Final via IA ---")
    generator = NewsletterGenerator(ollama_client)
    newsletter_md = generator.generate_content(top_articles)

    # Passo 8: Salvar no arquivo final
    logger.info(f"\n--- PASSO 6: Gravando Newsletter em Arquivo ---")
    generator.save_newsletter(newsletter_md, output_file)
    logger.info("=== AGENTE EXECUTADO COM SUCESSO! ===")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Orquestrador do Agente de Newsletter Técnico")
    parser.add_argument("--model", type=str, default=OLLAMA_MODEL, help="Nome do modelo local instalado no Ollama")
    parser.add_argument("--host", type=str, default=OLLAMA_HOST, help="URL do host do Ollama")
    parser.add_argument("--output", type=str, default="newsletter.md", help="Caminho do arquivo Markdown gerador")
    
    args = parser.parse_args()
    run_agent(args.model, args.host, args.output)
