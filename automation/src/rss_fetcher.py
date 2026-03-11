import logging
import feedparser
import httpx
import asyncio
from typing import List, Dict, Optional
from datetime import datetime
from email.utils import parsedate_to_datetime
from models import TrendItem
from config import TARGET_COUNTRIES

logger = logging.getLogger(__name__)

async def fetch_rss_trends(country_code: str) -> List[TrendItem]:
    """
    Fetches the latest news from a country's primary RSS feed.
    """
    country_info = TARGET_COUNTRIES.get(country_code)
    if not country_info or "rss_url" not in country_info:
        logger.error(f"No RSS URL configured for {country_code}")
        return []

    url = country_info["rss_url"]
    logger.info(f"[{country_code}] Fetching RSS trends from {url}...")

    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            # Use a browser-like User-Agent to avoid simple blocks
            headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
            response = await client.get(url, headers=headers, timeout=20.0)
            response.raise_for_status()
            xml_content = response.text
    except Exception as e:
        logger.error(f"[{country_code}] Failed to fetch RSS content: {e}")
        return []

    # feedparser is sync, but fast.
    feed = feedparser.parse(xml_content)
    
    trends: List[TrendItem] = []
    for entry in feed.entries:
        try:
            # RSS models title and link. We use the title as the trend.
            title = entry.get("title", "").strip()
            if not title:
                continue
                
            # Parse date
            pub_date_str = entry.get("published", entry.get("updated", ""))
            try:
                pub_date = parsedate_to_datetime(pub_date_str)
            except:
                pub_date = datetime.now()

            # For RSS, we treat the entry itself as a 'news article'
            news_url = entry.get("link", "")
            
            trends.append(TrendItem(
                title=title,
                approx_traffic="News RSS", # Not specifically search traffic, but a trending news
                pub_date=pub_date,
                news_titles=[title],
                news_urls=[news_url],
                country_code=country_code
            ))
        except Exception as e:
            logger.warning(f"[{country_code}] Error parsing RSS entry: {e}")

    logger.info(f"[{country_code}] Successfully fetched {len(trends)} RSS trends.")
    return trends

async def fetch_all_rss_trends() -> Dict[str, List[TrendItem]]:
    """
    Concurrently fetches RSS trends for all countries.
    """
    tasks = [fetch_rss_trends(code) for code in TARGET_COUNTRIES.keys()]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    all_rss_trends = {}
    for code, result in zip(TARGET_COUNTRIES.keys(), results):
        if isinstance(result, Exception):
            logger.error(f"Unhandled exception fetching {code}: {result}")
            all_rss_trends[code] = []
        else:
            all_rss_trends[code] = result
            
    return all_rss_trends

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    
    async def test():
        results = await fetch_all_rss_trends()
        for cc, trends in results.items():
            print(f"--- {cc} ({len(trends)}) ---")
            for t in trends[:3]:
                print(f" - {t.title[:50]}...")
                
    asyncio.run(test())
