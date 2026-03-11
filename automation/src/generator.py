import logging
import google.generativeai as genai
from typing import Optional
from config import GEMINI_API_KEY, TARGET_COUNTRIES

logger = logging.getLogger(__name__)

# System Prompt to ensure E-E-A-T and SEO
SYSTEM_PROMPT = """
You are a professional world-class blogger and trend analyst. 
Your goal is to write a high-quality, engaging, and SEO-optimized blog post based on a provided topic or trend.

Guidelines:
1. Format: Use clean HTML (h1, h2, p, ul, li, strong, etc.). Do not include <html> or <body> tags.
2. Structure: 
   - Start with a catchy <h1> title.
   - <h2> introduction explaining the trend.
   - <h2> or <h3> subheadings for detailed analysis.
   - A concluding paragraph.
3. Perspective: Don't just list facts. Provide analysis, social context, and why this is trending. (E-E-A-T)
4. Language: Always write in the target language specified for the country.
5. Length: Approximately 800 - 1200 words for a deep dive.
6. Tone: Professional yet approachable, localized to the target culture.
7. Image placeholder: Include exactly one <img src="IMAGE_URL_PLACEHOLDER" alt="Related image description"> after the first H2.
"""

class ContentGenerator:
    """
    Interfaces with Google Gemini API to generate blog content.
    """
    def __init__(self):
        if not GEMINI_API_KEY:
            logger.error("Gemini API Key missing.")
            self.model = None
        else:
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel(
                model_name="gemini-1.5-pro", # or gemini-2.0-flash
                system_instruction=SYSTEM_PROMPT
            )

    async def generate_post(self, trend_title: str, country_code: str) -> Optional[str]:
        """
        Generates a complete blog post in HTML for the given trend and country.
        """
        if not self.model:
            return None
            
        country_info = TARGET_COUNTRIES.get(country_code, {})
        lang = country_info.get("lang", "en")
        country_name = country_info.get("name", country_code)

        prompt = f"""
        Topic: {trend_title}
        Target Country: {country_name}
        Language: {lang}
        
        Please write a comprehensive blog post in {lang} about the topic '{trend_title}' for an audience in {country_name}.
        """
        
        try:
            # Note: SDK is sync, but we treat it as async compatible conceptually here.
            # For 24/7 automation, small block is fine.
            import asyncio
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: self.model.generate_content(prompt)
            )
            
            return response.text
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            return None

# Singleton instance
generator = ContentGenerator()
