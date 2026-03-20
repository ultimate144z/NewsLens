"""
Storage Layer - Database Manager
SQLite database for storing and querying analyzed news articles
"""

import os
import sqlite3
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path
from loguru import logger
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import get_project_root, ensure_dir_exists


class DatabaseManager:
    """
    Manages SQLite database for news articles with sentiment and entity data
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database manager
        
        Args:
            db_path: Path to SQLite database file (default: data/newslens.db)
        """
        if db_path is None:
            db_dir = get_project_root() / "data"
            ensure_dir_exists(db_dir)
            db_path = db_dir / "newslens.db"
        
        self.db_path = Path(db_path)
        self.conn = None
        self.cursor = None
        
        logger.info(f"Initializing DatabaseManager with database: {self.db_path}")
        
        # Create connection
        self._connect()
        
        # Create tables if they don't exist
        self._create_tables()
        
        logger.success("DatabaseManager initialized successfully")
    
    def _connect(self):
        """Create database connection"""
        try:
            self.conn = sqlite3.connect(str(self.db_path))
            self.conn.row_factory = sqlite3.Row  # Enable column access by name
            self.cursor = self.conn.cursor()
            logger.info(f"Connected to database: {self.db_path}")
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            raise
    
    def _create_tables(self):
        """Create database schema"""
        try:
            # Articles table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    link TEXT UNIQUE NOT NULL,
                    published TEXT,
                    source TEXT NOT NULL,
                    source_url TEXT,
                    
                    title_cleaned TEXT,
                    description_cleaned TEXT,
                    full_text_cleaned TEXT,
                    full_text_token_count INTEGER,
                    
                    sentiment TEXT,
                    sentiment_confidence REAL,
                    sentiment_score_positive REAL,
                    sentiment_score_neutral REAL,
                    sentiment_score_negative REAL,
                    
                    scraped_at TEXT,
                    preprocessing_timestamp TEXT,
                    sentiment_timestamp TEXT,
                    extraction_timestamp TEXT,
                    
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Entities table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS entities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER NOT NULL,
                    entity_text TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    entity_label TEXT NOT NULL,
                    start_pos INTEGER,
                    end_pos INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (article_id) REFERENCES articles (id) ON DELETE CASCADE
                )
            """)
            
            # Keywords table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS keywords (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER NOT NULL,
                    keyword TEXT NOT NULL,
                    count INTEGER DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (article_id) REFERENCES articles (id) ON DELETE CASCADE
                )
            """)
            
            # Create indexes for better query performance
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_articles_sentiment 
                ON articles(sentiment)
            """)
            
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_articles_source 
                ON articles(source)
            """)
            
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_articles_published 
                ON articles(published)
            """)
            
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_entities_article_id 
                ON entities(article_id)
            """)
            
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_entities_type 
                ON entities(entity_type)
            """)
            
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_keywords_article_id 
                ON keywords(article_id)
            """)
            
            self.conn.commit()
            logger.info("Database schema created successfully")
            
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise
    
    def insert_article(self, article: Dict) -> Optional[int]:
        """
        Insert a single article into the database
        
        Args:
            article: Article dictionary with all fields
            
        Returns:
            Article ID if successful, None otherwise
        """
        try:
            # Prepare article data
            sentiment_scores = article.get('sentiment_scores', {})
            
            self.cursor.execute("""
                INSERT INTO articles (
                    title, description, link, published, source, source_url,
                    title_cleaned, description_cleaned, full_text_cleaned, full_text_token_count,
                    sentiment, sentiment_confidence,
                    sentiment_score_positive, sentiment_score_neutral, sentiment_score_negative,
                    scraped_at, preprocessing_timestamp, sentiment_timestamp, extraction_timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                article.get('title'),
                article.get('description'),
                article.get('link'),
                article.get('published'),
                article.get('source'),
                article.get('source_url'),
                article.get('title_cleaned'),
                article.get('description_cleaned'),
                article.get('full_text_cleaned'),
                article.get('full_text_token_count'),
                article.get('sentiment'),
                article.get('sentiment_confidence'),
                sentiment_scores.get('positive'),
                sentiment_scores.get('neutral'),
                sentiment_scores.get('negative'),
                article.get('scraped_at'),
                article.get('preprocessing_timestamp'),
                article.get('sentiment_timestamp'),
                article.get('extraction_timestamp')
            ))
            
            article_id = self.cursor.lastrowid
            
            # Insert entities
            entities = article.get('entities', {})
            for entity_type, entity_list in entities.items():
                for entity in entity_list:
                    self.cursor.execute("""
                        INSERT INTO entities (
                            article_id, entity_text, entity_type, entity_label, start_pos, end_pos
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        article_id,
                        entity.get('text'),
                        entity_type,
                        entity.get('label'),
                        entity.get('start'),
                        entity.get('end')
                    ))
            
            # Insert keywords
            keywords = article.get('keywords', [])
            for keyword in keywords:
                self.cursor.execute("""
                    INSERT INTO keywords (article_id, keyword, count)
                    VALUES (?, ?, ?)
                """, (
                    article_id,
                    keyword.get('text'),
                    keyword.get('count', 1)
                ))
            
            return article_id
            
        except sqlite3.IntegrityError as e:
            # Article already exists (duplicate link)
            logger.warning(f"Article already exists: {article.get('link')}")
            return None
        except Exception as e:
            logger.error(f"Error inserting article: {e}")
            return None
    
    def insert_articles_batch(self, articles: List[Dict], commit_interval: int = 50) -> int:
        """
        Insert multiple articles in batch
        
        Args:
            articles: List of article dictionaries
            commit_interval: Commit every N articles for better performance
            
        Returns:
            Number of articles successfully inserted
        """
        logger.info(f"Inserting {len(articles)} articles into database...")
        
        inserted_count = 0
        
        for i, article in enumerate(articles):
            article_id = self.insert_article(article)
            if article_id:
                inserted_count += 1
            
            # Commit periodically
            if (i + 1) % commit_interval == 0:
                self.conn.commit()
                logger.info(f"Inserted {i + 1}/{len(articles)} articles ({(i + 1) / len(articles) * 100:.0f}%)")
        
        # Final commit
        self.conn.commit()
        
        logger.success(f"Successfully inserted {inserted_count} articles (skipped {len(articles) - inserted_count} duplicates)")
        return inserted_count
    
    def get_article_by_id(self, article_id: int) -> Optional[Dict]:
        """Get article by ID with entities and keywords"""
        self.cursor.execute("SELECT * FROM articles WHERE id = ?", (article_id,))
        row = self.cursor.fetchone()
        
        if not row:
            return None
        
        article = dict(row)
        
        # Get entities
        self.cursor.execute("""
            SELECT entity_text, entity_type, entity_label, start_pos, end_pos
            FROM entities WHERE article_id = ?
        """, (article_id,))
        
        entities = {}
        for entity_row in self.cursor.fetchall():
            entity_type = entity_row['entity_type']
            if entity_type not in entities:
                entities[entity_type] = []
            entities[entity_type].append({
                'text': entity_row['entity_text'],
                'label': entity_row['entity_label'],
                'start': entity_row['start_pos'],
                'end': entity_row['end_pos']
            })
        article['entities'] = entities
        
        # Get keywords
        self.cursor.execute("""
            SELECT keyword, count FROM keywords WHERE article_id = ?
        """, (article_id,))
        
        keywords = [{'text': row['keyword'], 'count': row['count']} for row in self.cursor.fetchall()]
        article['keywords'] = keywords
        
        return article
    
    def get_articles(self, limit: int = 100, offset: int = 0, 
                     sentiment: Optional[str] = None,
                     source: Optional[str] = None) -> List[Dict]:
        """
        Get articles with optional filtering
        
        Args:
            limit: Maximum number of articles to return
            offset: Number of articles to skip
            sentiment: Filter by sentiment (positive, neutral, negative)
            source: Filter by source name
            
        Returns:
            List of article dictionaries
        """
        query = "SELECT * FROM articles WHERE 1=1"
        params = []
        
        if sentiment:
            query += " AND sentiment = ?"
            params.append(sentiment)
        
        if source:
            query += " AND source = ?"
            params.append(source)
        
        query += " ORDER BY published DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        self.cursor.execute(query, params)
        
        articles = []
        for row in self.cursor.fetchall():
            articles.append(dict(row))
        
        return articles
    
    def get_sentiment_distribution(self) -> Dict[str, int]:
        """Get count of articles by sentiment"""
        self.cursor.execute("""
            SELECT sentiment, COUNT(*) as count
            FROM articles
            WHERE sentiment IS NOT NULL
            GROUP BY sentiment
        """)
        
        return {row['sentiment']: row['count'] for row in self.cursor.fetchall()}
    
    def get_source_distribution(self) -> Dict[str, int]:
        """Get count of articles by source"""
        self.cursor.execute("""
            SELECT source, COUNT(*) as count
            FROM articles
            GROUP BY source
            ORDER BY count DESC
        """)
        
        return {row['source']: row['count'] for row in self.cursor.fetchall()}
    
    def get_top_entities(self, entity_type: str, limit: int = 10) -> List[Tuple[str, int]]:
        """
        Get most frequently mentioned entities of a specific type
        
        Args:
            entity_type: Type of entity (people, organizations, locations, etc.)
            limit: Number of top entities to return
            
        Returns:
            List of (entity_text, count) tuples
        """
        self.cursor.execute("""
            SELECT entity_text, COUNT(*) as count
            FROM entities
            WHERE entity_type = ?
            GROUP BY entity_text
            ORDER BY count DESC
            LIMIT ?
        """, (entity_type, limit))
        
        return [(row['entity_text'], row['count']) for row in self.cursor.fetchall()]
    
    def get_top_keywords(self, limit: int = 20) -> List[Tuple[str, int]]:
        """Get most frequent keywords across all articles"""
        self.cursor.execute("""
            SELECT keyword, SUM(count) as total_count
            FROM keywords
            GROUP BY keyword
            ORDER BY total_count DESC
            LIMIT ?
        """, (limit,))
        
        return [(row['keyword'], row['total_count']) for row in self.cursor.fetchall()]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall database statistics"""
        stats = {}
        
        # Total articles
        self.cursor.execute("SELECT COUNT(*) as count FROM articles")
        stats['total_articles'] = self.cursor.fetchone()['count']
        
        # Total entities
        self.cursor.execute("SELECT COUNT(*) as count FROM entities")
        stats['total_entities'] = self.cursor.fetchone()['count']
        
        # Total keywords
        self.cursor.execute("SELECT COUNT(*) as count FROM keywords")
        stats['total_keywords'] = self.cursor.fetchone()['count']
        
        # Sentiment distribution
        stats['sentiment_distribution'] = self.get_sentiment_distribution()
        
        # Source distribution
        stats['source_distribution'] = self.get_source_distribution()
        
        # Average sentiment confidence
        self.cursor.execute("""
            SELECT AVG(sentiment_confidence) as avg_confidence
            FROM articles
            WHERE sentiment_confidence IS NOT NULL
        """)
        result = self.cursor.fetchone()
        stats['avg_sentiment_confidence'] = result['avg_confidence'] if result['avg_confidence'] else 0
        
        return stats
    
    def search_articles(self, keyword: str, limit: int = 50) -> List[Dict]:
        """
        Search articles by keyword in title or description
        
        Args:
            keyword: Search term
            limit: Maximum results
            
        Returns:
            List of matching articles
        """
        self.cursor.execute("""
            SELECT * FROM articles
            WHERE title LIKE ? OR description LIKE ?
            ORDER BY published DESC
            LIMIT ?
        """, (f'%{keyword}%', f'%{keyword}%', limit))
        
        return [dict(row) for row in self.cursor.fetchall()]
    
    def delete_all(self):
        """Delete all data from database (use with caution!)"""
        logger.warning("Deleting all data from database...")
        self.cursor.execute("DELETE FROM keywords")
        self.cursor.execute("DELETE FROM entities")
        self.cursor.execute("DELETE FROM articles")
        self.conn.commit()
        logger.info("All data deleted")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


if __name__ == "__main__":
    # Test database manager
    print("\n" + "=" * 60)
    print("Testing DatabaseManager")
    print("=" * 60)
    
    # Create test database
    db = DatabaseManager("data/test.db")
    
    # Test article data
    test_article = {
        'title': 'Test Article Title',
        'description': 'Test description',
        'link': 'https://example.com/test',
        'published': '2025-12-01',
        'source': 'Test Source',
        'source_url': 'https://example.com',
        'title_cleaned': 'test article title',
        'full_text_token_count': 10,
        'sentiment': 'positive',
        'sentiment_confidence': 0.95,
        'sentiment_scores': {
            'positive': 0.95,
            'neutral': 0.04,
            'negative': 0.01
        },
        'entities': {
            'people': [{'text': 'John Doe', 'label': 'PERSON', 'start': 0, 'end': 8}],
            'locations': [{'text': 'New York', 'label': 'GPE', 'start': 10, 'end': 18}]
        },
        'keywords': [
            {'text': 'test', 'count': 2},
            {'text': 'article', 'count': 1}
        ]
    }
    
    # Insert test article
    article_id = db.insert_article(test_article)
    print(f"\nInserted test article with ID: {article_id}")
    
    # Get statistics
    stats = db.get_statistics()
    print("\nDatabase Statistics:")
    print(f"  Total Articles: {stats['total_articles']}")
    print(f"  Total Entities: {stats['total_entities']}")
    print(f"  Total Keywords: {stats['total_keywords']}")
    
    # Clean up
    db.delete_all()
    db.close()
    
    print("\n✓ DatabaseManager test completed")
