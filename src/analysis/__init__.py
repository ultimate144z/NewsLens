"""
NLP Analysis Module
Provides sentiment analysis and entity extraction for news articles
"""

from .sentiment import SentimentAnalyzer
from .entities import EntityExtractor

__all__ = ['SentimentAnalyzer', 'EntityExtractor']
