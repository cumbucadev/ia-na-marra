import os

# Configurações do Agente de Newsletter (OpenAI / KoboldCpp)
# Dentro do ambiente do devcontainer com docker-compose, o host "koboldcpp" é usado
# para comunicação inter-container, e a porta padrão é a 5001.
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "http://koboldcpp:5001/v1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "any-string-for-kobold")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "Qwen3-8B")

# Fontes de RSS padrão
DEFAULT_FEEDS = [
    "https://news.ycombinator.com/rss",                         # Hacker News
    "https://dev.to/feed",                                      # Dev.to
    "https://techcrunch.com/category/developer/feed/"           # TechCrunch Developer
]

# Configurações gerais
NUM_ARTICLES_FINAL = 5  # Número de artigos final selecionado para a newsletter
CLASSIFICATIONS = ["Notícia", "Tutorial", "Promoção", "Outro"]
