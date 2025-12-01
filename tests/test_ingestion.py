"""
Test Data Ingestion Layer
Tests RSS and NewsAPI scrapers
"""
import sys
from pathlib import Path
import json
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.ingestion import RSScraper, NewsAPIScraper
from utils.logger import get_logger
from utils.helpers import get_data_dir

logger = get_logger("ingestion_test")


def test_rss_scraper():
    """Test RSS scraper functionality"""
    logger.info("\n" + "=" * 60)
    logger.info("Testing RSS Scraper")
    logger.info("=" * 60)
    
    try:
        scraper = RSScraper()
        
        # Test fetching from a few sources
        logger.info("\n1. Fetching from BBC and CNN...")
        articles = scraper.fetch_all_feeds(source_keys=['bbc', 'cnn'])
        
        if articles:
            logger.success(f"✓ Successfully fetched {len(articles)} articles")
            
            # Show sample articles
            logger.info("\nSample Articles:")
            for i, article in enumerate(articles[:3], 1):
                logger.info(f"\n  Article {i}:")
                logger.info(f"  Title: {article['title'][:80]}...")
                logger.info(f"  Source: {article['source']}")
                logger.info(f"  Published: {article['published']}")
            
            # Save to file
            output_file = get_data_dir("raw") / f"rss_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(articles, f, indent=2, ensure_ascii=False)
            logger.info(f"\n✓ Saved {len(articles)} articles to: {output_file}")
            
            return True
        else:
            logger.error("✗ No articles fetched from RSS feeds")
            return False
            
    except Exception as e:
        logger.error(f"✗ RSS Scraper test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_newsapi_scraper():
    """Test NewsAPI scraper functionality"""
    logger.info("\n" + "=" * 60)
    logger.info("Testing NewsAPI Scraper")
    logger.info("=" * 60)
    
    try:
        scraper = NewsAPIScraper()
        
        # Test fetching top headlines
        logger.info("\n1. Fetching top headlines from BBC News...")
        articles = scraper.fetch_top_headlines(sources=['bbc-news'])
        
        if articles:
            logger.success(f"✓ Successfully fetched {len(articles)} articles from NewsAPI")
            
            # Show sample articles
            logger.info("\nSample Articles:")
            for i, article in enumerate(articles[:3], 1):
                logger.info(f"\n  Article {i}:")
                logger.info(f"  Title: {article['title'][:80]}...")
                logger.info(f"  Source: {article['source']}")
                logger.info(f"  Published: {article['published']}")
                if article.get('description'):
                    logger.info(f"  Description: {article['description'][:100]}...")
            
            # Save to file
            output_file = get_data_dir("raw") / f"newsapi_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(articles, f, indent=2, ensure_ascii=False)
            logger.info(f"\n✓ Saved {len(articles)} articles to: {output_file}")
            
            return True
        else:
            logger.warning("⚠ No articles fetched from NewsAPI (check API key in .env)")
            return False
            
    except Exception as e:
        logger.error(f"✗ NewsAPI Scraper test failed: {e}")
        logger.warning("Make sure NEWSAPI_KEY is set in .env file")
        logger.info("Get free API key from: https://newsapi.org/")
        return False


def test_combined_ingestion():
    """Test fetching from both sources"""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Combined Ingestion")
    logger.info("=" * 60)
    
    all_articles = []
    
    # Fetch from RSS
    logger.info("\n1. Fetching from RSS feeds...")
    try:
        rss_scraper = RSScraper()
        rss_articles = rss_scraper.fetch_all_feeds(source_keys=['bbc', 'cnn', 'guardian'])
        all_articles.extend(rss_articles)
        logger.success(f"✓ RSS: {len(rss_articles)} articles")
    except Exception as e:
        logger.error(f"✗ RSS fetch failed: {e}")
    
    # Fetch from NewsAPI
    logger.info("\n2. Fetching from NewsAPI...")
    try:
        newsapi_scraper = NewsAPIScraper()
        api_articles = newsapi_scraper.fetch_top_headlines(sources=['bbc-news', 'cnn'])
        all_articles.extend(api_articles)
        logger.success(f"✓ NewsAPI: {len(api_articles)} articles")
    except Exception as e:
        logger.error(f"✗ NewsAPI fetch failed: {e}")
    
    if all_articles:
        logger.info("\n" + "=" * 60)
        logger.success(f"✓ Total articles collected: {len(all_articles)}")
        logger.info("=" * 60)
        
        # Statistics
        sources = {}
        for article in all_articles:
            source = article.get('source', 'Unknown')
            sources[source] = sources.get(source, 0) + 1
        
        logger.info("\nArticles by source:")
        for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"  - {source}: {count}")
        
        # Save combined data
        output_file = get_data_dir("raw") / f"combined_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_articles, f, indent=2, ensure_ascii=False)
        logger.info(f"\n✓ Saved all articles to: {output_file}")
        
        return True
    else:
        logger.error("✗ No articles collected from any source")
        return False


def main():
    """Run all ingestion tests"""
    logger.info("\n" + "=" * 60)
    logger.info("NEWSLENS DATA INGESTION TEST SUITE")
    logger.info("=" * 60)
    
    results = {
        'RSS Scraper': test_rss_scraper(),
        'NewsAPI Scraper': test_newsapi_scraper(),
        'Combined Ingestion': test_combined_ingestion()
    }
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        logger.info(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        logger.success("\n✓ All tests passed!")
        logger.info("\nNext Steps:")
        logger.info("1. Check data/raw/ folder for collected articles")
        logger.info("2. Proceed to Step 3: Preprocessing Module")
    else:
        logger.warning("\n⚠ Some tests failed. Check the logs above.")
        if not results['NewsAPI Scraper']:
            logger.info("\nFor NewsAPI:")
            logger.info("1. Sign up at https://newsapi.org/")
            logger.info("2. Add NEWSAPI_KEY to .env file")
            logger.info("3. Run the test again")
    
    logger.info("\n" + "=" * 60)
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
