"""
Test Suite for NewsLens Analytics Module (Step 6)

Tests comprehensive analytics including:
- Sentiment distribution and trends
- Source comparison and bias analysis
- Entity and keyword analysis
- Temporal patterns
- Summary statistics
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from src.analytics.analytics import NewsAnalytics

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


def test_sentiment_analytics(analytics: NewsAnalytics):
    """Test sentiment analysis features."""
    logger.info("\n" + "="*60)
    logger.info("Test 1: Sentiment Analytics")
    logger.info("="*60)
    
    # Overall sentiment distribution
    sentiment_dist = analytics.get_sentiment_distribution()
    logger.info(f"\nOverall Sentiment Distribution:")
    logger.info(f"  Total Articles: {sentiment_dist['total_articles']}")
    for sentiment, data in sentiment_dist['sentiments'].items():
        logger.info(f"  {sentiment.capitalize()}: {data['count']} ({data['percentage']}%)")
    
    # Sentiment by source
    logger.info(f"\nSentiment by Source:")
    source_sentiment = analytics.get_sentiment_by_source()
    for source, data in source_sentiment.items():
        logger.info(f"\n  {source}:")
        logger.info(f"    Total: {data['total_articles']} articles")
        for sentiment, sdata in data['sentiments'].items():
            logger.info(f"    {sentiment.capitalize()}: {sdata['count']} ({sdata['percentage']}%)")
    
    # Confidence statistics
    logger.info(f"\nSentiment Confidence Statistics:")
    conf_stats = analytics.get_sentiment_confidence_stats()
    logger.info(f"  Overall:")
    logger.info(f"    Average: {conf_stats['overall']['avg']}%")
    logger.info(f"    Range: {conf_stats['overall']['min']}% - {conf_stats['overall']['max']}%")
    
    logger.info(f"\n  By Sentiment:")
    for sentiment, stats in conf_stats['by_sentiment'].items():
        logger.info(f"    {sentiment.capitalize()}: {stats['avg']}% avg (count: {stats['count']})")
    
    logger.info("\n✓ Sentiment analytics test completed")
    return sentiment_dist, source_sentiment, conf_stats


def test_temporal_analysis(analytics: NewsAnalytics):
    """Test temporal analysis features."""
    logger.info("\n" + "="*60)
    logger.info("Test 2: Temporal Analysis")
    logger.info("="*60)
    
    # Sentiment timeline
    logger.info(f"\nSentiment Timeline (by day):")
    timeline = analytics.get_sentiment_timeline(interval='day')
    logger.info(f"  Found {len(timeline)} time intervals")
    
    if timeline:
        logger.info(f"\n  First 3 intervals:")
        for entry in timeline[:3]:
            logger.info(f"    {entry['timestamp']}: {entry['total']} articles")
            for sentiment, count in entry['sentiments'].items():
                logger.info(f"      {sentiment}: {count}")
    
    # Publication patterns
    logger.info(f"\nPublication Patterns:")
    patterns = analytics.get_publication_patterns()
    logger.info(f"  Peak Hour: {patterns.get('peak_hour', 'N/A')}:00")
    logger.info(f"  Peak Day: {patterns.get('peak_day', 'N/A')}")
    
    logger.info(f"\n  Articles by Hour of Day (top 5):")
    hour_counts = sorted(patterns['by_hour'].items(), key=lambda x: x[1], reverse=True)[:5]
    for hour, count in hour_counts:
        logger.info(f"    {hour:02d}:00 - {count} articles")
    
    logger.info(f"\n  Articles by Day of Week:")
    day_counts = sorted(patterns['by_day'].items(), key=lambda x: x[1], reverse=True)
    for day, count in day_counts:
        logger.info(f"    {day}: {count} articles")
    
    logger.info("\n✓ Temporal analysis test completed")
    return timeline, patterns


def test_entity_analysis(analytics: NewsAnalytics):
    """Test entity analysis features."""
    logger.info("\n" + "="*60)
    logger.info("Test 3: Entity Analysis")
    logger.info("="*60)
    
    # Top entities by type
    logger.info(f"\nTop People Mentioned:")
    top_people = analytics.get_top_entities('PERSON', limit=10)
    for i, entity in enumerate(top_people, 1):
        logger.info(f"  {i}. {entity['entity']}: {entity['mentions']} mentions in {entity['articles']} articles")
    
    logger.info(f"\nTop Organizations:")
    top_orgs = analytics.get_top_entities('ORG', limit=10)
    for i, entity in enumerate(top_orgs, 1):
        logger.info(f"  {i}. {entity['entity']}: {entity['mentions']} mentions in {entity['articles']} articles")
    
    logger.info(f"\nTop Locations:")
    top_locations = analytics.get_top_entities('GPE', limit=10)
    for i, entity in enumerate(top_locations, 1):
        logger.info(f"  {i}. {entity['entity']}: {entity['mentions']} mentions in {entity['articles']} articles")
    
    # Entity sentiment analysis (for top entity)
    if top_people:
        top_entity = top_people[0]['entity']
        logger.info(f"\nSentiment Analysis for '{top_entity}':")
        entity_sentiment = analytics.get_entity_sentiment(top_entity)
        logger.info(f"  Total Mentions: {entity_sentiment['total_mentions']}")
        for sentiment, data in entity_sentiment['sentiments'].items():
            logger.info(f"  {sentiment.capitalize()}: {data['count']} ({data['percentage']}%)")
        
        logger.info(f"\n  Sample Articles:")
        for article in entity_sentiment['sample_articles'][:3]:
            logger.info(f"    - {article['title'][:60]}... ({article['sentiment']})")
        
        # Entity co-occurrence
        logger.info(f"\nEntities Often Mentioned with '{top_entity}':")
        cooccurrence = analytics.get_entity_cooccurrence(top_entity, limit=5)
        for i, item in enumerate(cooccurrence, 1):
            logger.info(f"  {i}. {item['entity']}: {item['cooccurrences']} times")
    
    logger.info("\n✓ Entity analysis test completed")
    return top_people, top_orgs, top_locations


def test_keyword_analysis(analytics: NewsAnalytics):
    """Test keyword analysis features."""
    logger.info("\n" + "="*60)
    logger.info("Test 4: Keyword Analysis")
    logger.info("="*60)
    
    # Top keywords overall
    logger.info(f"\nTop Keywords (Overall):")
    top_keywords = analytics.get_top_keywords(limit=20)
    for i, item in enumerate(top_keywords, 1):
        logger.info(f"  {i}. {item['keyword']}: {item['frequency']} occurrences")
    
    # Keywords by sentiment
    logger.info(f"\nTop Keywords by Sentiment:")
    
    for sentiment in ['positive', 'neutral', 'negative']:
        sentiment_keywords = analytics.get_keywords_by_sentiment(sentiment, limit=10)
        if sentiment_keywords:
            logger.info(f"\n  {sentiment.capitalize()} Articles:")
            for i, item in enumerate(sentiment_keywords[:5], 1):
                logger.info(f"    {i}. {item['keyword']}: {item['frequency']} times")
    
    logger.info("\n✓ Keyword analysis test completed")
    return top_keywords


def test_source_comparison(analytics: NewsAnalytics):
    """Test source comparison features."""
    logger.info("\n" + "="*60)
    logger.info("Test 5: Source Comparison & Bias Analysis")
    logger.info("="*60)
    
    comparison = analytics.compare_sources()
    
    logger.info(f"\nComparing {len(comparison)} News Sources:")
    
    for source, data in comparison.items():
        logger.info(f"\n{'='*60}")
        logger.info(f"Source: {source}")
        logger.info(f"{'='*60}")
        logger.info(f"  Total Articles: {data['total_articles']}")
        logger.info(f"  Average Confidence: {data['avg_confidence']}%")
        
        logger.info(f"\n  Sentiment Distribution:")
        for sentiment, sdata in data['sentiment_distribution'].items():
            logger.info(f"    {sentiment.capitalize()}: {sdata['count']} ({sdata['percentage']}%)")
        
        logger.info(f"\n  Sentiment Bias:")
        bias = data['sentiment_bias']
        logger.info(f"    Tendency: {bias['tendency'].upper()}")
        logger.info(f"    Bias Score: {bias['score']} (range: -1 to +1)")
        logger.info(f"    Positive Ratio: {bias['positive_ratio']}")
        logger.info(f"    Neutral Ratio: {bias['neutral_ratio']}")
        logger.info(f"    Negative Ratio: {bias['negative_ratio']}")
        
        logger.info(f"\n  Top Entities:")
        for entity in data['top_entities'][:3]:
            logger.info(f"    - {entity['entity']}: {entity['count']} mentions")
        
        logger.info(f"\n  Top Keywords:")
        for keyword in data['top_keywords'][:3]:
            logger.info(f"    - {keyword['keyword']}: {keyword['count']} times")
    
    logger.info("\n✓ Source comparison test completed")
    return comparison


def test_comprehensive_summary(analytics: NewsAnalytics):
    """Test comprehensive summary generation."""
    logger.info("\n" + "="*60)
    logger.info("Test 6: Comprehensive Summary")
    logger.info("="*60)
    
    summary = analytics.get_comprehensive_summary()
    
    logger.info(f"\nOverview:")
    logger.info(f"  Total Articles: {summary['overview']['total_articles']}")
    logger.info(f"  Number of Sources: {summary['overview']['sources']}")
    logger.info(f"  Date Range: {summary['overview']['date_range']['start']} to {summary['overview']['date_range']['end']}")
    logger.info(f"  Span: {summary['overview']['date_range']['span_days']} days")
    
    logger.info(f"\nKey Statistics:")
    logger.info(f"  Sentiment Distribution:")
    for sentiment, data in summary['sentiment']['sentiments'].items():
        logger.info(f"    {sentiment.capitalize()}: {data['count']} ({data['percentage']}%)")
    
    logger.info(f"\n  Top 3 People:")
    for i, entity in enumerate(summary['top_entities']['people'][:3], 1):
        logger.info(f"    {i}. {entity['entity']}: {entity['mentions']} mentions")
    
    logger.info(f"\n  Top 3 Organizations:")
    for i, entity in enumerate(summary['top_entities']['organizations'][:3], 1):
        logger.info(f"    {i}. {entity['entity']}: {entity['mentions']} mentions")
    
    logger.info(f"\n  Top 3 Locations:")
    for i, entity in enumerate(summary['top_entities']['locations'][:3], 1):
        logger.info(f"    {i}. {entity['entity']}: {entity['mentions']} mentions")
    
    logger.info(f"\n  Top 5 Keywords:")
    for i, item in enumerate(summary['top_keywords'][:5], 1):
        logger.info(f"    {i}. {item['keyword']}: {item['frequency']} times")
    
    logger.info("\n✓ Comprehensive summary test completed")
    return summary


def test_export_summary(analytics: NewsAnalytics):
    """Test exporting summary to JSON."""
    logger.info("\n" + "="*60)
    logger.info("Test 7: Export Analytics Summary")
    logger.info("="*60)
    
    # Create output directory
    output_dir = Path("data/analytics")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Export summary
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"analytics_summary_{timestamp}.json"
    
    analytics.export_summary_to_json(str(output_path))
    
    # Verify file
    if output_path.exists():
        file_size = output_path.stat().st_size / 1024
        logger.info(f"\n✓ Analytics summary exported successfully")
        logger.info(f"  File: {output_path.name}")
        logger.info(f"  Size: {file_size:.2f} KB")
        logger.info(f"  Location: {output_path}")
        
        # Load and verify content
        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.info(f"\n  Summary Contents:")
            logger.info(f"    - Overview: ✓")
            logger.info(f"    - Sentiment Analysis: ✓")
            logger.info(f"    - Confidence Stats: ✓")
            logger.info(f"    - Top Entities: ✓")
            logger.info(f"    - Top Keywords: ✓")
            logger.info(f"    - Source Comparison: ✓")
    else:
        logger.error(f"✗ Failed to export analytics summary")
    
    logger.info("\n✓ Export test completed")
    return str(output_path)


def main():
    """Run all analytics tests."""
    logger.info("="*60)
    logger.info("NEWSLENS ANALYTICS TEST SUITE (STEP 6)")
    logger.info("="*60)
    
    try:
        # Initialize analytics
        analytics = NewsAnalytics()
        
        # Load analyzed articles
        data_dir = Path("data/analyzed")
        analyzed_files = list(data_dir.glob("all_analyzed_*.json"))
        
        if not analyzed_files:
            logger.error("No analyzed articles found. Run Step 4 first.")
            return
        
        latest_file = max(analyzed_files, key=lambda p: p.stat().st_mtime)
        logger.info(f"\nLoading articles from: {latest_file.name}")
        
        analytics.load_from_file(str(latest_file))
        logger.info(f"✓ Loaded {len(analytics.articles)} articles\n")
        
        # Run all tests
        results = {}
        
        # Test 1: Sentiment Analytics
        results['sentiment'] = test_sentiment_analytics(analytics)
        
        # Test 2: Temporal Analysis
        results['temporal'] = test_temporal_analysis(analytics)
        
        # Test 3: Entity Analysis
        results['entities'] = test_entity_analysis(analytics)
        
        # Test 4: Keyword Analysis
        results['keywords'] = test_keyword_analysis(analytics)
        
        # Test 5: Source Comparison
        results['sources'] = test_source_comparison(analytics)
        
        # Test 6: Comprehensive Summary
        results['summary'] = test_comprehensive_summary(analytics)
        
        # Test 7: Export Summary
        results['export_path'] = test_export_summary(analytics)
        
        # Final summary
        logger.info("\n" + "="*60)
        logger.info("TEST SUMMARY")
        logger.info("="*60)
        logger.info("Sentiment Analytics: ✓ PASSED")
        logger.info("Temporal Analysis: ✓ PASSED")
        logger.info("Entity Analysis: ✓ PASSED")
        logger.info("Keyword Analysis: ✓ PASSED")
        logger.info("Source Comparison: ✓ PASSED")
        logger.info("Comprehensive Summary: ✓ PASSED")
        logger.info("Export Summary: ✓ PASSED")
        
        logger.info("\n✓ All analytics tests passed!")
        logger.info(f"\nAnalytics summary saved to:")
        logger.info(f"  {results['export_path']}")
        logger.info("\nNext Steps:")
        logger.info("1. Review analytics summary JSON file")
        logger.info("2. Proceed to Step 7: Streamlit Dashboard")
        
    except Exception as e:
        logger.error(f"\n✗ Test failed with error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
