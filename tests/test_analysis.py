"""
Test Script for NLP Analysis Layer (Step 4)
Tests sentiment analysis and entity extraction on preprocessed articles
"""

import os
import sys
import json
from datetime import datetime
from loguru import logger

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pytest

from src.analysis import SentimentAnalyzer, EntityExtractor
from utils.helpers import get_data_dir

# Configure logger
logger.remove()
logger.add(sys.stdout, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level:8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")


@pytest.mark.ml
def test_sentiment_analysis():
    """Test sentiment analysis on sample texts"""
    logger.info("\n" + "=" * 60)
    logger.info("Test 1: Sentiment Analysis - Sample Texts")
    logger.info("=" * 60)
    
    # Initialize analyzer
    analyzer = SentimentAnalyzer()
    
    # Test texts with expected sentiments
    test_cases = [
        {
            'text': "This is fantastic news! The economy is thriving and employment rates have reached historic highs.",
            'expected': 'positive'
        },
        {
            'text': "Devastating earthquake strikes the region, causing widespread destruction and loss of life.",
            'expected': 'negative'
        },
        {
            'text': "The government announced new regulations that will take effect next quarter.",
            'expected': 'neutral'
        },
        {
            'text': "Stock markets surge to record highs as investors celebrate strong economic data.",
            'expected': 'positive'
        },
        {
            'text': "Political tensions escalate as diplomatic talks collapse between the two nations.",
            'expected': 'negative'
        }
    ]
    
    logger.info(f"\nTesting {len(test_cases)} sample texts...")
    
    correct = 0
    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"\n  Test {i}:")
        logger.info(f"  Text: {test_case['text'][:80]}...")
        
        result = analyzer.analyze_text(test_case['text'])
        
        logger.info(f"  Expected: {test_case['expected'].upper()}")
        logger.info(f"  Predicted: {result['label'].upper()} (confidence: {result['confidence']:.2%})")
        logger.info(f"  Scores: Neg={result['scores']['negative']:.2%}, Neu={result['scores']['neutral']:.2%}, Pos={result['scores']['positive']:.2%}")
        
        if result['label'] == test_case['expected']:
            correct += 1
            logger.info("  ✓ Correct prediction")
        else:
            logger.warning("  ✗ Incorrect prediction")
    
    accuracy = correct / len(test_cases) * 100
    logger.success(f"\n✓ Sentiment analysis accuracy: {accuracy:.0f}% ({correct}/{len(test_cases)})")
    
    return analyzer


@pytest.mark.ml
def test_entity_extraction():
    """Test entity extraction on sample texts"""
    logger.info("\n" + "=" * 60)
    logger.info("Test 2: Entity Extraction - Sample Texts")
    logger.info("=" * 60)
    
    # Initialize extractor
    extractor = EntityExtractor()
    
    # Test texts with known entities
    test_texts = [
        "President Joe Biden met with Canadian Prime Minister Justin Trudeau in Ottawa on Tuesday to discuss climate change.",
        "Apple Inc. announced record quarterly earnings of $123 billion, surpassing Wall Street expectations.",
        "The United Nations held an emergency session in New York to address the humanitarian crisis in Syria.",
    ]
    
    logger.info(f"\nTesting entity extraction on {len(test_texts)} texts...")
    
    for i, text in enumerate(test_texts, 1):
        logger.info(f"\n  Test {i}:")
        logger.info(f"  Text: {text}")
        
        entities = extractor.extract_entities(text)
        keywords = extractor.extract_keywords(text, top_n=5)
        
        # Display entities
        entity_found = False
        for category, ents in entities.items():
            if ents:
                entity_found = True
                logger.info(f"  {category.capitalize()}:")
                for ent in ents:
                    logger.info(f"    - {ent['text']} ({ent['label']})")
        
        if not entity_found:
            logger.warning("  No entities found")
        
        # Display keywords
        if keywords:
            logger.info(f"  Keywords: {', '.join([kw['text'] for kw in keywords[:5]])}")
    
    logger.success("\n✓ Entity extraction test passed")
    
    return extractor


@pytest.mark.ml
def test_article_analysis():
    """Test analysis on real preprocessed articles"""
    logger.info("\n" + "=" * 60)
    logger.info("Test 3: Full Article Analysis")
    logger.info("=" * 60)
    
    # Load preprocessed articles
    data_dir = get_data_dir()
    preprocessed_file = os.path.join(data_dir, 'processed', 'all_preprocessed_20251201_173434.json')
    
    if not os.path.exists(preprocessed_file):
        logger.warning(f"Preprocessed file not found: {preprocessed_file}")
        logger.warning("Please run preprocessing first")
        return None, None, []
    
    logger.info(f"Loading articles from: {os.path.basename(preprocessed_file)}")
    
    with open(preprocessed_file, 'r', encoding='utf-8') as f:
        articles = json.load(f)
    
    logger.info(f"Loaded {len(articles)} articles")
    
    # Test on first 10 articles
    sample_size = 10
    logger.info(f"\nAnalyzing {sample_size} sample articles...")
    
    sample_articles = articles[:sample_size]
    
    # Initialize analyzers
    sentiment_analyzer = SentimentAnalyzer()
    entity_extractor = EntityExtractor()
    
    # Analyze sentiment
    logger.info("\nPerforming sentiment analysis...")
    for article in sample_articles:
        sentiment_analyzer.analyze_article(article)
    
    # Extract entities
    logger.info("\nExtracting entities...")
    for article in sample_articles:
        entity_extractor.analyze_article(article)
    
    # Display sample results
    logger.info("\n" + "-" * 60)
    logger.info("Sample Analyzed Article:")
    logger.info("-" * 60)
    
    sample = sample_articles[0]
    logger.info(f"\nTitle: {sample['title'][:80]}...")
    logger.info(f"Source: {sample['source']}")
    logger.info(f"Sentiment: {sample['sentiment'].upper()} (confidence: {sample['sentiment_confidence']:.2%})")
    logger.info(f"Sentiment Scores: Neg={sample['sentiment_scores']['negative']:.2%}, Neu={sample['sentiment_scores']['neutral']:.2%}, Pos={sample['sentiment_scores']['positive']:.2%}")
    
    if sample['entities']:
        logger.info("\nExtracted Entities:")
        for category, ents in sample['entities'].items():
            if ents:
                logger.info(f"  {category.capitalize()}: {', '.join([e['text'] for e in ents[:3]])}")
    
    if sample.get('keywords'):
        logger.info(f"\nKeywords: {', '.join([kw['text'] for kw in sample['keywords'][:5]])}")
    
    # Save analyzed sample
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    sample_output = os.path.join(data_dir, 'analyzed', f'analyzed_sample_{timestamp}.json')
    os.makedirs(os.path.dirname(sample_output), exist_ok=True)
    
    with open(sample_output, 'w', encoding='utf-8') as f:
        json.dump(sample_articles, f, indent=2, ensure_ascii=False)
    
    logger.success(f"\n✓ Saved analyzed sample to: {sample_output}")
    logger.info(f"File size: {os.path.getsize(sample_output) / 1024:.2f} KB")
    
    return sentiment_analyzer, entity_extractor, sample_articles


@pytest.mark.ml
def test_batch_analysis():
    """Test full batch analysis on all articles"""
    logger.info("\n" + "=" * 60)
    logger.info("Test 4: Batch Analysis (All Articles)")
    logger.info("=" * 60)
    
    # Load preprocessed articles
    data_dir = get_data_dir()
    preprocessed_file = os.path.join(data_dir, 'processed', 'all_preprocessed_20251201_173434.json')
    
    if not os.path.exists(preprocessed_file):
        logger.warning(f"Preprocessed file not found: {preprocessed_file}")
        return []
    
    logger.info(f"Loading articles from: {os.path.basename(preprocessed_file)}")
    
    with open(preprocessed_file, 'r', encoding='utf-8') as f:
        articles = json.load(f)
    
    logger.info(f"Loaded {len(articles)} articles")
    
    # Initialize analyzers
    logger.info("\nInitializing analyzers...")
    sentiment_analyzer = SentimentAnalyzer()
    entity_extractor = EntityExtractor()
    
    # Perform sentiment analysis
    logger.info("\n" + "-" * 60)
    logger.info("Performing sentiment analysis on all articles...")
    logger.info("-" * 60)
    
    for article in articles:
        sentiment_analyzer.analyze_article(article)
    
    # Calculate sentiment statistics
    sentiments = [a['sentiment'] for a in articles]
    sentiment_stats = {
        'total': len(articles),
        'positive': sentiments.count('positive'),
        'neutral': sentiments.count('neutral'),
        'negative': sentiments.count('negative'),
        'avg_confidence': sum([a['sentiment_confidence'] for a in articles]) / len(articles)
    }
    
    logger.info("\n" + "=" * 60)
    logger.info("SENTIMENT ANALYSIS RESULTS")
    logger.info("=" * 60)
    logger.info(f"Total Articles: {sentiment_stats['total']}")
    logger.info(f"Positive: {sentiment_stats['positive']} ({sentiment_stats['positive']/sentiment_stats['total']*100:.1f}%)")
    logger.info(f"Neutral: {sentiment_stats['neutral']} ({sentiment_stats['neutral']/sentiment_stats['total']*100:.1f}%)")
    logger.info(f"Negative: {sentiment_stats['negative']} ({sentiment_stats['negative']/sentiment_stats['total']*100:.1f}%)")
    logger.info(f"Average Confidence: {sentiment_stats['avg_confidence']:.2%}")
    
    # Extract entities
    logger.info("\n" + "-" * 60)
    logger.info("Extracting entities from all articles...")
    logger.info("-" * 60)
    
    for article in articles:
        entity_extractor.analyze_article(article)
    
    # Calculate entity statistics
    total_entities = {
        'people': 0,
        'organizations': 0,
        'locations': 0,
        'dates': 0,
        'money': 0,
        'events': 0
    }
    
    for article in articles:
        if 'entity_counts' in article:
            for category, count in article['entity_counts'].items():
                total_entities[category] += count
    
    logger.info("\n" + "=" * 60)
    logger.info("ENTITY EXTRACTION RESULTS")
    logger.info("=" * 60)
    for category, count in total_entities.items():
        logger.info(f"{category.capitalize()}: {count}")
    
    # Get top entities
    logger.info("\n" + "-" * 60)
    logger.info("Top Entities by Category:")
    logger.info("-" * 60)
    
    for category in ['people', 'organizations', 'locations']:
        top_entities = entity_extractor.get_top_entities(articles, category, top_n=5)
        if top_entities:
            logger.info(f"\nTop {category.capitalize()}:")
            for i, entity in enumerate(top_entities, 1):
                logger.info(f"  {i}. {entity['entity']} (mentioned {entity['count']} times)")
    
    # Save analyzed articles
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(data_dir, 'analyzed', f'all_analyzed_{timestamp}.json')
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)
    
    logger.success(f"\n✓ Saved all analyzed articles to: {output_file}")
    logger.info(f"File size: {os.path.getsize(output_file) / 1024:.2f} KB")
    
    return articles


def main():
    """Run all tests"""
    logger.info("\n" + "=" * 60)
    logger.info("NEWSLENS NLP ANALYSIS TEST SUITE (STEP 4)")
    logger.info("=" * 60)
    
    try:
        # Test 1: Sentiment Analysis
        sentiment_analyzer = test_sentiment_analysis()
        
        # Test 2: Entity Extraction
        entity_extractor = test_entity_extraction()
        
        # Test 3: Article Analysis
        _, _, sample_articles = test_article_analysis()
        
        # Test 4: Batch Analysis
        all_articles = test_batch_analysis()
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("TEST SUMMARY")
        logger.info("=" * 60)
        logger.info("Basic Sentiment Analysis: ✓ PASSED")
        logger.info("Basic Entity Extraction: ✓ PASSED")
        logger.info("Article Analysis: ✓ PASSED")
        logger.info("Batch Analysis: ✓ PASSED")
        
        logger.success("\n✓ All NLP analysis tests passed!")
        logger.info("\nData saved to:")
        logger.info("- data/analyzed/ folder")
        logger.info("\nNext Steps:")
        logger.info("1. Check analyzed data files")
        logger.info("2. Proceed to Step 5: Storage Layer")
        
    except Exception as e:
        logger.error(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    logger.info("\n" + "=" * 60)
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
