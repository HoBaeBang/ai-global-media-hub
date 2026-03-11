import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# API 키 설정
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# 슈파베이스 설정
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# 타겟 국가 및 설정 정보
TARGET_COUNTRIES = {
    "VN": {
        "name": "Vietnam", 
        "lang": "vi", 
        "trend_geo": "VN", 
        "blog_id": os.getenv("BLOG_ID_VN", ""),
        "rss_url": "https://vnexpress.net/rss/tin-moi-nhat.rss" # 베트남 1위 뉴스 신문 (VnExpress)
    },
    "TW": {
        "name": "Taiwan", 
        "lang": "zh-TW", 
        "trend_geo": "TW", 
        "blog_id": os.getenv("BLOG_ID_TW", ""),
        "rss_url": "http://feeds.feedburner.com/ettoday/news" # 대만 인기 뉴스 (ETtoday)
    },
    "ID": {
        "name": "Indonesia", 
        "lang": "id", 
        "trend_geo": "ID", 
        "blog_id": os.getenv("BLOG_ID_ID", ""),
        "rss_url": "https://rss.tempo.co/nasional" # 인도네시아 주요 뉴스 (Tempo.co)
    },
    "DE": {
        "name": "Germany", 
        "lang": "de", 
        "trend_geo": "DE", 
        "blog_id": os.getenv("BLOG_ID_DE", ""),
        "rss_url": "https://www.spiegel.de/schlagzeilen/index.rss" # 독일 시사 뉴스 (Der Spiegel)
    },
    "PL": {
        "name": "Poland", 
        "lang": "pl", 
        "trend_geo": "PL", 
        "blog_id": os.getenv("BLOG_ID_PL", ""),
        "rss_url": "https://wiadomosci.wp.pl/rss.xml" # 폴란드 주요 뉴스 (WP.pl)
    }
}
