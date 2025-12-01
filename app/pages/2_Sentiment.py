"""
NewsLens Dashboard - Sentiment Analysis Page

Detailed sentiment analysis with confidence metrics, source comparisons, and sample articles.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils import (
    load_analytics_summary,
    load_articles,
    get_sentiment_color,
    format_large_number,
    create_metric_card
)

# Page configuration
st.set_page_config(
    page_title="Sentiment Analysis - NewsLens",
    page_icon="N",
    layout="wide"
)

st.title("Sentiment Analysis")
st.markdown("### Comprehensive Sentiment Insights and Confidence Metrics")

# Load data
analytics = load_analytics_summary()
articles = load_articles()

if not analytics:
    st.error("Unable to load analytics data. Please ensure the analytics files are available.")
    st.stop()

# Overall Sentiment Metrics
st.markdown("## Overall Sentiment Metrics")

sentiment_data = analytics.get("sentiment", {})
sentiments = sentiment_data.get("sentiments", {})

if sentiments:
    col1, col2, col3 = st.columns(3)
    
    for col, (sentiment_type, data) in zip([col1, col2, col3], sentiments.items()):
        with col:
            count = data.get("count", 0)
            percentage = data.get("percentage", 0)
            color = get_sentiment_color(sentiment_type)
            
            st.markdown(
                create_metric_card(
                    value=f"{count}",
                    label=f"{sentiment_type.capitalize()} ({percentage:.1f}%)",
                    color=color
                ),
                unsafe_allow_html=True
            )

st.markdown("---")

# Confidence Analysis
st.markdown("## Confidence Analysis")

confidence_stats = analytics.get("confidence_stats", {})
confidence_by_sentiment = confidence_stats.get("by_sentiment", {})

if confidence_by_sentiment:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Confidence by sentiment bar chart
        confidence_data = []
        for sentiment_type, stats in confidence_by_sentiment.items():
            confidence_data.append({
                'Sentiment': sentiment_type.capitalize(),
                'Avg Confidence': stats.get('avg', 0),
                'Min': stats.get('min', 0),
                'Max': stats.get('max', 0),
                'Count': stats.get('count', 0)
            })
        
        df_confidence = pd.DataFrame(confidence_data)
        
        fig_confidence = go.Figure()
        
        for _, row in df_confidence.iterrows():
            color = get_sentiment_color(row['Sentiment'].lower())
            fig_confidence.add_trace(go.Bar(
                name=row['Sentiment'],
                x=[row['Sentiment']],
                y=[row['Avg Confidence']],
                marker_color=color,
                text=[f"{row['Avg Confidence']:.2f}"],
                textposition='outside',
                hovertemplate=(
                    f"<b>{row['Sentiment']}</b><br>"
                    f"Avg: {row['Avg Confidence']:.2f}<br>"
                    f"Min: {row['Min']:.2f}<br>"
                    f"Max: {row['Max']:.2f}<br>"
                    f"Count: {row['Count']}<extra></extra>"
                )
            ))
        
        fig_confidence.update_layout(
            title="Average Confidence by Sentiment",
            showlegend=False,
            height=400,
            xaxis_title="",
            yaxis_title="Confidence Score",
            yaxis_range=[0, 1]
        )
        
        st.plotly_chart(fig_confidence, use_container_width=True)
    
    with col2:
        st.markdown("### Confidence Statistics")
        
        overall_stats = confidence_stats.get("overall", {})
        st.markdown(f"""
        **Overall Confidence**
        - Average: {overall_stats.get('avg', 0):.3f}
        - Minimum: {overall_stats.get('min', 0):.3f}
        - Maximum: {overall_stats.get('max', 0):.3f}
        - Total Articles: {overall_stats.get('count', 0)}
        """)
        
        st.markdown("---")
        
        st.markdown("**By Sentiment:**")
        for sentiment_type, stats in confidence_by_sentiment.items():
            st.markdown(f"""
            **{sentiment_type.capitalize()}**
            - Avg: {stats.get('avg', 0):.3f}
            - Range: {stats.get('min', 0):.2f} - {stats.get('max', 0):.2f}
            - Articles: {stats.get('count', 0)}
            """)

st.markdown("---")

# Sentiment by Source
st.markdown("## Sentiment Distribution by Source")

sentiment_by_source = analytics.get("sentiment_by_source", {})

if sentiment_by_source:
    # Prepare data for stacked bar chart
    source_sentiment_data = []
    
    for source, source_data in sentiment_by_source.items():
        sentiments_data = source_data.get("sentiments", {})
        for sentiment_type, sentiment_info in sentiments_data.items():
            source_sentiment_data.append({
                'Source': source,
                'Sentiment': sentiment_type.capitalize(),
                'Count': sentiment_info.get('count', 0),
                'Percentage': sentiment_info.get('percentage', 0)
            })
    
    df_source_sentiment = pd.DataFrame(source_sentiment_data)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Stacked bar chart
        fig_stacked = go.Figure()
        
        for sentiment_type in ['Positive', 'Neutral', 'Negative']:
            df_filtered = df_source_sentiment[df_source_sentiment['Sentiment'] == sentiment_type]
            if not df_filtered.empty:
                fig_stacked.add_trace(go.Bar(
                    name=sentiment_type,
                    x=df_filtered['Source'],
                    y=df_filtered['Count'],
                    marker_color=get_sentiment_color(sentiment_type.lower()),
                    text=df_filtered['Count'],
                    textposition='inside',
                    hovertemplate=(
                        f"<b>%{{x}}</b><br>"
                        f"{sentiment_type}: %{{y}}<br>"
                        f"<extra></extra>"
                    )
                ))
        
        fig_stacked.update_layout(
            title="Sentiment Count by Source",
            barmode='stack',
            height=400,
            xaxis_title="",
            yaxis_title="Number of Articles",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig_stacked, use_container_width=True)
    
    with col2:
        st.markdown("### Source Comparison")
        
        for source, source_data in sentiment_by_source.items():
            total = source_data.get("total_articles", 0)
            sentiments_data = source_data.get("sentiments", {})
            
            st.markdown(f"**{source}** ({total} articles)")
            
            for sentiment_type, sentiment_info in sentiments_data.items():
                percentage = sentiment_info.get('percentage', 0)
                count = sentiment_info.get('count', 0)
                st.markdown(
                    f"- {sentiment_type.capitalize()}: {count} ({percentage:.1f}%)"
                )
            
            st.markdown("")

st.markdown("---")

# Sample Articles
st.markdown("## Sample Articles by Sentiment")

if articles:
    # Group articles by sentiment
    articles_by_sentiment = {
        'positive': [],
        'neutral': [],
        'negative': []
    }
    
    for article in articles:
        sentiment = article.get('sentiment', '').lower()
        if sentiment in articles_by_sentiment:
            articles_by_sentiment[sentiment].append(article)
    
    # Create tabs for each sentiment
    tab_positive, tab_neutral, tab_negative = st.tabs(["Positive", "Neutral", "Negative"])
    
    def display_articles(sentiment_type, articles_list, tab):
        with tab:
            if not articles_list:
                st.info(f"No {sentiment_type} articles found")
                return
            
            st.markdown(f"### {len(articles_list)} {sentiment_type.capitalize()} Articles")
            
            # Show first 10 articles
            for i, article in enumerate(articles_list[:10], 1):
                confidence = article.get('sentiment_confidence', 0)
                source = article.get('source', 'Unknown')
                title = article.get('title', 'No title')
                description = article.get('description', 'No description')
                link = article.get('link', '#')
                published = article.get('published', 'Unknown date')
                
                with st.expander(f"{i}. {title[:100]}..."):
                    col_a, col_b = st.columns([3, 1])
                    
                    with col_a:
                        st.markdown(f"**Source:** {source}")
                        st.markdown(f"**Published:** {published}")
                        st.markdown(f"**Confidence:** {confidence:.3f}")
                    
                    with col_b:
                        sentiment_color = get_sentiment_color(sentiment_type)
                        st.markdown(
                            f"<div style='background-color: {sentiment_color}; "
                            f"color: white; padding: 10px; border-radius: 5px; "
                            f"text-align: center; font-weight: bold;'>"
                            f"{sentiment_type.upper()}</div>",
                            unsafe_allow_html=True
                        )
                    
                    st.markdown("---")
                    st.markdown(f"**Description:** {description}")
                    st.markdown(f"[Read full article]({link})")
            
            if len(articles_list) > 10:
                st.info(f"Showing 10 of {len(articles_list)} articles")
    
    display_articles('positive', articles_by_sentiment['positive'], tab_positive)
    display_articles('neutral', articles_by_sentiment['neutral'], tab_neutral)
    display_articles('negative', articles_by_sentiment['negative'], tab_negative)
else:
    st.warning("No articles data available for display")

# Footer
st.markdown("---")
st.caption("NewsLens Dashboard - Sentiment Analysis | Data updates every 5 minutes")
