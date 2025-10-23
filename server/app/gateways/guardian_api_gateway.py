from newspaper import Article as NewsArticle
from typing import Optional


def scrape_full_content(url: str) -> Optional[str]:
    try:
        article = NewsArticle(url)
        article.download()
        article.parse()
        
        return article.text
        
    except Exception as e:
        print(f"Scraping error for {url}: {e}")
        return None


def enhance_article_with_scraping(article_data: dict) -> dict:

    if not article_data.get("url"):
        return article_data
    
    if article_data.get("content") and len(article_data["content"]) > 1000:
        return article_data
    
    print(f"🔍 Scraping full content from: {article_data['url']}")
    
    full_content = scrape_full_content(article_data["url"])
    
    if full_content and len(full_content) > 200:
        article_data["content"] = full_content
        print(f"   ✅ Got {len(full_content)} characters")
    else:
        print(f"   ⚠️  Failed to scrape")
    
    return article_data