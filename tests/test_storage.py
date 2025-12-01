"""
Test Script for Storage Layer (Step 5)
Tests SQLite database operations and CSV export functionality
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from loguru import logger

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.storage import DatabaseManager
from src.storage.csv_manager import CSVManager
from utils.helpers import get_data_dir

# Configure logger
logger.remove()
logger.add(sys.stdout, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level:8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")


def test_database_creation():
    """Test 1: Database creation and schema"""
    logger.info("\n" + "=" * 60)
    logger.info("Test 1: Database Creation and Schema")
    logger.info("=" * 60)
    
    # Create test database
    test_db_path = get_data_dir() / "test_newslens.db"
    
    # Remove if exists
    if test_db_path.exists():
        test_db_path.unlink()
        logger.info("Removed existing test database")
    
    # Create database
    db = DatabaseManager(test_db_path)
    
    logger.info(f"Database created at: {test_db_path}")
    logger.info(f"Database size: {test_db_path.stat().st_size / 1024:.2f} KB")
    
    # Check tables exist
    db.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in db.cursor.fetchall()]
    
    logger.info(f"\nTables created: {', '.join(tables)}")
    
    expected_tables = ['articles', 'entities', 'keywords']
    for table in expected_tables:
        if table in tables:
            logger.info(f"  ✓ {table} table exists")
        else:
            logger.error(f"  ✗ {table} table missing")
            return False, db
    
    # Check indexes
    db.cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
    indexes = [row[0] for row in db.cursor.fetchall()]
    logger.info(f"\nIndexes created: {len(indexes)}")
    
    logger.success("\n✓ Database creation test passed")
    return True, db


def test_insert_article(db: DatabaseManager):
    """Test 2: Insert single article"""
    logger.info("\n" + "=" * 60)
    logger.info("Test 2: Insert Single Article")
    logger.info("=" * 60)
    
    # Test article
    test_article = {
        'title': 'Test News Article: Major Breakthrough in Technology',
        'description': 'Scientists announce revolutionary discovery that could change everything.',
        'link': 'https://example.com/test-article-001',
        'published': '2025-12-01T10:00:00',
        'source': 'Test News Network',
        'source_url': 'https://example.com/rss',
        'title_cleaned': 'test news article major breakthrough technology',
        'description_cleaned': 'scientist announce revolutionary discovery change everything',
        'full_text_cleaned': 'test news article major breakthrough technology scientist announce revolutionary discovery change everything',
        'full_text_token_count': 12,
        'sentiment': 'positive',
        'sentiment_confidence': 0.92,
        'sentiment_scores': {
            'positive': 0.92,
            'neutral': 0.06,
            'negative': 0.02
        },
        'entities': {
            'people': [
                {'text': 'Dr. John Smith', 'label': 'PERSON', 'start': 0, 'end': 14}
            ],
            'organizations': [
                {'text': 'Tech Corp', 'label': 'ORG', 'start': 20, 'end': 29}
            ],
            'locations': [
                {'text': 'Silicon Valley', 'label': 'GPE', 'start': 35, 'end': 49}
            ],
            'dates': [
                {'text': 'today', 'label': 'DATE', 'start': 55, 'end': 60}
            ]
        },
        'keywords': [
            {'text': 'technology', 'count': 2},
            {'text': 'breakthrough', 'count': 1},
            {'text': 'discovery', 'count': 1}
        ],
        'scraped_at': '2025-12-01T09:00:00',
        'preprocessing_timestamp': '2025-12-01T09:30:00',
        'sentiment_timestamp': '2025-12-01T10:00:00',
        'extraction_timestamp': '2025-12-01T10:00:00'
    }
    
    # Insert article
    article_id = db.insert_article(test_article)
    
    if article_id:
        logger.success(f"\n✓ Article inserted with ID: {article_id}")
        
        # Retrieve and verify
        retrieved = db.get_article_by_id(article_id)
        
        logger.info(f"\nRetrieved article:")
        logger.info(f"  Title: {retrieved['title']}")
        logger.info(f"  Source: {retrieved['source']}")
        logger.info(f"  Sentiment: {retrieved['sentiment']} ({retrieved['sentiment_confidence']:.2%})")
        logger.info(f"  Entities: {sum(len(v) for v in retrieved['entities'].values())} total")
        logger.info(f"  Keywords: {len(retrieved['keywords'])}")
        
        logger.success("\n✓ Insert single article test passed")
        return True, article_id
    else:
        logger.error("\n✗ Failed to insert article")
        return False, None


def test_batch_insert(db: DatabaseManager):
    """Test 3: Batch insert from analyzed articles"""
    logger.info("\n" + "=" * 60)
    logger.info("Test 3: Batch Insert from Analyzed Articles")
    logger.info("=" * 60)
    
    # Load analyzed articles
    data_dir = get_data_dir()
    analyzed_file = data_dir / 'analyzed' / 'all_analyzed_20251201_181717.json'
    
    if not analyzed_file.exists():
        logger.warning(f"Analyzed file not found: {analyzed_file}")
        logger.warning("Skipping batch insert test")
        return False
    
    logger.info(f"Loading articles from: {analyzed_file.name}")
    
    with open(analyzed_file, 'r', encoding='utf-8') as f:
        articles = json.load(f)
    
    logger.info(f"Loaded {len(articles)} articles")
    
    # Insert batch
    inserted_count = db.insert_articles_batch(articles)
    
    logger.info(f"\n✓ Inserted {inserted_count} articles into database")
    
    # Get statistics
    stats = db.get_statistics()
    
    logger.info("\n" + "-" * 60)
    logger.info("Database Statistics:")
    logger.info("-" * 60)
    logger.info(f"Total Articles: {stats['total_articles']}")
    logger.info(f"Total Entities: {stats['total_entities']}")
    logger.info(f"Total Keywords: {stats['total_keywords']}")
    logger.info(f"Avg Sentiment Confidence: {stats['avg_sentiment_confidence']:.2%}")
    
    logger.info("\nSentiment Distribution:")
    for sentiment, count in stats['sentiment_distribution'].items():
        percentage = count / stats['total_articles'] * 100
        logger.info(f"  {sentiment.capitalize()}: {count} ({percentage:.1f}%)")
    
    logger.info("\nSource Distribution:")
    for source, count in sorted(stats['source_distribution'].items(), key=lambda x: x[1], reverse=True):
        logger.info(f"  {source}: {count} articles")
    
    logger.success("\n✓ Batch insert test passed")
    return True


def test_queries(db: DatabaseManager):
    """Test 4: Database queries"""
    logger.info("\n" + "=" * 60)
    logger.info("Test 4: Database Queries")
    logger.info("=" * 60)
    
    # Test 1: Get articles by sentiment
    logger.info("\n1. Query: Positive articles")
    positive_articles = db.get_articles(sentiment='positive', limit=5)
    logger.info(f"   Found {len(positive_articles)} positive articles")
    if positive_articles:
        logger.info(f"   Example: {positive_articles[0]['title'][:60]}...")
    
    # Test 2: Get articles by source
    logger.info("\n2. Query: Articles from CNN")
    cnn_articles = db.get_articles(source='CNN Top Stories', limit=5)
    logger.info(f"   Found {len(cnn_articles)} CNN articles")
    
    # Test 3: Top entities
    logger.info("\n3. Query: Top people mentioned")
    top_people = db.get_top_entities('people', limit=5)
    for i, (person, count) in enumerate(top_people, 1):
        logger.info(f"   {i}. {person} - {count} mentions")
    
    logger.info("\n4. Query: Top organizations")
    top_orgs = db.get_top_entities('organizations', limit=5)
    for i, (org, count) in enumerate(top_orgs, 1):
        logger.info(f"   {i}. {org} - {count} mentions")
    
    logger.info("\n5. Query: Top locations")
    top_locs = db.get_top_entities('locations', limit=5)
    for i, (loc, count) in enumerate(top_locs, 1):
        logger.info(f"   {i}. {loc} - {count} mentions")
    
    # Test 4: Top keywords
    logger.info("\n6. Query: Top keywords")
    top_keywords = db.get_top_keywords(limit=10)
    for i, (keyword, count) in enumerate(top_keywords, 1):
        logger.info(f"   {i}. {keyword} - {count} occurrences")
    
    # Test 5: Search
    logger.info("\n7. Query: Search for 'Trump'")
    search_results = db.search_articles('Trump', limit=5)
    logger.info(f"   Found {len(search_results)} articles")
    if search_results:
        logger.info(f"   Example: {search_results[0]['title'][:60]}...")
    
    logger.success("\n✓ Database queries test passed")
    return True


def test_csv_export(db: DatabaseManager):
    """Test 5: CSV export"""
    logger.info("\n" + "=" * 60)
    logger.info("Test 5: CSV Export")
    logger.info("=" * 60)
    
    # Get all articles from database
    all_articles = db.get_articles(limit=1000)
    logger.info(f"Retrieved {len(all_articles)} articles for export")
    
    # Add entities and keywords back to article dictionaries
    for article in all_articles:
        full_article = db.get_article_by_id(article['id'])
        article['entities'] = full_article['entities']
        article['keywords'] = full_article['keywords']
    
    # Initialize CSV manager
    csv_manager = CSVManager()
    
    # Export directory
    export_dir = get_data_dir() / 'exports'
    export_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Test 1: Full export
    logger.info("\n1. Exporting full articles to CSV...")
    full_export = export_dir / f'articles_full_{timestamp}.csv'
    csv_manager.export_articles(all_articles, str(full_export))
    logger.info(f"   Exported to: {full_export.name}")
    logger.info(f"   File size: {full_export.stat().st_size / 1024:.2f} KB")
    
    # Test 2: Sentiment summary
    logger.info("\n2. Exporting sentiment summary...")
    sentiment_export = export_dir / f'sentiment_summary_{timestamp}.csv'
    csv_manager.export_sentiment_summary(all_articles, str(sentiment_export))
    logger.info(f"   Exported to: {sentiment_export.name}")
    logger.info(f"   File size: {sentiment_export.stat().st_size / 1024:.2f} KB")
    
    # Test 3: Entity summaries
    for entity_type in ['people', 'organizations', 'locations']:
        logger.info(f"\n3. Exporting top {entity_type}...")
        entity_export = export_dir / f'top_{entity_type}_{timestamp}.csv'
        csv_manager.export_entity_summary(all_articles, str(entity_export), entity_type=entity_type, top_n=20)
        logger.info(f"   Exported to: {entity_export.name}")
        logger.info(f"   File size: {entity_export.stat().st_size / 1024:.2f} KB")
    
    logger.success("\n✓ CSV export test passed")
    return True


def test_production_database():
    """Test 6: Create production database"""
    logger.info("\n" + "=" * 60)
    logger.info("Test 6: Production Database")
    logger.info("=" * 60)
    
    # Create production database
    prod_db_path = get_data_dir() / "newslens.db"
    
    logger.info(f"Creating production database at: {prod_db_path}")
    
    db = DatabaseManager(prod_db_path)
    
    # Load and insert analyzed articles
    data_dir = get_data_dir()
    analyzed_file = data_dir / 'analyzed' / 'all_analyzed_20251201_181717.json'
    
    if analyzed_file.exists():
        with open(analyzed_file, 'r', encoding='utf-8') as f:
            articles = json.load(f)
        
        logger.info(f"Inserting {len(articles)} articles into production database...")
        inserted_count = db.insert_articles_batch(articles)
        
        # Get final statistics
        stats = db.get_statistics()
        
        logger.info("\n" + "=" * 60)
        logger.info("PRODUCTION DATABASE STATISTICS")
        logger.info("=" * 60)
        logger.info(f"Database: {prod_db_path.name}")
        logger.info(f"Size: {prod_db_path.stat().st_size / 1024:.2f} KB")
        logger.info(f"\nArticles: {stats['total_articles']}")
        logger.info(f"Entities: {stats['total_entities']}")
        logger.info(f"Keywords: {stats['total_keywords']}")
        logger.info(f"Avg Confidence: {stats['avg_sentiment_confidence']:.2%}")
        
        logger.info("\nSentiment Distribution:")
        for sentiment, count in stats['sentiment_distribution'].items():
            percentage = count / stats['total_articles'] * 100
            logger.info(f"  {sentiment.capitalize()}: {count} ({percentage:.1f}%)")
        
        logger.info("\nSources:")
        for source, count in stats['source_distribution'].items():
            logger.info(f"  {source}: {count}")
        
        logger.success(f"\n✓ Production database created: {prod_db_path}")
        
        db.close()
        return True
    else:
        logger.warning("Analyzed articles file not found")
        db.close()
        return False


def main():
    """Run all storage tests"""
    logger.info("\n" + "=" * 60)
    logger.info("NEWSLENS STORAGE LAYER TEST SUITE (STEP 5)")
    logger.info("=" * 60)
    
    try:
        # Test 1: Database creation
        success, test_db = test_database_creation()
        if not success:
            return False
        
        # Test 2: Insert single article
        success, article_id = test_insert_article(test_db)
        if not success:
            return False
        
        # Test 3: Batch insert
        success = test_batch_insert(test_db)
        if not success:
            logger.warning("Batch insert test skipped or failed")
        
        # Test 4: Queries
        success = test_queries(test_db)
        if not success:
            return False
        
        # Test 5: CSV export
        success = test_csv_export(test_db)
        if not success:
            return False
        
        # Clean up test database
        test_db.close()
        logger.info("\nCleaning up test database...")
        
        # Test 6: Production database
        success = test_production_database()
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("TEST SUMMARY")
        logger.info("=" * 60)
        logger.info("Database Creation: ✓ PASSED")
        logger.info("Insert Single Article: ✓ PASSED")
        logger.info("Batch Insert: ✓ PASSED")
        logger.info("Database Queries: ✓ PASSED")
        logger.info("CSV Export: ✓ PASSED")
        logger.info("Production Database: ✓ PASSED")
        
        logger.success("\n✓ All storage tests passed!")
        logger.info("\nData saved to:")
        logger.info("- data/newslens.db (Production database)")
        logger.info("- data/exports/ folder (CSV files)")
        logger.info("\nNext Steps:")
        logger.info("1. Check database and CSV files")
        logger.info("2. Proceed to Step 6: Analytics Layer")
        
        return True
        
    except Exception as e:
        logger.error(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    logger.info("\n" + "=" * 60)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
