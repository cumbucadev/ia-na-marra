import feedparser
import re
from typing import List, Dict, Any
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class RSSCollector:
    def __init__(self, feed_urls: List[str]):
        self.feed_urls = feed_urls

    def clean_text(self, text: str) -> str:
        """Limpa tags HTML de strings."""
        if not text:
            return ""
        # Remove tags HTML
        clean = re.compile('<.*?>')
        text = re.sub(clean, '', text)
        # Remove espaços em excesso
        text = " ".join(text.split())
        return text

    def fetch_articles(self) -> List[Dict[str, Any]]:
        """Busca artigos de todas as fontes RSS configuradas."""
        articles = []
        for url in self.feed_urls:
            logger.info(f"Coletando feed de: {url}")
            try:
                feed = feedparser.parse(url)
                source_name = feed.feed.get("title", url)
                
                for entry in feed.entries:
                    summary = entry.get("summary", entry.get("description", ""))
                    articles.append({
                        "title": entry.get("title", "").strip(),
                        "link": entry.get("link", "").strip(),
                        "summary": self.clean_text(summary).strip(),
                        "published": entry.get("published", entry.get("updated", "")),
                        "source": source_name
                    })
            except Exception as e:
                logger.error(f"Erro ao ler feed {url}: {e}")
                
        return articles

    def deduplicate(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicados com base no link ou título padronizado."""
        seen_links = set()
        seen_titles = set()
        unique_articles = []

        for article in articles:
            # Normalização de link (remover querystring e barras finais)
            link = article["link"].strip().lower()
            link = re.sub(r'\?.*$', '', link)  # remove query string
            link = link.rstrip('/')
            
            # Normalização de título (minúsculo e sem espaços extras)
            title_norm = article["title"].strip().lower()
            title_norm = re.sub(r'[^a-z0-9]', '', title_norm)  # mantém apenas alfanuméricos para comparação robusta
            
            if not title_norm:
                continue

            if link not in seen_links and title_norm not in seen_titles:
                seen_links.add(link)
                seen_titles.add(title_norm)
                unique_articles.append(article)
            else:
                logger.debug(f"Duplicado removido: {article['title']}")

        logger.info(f"Coleta finalizada: {len(articles)} coletados, {len(unique_articles)} únicos após deduplicação.")
        return unique_articles
