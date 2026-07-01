import os

# Configurações do Agente de Newsletter
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# Fontes de RSS padrão
DEFAULT_FEEDS = [
    "https://news.ycombinator.com/rss",                         # Hacker News
    "https://dev.to/feed",                                      # Dev.to
    "https://techcrunch.com/category/developer/feed/"           # TechCrunch Developer
]

# Configurações gerais
NUM_ARTICLES_FINAL = 5  # Número de artigos final selecionado para a newsletter
CLASSIFICATIONS = ["Notícia", "Tutorial", "Promoção", "Outro"]
