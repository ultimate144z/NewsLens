"""
NewsAPI Scraper
Fetches news articles from NewsAPI.org
"""
from newsapi import NewsApiClient
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import time
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.logger import get_logger
from utils.helpers import load_config, get_env_variable

logger = get_logger("newsapi_scraper")


class NewsAPIScraper:
    """Scraper for NewsAPI.org"""
    
    def __init__(self, api_key: str = None):
        """
        Initialize NewsAPI scraper
        
        Args:
            api_key: NewsAPI key. If None, loads from environment variable
        """
        self.config = load_config("newsapi_config")
        
        # Get API key
        if api_key is None:
            try:
                api_key = get_env_variable("NEWSAPI_KEY")
            except ValueError:
                logger.warning("NEWSAPI_KEY not found in environment. API calls will fail.")
                api_key = "dummy_key"
        
        self.api_key = api_key
        self.newsapi = NewsApiClient(api_key=api_key)
        
        # Load configuration
        self.search_config = self.config.get("search", {})
        self.language = self.search_config.get("language", "en")
        self.sort_by = self.search_config.get("sort_by", "publishedAt")
        self.page_size = self.search_config.get("page_size", 100)
        
        self.rate_limit = self.config.get("rate_limit", {})
        self.delay = self.rate_limit.get("delay_between_requests", 1)
        
        logger.info(f"Initialized NewsAPI Scraper")
    
    def fetch_top_headlines(self, 
                           sources: List[str] = None,
                           category: str = None,
                           country: str = None) -> List[Dict[str, Any]]:
        """
        Fetch top headlines from NewsAPI with comprehensive error handling.
        
        Args:
            sources: List of news source IDs (e.g., ['bbc-news', 'cnn'])
            category: News category (business, entertainment, general, health, science, sports, technology)
            country: ISO 3166-1 alpha-2 country code (us, gb, ca, au, etc.)
            
        Returns:
            List of article dictionaries. Returns empty list on error.
            
        Note:
            - Cannot use both 'sources' and 'category'/'country' parameters together
            - NewsAPI free tier has rate limits (100 requests/day, 500 results/day)
            
        Raises:
            None: All exceptions are caught and logged
            
        Example:
            >>> scraper = NewsAPIScraper()
            >>> articles = scraper.fetch_top_headlines(sources=['bbc-news'])
        """
        articles = []
        
        try:
            # Validate API key
            if not self.api_key or self.api_key == "dummy_key":
                logger.error("Invalid NewsAPI key. Please set NEWSAPI_KEY environment variable.")
                return articles
            
            logger.info(f"Fetching top headlines (sources={sources}, category={category}, country={country})")
            
            # Prepare parameters
            params = {
                'language': self.language,
                'page_size': self.page_size
            }
            
            # Validate parameter combinations
            if sources:
                if not isinstance(sources, list):
                    logger.error("Sources must be a list")
                    return articles
                params['sources'] = ','.join(sources)
                if category:
                    logger.warning("Cannot use both 'sources' and 'category' - ignoring category")
                if country:
                    logger.warning("Cannot use both 'sources' and 'country' - ignoring country")
            else:
                if category and not sources:
                    valid_categories = ['business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology']
                    if category not in valid_categories:
                        logger.error(f"Invalid category '{category}'. Must be one of: {valid_categories}")
                        return articles
                    params['category'] = category
                if country and not sources:
                    if len(country) != 2:
                        logger.error(f"Invalid country code '{country}'. Must be 2-letter ISO code.")
                        return articles
                    params['country'] = country
            
            # Fetch articles with timeout and error handling
            try:
                response = self.newsapi.get_top_headlines(**params)
            except newsapi.newsapi_exception.NewsAPIException as api_error:
                logger.error(f"NewsAPI error: {api_error}")
                return articles
            except Exception as request_error:
                logger.error(f"Request error: {request_error}")
                return articles
            
            # Check response status
            if response.get('status') == 'ok':
                raw_articles = response.get('articles', [])
                logger.success(f"Fetched {len(raw_articles)} articles from NewsAPI")
                
                # Parse articles with error handling for each
                for article in raw_articles:
                    try:
                        parsed_article = self._parse_article(article, "top_headlines")
                        articles.append(parsed_article)
                    except Exception as parse_error:
                        logger.warning(f"Error parsing article: {parse_error}")
                        continue
            elif response.get('status') == 'error':
                error_code = response.get('code', 'unknown')
                error_message = response.get('message', 'Unknown error')
                logger.error(f"NewsAPI error [{error_code}]: {error_message}")
            else:
                logger.error(f"NewsAPI returned unexpected status: {response.get('status')}")
                
        except Exception as e:
            logger.error(f"Unexpected error fetching top headlines: {e}")
        
        return articles
    
    def fetch_everything(self,
                        query: str,
                        from_date: datetime = None,
                        to_date: datetime = None,
                        sources: List[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch all articles matching query from NewsAPI with error handling.
        
        Args:
            query: Search query/keywords (required, cannot be empty)
            from_date: Start date for articles (defaults to 7 days ago)
            to_date: End date for articles (defaults to now)
            sources: List of news source IDs to search (optional)
            
        Returns:
            List of article dictionaries. Returns empty list on error.
            
        Note:
            - NewsAPI free tier only allows searches up to 1 month old
            - Maximum 100 results returned
            
        Raises:
            None: All exceptions are caught and logged
            
        Example:
            >>> scraper = NewsAPIScraper()
            >>> articles = scraper.fetch_everything(query="artificial intelligence", from_date=datetime.now() - timedelta(days=3))
        """
        articles = []
        
        try:
            # Validate inputs
            if not query or not isinstance(query, str) or not query.strip():
                logger.error("Query parameter is required and cannot be empty")
                return articles
            
            # Validate API key
            if not self.api_key or self.api_key == "dummy_key":
                logger.error("Invalid NewsAPI key. Please set NEWSAPI_KEY environment variable.")
                return articles
                
            # Default date range: last 7 days
            if from_date is None:
                from_date = datetime.now() - timedelta(days=7)
            if to_date is None:
                to_date = datetime.now()
            
            # Validate date range
            if from_date > to_date:
                logger.error(f"Invalid date range: from_date ({from_date}) is after to_date ({to_date})")
                return articles
            
            # Check if date range exceeds free tier limit (1 month)
            max_lookback = datetime.now() - timedelta(days=30)
            if from_date < max_lookback:
                logger.warning(f"NewsAPI free tier only allows searches up to 1 month old. Adjusting from_date.")
                from_date = max_lookback
            
            logger.info(f"Searching for '{query}' from {from_date.date()} to {to_date.date()}")
            
            # Prepare parameters
            params = {
                'q': query.strip(),
                'language': self.language,
                'sort_by': self.sort_by,
                'page_size': self.page_size,
                'from_param': from_date.strftime('%Y-%m-%d'),
                'to': to_date.strftime('%Y-%m-%d')
            }
            
            if sources:
                if not isinstance(sources, list):
                    logger.error("Sources must be a list")
                    return articles
                params['sources'] = ','.join(sources)
            
            # Fetch articles with error handling
            try:
                response = self.newsapi.get_everything(**params)
            except newsapi.newsapi_exception.NewsAPIException as api_error:
                logger.error(f"NewsAPI error: {api_error}")
                return articles
            except Exception as request_error:
                logger.error(f"Request error: {request_error}")
                return articles
            
            # Check response
            if response.get('status') == 'ok':
                raw_articles = response.get('articles', [])
                logger.success(f"Found {len(raw_articles)} articles for query '{query}'")
                
                # Parse articles with individual error handling
                for article in raw_articles:
                    try:
                        parsed_article = self._parse_article(article, "search", query)
                        articles.append(parsed_article)
                    except Exception as parse_error:
                        logger.warning(f"Error parsing article: {parse_error}")
                        continue
            elif response.get('status') == 'error':
                error_code = response.get('code', 'unknown')
                error_message = response.get('message', 'Unknown error')
                logger.error(f"NewsAPI error [{error_code}]: {error_message}")
            else:
                logger.error(f"NewsAPI returned unexpected status: {response.get('status')}")
                
        except Exception as e:
            logger.error(f"Unexpected error searching for '{query}': {e}")
        
        return articles
    
    def fetch_by_categories(self, categories: List[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch articles from multiple categories
        
        Args:
            categories: List of categories to fetch. If None, uses config.
            
        Returns:
            List of all articles
        """
        all_articles = []
        
        if categories is None:
            categories = self.config.get("categories", ["general"])
        
        logger.info(f"Fetching articles from {len(categories)} categories")
        
        for category in categories:
            articles = self.fetch_top_headlines(category=category)
            all_articles.extend(articles)
            
            # Respect rate limiting
            time.sleep(self.delay)
        
        logger.info(f"Total articles fetched from categories: {len(all_articles)}")
        return all_articles
    
    def _parse_article(self, article: Dict, fetch_type: str, query: str = None) -> Dict[str, Any]:
        """
        Parse NewsAPI article into standard format
        
        Args:
            article: Raw article from NewsAPI
            fetch_type: Type of fetch (top_headlines, search)
            query: Search query if applicable
            
        Returns:
            Parsed article dictionary
        """
        source = article.get('source', {})
        
        parsed = {
            'title': article.get('title', ''),
            'description': article.get('description', ''),
            'content': article.get('content', ''),
            'link': article.get('url', ''),
            'published': article.get('publishedAt', ''),
            'author': article.get('author', ''),
            'source': source.get('name', 'Unknown'),
            'source_id': source.get('id', ''),
            'image_url': article.get('urlToImage', ''),
            'scraped_at': datetime.now().isoformat(),
            'scraper_type': 'newsapi',
            'fetch_type': fetch_type
        }
        
        if query:
            parsed['search_query'] = query
        
        return parsed


def main():
    """Test the NewsAPI scraper"""
    scraper = NewsAPIScraper()
    
    # Test 1: Fetch top headlines from BBC
    logger.info("\n=== Test 1: Fetching top headlines from BBC ===")
    articles = scraper.fetch_top_headlines(sources=['bbc-news'])
    
    if articles:
        logger.info(f"Fetched {len(articles)} articles")
        logger.info(f"\nSample article:")
        logger.info(f"Title: {articles[0]['title']}")
        logger.info(f"Source: {articles[0]['source']}")
        logger.info(f"Published: {articles[0]['published']}")
    
    # Test 2: Search for a topic
    logger.info("\n=== Test 2: Searching for 'technology' ===")
    search_articles = scraper.fetch_everything(query="technology", from_date=datetime.now() - timedelta(days=3))
    
    if search_articles:
        logger.info(f"Found {len(search_articles)} articles about 'technology'")
    
    return articles + search_articles


if __name__ == "__main__":
    main()
