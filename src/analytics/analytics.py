"""
NewsLens Analytics Module

Provides analytical insights including:
- Sentiment trends over time
- Source comparison and bias analysis
- Entity trend analysis
- Keyword frequency analysis
- Topic distribution
- Temporal patterns
"""

import json
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import logging

# Get logger
logger = logging.getLogger(__name__)


class NewsAnalytics:
    """
    Comprehensive analytics for news articles with sentiment, entities, and trends.
    """
    
    def __init__(self):
        """Initialize the NewsAnalytics class."""
        logger.info("Initializing NewsAnalytics")
        self.articles = []
        self.loaded = False
        
    def load_articles(self, articles: List[Dict[str, Any]]) -> None:
        """
        Load articles for analysis.
        
        Args:
            articles: List of article dictionaries with sentiment and entity data
        """
        self.articles = articles
        self.loaded = True
        logger.info(f"Loaded {len(articles)} articles for analysis")
        
    def load_from_file(self, filepath: str) -> None:
        """
        Load articles from JSON file.
        
        Args:
            filepath: Path to JSON file containing analyzed articles
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.articles = data if isinstance(data, list) else data.get('articles', [])
                self.loaded = True
                logger.info(f"Loaded {len(self.articles)} articles from {filepath}")
        except Exception as e:
            logger.error(f"Error loading articles from {filepath}: {e}")
            raise
            
    def _ensure_loaded(self) -> None:
        """Ensure articles are loaded before analysis."""
        if not self.loaded or not self.articles:
            raise ValueError("No articles loaded. Call load_articles() or load_from_file() first.")
    
    # ===== SENTIMENT ANALYSIS =====
    
    def get_sentiment_distribution(self) -> Dict[str, Any]:
        """
        Get overall sentiment distribution.
        
        Returns:
            Dictionary with sentiment counts and percentages
        """
        self._ensure_loaded()
        
        sentiment_counts = Counter()
        total = len(self.articles)
        
        for article in self.articles:
            sentiment = article.get('sentiment', article.get('sentiment_label', 'unknown'))
            sentiment_counts[sentiment] += 1
            
        distribution = {
            'total_articles': total,
            'sentiments': {}
        }
        
        for sentiment, count in sentiment_counts.items():
            distribution['sentiments'][sentiment] = {
                'count': count,
                'percentage': round((count / total) * 100, 2) if total > 0 else 0
            }
            
        logger.info(f"Sentiment distribution calculated: {len(sentiment_counts)} sentiment types")
        return distribution
    
    def get_sentiment_by_source(self) -> Dict[str, Dict[str, Any]]:
        """
        Get sentiment distribution by news source.
        
        Returns:
            Dictionary mapping source to sentiment distribution
        """
        self._ensure_loaded()
        
        source_sentiments = defaultdict(lambda: Counter())
        source_totals = Counter()
        
        for article in self.articles:
            source = article.get('source', 'Unknown')
            sentiment = article.get('sentiment', article.get('sentiment_label', 'unknown'))
            source_sentiments[source][sentiment] += 1
            source_totals[source] += 1
            
        result = {}
        for source, sentiments in source_sentiments.items():
            total = source_totals[source]
            result[source] = {
                'total_articles': total,
                'sentiments': {}
            }
            
            for sentiment, count in sentiments.items():
                result[source]['sentiments'][sentiment] = {
                    'count': count,
                    'percentage': round((count / total) * 100, 2) if total > 0 else 0
                }
                
        logger.info(f"Sentiment by source calculated for {len(result)} sources")
        return result
    
    def get_sentiment_confidence_stats(self) -> Dict[str, Any]:
        """
        Get statistics on sentiment confidence scores.
        
        Returns:
            Dictionary with confidence statistics
        """
        self._ensure_loaded()
        
        confidences = []
        confidence_by_sentiment = defaultdict(list)
        
        for article in self.articles:
            confidence = article.get('sentiment_confidence', 0)
            sentiment = article.get('sentiment', article.get('sentiment_label', 'unknown'))
            
            confidences.append(confidence)
            confidence_by_sentiment[sentiment].append(confidence)
            
        stats = {
            'overall': self._calculate_stats(confidences),
            'by_sentiment': {}
        }
        
        for sentiment, conf_list in confidence_by_sentiment.items():
            stats['by_sentiment'][sentiment] = self._calculate_stats(conf_list)
            
        logger.info("Sentiment confidence statistics calculated")
        return stats
    
    def _calculate_stats(self, values: List[float]) -> Dict[str, float]:
        """Calculate basic statistics for a list of values."""
        if not values:
            return {'min': 0, 'max': 0, 'avg': 0, 'count': 0}
            
        return {
            'min': round(min(values), 2),
            'max': round(max(values), 2),
            'avg': round(sum(values) / len(values), 2),
            'count': len(values)
        }
    
    # ===== TEMPORAL ANALYSIS =====
    
    def get_sentiment_timeline(self, interval: str = 'day') -> List[Dict[str, Any]]:
        """
        Get sentiment distribution over time.
        
        Args:
            interval: Time interval ('hour', 'day', 'week')
            
        Returns:
            List of time intervals with sentiment counts
        """
        self._ensure_loaded()
        
        timeline = defaultdict(lambda: Counter())
        
        for article in self.articles:
            published = article.get('published', '')
            sentiment = article.get('sentiment', article.get('sentiment_label', 'unknown'))
            
            # Parse date
            try:
                dt = self._parse_date(published)
                if interval == 'hour':
                    key = dt.strftime('%Y-%m-%d %H:00')
                elif interval == 'day':
                    key = dt.strftime('%Y-%m-%d')
                elif interval == 'week':
                    key = dt.strftime('%Y-W%U')
                else:
                    key = dt.strftime('%Y-%m-%d')
                    
                timeline[key][sentiment] += 1
            except:
                continue
                
        # Convert to list and sort
        result = []
        for timestamp, sentiments in sorted(timeline.items()):
            entry = {
                'timestamp': timestamp,
                'total': sum(sentiments.values()),
                'sentiments': dict(sentiments)
            }
            result.append(entry)
            
        logger.info(f"Sentiment timeline created with {len(result)} intervals")
        return result
    
    def get_publication_patterns(self) -> Dict[str, Any]:
        """
        Analyze publication patterns (time of day, day of week).
        
        Returns:
            Dictionary with publication patterns
        """
        self._ensure_loaded()
        
        hours = Counter()
        days = Counter()
        sources_by_hour = defaultdict(lambda: Counter())
        
        for article in self.articles:
            published = article.get('published', '')
            source = article.get('source', 'Unknown')
            
            try:
                dt = self._parse_date(published)
                hour = dt.hour
                day = dt.strftime('%A')
                
                hours[hour] += 1
                days[day] += 1
                sources_by_hour[source][hour] += 1
            except:
                continue
                
        result = {
            'by_hour': dict(hours),
            'by_day': dict(days),
            'by_source_and_hour': {source: dict(hours) for source, hours in sources_by_hour.items()},
            'peak_hour': max(hours.items(), key=lambda x: x[1])[0] if hours else None,
            'peak_day': max(days.items(), key=lambda x: x[1])[0] if days else None
        }
        
        logger.info("Publication patterns analyzed")
        return result
    
    def _parse_date(self, date_string: str) -> datetime:
        """Parse date string in various formats."""
        formats = [
            '%a, %d %b %Y %H:%M:%S %Z',
            '%a, %d %b %Y %H:%M:%S %z',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_string.split('+')[0].strip(), fmt)
            except:
                continue
                
        # If all fail, return current time
        return datetime.now()
    
    # ===== ENTITY ANALYSIS =====
    
    def get_top_entities(self, entity_type: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get most mentioned entities.
        
        Args:
            entity_type: Filter by entity type (PERSON, ORG, GPE, etc.) or None for all
            limit: Maximum number of entities to return
            
        Returns:
            List of entities with mention counts
        """
        self._ensure_loaded()
        
        entity_counts = Counter()
        entity_types = {}
        entity_articles = defaultdict(set)
        
        # Map entity type names to category keys
        type_map = {
            'PERSON': 'people',
            'ORG': 'organizations',
            'GPE': 'locations',
            'LOC': 'locations',
            'DATE': 'dates',
            'MONEY': 'money',
            'EVENT': 'events'
        }
        
        for article in self.articles:
            entities_data = article.get('entities', {})
            article_id = article.get('link', '')
            
            # Handle both dict and list formats
            if isinstance(entities_data, dict):
                # New format: {people: [...], organizations: [...], ...}
                for category, entity_list in entities_data.items():
                    if not isinstance(entity_list, list):
                        continue
                    
                    for entity in entity_list:
                        if isinstance(entity, dict):
                            entity_text = entity.get('text', '')
                            ent_label = entity.get('label', '')
                            
                            # Filter by type if specified
                            if entity_type:
                                if entity_type == 'PERSON' and category != 'people':
                                    continue
                                elif entity_type == 'ORG' and category != 'organizations':
                                    continue
                                elif entity_type == 'GPE' and category != 'locations':
                                    continue
                            
                            if entity_text:
                                entity_counts[entity_text] += 1
                                entity_types[entity_text] = ent_label
                                entity_articles[entity_text].add(article_id)
                        elif isinstance(entity, str):
                            # Simple string format
                            if not entity_type or type_map.get(entity_type, '').lower() == category.lower():
                                entity_counts[entity] += 1
                                entity_types[entity] = category.upper()
                                entity_articles[entity].add(article_id)
                                
            elif isinstance(entities_data, list):
                # Old format: [{text: ..., type: ...}, ...]
                for entity in entities_data:
                    if isinstance(entity, dict):
                        entity_text = entity.get('text', '')
                        ent_type = entity.get('type', '')
                        
                        # Filter by type if specified
                        if entity_type and ent_type != entity_type:
                            continue
                            
                        entity_counts[entity_text] += 1
                        entity_types[entity_text] = ent_type
                        entity_articles[entity_text].add(article_id)
                
        result = []
        for entity, count in entity_counts.most_common(limit):
            result.append({
                'entity': entity,
                'type': entity_types.get(entity, 'UNKNOWN'),
                'mentions': count,
                'articles': len(entity_articles[entity])
            })
            
        logger.info(f"Top {len(result)} entities retrieved" + (f" (type: {entity_type})" if entity_type else ""))
        return result
    
    def get_entity_sentiment(self, entity: str) -> Dict[str, Any]:
        """
        Get sentiment distribution for articles mentioning a specific entity.
        
        Args:
            entity: Entity name to analyze
            
        Returns:
            Dictionary with sentiment distribution for this entity
        """
        self._ensure_loaded()
        
        sentiments = Counter()
        articles_list = []
        
        for article in self.articles:
            entities_data = article.get('entities', {})
            entity_texts = []
            
            # Extract all entity texts from different formats
            if isinstance(entities_data, dict):
                for category, entity_list in entities_data.items():
                    if isinstance(entity_list, list):
                        for ent in entity_list:
                            if isinstance(ent, dict):
                                entity_texts.append(ent.get('text', ''))
                            elif isinstance(ent, str):
                                entity_texts.append(ent)
            elif isinstance(entities_data, list):
                entity_texts = [e.get('text', '') if isinstance(e, dict) else str(e) for e in entities_data]
            
            if entity in entity_texts:
                sentiment = article.get('sentiment', article.get('sentiment_label', 'unknown'))
                sentiments[sentiment] += 1
                articles_list.append({
                    'title': article.get('title', ''),
                    'source': article.get('source', ''),
                    'sentiment': sentiment,
                    'link': article.get('link', '')
                })
                
        total = sum(sentiments.values())
        result = {
            'entity': entity,
            'total_mentions': total,
            'sentiments': {
                sentiment: {
                    'count': count,
                    'percentage': round((count / total) * 100, 2) if total > 0 else 0
                }
                for sentiment, count in sentiments.items()
            },
            'sample_articles': articles_list[:5]
        }
        
        logger.info(f"Entity sentiment analyzed for: {entity}")
        return result
    
    def get_entity_cooccurrence(self, entity: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Find entities that frequently appear with the given entity.
        
        Args:
            entity: Entity name to analyze
            limit: Maximum number of co-occurring entities
            
        Returns:
            List of entities that appear with the target entity
        """
        self._ensure_loaded()
        
        cooccurrence = Counter()
        
        for article in self.articles:
            entities_data = article.get('entities', {})
            entity_texts = []
            
            # Extract all entity texts from different formats
            if isinstance(entities_data, dict):
                for category, entity_list in entities_data.items():
                    if isinstance(entity_list, list):
                        for ent in entity_list:
                            if isinstance(ent, dict):
                                entity_texts.append(ent.get('text', ''))
                            elif isinstance(ent, str):
                                entity_texts.append(ent)
            elif isinstance(entities_data, list):
                entity_texts = [e.get('text', '') if isinstance(e, dict) else str(e) for e in entities_data]
            
            if entity in entity_texts:
                for other_entity in entity_texts:
                    if other_entity != entity:
                        cooccurrence[other_entity] += 1
                        
        result = [
            {'entity': ent, 'cooccurrences': count}
            for ent, count in cooccurrence.most_common(limit)
        ]
        
        logger.info(f"Entity co-occurrence analyzed for: {entity}")
        return result
    
    # ===== KEYWORD ANALYSIS =====
    
    def get_top_keywords(self, limit: int = 30) -> List[Dict[str, Any]]:
        """
        Get most frequent keywords across all articles.
        
        Args:
            limit: Maximum number of keywords to return
            
        Returns:
            List of keywords with frequencies
        """
        self._ensure_loaded()
        
        keyword_counts = Counter()
        
        for article in self.articles:
            keywords = article.get('keywords', [])
            for keyword in keywords:
                # Handle both string and dictionary formats
                if isinstance(keyword, dict):
                    kw_text = keyword.get('text', '')
                    kw_count = keyword.get('count', 1)
                    keyword_counts[kw_text] += kw_count
                elif isinstance(keyword, str):
                    keyword_counts[keyword] += 1
                
        result = [
            {'keyword': kw, 'frequency': count}
            for kw, count in keyword_counts.most_common(limit)
        ]
        
        logger.info(f"Top {len(result)} keywords retrieved")
        return result
    
    def get_keywords_by_sentiment(self, sentiment: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get most frequent keywords in articles with specific sentiment.
        
        Args:
            sentiment: Sentiment label (positive, neutral, negative)
            limit: Maximum number of keywords
            
        Returns:
            List of keywords for this sentiment
        """
        self._ensure_loaded()
        
        keyword_counts = Counter()
        
        for article in self.articles:
            if article.get('sentiment', article.get('sentiment_label', '')) == sentiment:
                keywords = article.get('keywords', [])
                for keyword in keywords:
                    # Handle both string and dictionary formats
                    if isinstance(keyword, dict):
                        kw_text = keyword.get('text', '')
                        kw_count = keyword.get('count', 1)
                        keyword_counts[kw_text] += kw_count
                    elif isinstance(keyword, str):
                        keyword_counts[keyword] += 1
                    
        result = [
            {'keyword': kw, 'frequency': count}
            for kw, count in keyword_counts.most_common(limit)
        ]
        
        logger.info(f"Top {len(result)} keywords retrieved for sentiment: {sentiment}")
        return result
    
    # ===== SOURCE COMPARISON =====
    
    def compare_sources(self) -> Dict[str, Any]:
        """
        Compare different news sources on multiple dimensions.
        
        Returns:
            Comprehensive comparison of news sources
        """
        self._ensure_loaded()
        
        sources = {}
        
        for article in self.articles:
            source = article.get('source', 'Unknown')
            
            if source not in sources:
                sources[source] = {
                    'articles': [],
                    'sentiments': Counter(),
                    'entities': Counter(),
                    'keywords': Counter(),
                    'confidences': []
                }
                
            sources[source]['articles'].append(article)
            sources[source]['sentiments'][article.get('sentiment', article.get('sentiment_label', 'unknown'))] += 1
            sources[source]['confidences'].append(article.get('sentiment_confidence', 0))
            
            # Handle entities in different formats
            entities_data = article.get('entities', {})
            if isinstance(entities_data, dict):
                for category, entity_list in entities_data.items():
                    if isinstance(entity_list, list):
                        for ent in entity_list:
                            if isinstance(ent, dict):
                                sources[source]['entities'][ent.get('text', '')] += 1
                            elif isinstance(ent, str):
                                sources[source]['entities'][ent] += 1
            elif isinstance(entities_data, list):
                for entity in entities_data:
                    if isinstance(entity, dict):
                        sources[source]['entities'][entity.get('text', '')] += 1
                    elif isinstance(entity, str):
                        sources[source]['entities'][entity] += 1
            
            # Handle keywords in different formats
            for keyword in article.get('keywords', []):
                # Handle both string and dictionary formats
                if isinstance(keyword, dict):
                    kw_text = keyword.get('text', '')
                    kw_count = keyword.get('count', 1)
                    sources[source]['keywords'][kw_text] += kw_count
                elif isinstance(keyword, str):
                    sources[source]['keywords'][keyword] += 1
                
        # Build comparison
        comparison = {}
        for source, data in sources.items():
            total = len(data['articles'])
            comparison[source] = {
                'total_articles': total,
                'sentiment_distribution': {
                    sent: {
                        'count': count,
                        'percentage': round((count / total) * 100, 2) if total > 0 else 0
                    }
                    for sent, count in data['sentiments'].items()
                },
                'avg_confidence': round(sum(data['confidences']) / len(data['confidences']), 2) if data['confidences'] else 0,
                'top_entities': [
                    {'entity': ent, 'count': count}
                    for ent, count in data['entities'].most_common(5)
                ],
                'top_keywords': [
                    {'keyword': kw, 'count': count}
                    for kw, count in data['keywords'].most_common(5)
                ],
                'sentiment_bias': self._calculate_sentiment_bias(data['sentiments'], total)
            }
            
        logger.info(f"Source comparison completed for {len(comparison)} sources")
        return comparison
    
    def _calculate_sentiment_bias(self, sentiments: Counter, total: int) -> Dict[str, Any]:
        """Calculate sentiment bias score for a source."""
        if total == 0:
            return {'score': 0, 'tendency': 'neutral'}
            
        positive = sentiments.get('positive', 0)
        negative = sentiments.get('negative', 0)
        neutral = sentiments.get('neutral', 0)
        
        # Bias score: -1 (negative bias) to +1 (positive bias)
        bias_score = (positive - negative) / total
        
        if bias_score > 0.15:
            tendency = 'positive'
        elif bias_score < -0.15:
            tendency = 'negative'
        else:
            tendency = 'neutral'
            
        return {
            'score': round(bias_score, 3),
            'tendency': tendency,
            'positive_ratio': round(positive / total, 3) if total > 0 else 0,
            'negative_ratio': round(negative / total, 3) if total > 0 else 0,
            'neutral_ratio': round(neutral / total, 3) if total > 0 else 0
        }
    
    # ===== SUMMARY STATISTICS =====
    
    def get_comprehensive_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive analytics summary.
        
        Returns:
            Dictionary with all major analytics
        """
        self._ensure_loaded()
        
        summary = {
            'overview': {
                'total_articles': len(self.articles),
                'sources': len(set(a.get('source', 'Unknown') for a in self.articles)),
                'date_range': self._get_date_range(),
            },
            'sentiment': self.get_sentiment_distribution(),
            'sentiment_by_source': self.get_sentiment_by_source(),
            'confidence_stats': self.get_sentiment_confidence_stats(),
            'top_entities': {
                'people': self.get_top_entities('PERSON', 10),
                'organizations': self.get_top_entities('ORG', 10),
                'locations': self.get_top_entities('GPE', 10),
            },
            'top_keywords': self.get_top_keywords(20),
            'source_comparison': self.compare_sources()
        }
        
        logger.info("Comprehensive summary generated")
        return summary
    
    def _get_date_range(self) -> Dict[str, str]:
        """Get the date range of articles."""
        dates = []
        for article in self.articles:
            try:
                dt = self._parse_date(article.get('published', ''))
                dates.append(dt)
            except:
                continue
                
        if not dates:
            return {'start': 'N/A', 'end': 'N/A', 'span_days': 0}
            
        start_date = min(dates)
        end_date = max(dates)
        span = (end_date - start_date).days
        
        return {
            'start': start_date.strftime('%Y-%m-%d'),
            'end': end_date.strftime('%Y-%m-%d'),
            'span_days': span
        }
    
    def export_summary_to_json(self, output_path: str) -> None:
        """
        Export comprehensive summary to JSON file.
        
        Args:
            output_path: Path to save JSON file
        """
        summary = self.get_comprehensive_summary()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Analytics summary exported to {output_path}")


if __name__ == "__main__":
    # Example usage
    print("NewsAnalytics module loaded successfully")
