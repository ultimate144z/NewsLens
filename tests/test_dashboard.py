"""
Test Dashboard - Verify all pages load correctly
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all dashboard modules can be imported."""
    print("Testing imports...")
    try:
        # Test utility imports
        from app.utils import (
            load_analytics_summary,
            load_articles,
            format_large_number,
            get_sentiment_color,
            get_bias_color,
            create_metric_card,
            format_percentage
        )
        print("✓ Utils module imported successfully")
        
        # Test data loading
        data = load_analytics_summary()
        articles = load_articles()
        
        if data:
            print(f"✓ Analytics data loaded: {len(data)} top-level keys")
        else:
            print("✗ Failed to load analytics data")
            return False
        
        if articles:
            print(f"✓ Articles loaded: {len(articles)} articles")
        else:
            print("✗ Failed to load articles")
            return False
        
        # Test utility functions
        assert format_large_number(1500) == "1.5K"
        assert format_percentage(0.756, 1) == "75.6%"
        assert get_sentiment_color("positive") == "#22c55e"
        print("✓ Utility functions work correctly")
        
        return True
        
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False


def test_data_structure():
    """Test that data has expected structure."""
    print("\nTesting data structure...")
    try:
        from app.utils import load_analytics_summary, load_articles
        
        data = load_analytics_summary()
        
        # Check for required keys
        required_keys = ['overview', 'sentiment', 'source_comparison', 'top_entities', 'top_keywords']
        for key in required_keys:
            if key in data:
                print(f"✓ Found '{key}' in analytics data")
            else:
                print(f"✗ Missing '{key}' in analytics data")
                return False
        
        # Check overview
        overview = data.get('overview', {})
        assert 'total_articles' in overview
        assert 'total_sources' in overview
        print(f"✓ Overview contains {overview['total_articles']} articles from {overview['total_sources']} sources")
        
        # Check sentiment
        sentiment = data.get('sentiment', {})
        assert 'distribution' in sentiment
        print(f"✓ Sentiment distribution found")
        
        # Check source comparison
        sources = data.get('source_comparison', {})
        assert len(sources) > 0
        print(f"✓ Found {len(sources)} sources for comparison")
        
        return True
        
    except Exception as e:
        print(f"✗ Data structure error: {e}")
        return False


def test_pages_exist():
    """Test that all page files exist."""
    print("\nTesting page files...")
    pages_dir = Path('app/pages')
    
    required_pages = [
        '1_Overview.py',
        '2_Sentiment.py',
        '3_Sources.py'
    ]
    
    all_exist = True
    for page in required_pages:
        page_path = pages_dir / page
        if page_path.exists():
            size = page_path.stat().st_size / 1024
            print(f"✓ {page} exists ({size:.2f} KB)")
        else:
            print(f"✗ {page} not found")
            all_exist = False
    
    return all_exist


def main():
    """Run all tests."""
    print("=" * 60)
    print("NewsLens Dashboard - Test Suite")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Data Structure", test_data_structure),
        ("Page Files", test_pages_exist)
    ]
    
    results = []
    for name, test_func in tests:
        result = test_func()
        results.append((name, result))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {name}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("✓ All tests PASSED! Dashboard is ready to use.")
        print("\nTo launch dashboard:")
        print("  streamlit run app\\dashboard.py")
        print("\nDashboard will be available at:")
        print("  http://localhost:8501")
        return 0
    else:
        print("✗ Some tests FAILED. Please review errors above.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
