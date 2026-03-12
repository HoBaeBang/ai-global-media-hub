import logging
import os
from typing import List, Dict
from datetime import datetime
from googleapiclient.discovery import build
from tenacity import retry, stop_after_attempt, wait_exponential
from models import TrendItem
from config import TARGET_COUNTRIES, YOUTUBE_API_KEY

logger = logging.getLogger(__name__)

async def fetch_youtube_trends(country_code: str) -> List[TrendItem]:
    """
    Fetches trending videos for a specific region using the YouTube Data API v3.
    """
    if not YOUTUBE_API_KEY:
        logger.warning(f"[{country_code}] YOUTUBE_API_KEY is missing. Skipping YouTube trends.")
        return []

    country_info = TARGET_COUNTRIES.get(country_code)
    geo_code = country_info.get("trend_geo", country_code)
    
    logger.info(f"[{country_code}] Fetching YouTube Trending videos for {geo_code}...")

    try:
        # Note: google-api-python-client is technically synchronous, 
        # but we run it in a thread pool to avoid blocking the event loop.
        import asyncio
        loop = asyncio.get_event_loop()
        
        @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
        def _get_trends():
            youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
            request = youtube.videos().list(
                part="snippet,statistics",
                chart="mostPopular",
                regionCode=geo_code,
                maxResults=10
            )
            return request.execute()

        response = await loop.run_in_executor(None, _get_trends)
        
        trends: List[TrendItem] = []
        for item in response.get("items", []):
            snippet = item.get("snippet", {})
            title = snippet.get("title", "")
            video_id = item.get("id", "")
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            publish_time_str = snippet.get("publishedAt", "")
            
            try:
                # YouTube uses ISO 8601
                pub_date = datetime.fromisoformat(publish_time_str.replace("Z", "+00:00"))
            except:
                pub_date = datetime.now()

            trends.append(TrendItem(
                title=title,
                approx_traffic="YouTube Trending",
                pub_date=pub_date,
                news_titles=[f"Video: {title}"],
                news_urls=[video_url],
                country_code=country_code
            ))
            
        logger.info(f"[{country_code}] Successfully fetched {len(trends)} YouTube trends.")
        return trends

    except Exception as e:
        logger.error(f"[{country_code}] Failed to fetch YouTube trends: {e}")
        return []

async def fetch_all_youtube_trends() -> Dict[str, List[TrendItem]]:
    """
    Concurrently fetches YouTube trends for all targeted countries.
    """
    import asyncio
    tasks = [fetch_youtube_trends(code) for code in TARGET_COUNTRIES.keys()]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    all_yt_trends = {}
    for code, result in zip(TARGET_COUNTRIES.keys(), results):
        if isinstance(result, Exception):
            logger.error(f"Error in youtube fetch task for {code}: {result}")
            all_yt_trends[code] = []
        else:
            all_yt_trends[code] = result
            
    return all_yt_trends

if __name__ == "__main__":
    # For local Testing
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    from dotenv import load_dotenv
    load_dotenv()
    
    async def test():
        global YOUTUBE_API_KEY
        YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
        if not YOUTUBE_API_KEY:
            print("Please set YOUTUBE_API_KEY in .env to test this module.")
            return
            
        results = await fetch_all_youtube_trends()
        for cc, trends in results.items():
            print(f"--- {cc} ({len(trends)}) ---")
            for t in trends[:3]:
                print(f" - {t.title}")
                
    import asyncio
    asyncio.run(test())
