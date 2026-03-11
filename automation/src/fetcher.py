import logging
import feedparser
import httpx
import asyncio
from typing import List, Dict, Any
from datetime import datetime
from email.utils import parsedate_to_datetime
from models import TrendItem
from config import TARGET_COUNTRIES

logger = logging.getLogger(__name__)

# Base URL for Google Trends Daily RSS
GOOGLE_TRENDS_RSS_URL = "https://trends.google.com/trends/trendingsearches/daily/rss?geo={geo}"

async def _fetch_feed_content(client: httpx.AsyncClient, url: str) -> str:
    """Asynchronously fetches the raw XML content of an RSS feed."""
    try:
        response = await client.get(url, timeout=15.0)
        response.raise_for_status()
        return response.text
    except httpx.HTTPError as e:
        logger.error(f"HTTP error occurred while fetching {url}: {e}")
        raise

def _parse_trend_item(entry: Dict[Any, Any], country_code: str) -> TrendItem:
    """Parses a single feedparser entry into a strictly typed TrendItem model."""
    
    # Safely extract related news
    news_items = entry.get("ht_news_item", [])
    news_titles = []
    news_urls = []
    
    # feedparser might return a single dict if there's only one news item, or a list
    if isinstance(news_items, dict):
        news_items = [news_items]
        
    for news in news_items:
        title = news.get("ht_news_item_title", "")
        url = news.get("ht_news_item_url", "")
        if title and url:
            news_titles.append(title)
            news_urls.append(url)
            
    # Parse publish date
    pub_date_str = entry.get("published", "")
    try:
        # Google Trends RSS uses standard RFC 822 format
        pub_date = parsedate_to_datetime(pub_date_str)
    except Exception:
        pub_date = datetime.now()
        
    return TrendItem(
        title=entry.get("title", ""),
        approx_traffic=entry.get("ht_approx_traffic", "0+"),
        pub_date=pub_date,
        news_titles=news_titles,
        news_urls=news_urls,
        country_code=country_code
    )

async def fetch_trends_for_country(country_code: str, geo_code: str) -> List[TrendItem]:
    """
    Fetches Google Trends for a specific country using async HTTP requests and
    returns a list of validated TrendItem objects.
    """
    url = GOOGLE_TRENDS_RSS_URL.format(geo=geo_code)
    logger.info(f"Fetching trends for {country_code} ({geo_code})...")
    
    async with httpx.AsyncClient() as client:
        xml_content = await _fetch_feed_content(client, url)
        
    # Feedparser parses the string synchronously (CPU bound, but fast enough for RSS)
    feed = feedparser.parse(xml_content)
    
    trends: List[TrendItem] = []
    for entry in feed.entries:
        try:
            trend_item = _parse_trend_item(entry, country_code)
            trends.append(trend_item)
        except Exception as e:
            logger.warning(f"Failed to parse a trend entry for {country_code}: {e}")
            
    logger.info(f"Successfully fetched {len(trends)} trends for {country_code}.")
    return trends

async def fetch_all_trends() -> Dict[str, List[TrendItem]]:
    """
    Concurrently fetches trends for all configured target countries.
    """
    tasks = []
    country_codes = []
    
    for code, info in TARGET_COUNTRIES.items():
        geo = info["trend_geo"]
        if geo:
            tasks.append(fetch_trends_for_country(code, geo))
            country_codes.append(code)
            
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    all_trends: Dict[str, List[TrendItem]] = {}
    for code, result in zip(country_codes, results):
        if isinstance(result, Exception):
            logger.error(f"Failed to fetch trends for {code}: {result}")
            all_trends[code] = []
        else:
            all_trends[code] = result
            
    return all_trends

# Simple test block when running this file directly
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    
    async def run_test():
        trends_map = await fetch_all_trends()
        for country, trends in trends_map.items():
            print(f"--- {country} ---")
            for t in trends[:2]: # Show top 2 for brevity
                print(f"- {t.title} (Traffic: {t.approx_traffic}) -> News: {len(t.news_titles)}")
            print()

    asyncio.run(run_test())
