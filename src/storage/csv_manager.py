"""
Storage Layer - CSV Manager
Export analyzed articles to CSV format for Excel, Tableau, etc.
"""

import os
import csv
import json
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime
from loguru import logger
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import ensure_dir_exists


class CSVManager:
    """
    Manages CSV export of analyzed articles
    """
    
    def __init__(self):
        """Initialize CSV manager"""
        logger.info("Initializing CSVManager")
    
    def export_articles(self, articles: List[Dict], output_path: str,
                       include_entities: bool = True,
                       include_keywords: bool = True) -> bool:
        """
        Export articles to CSV file
        
        Args:
            articles: List of article dictionaries
            output_path: Path to output CSV file
            include_entities: Include entity columns
            include_keywords: Include keyword columns
            
        Returns:
            True if successful
        """
        try:
            # Ensure output directory exists
            ensure_dir_exists(os.path.dirname(output_path))
            
            logger.info(f"Exporting {len(articles)} articles to CSV: {output_path}")
            
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                # Define CSV columns
                fieldnames = [
                    'id',
                    'title',
                    'description',
                    'link',
                    'published',
                    'source',
                    'source_url',
                    'sentiment',
                    'sentiment_confidence',
                    'sentiment_positive',
                    'sentiment_neutral',
                    'sentiment_negative',
                    'token_count',
                    'scraped_at'
                ]
                
                if include_entities:
                    fieldnames.extend([
                        'people',
                        'organizations',
                        'locations',
                        'dates',
                        'money',
                        'events',
                        'entity_count'
                    ])
                
                if include_keywords:
                    fieldnames.extend(['keywords', 'top_keywords'])
                
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                # Write each article
                for i, article in enumerate(articles):
                    row = self._article_to_row(article, include_entities, include_keywords)
                    writer.writerow(row)
                    
                    if (i + 1) % 50 == 0:
                        logger.info(f"Exported {i + 1}/{len(articles)} articles")
                
            logger.success(f"Successfully exported {len(articles)} articles to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return False
    
    def _article_to_row(self, article: Dict, include_entities: bool, include_keywords: bool) -> Dict:
        """Convert article dictionary to CSV row"""
        sentiment_scores = article.get('sentiment_scores', {})
        
        row = {
            'id': article.get('id', ''),
            'title': article.get('title', ''),
            'description': article.get('description', ''),
            'link': article.get('link', ''),
            'published': article.get('published', ''),
            'source': article.get('source', ''),
            'source_url': article.get('source_url', ''),
            'sentiment': article.get('sentiment', ''),
            'sentiment_confidence': article.get('sentiment_confidence', 0),
            'sentiment_positive': sentiment_scores.get('positive', 0),
            'sentiment_neutral': sentiment_scores.get('neutral', 0),
            'sentiment_negative': sentiment_scores.get('negative', 0),
            'token_count': article.get('full_text_token_count', 0),
            'scraped_at': article.get('scraped_at', '')
        }
        
        if include_entities:
            entities = article.get('entities', {})
            entity_counts = article.get('entity_counts', {})
            
            # Join entity texts with semicolons
            row['people'] = '; '.join([e['text'] for e in entities.get('people', [])])
            row['organizations'] = '; '.join([e['text'] for e in entities.get('organizations', [])])
            row['locations'] = '; '.join([e['text'] for e in entities.get('locations', [])])
            row['dates'] = '; '.join([e['text'] for e in entities.get('dates', [])])
            row['money'] = '; '.join([e['text'] for e in entities.get('money', [])])
            row['events'] = '; '.join([e['text'] for e in entities.get('events', [])])
            row['entity_count'] = sum(entity_counts.values()) if entity_counts else 0
        
        if include_keywords:
            keywords = article.get('keywords', [])
            row['keywords'] = '; '.join([kw['text'] for kw in keywords])
            row['top_keywords'] = '; '.join([kw['text'] for kw in keywords[:5]])
        
        return row
    
    def export_sentiment_summary(self, articles: List[Dict], output_path: str) -> bool:
        """
        Export sentiment summary by source
        
        Args:
            articles: List of article dictionaries
            output_path: Path to output CSV file
            
        Returns:
            True if successful
        """
        try:
            ensure_dir_exists(os.path.dirname(output_path))
            
            logger.info(f"Exporting sentiment summary to: {output_path}")
            
            # Aggregate by source
            source_stats = {}
            for article in articles:
                source = article.get('source', 'Unknown')
                sentiment = article.get('sentiment', 'unknown')
                
                if source not in source_stats:
                    source_stats[source] = {
                        'total': 0,
                        'positive': 0,
                        'neutral': 0,
                        'negative': 0,
                        'avg_confidence': []
                    }
                
                source_stats[source]['total'] += 1
                source_stats[source][sentiment] = source_stats[source].get(sentiment, 0) + 1
                
                confidence = article.get('sentiment_confidence')
                if confidence:
                    source_stats[source]['avg_confidence'].append(confidence)
            
            # Write summary
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                fieldnames = [
                    'source', 'total_articles',
                    'positive', 'neutral', 'negative',
                    'positive_pct', 'neutral_pct', 'negative_pct',
                    'avg_confidence'
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for source, stats in sorted(source_stats.items()):
                    total = stats['total']
                    avg_conf = sum(stats['avg_confidence']) / len(stats['avg_confidence']) if stats['avg_confidence'] else 0
                    
                    writer.writerow({
                        'source': source,
                        'total_articles': total,
                        'positive': stats['positive'],
                        'neutral': stats['neutral'],
                        'negative': stats['negative'],
                        'positive_pct': f"{stats['positive'] / total * 100:.1f}%",
                        'neutral_pct': f"{stats['neutral'] / total * 100:.1f}%",
                        'negative_pct': f"{stats['negative'] / total * 100:.1f}%",
                        'avg_confidence': f"{avg_conf:.2%}"
                    })
            
            logger.success(f"Sentiment summary exported to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting sentiment summary: {e}")
            return False
    
    def export_entity_summary(self, articles: List[Dict], output_path: str, 
                             entity_type: str = 'people', top_n: int = 50) -> bool:
        """
        Export top entities of a specific type
        
        Args:
            articles: List of article dictionaries
            output_path: Path to output CSV file
            entity_type: Type of entity to export
            top_n: Number of top entities to include
            
        Returns:
            True if successful
        """
        try:
            ensure_dir_exists(os.path.dirname(output_path))
            
            logger.info(f"Exporting top {top_n} {entity_type} to: {output_path}")
            
            # Count entity occurrences
            entity_counts = {}
            entity_sources = {}
            
            for article in articles:
                source = article.get('source', 'Unknown')
                entities = article.get('entities', {}).get(entity_type, [])
                
                for entity in entities:
                    entity_text = entity['text']
                    
                    if entity_text not in entity_counts:
                        entity_counts[entity_text] = 0
                        entity_sources[entity_text] = set()
                    
                    entity_counts[entity_text] += 1
                    entity_sources[entity_text].add(source)
            
            # Get top N
            top_entities = sorted(entity_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
            
            # Write to CSV
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['rank', 'entity', 'count', 'sources', 'source_count']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for rank, (entity, count) in enumerate(top_entities, 1):
                    sources = entity_sources[entity]
                    writer.writerow({
                        'rank': rank,
                        'entity': entity,
                        'count': count,
                        'sources': '; '.join(sorted(sources)),
                        'source_count': len(sources)
                    })
            
            logger.success(f"Entity summary exported to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting entity summary: {e}")
            return False
