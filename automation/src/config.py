import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Blogger API
BLOGGER_CLIENT_ID = os.getenv("BLOGGER_CLIENT_ID")
BLOGGER_CLIENT_SECRET = os.getenv("BLOGGER_CLIENT_SECRET")
BLOGGER_REFRESH_TOKEN = os.getenv("BLOGGER_REFRESH_TOKEN")

# 타겟 국가 및 설정 정보
TARGET_COUNTRIES = {
    "VN": {"name": "Vietnam", "lang": "vi", "trend_geo": "VN", "blog_id": ""},
    "TW": {"name": "Taiwan", "lang": "zh-TW", "trend_geo": "TW", "blog_id": ""},
    "ID": {"name": "Indonesia", "lang": "id", "trend_geo": "ID", "blog_id": ""},
    "DE": {"name": "Germany", "lang": "de", "trend_geo": "DE", "blog_id": ""},
    "PL": {"name": "Poland", "lang": "pl", "trend_geo": "PL", "blog_id": ""}
}
