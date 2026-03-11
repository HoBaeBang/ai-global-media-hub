import logging
import os
from typing import Optional, List
from googleapiclient.discovery import build
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from config import TARGET_COUNTRIES

logger = logging.getLogger(__name__)

# Note: Authenticating with Blogger API can be tricky (OAuth vs Service Account).
# Most users prefer Service Account for server-side automation if the blog 
# belongs to a workspace, but for personal blogs, OAuth2 with Refresh Token is common.
# I'll implement a flexible structure that looks for credentials.

class BloggerPublisher:
    """
    Handles automated posting to Blogger using Google API.
    """
    def __init__(self):
        self.service = self._authenticate()

    def _authenticate(self):
        """
        Initializes the Blogger service. 
        Expects a token.json for OAuth2 or a service_account.json.
        """
        # Placeholder authentication logic
        # In a real scenario, we'll need either 
        # 1. client_secrets.json (OAuth2) -> generates token.json
        # 2. service_account.json
        
        credentials_path = "credentials/service_account.json"
        
        try:
            if os.path.exists(credentials_path):
                creds = service_account.Credentials.from_service_account_file(
                    credentials_path, 
                    scopes=['https://www.googleapis.com/auth/blogger']
                )
                return build('blogger', 'v3', credentials=creds)
            else:
                logger.warning("Blogger credentials not found. Publishing will be disabled.")
                return None
        except Exception as e:
            logger.error(f"Blogger authentication failed: {e}")
            return None

    def publish_post(self, country_code: str, title: str, content: str, labels: List[str] = None) -> Optional[str]:
        """
        Publishes a new blog post. Returns the post_id on success.
        """
        if not self.service:
            logger.error("Blogger service not initialized.")
            return None

        country_info = TARGET_COUNTRIES.get(country_code, {})
        blog_id = country_info.get("blog_id")
        
        if not blog_id:
            logger.error(f"Missing blog_id for {country_code}")
            return None

        try:
            # Create post body
            post_body = {
                'kind': 'blogger#post',
                'blog': {'id': blog_id},
                'title': title,
                'content': content,
                'labels': labels or []
            }
            
            # Execute request
            posts = self.service.posts()
            request = posts.insert(blogId=blog_id, body=post_body, isDraft=False)
            response = request.execute()
            
            post_id = response.get("id")
            logger.info(f"Successfully published post '{title}' to {country_code}. Post ID: {post_id}")
            return post_id
            
        except Exception as e:
            logger.error(f"Failed to publish to Blogger: {e}")
            return None

# Singleton instance
publisher = BloggerPublisher()
