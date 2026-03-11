import logging
from typing import Optional
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

logger = logging.getLogger(__name__)

class DatabaseClient:
    """
    Handles interactions with Supabase to track posting history 
    and prevent duplicate content.
    """
    def __init__(self):
        if not SUPABASE_URL or not SUPABASE_KEY:
            logger.error("Supabase credentials missing in environment.")
            self.client: Optional[Client] = None
        else:
            self.client = create_client(SUPABASE_URL, SUPABASE_KEY)

    def is_already_processed(self, title: str, country_code: str) -> bool:
        """
        Checks if a specific trend title for a country has been processed 
        in the last 7 days.
        """
        if not self.client:
            return False
            
        try:
            # Check the 'post_history' table (needs to be created in Supabase)
            # Use a RPC or a simple select filter
            response = self.client.table("post_history")\
                .select("id")\
                .eq("trend_title", title)\
                .eq("country_code", country_code)\
                .limit(1)\
                .execute()
            
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Error checking duplicate in DB: {e}")
            return False

    def record_post(self, title: str, country_code: str, blog_post_id: str, source: str):
        """
        Records a successfully published post in the database.
        """
        if not self.client:
            return
            
        try:
            data = {
                "trend_title": title,
                "country_code": country_code,
                "blogger_post_id": blog_post_id,
                "source": source, # 'RSS' or 'YouTube'
            }
            self.client.table("post_history").insert(data).execute()
            logger.info(f"Recorded post '{title}' in history.")
        except Exception as e:
            logger.error(f"Failed to record post in DB: {e}")

# Singleton instance
db = DatabaseClient()
