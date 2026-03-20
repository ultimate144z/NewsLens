"""
Root-level pytest configuration and shared fixtures.
"""

import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Skip test files whose top-level imports require unavailable heavy deps.
# These are integration/manual tests; unit tests live in the other files.
# ---------------------------------------------------------------------------
collect_ignore = [
    "tests/test_analysis.py",      # imports torch + transformers at module level
    "tests/test_ingestion.py",     # imports feedparser + live network calls
]

# Ensure project root is on sys.path for all tests
sys.path.insert(0, str(Path(__file__).parent))

from src.analytics.analytics import NewsAnalytics
from src.storage.database import DatabaseManager


# ---------------------------------------------------------------------------
# Sample data used across test fixtures
# ---------------------------------------------------------------------------

SAMPLE_ARTICLES = [
    {
        "title": "Scientists Announce Major Breakthrough",
        "description": "Researchers at MIT have made a revolutionary discovery.",
        "link": "https://example.com/article-1",
        "published": "2025-12-01T10:00:00",
        "source": "BBC News",
        "source_url": "https://bbc.com/rss",
        "sentiment": "positive",
        "sentiment_confidence": 0.91,
        "sentiment_scores": {"positive": 0.91, "neutral": 0.07, "negative": 0.02},
        "entities": {
            "people": [{"text": "Dr. Jane Smith", "label": "PERSON", "start": 0, "end": 14}],
            "organizations": [{"text": "MIT", "label": "ORG", "start": 20, "end": 23}],
            "locations": [{"text": "Boston", "label": "GPE", "start": 30, "end": 36}],
            "dates": [],
            "money": [],
            "events": [],
        },
        "keywords": [
            {"text": "breakthrough", "count": 2},
            {"text": "discovery", "count": 1},
        ],
        "scraped_at": "2025-12-01T09:00:00",
        "preprocessing_timestamp": "2025-12-01T09:30:00",
        "sentiment_timestamp": "2025-12-01T10:00:00",
        "extraction_timestamp": "2025-12-01T10:00:00",
    },
    {
        "title": "Markets Fall Amid Economic Uncertainty",
        "description": "Global markets declined sharply following disappointing data.",
        "link": "https://example.com/article-2",
        "published": "2025-12-01T11:00:00",
        "source": "Reuters",
        "source_url": "https://reuters.com/rss",
        "sentiment": "negative",
        "sentiment_confidence": 0.85,
        "sentiment_scores": {"positive": 0.05, "neutral": 0.10, "negative": 0.85},
        "entities": {
            "people": [],
            "organizations": [{"text": "Federal Reserve", "label": "ORG", "start": 0, "end": 15}],
            "locations": [{"text": "New York", "label": "GPE", "start": 20, "end": 28}],
            "dates": [{"text": "Monday", "label": "DATE", "start": 30, "end": 36}],
            "money": [{"text": "$500 billion", "label": "MONEY", "start": 40, "end": 52}],
            "events": [],
        },
        "keywords": [
            {"text": "markets", "count": 3},
            {"text": "economy", "count": 2},
        ],
        "scraped_at": "2025-12-01T09:00:00",
        "preprocessing_timestamp": "2025-12-01T09:30:00",
        "sentiment_timestamp": "2025-12-01T10:00:00",
        "extraction_timestamp": "2025-12-01T10:00:00",
    },
    {
        "title": "Government Announces New Infrastructure Plan",
        "description": "The administration unveiled a $1 trillion infrastructure package.",
        "link": "https://example.com/article-3",
        "published": "2025-12-02T09:00:00",
        "source": "CNN",
        "source_url": "https://cnn.com/rss",
        "sentiment": "neutral",
        "sentiment_confidence": 0.72,
        "sentiment_scores": {"positive": 0.20, "neutral": 0.72, "negative": 0.08},
        "entities": {
            "people": [{"text": "President Biden", "label": "PERSON", "start": 0, "end": 15}],
            "organizations": [{"text": "Congress", "label": "ORG", "start": 20, "end": 28}],
            "locations": [{"text": "Washington DC", "label": "GPE", "start": 30, "end": 43}],
            "dates": [],
            "money": [{"text": "$1 trillion", "label": "MONEY", "start": 50, "end": 61}],
            "events": [],
        },
        "keywords": [
            {"text": "infrastructure", "count": 4},
            {"text": "government", "count": 2},
        ],
        "scraped_at": "2025-12-02T08:00:00",
        "preprocessing_timestamp": "2025-12-02T08:30:00",
        "sentiment_timestamp": "2025-12-02T09:00:00",
        "extraction_timestamp": "2025-12-02T09:00:00",
    },
]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_articles():
    """Return a list of pre-built article dicts."""
    return SAMPLE_ARTICLES.copy()


@pytest.fixture
def analytics(sample_articles):
    """A NewsAnalytics instance pre-loaded with sample articles."""
    na = NewsAnalytics()
    na.load_articles(sample_articles)
    return na


@pytest.fixture
def db(tmp_path):
    """A temporary DatabaseManager instance, cleaned up after each test."""
    db_path = tmp_path / "test_newslens.db"
    manager = DatabaseManager(str(db_path))
    yield manager
    manager.close()
