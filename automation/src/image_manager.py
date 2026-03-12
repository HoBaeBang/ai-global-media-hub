import logging
import uuid
import io
import google.generativeai as genai
from PIL import Image
from typing import List, Dict, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
from config import GEMINI_API_KEY, SUPABASE_URL, SUPABASE_KEY, SUPABASE_BUCKET_NAME
from supabase import create_client, Client

logger = logging.getLogger(__name__)

class ImageManager:
    """
    Handles AI image generation using Imagen 3 and 
    hosting on Supabase Storage.
    """
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        # Imagen 3 model name
        self.model_name = "imagen-3.0-generate-001"
        try:
            self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            self.supabase = None

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=2, min=5, max=30))
    def generate_image(self, prompt: str) -> Optional[Image.Image]:
        """Generates an image using Imagen 3 model."""
        try:
            logger.info(f"Generating image with Imagen 3 for prompt: {prompt[:50]}...")
            model = genai.ImageGenerationModel(self.model_name)
            response = model.generate_images(
                prompt=prompt,
                number_of_images=1,
                safety_filter_level="BLOCK_ONLY_HIGH",
                person_generation="ALLOW_ADULT" # Adjust based on needs
            )
            if response.images:
                return response.images[0]
            return None
        except Exception as e:
            logger.error(f"Imagen generation error: {e}")
            raise # Retry

    def upload_to_supabase(self, image: Image.Image, filename: str) -> Optional[str]:
        """Uploads PIL Image to Supabase Storage and returns public URL."""
        if not self.supabase:
            return None

        try:
            # Convert PIL Image to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_bytes = img_byte_arr.getvalue()

            path_on_storage = f"thumbnails/{filename}"
            
            # Upload
            res = self.supabase.storage.from_(SUPABASE_BUCKET_NAME).upload(
                path=path_on_storage,
                file=img_bytes,
                file_options={"content-type": "image/png"}
            )
            
            # Get Public URL (Supabase storage.getPublicUrl returns a dict or object depending on version)
            # For supabase-py 2.x:
            public_url = self.supabase.storage.from_(SUPABASE_BUCKET_NAME).get_public_url(path_on_storage)
            return public_url
        except Exception as e:
            logger.error(f"Supabase upload error: {e}")
            return None

    async def create_thumbnail(self, trend_title: str) -> Optional[str]:
        """
        Orchestrates full process: prompt creation -> generation -> upload.
        """
        # 1. Create a specialized prompt for thumbnail
        image_prompt = f"Professional blog thumbnail for: {trend_title}. Cinematic lighting, high quality, 16:9 aspect ratio, no text."
        
        try:
            # 2. Generate
            # Using run_in_executor since generate_images is sync
            import asyncio
            loop = asyncio.get_event_loop()
            img = await loop.run_in_executor(None, lambda: self.generate_image(image_prompt))
            
            if not img:
                return None

            # 3. Upload
            filename = f"{uuid.uuid4()}.png"
            public_url = await loop.run_in_executor(None, lambda: self.upload_to_supabase(img, filename))
            
            return public_url
        except Exception as e:
            logger.error(f"Thumbnail creation pipeline failed: {e}")
            return None

image_manager = ImageManager()
