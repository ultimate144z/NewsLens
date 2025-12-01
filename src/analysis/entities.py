"""
NLP Analysis Module - Entity Extraction
Uses spaCy for named entity recognition (NER) in news articles
"""

import os
import json
from typing import Dict, List, Optional, Set, Union
from datetime import datetime
from collections import Counter
import spacy
from loguru import logger
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import load_config, ensure_dir_exists


class EntityExtractor:
    """
    Extract named entities from news articles using spaCy
    """
    
    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize the entity extractor
        
        Args:
            model_name: Name of the spaCy model to use (default from config)
        """
        # Load configuration
        self.config = load_config('model_config')
        
        # Get spaCy config
        spacy_config = self.config['spacy_model']
        
        # Set model name
        self.model_name = model_name or spacy_config['name']
        
        logger.info(f"Initializing EntityExtractor with model: {self.model_name}")
        
        # Load spaCy model
        self._load_model()
        
        # Entity types we're interested in
        self.entity_types = {
            'PERSON': 'people',
            'ORG': 'organizations',
            'GPE': 'locations',  # Geopolitical entities (countries, cities, states)
            'LOC': 'locations',  # Non-GPE locations
            'DATE': 'dates',
            'MONEY': 'money',
            'EVENT': 'events'
        }
        
        logger.success("EntityExtractor initialized successfully")
    
    def _load_model(self):
        """Load the spaCy model"""
        try:
            logger.info("Loading spaCy model...")
            self.nlp = spacy.load(self.model_name)
            logger.success(f"spaCy model loaded: {self.model_name}")
            
        except OSError:
            logger.warning(f"Model {self.model_name} not found. Attempting to download...")
            try:
                import subprocess
                subprocess.run(['python', '-m', 'spacy', 'download', self.model_name], check=True)
                self.nlp = spacy.load(self.model_name)
                logger.success(f"Model downloaded and loaded: {self.model_name}")
            except Exception as e:
                logger.error(f"Error downloading model: {e}")
                raise
        except Exception as e:
            logger.error(f"Error loading spaCy model: {e}")
            raise
    
    def extract_entities(self, text: str) -> Dict[str, List[Dict]]:
        """
        Extract named entities from text
        
        Args:
            text: Text to extract entities from
            
        Returns:
            Dictionary with entity types as keys and lists of entities as values
        """
        if not text or not text.strip():
            return {category: [] for category in set(self.entity_types.values())}
        
        try:
            # Process text with spaCy
            doc = self.nlp(text)
            
            # Initialize entity dictionary
            entities = {category: [] for category in set(self.entity_types.values())}
            
            # Extract entities
            for ent in doc.ents:
                if ent.label_ in self.entity_types:
                    category = self.entity_types[ent.label_]
                    entity_info = {
                        'text': ent.text,
                        'label': ent.label_,
                        'start': ent.start_char,
                        'end': ent.end_char
                    }
                    entities[category].append(entity_info)
            
            # Remove duplicates while preserving order
            for category in entities:
                seen = set()
                unique_entities = []
                for entity in entities[category]:
                    entity_text = entity['text'].lower()
                    if entity_text not in seen:
                        seen.add(entity_text)
                        unique_entities.append(entity)
                entities[category] = unique_entities
            
            return entities
            
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return {category: [] for category in set(self.entity_types.values())}
    
    def extract_keywords(self, text: str, top_n: int = 10) -> List[Dict[str, Union[str, int]]]:
        """
        Extract important keywords/noun phrases from text
        
        Args:
            text: Text to extract keywords from
            top_n: Number of top keywords to return
            
        Returns:
            List of keyword dictionaries with text and frequency
        """
        if not text or not text.strip():
            return []
        
        try:
            doc = self.nlp(text)
            
            # Extract noun chunks and important words
            keywords = []
            
            # Add noun chunks
            for chunk in doc.noun_chunks:
                # Filter out very short chunks and stopwords
                if len(chunk.text) > 3 and not chunk.root.is_stop:
                    keywords.append(chunk.text.lower())
            
            # Add important single tokens (nouns, proper nouns)
            for token in doc:
                if token.pos_ in ['NOUN', 'PROPN'] and not token.is_stop and len(token.text) > 2:
                    keywords.append(token.text.lower())
            
            # Count frequencies
            keyword_counts = Counter(keywords)
            
            # Get top N
            top_keywords = [
                {'text': keyword, 'count': count}
                for keyword, count in keyword_counts.most_common(top_n)
            ]
            
            return top_keywords
            
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return []
    
    def analyze_article(self, article: Dict) -> Dict:
        """
        Extract entities and keywords from an article
        
        Args:
            article: Article dictionary with text content
            
        Returns:
            Article dictionary with added entity and keyword fields
        """
        # Get text (prefer original over cleaned for entity extraction)
        title_text = article.get('title', '')
        desc_text = article.get('description', '')
        
        # Combine title and description
        full_text = f"{title_text} {desc_text}".strip()
        
        # Extract entities
        entities = self.extract_entities(full_text)
        
        # Extract keywords
        keywords = self.extract_keywords(full_text, top_n=10)
        
        # Add to article
        article['entities'] = entities
        article['entity_counts'] = {
            category: len(ents) for category, ents in entities.items()
        }
        article['keywords'] = keywords
        article['extraction_timestamp'] = datetime.now().isoformat()
        
        return article
    
    def analyze_batch(self, articles: List[Dict], save_path: Optional[str] = None) -> List[Dict]:
        """
        Extract entities and keywords from a batch of articles
        
        Args:
            articles: List of article dictionaries
            save_path: Optional path to save results
            
        Returns:
            List of articles with added entity and keyword fields
        """
        logger.info(f"Extracting entities from {len(articles)} articles...")
        
        analyzed_articles = []
        
        for i, article in enumerate(articles):
            try:
                analyzed = self.analyze_article(article)
                analyzed_articles.append(analyzed)
                
                # Log progress
                if (i + 1) % 10 == 0 or (i + 1) == len(articles):
                    logger.info(f"Processed {i + 1}/{len(articles)} articles ({(i + 1) / len(articles) * 100:.0f}%)")
                    
            except Exception as e:
                logger.error(f"Error analyzing article {i + 1}: {e}")
                # Add original article with error flag
                article['extraction_error'] = str(e)
                analyzed_articles.append(article)
        
        # Calculate statistics
        total_entities = {
            'people': 0,
            'organizations': 0,
            'locations': 0,
            'dates': 0,
            'money': 0,
            'events': 0
        }
        
        for article in analyzed_articles:
            if 'entity_counts' in article:
                for category, count in article['entity_counts'].items():
                    total_entities[category] += count
        
        logger.info("Entity extraction statistics:")
        for category, count in total_entities.items():
            logger.info(f"  - {category.capitalize()}: {count}")
        
        # Save if path provided
        if save_path:
            ensure_dir_exists(os.path.dirname(save_path))
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(analyzed_articles, f, indent=2, ensure_ascii=False)
            logger.success(f"Saved analyzed articles to: {save_path}")
        
        logger.success(f"Successfully extracted entities from {len(analyzed_articles)} articles")
        return analyzed_articles
    
    def get_top_entities(self, articles: List[Dict], category: str, top_n: int = 10) -> List[Dict]:
        """
        Get the most frequently mentioned entities across all articles
        
        Args:
            articles: List of analyzed articles
            category: Entity category ('people', 'organizations', 'locations', etc.)
            top_n: Number of top entities to return
            
        Returns:
            List of top entities with counts
        """
        entity_counter = Counter()
        
        for article in articles:
            if 'entities' in article and category in article['entities']:
                for entity in article['entities'][category]:
                    entity_counter[entity['text']] += 1
        
        return [
            {'entity': entity, 'count': count}
            for entity, count in entity_counter.most_common(top_n)
        ]


if __name__ == "__main__":
    # Test the entity extractor
    extractor = EntityExtractor()
    
    # Test text
    test_text = """
    President Joe Biden met with UK Prime Minister Rishi Sunak in London yesterday.
    They discussed the ongoing situation in Ukraine and announced a $500 million aid package.
    The meeting took place at 10 Downing Street and was attended by officials from NATO.
    """
    
    print("\n" + "=" * 60)
    print("Testing Entity Extractor")
    print("=" * 60)
    print(f"\nText: {test_text.strip()}")
    
    entities = extractor.extract_entities(test_text)
    
    print("\nExtracted Entities:")
    for category, ents in entities.items():
        if ents:
            print(f"\n{category.capitalize()}:")
            for ent in ents:
                print(f"  - {ent['text']} ({ent['label']})")
    
    keywords = extractor.extract_keywords(test_text, top_n=5)
    print("\nExtracted Keywords:")
    for kw in keywords:
        print(f"  - {kw['text']} (count: {kw['count']})")
