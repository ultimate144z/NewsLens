"""
NewsLens Streamlit Dashboard - Main Application

A multi-page interactive dashboard for news sentiment analysis and insights.
Features:
- Overview with key metrics
- Sentiment analysis visualizations
- Source comparison
- Entity tracking
- Keyword analysis
- Temporal trends
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Page configuration
st.set_page_config(
    page_title="NewsLens Dashboard",
    page_icon="N",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better visual appeal
st.markdown("""
    <style>
    /* Main container styling */
    .main {
        padding: 0rem 1rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 10px 0;
    }
    
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    
    /* Headers */
    h1 {
        color: #1e3a8a;
        font-weight: 700;
    }
    
    h2 {
        color: #2563eb;
        font-weight: 600;
        margin-top: 2rem;
    }
    
    h3 {
        color: #3b82f6;
        font-weight: 500;
    }
    
    /* Dataframe styling */
    .dataframe {
        font-size: 0.9rem;
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 8px;
    }
    
    /* Buttons */
    .stButton>button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* Selectbox */
    .stSelectbox {
        margin-bottom: 1rem;
    }
    
    /* Chart containers */
    .plot-container {
        background: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin: 10px 0;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 20px;
        color: #6b7280;
        font-size: 0.9rem;
        border-top: 1px solid #e5e7eb;
        margin-top: 3rem;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("NewsLens Dashboard")
st.sidebar.markdown("---")

st.sidebar.markdown("""
### About NewsLens

NewsLens is an advanced news sentiment analysis platform that processes articles from multiple sources to provide insights into:

- Sentiment trends
- Source bias detection
- Entity mentions
- Keyword patterns
- Publication patterns

**Version**: 1.0.0  
**Last Updated**: December 2025
""")

st.sidebar.markdown("---")
st.sidebar.info("Use the navigation above to explore different analytics pages.")

# Main content area - Home page
st.title("Welcome to NewsLens Dashboard")
st.markdown("### Comprehensive News Analytics and Insights")

st.markdown("""
NewsLens provides deep insights into news articles from multiple sources. 
Navigate through different pages using the sidebar to explore various analytics.
""")

st.markdown("---")

# Features overview
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    #### Overview
    Comprehensive view of analyzed articles with key metrics and summary statistics.
    
    #### Sentiment Analysis
    Sentiment distribution across articles and sources with confidence metrics.
    
    #### Source Comparison
    Compare bias scores and reporting patterns across news sources.
    """)

with col2:
    st.markdown("""
    #### Entity Tracking
    Track mentions of people, organizations, and locations.
    
    #### Keyword Analysis
    Trending keywords and topics with word cloud visualizations.
    
    #### Temporal Trends
    Publication patterns and trends over time with interactive charts.
    """)

# Footer
st.markdown("""
<div class="footer">
    NewsLens Dashboard | Advanced News Sentiment Analysis Platform<br>
    Powered by Transformers, spaCy, and Streamlit
</div>
""", unsafe_allow_html=True)
