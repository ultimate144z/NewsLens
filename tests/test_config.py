"""
Test Configuration Setup
This script tests that all configuration files are loaded correctly
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.helpers import load_config, get_data_dir, ensure_dir_exists
from utils.logger import get_logger

logger = get_logger("config_test")

def test_configurations():
    """Test loading all configuration files"""
    
    logger.info("=" * 60)
    logger.info("Testing NewsLens Configuration Setup")
    logger.info("=" * 60)
    
    # Test RSS Feeds Config
    try:
        logger.info("\n1. Testing RSS Feeds Configuration...")
        rss_config = load_config("rss_feeds")
        num_sources = len(rss_config.get("news_sources", {}))
        logger.success(f"✓ RSS Config loaded successfully: {num_sources} news sources found")
        
        # Print sources
        for key, source in rss_config["news_sources"].items():
            logger.info(f"  - {source['name']}: {source['url'][:50]}...")
            
    except Exception as e:
        logger.error(f"✗ Failed to load RSS config: {e}")
        return False
    
    # Test NewsAPI Config
    try:
        logger.info("\n2. Testing NewsAPI Configuration...")
        newsapi_config = load_config("newsapi_config")
        base_url = newsapi_config.get("api", {}).get("base_url")
        num_sources = len(newsapi_config.get("sources", []))
        logger.success(f"✓ NewsAPI Config loaded successfully")
        logger.info(f"  - Base URL: {base_url}")
        logger.info(f"  - Configured sources: {num_sources}")
        logger.info(f"  - Page size: {newsapi_config['search']['page_size']}")
        
    except Exception as e:
        logger.error(f"✗ Failed to load NewsAPI config: {e}")
        return False
    
    # Test Model Config
    try:
        logger.info("\n3. Testing Model Configuration...")
        model_config = load_config("model_config")
        sentiment_model = model_config.get("sentiment_model", {}).get("name")
        spacy_model = model_config.get("spacy_model", {}).get("name")
        logger.success(f"✓ Model Config loaded successfully")
        logger.info(f"  - Sentiment Model: {sentiment_model}")
        logger.info(f"  - spaCy Model: {spacy_model}")
        logger.info(f"  - Device: {model_config['sentiment_model']['device']}")
        
    except Exception as e:
        logger.error(f"✗ Failed to load Model config: {e}")
        return False
    
    # Test Data Directories
    try:
        logger.info("\n4. Testing Data Directory Structure...")
        raw_dir = get_data_dir("raw")
        processed_dir = get_data_dir("processed")
        logger.success(f"✓ Data directories verified")
        logger.info(f"  - Raw: {raw_dir}")
        logger.info(f"  - Processed: {processed_dir}")
        
    except Exception as e:
        logger.error(f"✗ Failed to create data directories: {e}")
        return False
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.success("✓ All Configuration Tests Passed!")
    logger.info("=" * 60)
    logger.info("\nNext Steps:")
    logger.info("1. Copy .env.template to .env")
    logger.info("2. Add your NewsAPI key to .env file")
    logger.info("3. Download spaCy model: python -m spacy download en_core_web_sm")
    logger.info("4. Proceed to Step 2: Data Ingestion Layer")
    
    return True

if __name__ == "__main__":
    success = test_configurations()
    sys.exit(0 if success else 1)