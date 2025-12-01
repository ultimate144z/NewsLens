"""
Data Ingestion Module
Exports scrapers for easy import
"""
from .rss_scraper import RSScraper
from .newsapi_scraper import NewsAPIScraper

__all__ = ['RSScraper', 'NewsAPIScraper']
