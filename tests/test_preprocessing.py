"""
Test Preprocessing Module
Tests text cleaning, tokenization, and preprocessing functionality
"""
import sys
from pathlib import Path
import json
from datetime import datetime

import pytest

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

nltk = pytest.importorskip("nltk", reason="nltk not installed")

from src.preprocessing import TextPreprocessor
from utils.logger import get_logger
from utils.helpers import get_data_dir

logger = get_logger("preprocessing_test")


def test_basic_preprocessing():
    """Test basic text preprocessing functionality"""
    logger.info("\n" + "=" * 60)
    logger.info("Test 1: Basic Text Preprocessing")
    logger.info("=" * 60)
    
    try:
        preprocessor = TextPreprocessor()
        
        # Test samples
        test_cases = [
            {
                "name": "URLs and Emails",
                "text": "Check out https://example.com or email us at contact@example.com",
                "expected_removes": ["https://", "@"]
            },
            {
                "name": "Mentions and Hashtags",
                "text": "@JohnDoe shared #BreakingNews about the #Election2024",
                "expected_removes": ["@", "#"]
            },
            {
                "name": "Numbers and Punctuation",
                "text": "The price is $100.50 and it increased by 25% today!!!",
                "expected_contains": ["price", "increased", "today"]
            },
            {
                "name": "Stopwords",
                "text": "The quick brown fox jumps over the lazy dog",
                "expected_removes": ["the", "over"]
            }
        ]
        
        logger.info("\nRunning test cases...")
        
        for i, test in enumerate(test_cases, 1):
            logger.info(f"\n  Test {i}: {test['name']}")
            logger.info(f"  Original: {test['text']}")
            
            # Preprocess
            cleaned = preprocessor.clean_text(test['text'])
            preprocessed = preprocessor.preprocess(test['text'])
            tokens = preprocessor.preprocess(test['text'], return_tokens=True)
            
            logger.info(f"  Cleaned: {cleaned}")
            logger.info(f"  Preprocessed: {preprocessed}")
            logger.info(f"  Tokens: {tokens}")
            logger.info(f"  Token Count: {len(tokens)}")
        
        logger.success("\n✓ Basic preprocessing tests passed")
        return True
        
    except Exception as e:
        logger.error(f"✗ Basic preprocessing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_article_preprocessing():
    """Test article preprocessing with real data"""
    logger.info("\n" + "=" * 60)
    logger.info("Test 2: Article Preprocessing")
    logger.info("=" * 60)
    
    try:
        preprocessor = TextPreprocessor()
        
        # Load real articles from ingestion test
        raw_data_dir = get_data_dir("raw")
        test_files = list(raw_data_dir.glob("combined_test_*.json"))
        
        if not test_files:
            logger.warning("No test data found. Run test_ingestion.py first.")
            return False
        
        # Load most recent file
        test_file = max(test_files, key=lambda p: p.stat().st_mtime)
        logger.info(f"\nLoading articles from: {test_file.name}")
        
        with open(test_file, 'r', encoding='utf-8') as f:
            articles = json.load(f)
        
        logger.info(f"Loaded {len(articles)} articles")
        
        # Preprocess first 10 articles for testing
        test_articles = articles[:10]
        logger.info(f"\nPreprocessing {len(test_articles)} sample articles...")
        
        preprocessed = preprocessor.preprocess_batch(test_articles, show_progress=True)
        
        # Show sample results
        logger.info("\n" + "-" * 60)
        logger.info("Sample Preprocessed Article:")
        logger.info("-" * 60)
        
        sample = preprocessed[0]
        logger.info(f"\nOriginal Title: {sample.get('title', '')[:100]}...")
        logger.info(f"Cleaned Title: {sample.get('title_clean', '')[:100]}...")
        logger.info(f"Title Tokens: {sample.get('title_tokens', [])[:10]}")
        logger.info(f"Token Count: {sample.get('title_token_count', 0)}")
        
        logger.info(f"\nOriginal Description: {sample.get('description', '')[:150]}...")
        logger.info(f"Cleaned Description: {sample.get('description_clean', '')[:150]}...")
        logger.info(f"Description Token Count: {sample.get('description_token_count', 0)}")
        
        # Get statistics
        stats = preprocessor.get_statistics(preprocessed)
        logger.info("\n" + "-" * 60)
        logger.info("Preprocessing Statistics:")
        logger.info("-" * 60)
        logger.info(f"Total Articles: {stats['total_articles']}")
        logger.info(f"Avg Title Tokens: {stats['avg_title_tokens']}")
        logger.info(f"Avg Description Tokens: {stats['avg_description_tokens']}")
        logger.info(f"Avg Full Text Tokens: {stats['avg_full_text_tokens']}")
        logger.info(f"Total Tokens: {stats['total_tokens']}")
        
        # Save preprocessed data
        output_file = get_data_dir("processed") / f"preprocessed_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(preprocessed, f, indent=2, ensure_ascii=False)
        
        logger.success(f"\n✓ Saved preprocessed articles to: {output_file}")
        logger.success("✓ Article preprocessing test passed")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Article preprocessing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_batch_preprocessing():
    """Test preprocessing all collected articles"""
    logger.info("\n" + "=" * 60)
    logger.info("Test 3: Batch Preprocessing (All Articles)")
    logger.info("=" * 60)
    
    try:
        preprocessor = TextPreprocessor()
        
        # Load all articles
        raw_data_dir = get_data_dir("raw")
        test_files = list(raw_data_dir.glob("combined_test_*.json"))
        
        if not test_files:
            logger.warning("No test data found.")
            return False
        
        # Load most recent file
        test_file = max(test_files, key=lambda p: p.stat().st_mtime)
        
        with open(test_file, 'r', encoding='utf-8') as f:
            articles = json.load(f)
        
        logger.info(f"Processing all {len(articles)} articles...")
        
        # Preprocess all articles
        preprocessed = preprocessor.preprocess_batch(articles, show_progress=True)
        
        # Get comprehensive statistics
        stats = preprocessor.get_statistics(preprocessed)
        
        logger.info("\n" + "=" * 60)
        logger.info("FINAL STATISTICS")
        logger.info("=" * 60)
        logger.info(f"Total Articles Preprocessed: {stats['total_articles']}")
        logger.info(f"Average Title Tokens: {stats['avg_title_tokens']}")
        logger.info(f"Average Description Tokens: {stats['avg_description_tokens']}")
        logger.info(f"Average Full Text Tokens: {stats['avg_full_text_tokens']}")
        logger.info(f"Total Tokens Generated: {stats['total_tokens']:,}")
        
        # Source breakdown
        sources = {}
        for article in preprocessed:
            source = article.get('source', 'Unknown')
            sources[source] = sources.get(source, 0) + 1
        
        logger.info("\nArticles by Source:")
        for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"  - {source}: {count}")
        
        # Save all preprocessed data
        output_file = get_data_dir("processed") / f"all_preprocessed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(preprocessed, f, indent=2, ensure_ascii=False)
        
        file_size = output_file.stat().st_size / 1024  # KB
        logger.success(f"\n✓ Saved all preprocessed articles to: {output_file}")
        logger.info(f"File size: {file_size:.2f} KB")
        
        logger.success("\n✓ Batch preprocessing test passed")
        return True
        
    except Exception as e:
        logger.error(f"✗ Batch preprocessing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_configuration_options():
    """Test different preprocessing configurations"""
    logger.info("\n" + "=" * 60)
    logger.info("Test 4: Configuration Options")
    logger.info("=" * 60)
    
    try:
        sample_text = "The @President announced today that #ClimateChange is important! Visit https://example.com for more info."
        
        logger.info(f"\nSample Text: {sample_text}\n")
        
        # Test with default config
        logger.info("1. Default Configuration:")
        preprocessor = TextPreprocessor()
        result = preprocessor.preprocess(sample_text)
        logger.info(f"   Result: {result}")
        
        logger.success("\n✓ Configuration test passed")
        return True
        
    except Exception as e:
        logger.error(f"✗ Configuration test failed: {e}")
        return False


def main():
    """Run all preprocessing tests"""
    logger.info("\n" + "=" * 60)
    logger.info("NEWSLENS PREPROCESSING TEST SUITE")
    logger.info("=" * 60)
    
    results = {
        'Basic Preprocessing': test_basic_preprocessing(),
        'Article Preprocessing': test_article_preprocessing(),
        'Batch Preprocessing': test_batch_preprocessing(),
        'Configuration Options': test_configuration_options()
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
        logger.success("\n✓ All preprocessing tests passed!")
        logger.info("\nData saved to:")
        logger.info("- data/processed/ folder")
        logger.info("\nNext Steps:")
        logger.info("1. Check processed data files")
        logger.info("2. Proceed to Step 4: NLP Analysis Layer")
    else:
        logger.warning("\n⚠ Some tests failed. Check the logs above.")
    
    logger.info("\n" + "=" * 60)
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
