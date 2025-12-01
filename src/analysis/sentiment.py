"""
NLP Analysis Module - Sentiment Analysis
Uses transformer models for sentiment classification of news articles
"""

import os
import json
from typing import Dict, List, Optional, Union
from datetime import datetime
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from loguru import logger
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import load_config, ensure_dir_exists, get_data_dir


class SentimentAnalyzer:
    """
    Sentiment analyzer using transformer models for news articles
    """
    
    def __init__(self, model_name: Optional[str] = None, batch_size: Optional[int] = None):
        """
        Initialize the sentiment analyzer
        
        Args:
            model_name: Name of the model to use (default from config)
            batch_size: Batch size for inference (default from config)
        """
        # Load configuration
        self.config = load_config('model_config')
        
        # Get sentiment config
        sentiment_config = self.config['sentiment_model']
        
        # Set model name and parameters
        self.model_name = model_name or sentiment_config['name']
        self.batch_size = batch_size or sentiment_config['batch_size']
        self.max_length = sentiment_config['max_length']
        
        # Device setup
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        logger.info(f"Initializing SentimentAnalyzer with model: {self.model_name}")
        logger.info(f"Device: {self.device}")
        
        # Load model and tokenizer
        self._load_model()
        
        # Label mapping
        self.label_map = {
            0: 'negative',
            1: 'neutral',
            2: 'positive'
        }
        
        logger.success("SentimentAnalyzer initialized successfully")
    
    def _load_model(self):
        """Load the transformer model and tokenizer"""
        try:
            logger.info("Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            logger.info("Loading model...")
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()
            
            logger.success(f"Model loaded: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def analyze_text(self, text: str) -> Dict[str, Union[str, float, Dict]]:
        """
        Analyze sentiment of a single text
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment label, scores, and confidence
        """
        if not text or not text.strip():
            return {
                'label': 'neutral',
                'confidence': 0.0,
                'scores': {'negative': 0.33, 'neutral': 0.34, 'positive': 0.33}
            }
        
        try:
            # Tokenize
            inputs = self.tokenizer(
                text,
                return_tensors='pt',
                truncation=True,
                max_length=self.max_length,
                padding=True
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Get predictions
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probs = torch.nn.functional.softmax(logits, dim=-1)
            
            # Get scores and prediction
            scores = probs[0].cpu().numpy()
            predicted_label_id = scores.argmax()
            
            # Create result
            result = {
                'label': self.label_map[predicted_label_id],
                'confidence': float(scores[predicted_label_id]),
                'scores': {
                    'negative': float(scores[0]),
                    'neutral': float(scores[1]),
                    'positive': float(scores[2])
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing text: {e}")
            return {
                'label': 'neutral',
                'confidence': 0.0,
                'scores': {'negative': 0.33, 'neutral': 0.34, 'positive': 0.33},
                'error': str(e)
            }
    
    def analyze_article(self, article: Dict) -> Dict:
        """
        Analyze sentiment of an article (title + description)
        
        Args:
            article: Article dictionary with preprocessed text
            
        Returns:
            Article dictionary with added sentiment fields
        """
        # Get cleaned text (use preprocessed if available, otherwise original)
        title_text = article.get('title_cleaned', article.get('title', ''))
        desc_text = article.get('description_cleaned', article.get('description', ''))
        
        # Combine title and description
        full_text = f"{title_text} {desc_text}".strip()
        
        # Analyze sentiment
        sentiment = self.analyze_text(full_text)
        
        # Add sentiment fields to article
        article['sentiment'] = sentiment['label']
        article['sentiment_confidence'] = sentiment['confidence']
        article['sentiment_scores'] = sentiment['scores']
        article['sentiment_timestamp'] = datetime.now().isoformat()
        
        return article
    
    def analyze_batch(self, articles: List[Dict], save_path: Optional[str] = None) -> List[Dict]:
        """
        Analyze sentiment for a batch of articles
        
        Args:
            articles: List of article dictionaries
            save_path: Optional path to save results
            
        Returns:
            List of articles with added sentiment fields
        """
        logger.info(f"Analyzing sentiment for {len(articles)} articles...")
        
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
                article['sentiment_error'] = str(e)
                analyzed_articles.append(article)
        
        # Calculate statistics
        sentiments = [a.get('sentiment') for a in analyzed_articles if 'sentiment' in a]
        if sentiments:
            stats = {
                'total': len(analyzed_articles),
                'positive': sentiments.count('positive'),
                'negative': sentiments.count('negative'),
                'neutral': sentiments.count('neutral'),
                'avg_confidence': sum([a.get('sentiment_confidence', 0) for a in analyzed_articles]) / len(analyzed_articles)
            }
            logger.info(f"Sentiment distribution: Positive={stats['positive']}, Neutral={stats['neutral']}, Negative={stats['negative']}")
            logger.info(f"Average confidence: {stats['avg_confidence']:.2%}")
        
        # Save if path provided
        if save_path:
            ensure_dir_exists(os.path.dirname(save_path))
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(analyzed_articles, f, indent=2, ensure_ascii=False)
            logger.success(f"Saved analyzed articles to: {save_path}")
        
        logger.success(f"Successfully analyzed {len(analyzed_articles)} articles")
        return analyzed_articles


if __name__ == "__main__":
    # Test the sentiment analyzer
    analyzer = SentimentAnalyzer()
    
    # Test texts
    test_texts = [
        "This is excellent news! The economy is booming and unemployment is at record lows.",
        "Tragedy strikes as natural disaster devastates the region, leaving thousands homeless.",
        "The government announced new regulations that will take effect next month."
    ]
    
    print("\n" + "=" * 60)
    print("Testing Sentiment Analyzer")
    print("=" * 60)
    
    for i, text in enumerate(test_texts, 1):
        print(f"\nTest {i}:")
        print(f"Text: {text}")
        result = analyzer.analyze_text(text)
        print(f"Sentiment: {result['label'].upper()} (confidence: {result['confidence']:.2%})")
        print(f"Scores: Neg={result['scores']['negative']:.2%}, Neu={result['scores']['neutral']:.2%}, Pos={result['scores']['positive']:.2%}")
