"""
NewsLens Pipeline Runner

Command-line interface to execute the complete NewsLens workflow:
1. Data Ingestion (RSS + NewsAPI)
2. Preprocessing
3. NLP Analysis (Sentiment + Entities)
4. Storage (Database + CSV)
5. Analytics Generation
6. Dashboard Launch (optional)

Usage:
    python run.py --full              # Run complete pipeline
    python run.py --ingest            # Only data ingestion
    python run.py --analyze           # Only analysis
    python run.py --dashboard         # Only launch dashboard
    python run.py --help              # Show help
"""

import argparse
import sys
import time
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.ingestion.rss_scraper import RSScraper
from src.ingestion.newsapi_scraper import NewsAPIScraper
from src.preprocessing.preprocess import TextPreprocessor
from src.analysis.sentiment import SentimentAnalyzer
from src.analysis.entities import EntityExtractor
from src.storage.database import DatabaseManager
from src.storage.csv_manager import CSVManager
from src.analytics.analytics import NewsAnalytics


class PipelineRunner:
    """Main pipeline orchestrator for NewsLens."""
    
    def __init__(self, verbose=True):
        """Initialize pipeline components."""
        self.verbose = verbose
        self.data_dir = Path('data')
        self.logs_dir = Path('logs')
        
        # Create directories
        self.data_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        
        # Initialize components
        self.rss_scraper = None
        self.news_api = None
        self.preprocessor = None
        self.sentiment_analyzer = None
        self.entity_extractor = None
        self.db_manager = None
        self.csv_manager = None
        self.analytics = None
        
        self.stats = {
            'start_time': None,
            'end_time': None,
            'articles_ingested': 0,
            'articles_analyzed': 0,
            'articles_stored': 0,
            'errors': []
        }
    
    def log(self, message, level='INFO'):
        """Log message to console and file."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] [{level}] {message}"
        
        if self.verbose:
            print(log_message)
        
        # Write to log file
        log_file = self.logs_dir / f"pipeline_{datetime.now().strftime('%Y%m%d')}.log"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')
    
    def run_ingestion(self):
        """Step 1: Ingest data from RSS feeds and NewsAPI."""
        self.log("=" * 60)
        self.log("STEP 1: DATA INGESTION")
        self.log("=" * 60)
        
        try:
            # Initialize scrapers
            self.rss_scraper = RSScraper()
            self.news_api = NewsAPIScraper()
            
            # Scrape RSS feeds
            self.log("Scraping RSS feeds...")
            rss_articles = self.rss_scraper.fetch_all_feeds()
            self.log(f"RSS feeds scraped: {len(rss_articles)} articles")

            # Fetch from NewsAPI
            self.log("Fetching from NewsAPI...")
            api_articles = self.news_api.fetch_by_categories()
            self.log(f"NewsAPI fetched: {len(api_articles)} articles")
            
            # Combine and deduplicate
            all_articles = rss_articles + api_articles
            unique_articles = self._deduplicate_articles(all_articles)
            
            self.stats['articles_ingested'] = len(unique_articles)
            self.log(f"Total unique articles: {len(unique_articles)}")
            
            # Save raw data
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            raw_file = self.data_dir / 'raw' / f'articles_raw_{timestamp}.json'
            raw_file.parent.mkdir(exist_ok=True)
            
            with open(raw_file, 'w', encoding='utf-8') as f:
                json.dump(unique_articles, f, indent=2, ensure_ascii=False)
            
            self.log(f"Raw data saved: {raw_file}")
            return unique_articles
            
        except Exception as e:
            error_msg = f"Ingestion failed: {str(e)}"
            self.log(error_msg, 'ERROR')
            self.stats['errors'].append(error_msg)
            return []
    
    def run_preprocessing(self, articles):
        """Step 2: Clean and preprocess text."""
        self.log("=" * 60)
        self.log("STEP 2: PREPROCESSING")
        self.log("=" * 60)
        
        try:
            # Initialize preprocessor
            self.preprocessor = TextPreprocessor()

            preprocessed = []
            for i, article in enumerate(articles, 1):
                if self.verbose and i % 10 == 0:
                    self.log(f"Preprocessing: {i}/{len(articles)}")

                # Clean text
                article['cleaned_text'] = self.preprocessor.clean_text(article.get('description', ''))
                
                # Preprocess
                article['preprocessed_title'] = self.preprocessor.preprocess(article.get('title', ''))
                article['preprocessed_description'] = self.preprocessor.preprocess(article.get('description', ''))
                
                preprocessed.append(article)
            
            self.log(f"Preprocessed {len(preprocessed)} articles")
            
            # Save preprocessed data
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            prep_file = self.data_dir / 'preprocessed' / f'articles_preprocessed_{timestamp}.json'
            prep_file.parent.mkdir(exist_ok=True)
            
            with open(prep_file, 'w', encoding='utf-8') as f:
                json.dump(preprocessed, f, indent=2, ensure_ascii=False)
            
            self.log(f"Preprocessed data saved: {prep_file}")
            return preprocessed
            
        except Exception as e:
            error_msg = f"Preprocessing failed: {str(e)}"
            self.log(error_msg, 'ERROR')
            self.stats['errors'].append(error_msg)
            return articles
    
    def run_analysis(self, articles):
        """Step 3: Perform sentiment analysis and entity extraction."""
        self.log("=" * 60)
        self.log("STEP 3: NLP ANALYSIS")
        self.log("=" * 60)
        
        try:
            # Initialize analyzers
            self.log("Loading NLP models...")
            self.sentiment_analyzer = SentimentAnalyzer()
            self.entity_extractor = EntityExtractor()
            
            # Analyze articles
            self.log("Analyzing sentiment...")
            analyzed = self.sentiment_analyzer.analyze_batch(articles)
            
            self.log("Extracting entities and keywords...")
            for i, article in enumerate(analyzed, 1):
                if self.verbose and i % 10 == 0:
                    self.log(f"Extracting entities: {i}/{len(analyzed)}")
                
                text = article.get('cleaned_text', '') or article.get('description', '')
                entities = self.entity_extractor.extract_entities(text)
                keywords = self.entity_extractor.extract_keywords(text)

                article['entities'] = entities
                article['keywords'] = keywords
            
            self.stats['articles_analyzed'] = len(analyzed)
            self.log(f"Analyzed {len(analyzed)} articles")
            
            # Save analyzed data
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            analyzed_file = self.data_dir / 'analyzed' / f'all_analyzed_{timestamp}.json'
            analyzed_file.parent.mkdir(exist_ok=True)
            
            with open(analyzed_file, 'w', encoding='utf-8') as f:
                json.dump(analyzed, f, indent=2, ensure_ascii=False)
            
            self.log(f"Analyzed data saved: {analyzed_file}")
            return analyzed
            
        except Exception as e:
            error_msg = f"Analysis failed: {str(e)}"
            self.log(error_msg, 'ERROR')
            self.stats['errors'].append(error_msg)
            return articles
    
    def run_storage(self, articles):
        """Step 4: Store in database and export to CSV."""
        self.log("=" * 60)
        self.log("STEP 4: STORAGE")
        self.log("=" * 60)
        
        try:
            # Initialize storage managers
            db_path = self.data_dir / 'newslens.db'
            self.db_manager = DatabaseManager(str(db_path))
            self.csv_manager = CSVManager()
            
            # Store in database
            self.log("Storing articles in database...")
            stored = self.db_manager.insert_articles_batch(articles)
            self.stats['articles_stored'] = stored
            self.log(f"Stored {stored} articles in database")
            
            # Get statistics
            stats = self.db_manager.get_statistics()
            self.log(f"Database statistics: {stats}")
            
            # Export to CSV
            self.log("Exporting to CSV...")
            csv_files = self.csv_manager.export_all(articles)
            self.log(f"Exported {len(csv_files)} CSV files")
            
            return True
            
        except Exception as e:
            error_msg = f"Storage failed: {str(e)}"
            self.log(error_msg, 'ERROR')
            self.stats['errors'].append(error_msg)
            return False
    
    def run_analytics(self, articles):
        """Step 5: Generate analytics and summary."""
        self.log("=" * 60)
        self.log("STEP 5: ANALYTICS")
        self.log("=" * 60)
        
        try:
            # Initialize analytics
            self.analytics = NewsAnalytics(articles)
            
            # Generate comprehensive summary
            self.log("Generating analytics summary...")
            summary = self.analytics.get_comprehensive_summary()
            
            # Save analytics
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            analytics_file = self.data_dir / 'analytics' / f'analytics_summary_{timestamp}.json'
            analytics_file.parent.mkdir(exist_ok=True)
            
            with open(analytics_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            self.log(f"Analytics saved: {analytics_file}")
            
            # Print key insights
            overview = summary.get('overview', {})
            self.log(f"Total articles: {overview.get('total_articles', 0)}")
            self.log(f"Sources: {overview.get('total_sources', 0)}")
            self.log(f"Average confidence: {overview.get('average_confidence', 0):.2f}%")
            
            sentiment_dist = summary.get('sentiment', {}).get('distribution', {})
            self.log(f"Sentiment: Pos={sentiment_dist.get('positive', 0)}, "
                    f"Neu={sentiment_dist.get('neutral', 0)}, "
                    f"Neg={sentiment_dist.get('negative', 0)}")
            
            return summary
            
        except Exception as e:
            error_msg = f"Analytics failed: {str(e)}"
            self.log(error_msg, 'ERROR')
            self.stats['errors'].append(error_msg)
            return None
    
    def launch_dashboard(self):
        """Step 6: Launch Streamlit dashboard."""
        self.log("=" * 60)
        self.log("STEP 6: LAUNCHING DASHBOARD")
        self.log("=" * 60)
        
        try:
            import subprocess
            self.log("Starting Streamlit dashboard...")
            self.log("Dashboard will open in your browser at: http://localhost:8501")
            
            # Launch dashboard
            subprocess.run([
                sys.executable, '-m', 'streamlit', 'run',
                str(project_root / 'app' / 'dashboard.py')
            ])
            
        except Exception as e:
            error_msg = f"Dashboard launch failed: {str(e)}"
            self.log(error_msg, 'ERROR')
            self.stats['errors'].append(error_msg)
    
    def run_full_pipeline(self, launch_dashboard=False):
        """Execute the complete pipeline."""
        self.stats['start_time'] = time.time()
        
        self.log("=" * 60)
        self.log("NEWSLENS PIPELINE EXECUTION STARTED")
        self.log("=" * 60)
        
        # Step 1: Ingestion
        articles = self.run_ingestion()
        if not articles:
            self.log("No articles ingested. Stopping pipeline.", 'ERROR')
            return False
        
        # Step 2: Preprocessing
        articles = self.run_preprocessing(articles)
        
        # Step 3: Analysis
        articles = self.run_analysis(articles)
        
        # Step 4: Storage
        self.run_storage(articles)
        
        # Step 5: Analytics
        self.run_analytics(articles)
        
        self.stats['end_time'] = time.time()
        elapsed = self.stats['end_time'] - self.stats['start_time']
        
        # Final summary
        self.log("=" * 60)
        self.log("PIPELINE EXECUTION COMPLETED")
        self.log("=" * 60)
        self.log(f"Total time: {elapsed:.2f} seconds ({elapsed/60:.2f} minutes)")
        self.log(f"Articles ingested: {self.stats['articles_ingested']}")
        self.log(f"Articles analyzed: {self.stats['articles_analyzed']}")
        self.log(f"Articles stored: {self.stats['articles_stored']}")
        
        if self.stats['errors']:
            self.log(f"Errors encountered: {len(self.stats['errors'])}", 'WARNING')
            for error in self.stats['errors']:
                self.log(f"  - {error}", 'WARNING')
        
        # Launch dashboard if requested
        if launch_dashboard:
            self.launch_dashboard()
        
        return True
    
    def _deduplicate_articles(self, articles):
        """Remove duplicate articles based on URL."""
        seen_urls = set()
        unique = []
        
        for article in articles:
            url = article.get('link', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique.append(article)
        
        return unique


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='NewsLens Pipeline Runner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py --full              # Run complete pipeline
  python run.py --full --dashboard  # Run pipeline and launch dashboard
  python run.py --ingest            # Only data ingestion
  python run.py --analyze           # Only analysis (requires existing data)
  python run.py --dashboard         # Only launch dashboard
        """
    )
    
    parser.add_argument('--full', action='store_true',
                       help='Run the complete pipeline')
    parser.add_argument('--ingest', action='store_true',
                       help='Run only data ingestion')
    parser.add_argument('--preprocess', action='store_true',
                       help='Run only preprocessing')
    parser.add_argument('--analyze', action='store_true',
                       help='Run only analysis')
    parser.add_argument('--store', action='store_true',
                       help='Run only storage')
    parser.add_argument('--analytics', action='store_true',
                       help='Run only analytics')
    parser.add_argument('--dashboard', action='store_true',
                       help='Launch Streamlit dashboard')
    parser.add_argument('--quiet', action='store_true',
                       help='Suppress verbose output')
    
    args = parser.parse_args()
    
    # If no arguments, show help
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    # Initialize pipeline
    runner = PipelineRunner(verbose=not args.quiet)
    
    # Execute based on arguments
    if args.full:
        runner.run_full_pipeline(launch_dashboard=args.dashboard)
    elif args.ingest:
        articles = runner.run_ingestion()
        print(f"\nIngested {len(articles)} articles")
    elif args.dashboard:
        runner.launch_dashboard()
    else:
        # Individual steps require loading existing data
        print("Individual step execution requires existing data files.")
        print("Use --full to run the complete pipeline first.")


if __name__ == '__main__':
    main()
