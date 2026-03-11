from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class TrendItem(BaseModel):
    """
    Represents a single trending topic fetched from Google Trends.
    """
    title: str = Field(..., description="The main keyword or title of the trend.")
    approx_traffic: str = Field(..., description="Approximate search volume (e.g., '10,000+').")
    pub_date: datetime = Field(..., description="The time the trend was published or spiked.")
    news_titles: List[str] = Field(default_factory=list, description="Titles of related news articles.")
    news_urls: List[str] = Field(default_factory=list, description="URLs of related news articles.")
    country_code: str = Field(..., description="The target country code (e.g., 'VN', 'TW').")
