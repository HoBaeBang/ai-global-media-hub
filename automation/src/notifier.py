import logging
import httpx
from typing import Optional
from config import SLACK_WEBHOOK_URL

logger = logging.getLogger(__name__)

async def send_slack_notification(message: str):
    """
    Sends a message to the configured Slack webhook.
    """
    if not SLACK_WEBHOOK_URL:
        logger.debug("No Slack webhook URL configured, skipping notification.")
        return

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            payload = {"text": message}
            response = await client.post(SLACK_WEBHOOK_URL, json=payload)
            response.raise_for_status()
            logger.info("Slack notification sent successfully.")
    except Exception as e:
        logger.error(f"Failed to send Slack notification: {e}")

async def notify_post_success(country_code: str, title: str, post_id: str):
    msg = f"✅ *[Blogger Automation]* New Post Published!\n*Country:* {country_code}\n*Title:* {title}\n*Post ID:* {post_id}"
    await send_slack_notification(msg)

async def notify_error(task: str, error_msg: str):
    msg = f"❌ *[Blogger Automation Error]*\n*Task:* {task}\n*Error:* {error_msg}"
    await send_slack_notification(msg)
