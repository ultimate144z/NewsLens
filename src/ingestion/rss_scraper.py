"""
RSS Feed Scraper
Scrapes news headlines from RSS feeds of multiple news sources
"""
import feedparser
import requests
from datetime import datetime
from typing import List, Dict, Any
import time
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.logger import get_logger
from utils.helpers import load_config

logger = get_logger("rss_scraper")


class RSScraper:
    """Scraper for RSS news feeds"""
    
    def __init__(self):
        """Initialize RSS scraper with configuration"""
        self.config = load_config("rss_feeds")
        self.sources = self.config.get("news_sources", {})
        self.scraping_config = self.config.get("scraping", {})
        self.timeout = self.scraping_config.get("timeout", 30)
        self.retry_attempts = self.scraping_config.get("retry_attempts", 3)
        self.user_agent = self.scraping_config.get("user_agent", "NewsLens/1.0")
        
        logger.info(f"Initialized RSS Scraper with {len(self.sources)} sources")
    
    def fetch_feed(self, url: str, source_name: str) -> List[Dict[str, Any]]:
        """
        Fetch articles from a single RSS feed with retry logic and error handling.
        
        Args:
            url: RSS feed URL to fetch from
            source_name: Human-readable name of the news source
            
        Returns:
            List of article dictionaries containing title, description, link, etc.
            Returns empty list if all retry attempts fail.
            
        Raises:
            None: Catches all exceptions and logs errors
            
        Example:
            >>> scraper = RSScraper()
            >>> articles = scraper.fetch_feed("https://feeds.bbci.co.uk/news/rss.xml", "BBC News")
        """
        articles = []
        
        # Validate inputs
        if not url or not isinstance(url, str):
            logger.error(f"Invalid URL provided for {source_name}: {url}")
            return articles
            
        if not source_name or not isinstance(source_name, str):
            logger.warning(f"Invalid source name provided for {url}, using default")
            source_name = "Unknown Source"
        
        for attempt in range(self.retry_attempts):
            try:
                logger.info(f"Fetching feed from {source_name} (attempt {attempt + 1}/{self.retry_attempts})")
                
                # Set custom user agent
                feedparser.USER_AGENT = self.user_agent
                
                # Parse the feed with timeout handling
                try:
                    feed = feedparser.parse(url, request_headers={'User-Agent': self.user_agent})
                except Exception as parse_error:
                    logger.error(f"Feed parsing error for {source_name}: {parse_error}")
                    raise
                
                # Check for feed errors
                if feed.bozo:
                    logger.warning(f"Feed parsing warning for {source_name}: {feed.bozo_exception}")
                    # Continue anyway as some feeds work despite bozo flag
                
                if not hasattr(feed, 'entries') or not feed.entries:
                    logger.warning(f"No entries found in feed for {source_name}")
                    return articles
                
                # Extract articles
                for entry in feed.entries:
                    try:
                        article = {
                            "title": entry.get("title", "").strip(),
                            "description": (entry.get("description", "") or entry.get("summary", "")).strip(),
                            "link": entry.get("link", "").strip(),
                            "published": self._parse_date(entry.get("published", "")),
                            "source": source_name,
                            "source_url": url,
                            "scraped_at": datetime.now().isoformat(),
                            "scraper_type": "rss"
                        }
                        
                        # Only add if we have at least a title and link
                        if article["title"] and article["link"]:
                            articles.append(article)
                        else:
                            logger.debug(f"Skipping entry without title or link from {source_name}")
                            
                    except Exception as entry_error:
                        logger.warning(f"Error parsing entry from {source_name}: {entry_error}")
                        continue
                
                logger.success(f"Successfully fetched {len(articles)} articles from {source_name}")
                break
                
            except requests.exceptions.Timeout:
                logger.error(f"Timeout fetching feed from {source_name} (attempt {attempt + 1})")
                if attempt < self.retry_attempts - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
            except requests.exceptions.ConnectionError:
                logger.error(f"Connection error fetching feed from {source_name} (attempt {attempt + 1})")
                if attempt < self.retry_attempts - 1:
                    time.sleep(2 ** attempt)
            except requests.exceptions.RequestException as req_error:
                logger.error(f"Request error fetching feed from {source_name}: {req_error}")
                if attempt < self.retry_attempts - 1:
                    time.sleep(2 ** attempt)
            except Exception as e:
                logger.error(f"Unexpected error fetching feed from {source_name} (attempt {attempt + 1}): {e}")
                if attempt < self.retry_attempts - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Failed to fetch feed from {source_name} after {self.retry_attempts} attempts")
        
        return articles
    
    def fetch_all_feeds(self, source_keys: List[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch articles from all configured RSS feeds
        
        Args:
            source_keys: Optional list of specific source keys to fetch. If None, fetches all.
            
        Returns:
            List of all articles from all sources
        """
        all_articles = []
        
        sources_to_fetch = source_keys if source_keys else list(self.sources.keys())
        
        logger.info(f"Starting to fetch {len(sources_to_fetch)} RSS feeds")
        
        for source_key in sources_to_fetch:
            if source_key not in self.sources:
                logger.warning(f"Source '{source_key}' not found in configuration")
                continue
            
            source_info = self.sources[source_key]
            source_name = source_info.get("name", source_key)
            url = source_info.get("url")
            
            if not url:
                logger.warning(f"No URL configured for source '{source_key}'")
                continue
            
            articles = self.fetch_feed(url, source_name)
            all_articles.extend(articles)
            
            # Small delay between requests to be respectful
            time.sleep(1)
        
        logger.info(f"Total articles fetched: {len(all_articles)} from {len(sources_to_fetch)} sources")
        return all_articles
    
    def _parse_date(self, date_string: str) -> str:
        """
        Parse date string to ISO format with error handling.
        
        Args:
            date_string: Date string from RSS feed in various formats
            
        Returns:
            ISO formatted date string (YYYY-MM-DD) or original string if parsing fails.
            Returns empty string if input is None or empty.
            
        Note:
            Handles multiple date formats commonly found in RSS feeds.
        """
        if not date_string:
            return ""
        
        try:
            # feedparser usually provides a time_struct
            # For simplicity and reliability, return the original string
            # Could be enhanced to convert to standardized ISO format
            return date_string.strip()
        except AttributeError:
            logger.debug(f"Date parsing error for: {date_string}")
            return ""
        except Exception as e:
            logger.debug(f"Unexpected error parsing date '{date_string}': {e}")
            return date_string
    
    def get_source_list(self) -> List[str]:
        """Get list of available source names"""
        return [info.get("name", key) for key, info in self.sources.items()]


def main():
    """Test the RSS scraper"""
    scraper = RSScraper()
    
    # Fetch from all sources
    articles = scraper.fetch_all_feeds()
    
    if articles:
        logger.info(f"\nSample article:")
        logger.info(f"Title: {articles[0]['title']}")
        logger.info(f"Source: {articles[0]['source']}")
        logger.info(f"Link: {articles[0]['link'][:80]}...")
    
    return articles


if __name__ == "__main__":
    main()
