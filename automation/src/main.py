import asyncio
import logging
from fetchers_manager import collect_all_trends
from db_client import db
from generator import generator
from publisher import publisher
from config import TARGET_COUNTRIES

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("main_pipeline")

async def process_country_trends(country_code: str, trends):
    """
    Processes trends for a single country: Duplicate check -> Generate -> Publish.
    """
    if not trends:
        logger.info(f"[{country_code}] No trends found to process.")
        return

    # We only process the top 1 trend per execution to avoid API limits 
    # and keep the blog from being spammy.
    trend = trends[0]
    title = trend.title
    
    logger.info(f"[{country_code}] Processing top trend: {title}")

    # 1. Duplicate Check
    if db.is_already_processed(title, country_code):
        logger.info(f"[{country_code}] Trend '{title}' already processed. Skipping.")
        return

    # 2. Content Generation
    logger.info(f"[{country_code}] Generating AI content...")
    html_content = await generator.generate_post(title, country_code)
    
    if not html_content:
        logger.error(f"[{country_code}] Failed to generate content.")
        return

    # 3. Publishing to Blogger
    logger.info(f"[{country_code}] Publishing to Blogger...")
    # Extract labels from country info or trend source
    labels = ["Trends", TARGET_COUNTRIES[country_code]["name"]]
    
    post_id = publisher.publish_post(
        country_code=country_code,
        title=title,
        content=html_content,
        labels=labels
    )

    if post_id:
        # 4. Record success in DB
        db.record_post(
            title=title,
            country_code=country_code,
            blog_post_id=post_id,
            source=trend.approx_traffic # 'RSS' or 'YouTube Trending'
        )
        logger.info(f"[{country_code}] Successfully completed pipeline for '{title}'.")
    else:
        logger.error(f"[{country_code}] Failed to publish. Check API credentials.")

async def main():
    """
    Main entry point for the global blog automation.
    """
    logger.info("Starting Global Trend-Jacking Automation Pipeline...")

    # 1. Fetch all trends concurrently
    trends_map = await collect_all_trends()

    # 2. Process each country
    tasks = []
    for country_code, trends in trends_map.items():
        tasks.append(process_country_trends(country_code, trends))
    
    await asyncio.gather(*tasks)
    
    logger.info("Pipeline execution finished.")

if __name__ == "__main__":
    asyncio.run(main())
