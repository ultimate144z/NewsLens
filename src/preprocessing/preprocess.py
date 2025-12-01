"""
Text Preprocessing Module
Cleans and preprocesses text for NLP analysis
"""
import re
import string
from typing import List, Dict, Any, Optional
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.logger import get_logger
from utils.helpers import load_config

# NLTK imports
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

logger = get_logger("preprocessor")


class TextPreprocessor:
    """Text preprocessing pipeline for news articles"""
    
    def __init__(self):
        """Initialize preprocessor with configuration"""
        self.config = load_config("model_config")
        self.preprocess_config = self.config.get("preprocessing", {})
        
        # Download required NLTK data
        self._download_nltk_data()
        
        # Initialize tools
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        # Load configuration settings
        self.lowercase = self.preprocess_config.get("lowercase", True)
        self.remove_urls = self.preprocess_config.get("remove_urls", True)
        self.remove_emails = self.preprocess_config.get("remove_emails", True)
        self.remove_mentions = self.preprocess_config.get("remove_mentions", True)
        self.remove_hashtags = self.preprocess_config.get("remove_hashtags", False)
        self.remove_numbers = self.preprocess_config.get("remove_numbers", False)
        self.remove_punctuation = self.preprocess_config.get("remove_punctuation", False)
        self.remove_stopwords = self.preprocess_config.get("remove_stopwords", True)
        self.lemmatize = self.preprocess_config.get("lemmatize", True)
        self.min_word_length = self.preprocess_config.get("min_word_length", 2)
        
        logger.info("Initialized TextPreprocessor")
        logger.info(f"Settings: lowercase={self.lowercase}, remove_stopwords={self.remove_stopwords}, lemmatize={self.lemmatize}")
    
    def _download_nltk_data(self):
        """Download required NLTK data packages"""
        required_packages = [
            ('punkt', 'tokenizers/punkt'),
            ('stopwords', 'corpora/stopwords'),
            ('wordnet', 'corpora/wordnet'),
            ('averaged_perceptron_tagger', 'taggers/averaged_perceptron_tagger'),
            ('omw-1.4', 'corpora/omw-1.4')
        ]
        
        for package_name, package_path in required_packages:
            try:
                nltk.data.find(package_path)
            except LookupError:
                try:
                    logger.info(f"Downloading NLTK package: {package_name}")
                    nltk.download(package_name, quiet=True)
                except Exception as e:
                    logger.warning(f"Could not download {package_name}: {e}")
    
    def clean_text(self, text: str) -> str:
        """
        Clean text by removing unwanted elements
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Convert to string if not already
        text = str(text)
        
        # Remove URLs
        if self.remove_urls:
            text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove email addresses
        if self.remove_emails:
            text = re.sub(r'\S+@\S+', '', text)
        
        # Remove mentions (@username)
        if self.remove_mentions:
            text = re.sub(r'@\w+', '', text)
        
        # Remove hashtags
        if self.remove_hashtags:
            text = re.sub(r'#\w+', '', text)
        
        # Remove numbers
        if self.remove_numbers:
            text = re.sub(r'\d+', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words
        
        Args:
            text: Text to tokenize
            
        Returns:
            List of tokens
        """
        if not text:
            return []
        
        try:
            tokens = word_tokenize(text)
        except Exception as e:
            logger.warning(f"Tokenization error: {e}. Using simple split.")
            tokens = text.split()
        
        return tokens
    
    def remove_punctuation_from_tokens(self, tokens: List[str]) -> List[str]:
        """
        Remove punctuation from tokens
        
        Args:
            tokens: List of tokens
            
        Returns:
            Tokens without punctuation
        """
        if self.remove_punctuation:
            return [token for token in tokens if token not in string.punctuation]
        return tokens
    
    def filter_stopwords(self, tokens: List[str]) -> List[str]:
        """
        Remove stopwords from tokens
        
        Args:
            tokens: List of tokens
            
        Returns:
            Tokens without stopwords
        """
        if self.remove_stopwords:
            return [token for token in tokens if token.lower() not in self.stop_words]
        return tokens
    
    def lemmatize_tokens(self, tokens: List[str]) -> List[str]:
        """
        Lemmatize tokens
        
        Args:
            tokens: List of tokens
            
        Returns:
            Lemmatized tokens
        """
        if self.lemmatize:
            return [self.lemmatizer.lemmatize(token) for token in tokens]
        return tokens
    
    def filter_by_length(self, tokens: List[str]) -> List[str]:
        """
        Filter tokens by minimum length
        
        Args:
            tokens: List of tokens
            
        Returns:
            Filtered tokens
        """
        return [token for token in tokens if len(token) >= self.min_word_length]
    
    def preprocess(self, text: str, return_tokens: bool = False) -> str | List[str]:
        """
        Complete preprocessing pipeline
        
        Args:
            text: Raw text to preprocess
            return_tokens: If True, return list of tokens. If False, return string.
            
        Returns:
            Preprocessed text or tokens
        """
        # Clean text
        text = self.clean_text(text)
        
        # Convert to lowercase
        if self.lowercase:
            text = text.lower()
        
        # Tokenize
        tokens = self.tokenize(text)
        
        # Remove punctuation
        tokens = self.remove_punctuation_from_tokens(tokens)
        
        # Filter stopwords
        tokens = self.filter_stopwords(tokens)
        
        # Lemmatize
        tokens = self.lemmatize_tokens(tokens)
        
        # Filter by length
        tokens = self.filter_by_length(tokens)
        
        if return_tokens:
            return tokens
        else:
            return ' '.join(tokens)
    
    def preprocess_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocess an article dictionary
        
        Args:
            article: Article dictionary with 'title' and 'description' fields
            
        Returns:
            Article with added preprocessed fields
        """
        # Preprocess title
        title = article.get('title', '')
        article['title_clean'] = self.preprocess(title)
        article['title_tokens'] = self.preprocess(title, return_tokens=True)
        
        # Preprocess description
        description = article.get('description', '')
        article['description_clean'] = self.preprocess(description)
        article['description_tokens'] = self.preprocess(description, return_tokens=True)
        
        # Combine for full text processing
        full_text = f"{title} {description}"
        article['full_text_clean'] = self.preprocess(full_text)
        article['full_text_tokens'] = self.preprocess(full_text, return_tokens=True)
        
        # Add token counts
        article['title_token_count'] = len(article['title_tokens'])
        article['description_token_count'] = len(article['description_tokens'])
        article['full_text_token_count'] = len(article['full_text_tokens'])
        
        return article
    
    def preprocess_batch(self, articles: List[Dict[str, Any]], show_progress: bool = True) -> List[Dict[str, Any]]:
        """
        Preprocess a batch of articles
        
        Args:
            articles: List of article dictionaries
            show_progress: Whether to show progress
            
        Returns:
            List of preprocessed articles
        """
        preprocessed = []
        total = len(articles)
        
        logger.info(f"Preprocessing {total} articles...")
        
        for i, article in enumerate(articles, 1):
            try:
                preprocessed_article = self.preprocess_article(article)
                preprocessed.append(preprocessed_article)
                
                if show_progress and i % 10 == 0:
                    logger.info(f"Processed {i}/{total} articles ({i*100//total}%)")
            except Exception as e:
                logger.error(f"Error preprocessing article {i}: {e}")
                preprocessed.append(article)  # Keep original on error
        
        logger.success(f"Successfully preprocessed {len(preprocessed)} articles")
        return preprocessed
    
    def get_statistics(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get preprocessing statistics
        
        Args:
            articles: List of preprocessed articles
            
        Returns:
            Dictionary of statistics
        """
        total = len(articles)
        
        if total == 0:
            return {"total": 0}
        
        avg_title_tokens = sum(a.get('title_token_count', 0) for a in articles) / total
        avg_desc_tokens = sum(a.get('description_token_count', 0) for a in articles) / total
        avg_full_tokens = sum(a.get('full_text_token_count', 0) for a in articles) / total
        
        stats = {
            'total_articles': total,
            'avg_title_tokens': round(avg_title_tokens, 2),
            'avg_description_tokens': round(avg_desc_tokens, 2),
            'avg_full_text_tokens': round(avg_full_tokens, 2),
            'total_tokens': sum(a.get('full_text_token_count', 0) for a in articles)
        }
        
        return stats


def main():
    """Test the preprocessor"""
    preprocessor = TextPreprocessor()
    
    # Test text
    sample_text = """
    Breaking News: The @president announced today at https://whitehouse.gov 
    that #ClimateChange initiatives will receive $10 billion in funding. 
    Email concerns to feedback@example.com for more information!!!
    """
    
    logger.info("\n=== Sample Text ===")
    logger.info(sample_text)
    
    logger.info("\n=== Cleaned Text ===")
    cleaned = preprocessor.clean_text(sample_text)
    logger.info(cleaned)
    
    logger.info("\n=== Preprocessed Text ===")
    preprocessed = preprocessor.preprocess(sample_text)
    logger.info(preprocessed)
    
    logger.info("\n=== Tokens ===")
    tokens = preprocessor.preprocess(sample_text, return_tokens=True)
    logger.info(tokens)


if __name__ == "__main__":
    main()
