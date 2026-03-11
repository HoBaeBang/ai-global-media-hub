import logging
import random
from typing import List, Dict
from models import TrendItem
from rss_fetcher import fetch_rss_trends
from youtube_fetcher import fetch_youtube_trends

logger = logging.getLogger(__name__)

async def get_latest_trends(country_code: str) -> List[TrendItem]:
    """
    Orchestrates trend fetching by alternating between RSS (News) 
    and YouTube (Video) sources.
    """
    # 50/50 chance to pick either source
    source_choice = random.choice(["RSS", "YouTube"])
    
    logger.info(f"[{country_code}] Selected source for today: {source_choice}")
    
    trends: List[TrendItem] = []
    
    if source_choice == "RSS":
        trends = await fetch_rss_trends(country_code)
        # If RSS fails or empty, fallback to YouTube
        if not trends:
            logger.info(f"[{country_code}] RSS source empty, falling back to YouTube...")
            trends = await fetch_youtube_trends(country_code)
            
    else: # YouTube
        trends = await fetch_youtube_trends(country_code)
        # If YouTube fails or empty (e.g. no API key), fallback to RSS
        if not trends:
            logger.info(f"[{country_code}] YouTube source empty/unavailable, falling back to RSS...")
            trends = await fetch_rss_trends(country_code)

    # Limit to top 5 trends to avoid overwhelming the generator
    return trends[:5]

async def collect_all_trends() -> Dict[str, List[TrendItem]]:
    """
    Collects trends for all countries using the orchestrated logic.
    """
    import asyncio
    tasks = [get_latest_trends(code) for code in ["VN", "TW", "ID", "DE", "PL"]]
    results = await asyncio.gather(*tasks)
    
    return dict(zip(["VN", "TW", "ID", "DE", "PL"], results))

if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)
    
    async def test():
        trends = await collect_all_trends()
        for cc, items in trends.items():
            print(f"{cc}: Found {len(items)} items")

    asyncio.run(test())
