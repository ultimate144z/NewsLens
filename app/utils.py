"""
Utility functions for the NewsLens dashboard.

Provides data loading, caching, and helper functions.
"""

import streamlit as st
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_analytics_summary() -> Optional[Dict[str, Any]]:
    """
    Load the latest analytics summary from JSON file.
    
    Returns:
        Dictionary with analytics data or None if not found
    """
    try:
        analytics_dir = Path("data/analytics")
        if not analytics_dir.exists():
            st.error("Analytics directory not found. Please run analytics first.")
            return None
        
        # Find latest analytics file
        analytics_files = list(analytics_dir.glob("analytics_summary_*.json"))
        if not analytics_files:
            st.error("No analytics summary found. Please run analytics first.")
            return None
        
        latest_file = max(analytics_files, key=lambda p: p.stat().st_mtime)
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data
    except Exception as e:
        st.error(f"Error loading analytics data: {e}")
        logger.error(f"Error loading analytics: {e}", exc_info=True)
        return None


@st.cache_data(ttl=300)
def load_articles() -> Optional[List[Dict[str, Any]]]:
    """
    Load analyzed articles from JSON file.
    
    Returns:
        List of article dictionaries or None if not found
    """
    try:
        analyzed_dir = Path("data/analyzed")
        if not analyzed_dir.exists():
            st.error("Analyzed data directory not found.")
            return None
        
        # Find latest analyzed file
        analyzed_files = list(analyzed_dir.glob("all_analyzed_*.json"))
        if not analyzed_files:
            st.error("No analyzed articles found.")
            return None
        
        latest_file = max(analyzed_files, key=lambda p: p.stat().st_mtime)
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            articles = json.load(f)
        
        return articles
    except Exception as e:
        st.error(f"Error loading articles: {e}")
        logger.error(f"Error loading articles: {e}", exc_info=True)
        return None


def format_large_number(num: int) -> str:
    """
    Format large numbers with K, M suffixes.
    
    Args:
        num: Number to format
        
    Returns:
        Formatted string
    """
    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.1f}K"
    else:
        return str(num)


def get_sentiment_color(sentiment: str) -> str:
    """
    Get color for sentiment label.
    
    Args:
        sentiment: Sentiment label (positive, neutral, negative)
        
    Returns:
        Hex color code
    """
    colors = {
        'positive': '#10b981',  # Green
        'neutral': '#6b7280',   # Gray
        'negative': '#ef4444',  # Red
        'unknown': '#9ca3af'    # Light gray
    }
    return colors.get(sentiment.lower(), '#9ca3af')


def get_bias_color(bias_score: float) -> str:
    """
    Get color for bias score.
    
    Args:
        bias_score: Bias score from -1 to +1
        
    Returns:
        Hex color code
    """
    if bias_score > 0.15:
        return '#10b981'  # Green (positive bias)
    elif bias_score < -0.15:
        return '#ef4444'  # Red (negative bias)
    else:
        return '#6b7280'  # Gray (neutral)


def create_metric_card(value: str, label: str, color: str = "#667eea") -> str:
    """
    Create HTML for a metric card.
    
    Args:
        value: Metric value
        label: Metric label
        color: Background color
        
    Returns:
        HTML string
    """
    return f"""
    <div style="
        background: linear-gradient(135deg, {color} 0%, {color}dd 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 10px 0;
    ">
        <div style="font-size: 2.5rem; font-weight: bold; margin: 10px 0;">
            {value}
        </div>
        <div style="font-size: 1rem; opacity: 0.9;">
            {label}
        </div>
    </div>
    """


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def safe_percentage(value: float, decimals: int = 1) -> str:
    """
    Safely format percentage value.
    
    Args:
        value: Value to format (0-100 or 0-1)
        decimals: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    try:
        if value > 1:
            return f"{value:.{decimals}f}%"
        else:
            return f"{value * 100:.{decimals}f}%"
    except:
        return "N/A"


# Alias for backward compatibility
format_percentage = safe_percentage
