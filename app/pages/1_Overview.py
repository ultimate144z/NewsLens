"""
NewsLens Dashboard - Overview Page

Displays key metrics, sentiment distribution, top sources, and entity mentions.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys
from pathlib import Path

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
    page_title="Overview - NewsLens",
    page_icon="N",
    layout="wide"
)

st.title("Overview")
st.markdown("### Key Metrics and Summary Statistics")

# Load data
analytics = load_analytics_summary()
articles = load_articles()

if not analytics:
    st.error("Unable to load analytics data. Please ensure the analytics files are available.")
    st.stop()

if not articles:
    st.warning("Unable to load articles data. Some features may be limited.")

# Key Metrics Row
st.markdown("## Key Metrics")
col1, col2, col3, col4 = st.columns(4)

overview = analytics.get("overview", {})
confidence_stats = analytics.get("confidence_stats", {}).get("overall", {})
date_range = overview.get("date_range", {})

with col1:
    total_articles = overview.get("total_articles", 0)
    st.markdown(
        create_metric_card(
            value=format_large_number(total_articles),
            label="Total Articles",
            color="#1e3a8a"
        ),
        unsafe_allow_html=True
    )

with col2:
    total_sources = overview.get("sources", 0)
    st.markdown(
        create_metric_card(
            value=str(total_sources),
            label="News Sources",
            color="#2563eb"
        ),
        unsafe_allow_html=True
    )

with col3:
    avg_confidence = confidence_stats.get("avg", 0)
    st.markdown(
        create_metric_card(
            value=f"{avg_confidence:.2f}",
            label="Avg Confidence",
            color="#3b82f6"
        ),
        unsafe_allow_html=True
    )

with col4:
    span_days = date_range.get("span_days", 0)
    st.markdown(
        create_metric_card(
            value=str(span_days),
            label="Days Analyzed",
            color="#60a5fa"
        ),
        unsafe_allow_html=True
    )

st.markdown("---")

# Date Range Info
if date_range:
    st.info(
        f"Data Range: {date_range.get('start', 'N/A')} to {date_range.get('end', 'N/A')}"
    )

# Sentiment Distribution
st.markdown("## Sentiment Distribution")

sentiment_data = analytics.get("sentiment", {})
sentiments = sentiment_data.get("sentiments", {})

if sentiments:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Pie chart
        sentiment_labels = []
        sentiment_values = []
        sentiment_colors = []
        
        for sentiment_type, data in sentiments.items():
            sentiment_labels.append(sentiment_type.capitalize())
            sentiment_values.append(data.get("count", 0))
            sentiment_colors.append(get_sentiment_color(sentiment_type))
        
        fig_pie = go.Figure(data=[go.Pie(
            labels=sentiment_labels,
            values=sentiment_values,
            marker=dict(colors=sentiment_colors),
            hole=0.4,
            textinfo='label+percent',
            textposition='auto',
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        )])
        
        fig_pie.update_layout(
            title="Overall Sentiment Distribution",
            height=400,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            )
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Bar chart with counts
        df_sentiment = pd.DataFrame([
            {
                'Sentiment': s.capitalize(),
                'Count': d.get('count', 0),
                'Percentage': d.get('percentage', 0)
            }
            for s, d in sentiments.items()
        ])
        
        fig_bar = px.bar(
            df_sentiment,
            x='Sentiment',
            y='Count',
            color='Sentiment',
            color_discrete_map={
                'Positive': get_sentiment_color('positive'),
                'Neutral': get_sentiment_color('neutral'),
                'Negative': get_sentiment_color('negative')
            },
            text='Count',
            title="Article Count by Sentiment"
        )
        
        fig_bar.update_traces(textposition='outside')
        fig_bar.update_layout(
            showlegend=False,
            height=400,
            xaxis_title="",
            yaxis_title="Number of Articles"
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# Top Sources
st.markdown("## Top Sources")

source_comparison = analytics.get("source_comparison", {})

if source_comparison:
    # Prepare data for bar chart
    source_data = []
    for source_name, source_info in source_comparison.items():
        source_data.append({
            'Source': source_name,
            'Articles': source_info.get('total_articles', 0),
            'Avg Confidence': source_info.get('avg_confidence', 0)
        })
    
    df_sources = pd.DataFrame(source_data)
    df_sources = df_sources.sort_values('Articles', ascending=False)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig_sources = px.bar(
            df_sources,
            x='Source',
            y='Articles',
            title="Articles by Source",
            color='Articles',
            color_continuous_scale='Blues',
            text='Articles'
        )
        
        fig_sources.update_traces(textposition='outside')
        fig_sources.update_layout(
            showlegend=False,
            height=400,
            xaxis_title="",
            yaxis_title="Number of Articles"
        )
        
        st.plotly_chart(fig_sources, use_container_width=True)
    
    with col2:
        st.markdown("### Source Statistics")
        for _, row in df_sources.iterrows():
            st.markdown(f"""
            **{row['Source']}**
            - Articles: {row['Articles']}
            - Avg Confidence: {row['Avg Confidence']:.2f}
            """)

st.markdown("---")

# Top Entities
st.markdown("## Top Entities")

top_entities = analytics.get("top_entities", {})

if top_entities:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### Top People")
        people = top_entities.get("people", [])[:10]
        if people:
            for i, entity in enumerate(people, 1):
                st.markdown(
                    f"{i}. **{entity.get('entity', 'N/A')}** - "
                    f"{entity.get('mentions', 0)} mentions"
                )
        else:
            st.info("No people entities found")
    
    with col2:
        st.markdown("### Top Organizations")
        organizations = top_entities.get("organizations", [])[:10]
        if organizations:
            for i, entity in enumerate(organizations, 1):
                st.markdown(
                    f"{i}. **{entity.get('entity', 'N/A')}** - "
                    f"{entity.get('mentions', 0)} mentions"
                )
        else:
            st.info("No organization entities found")
    
    with col3:
        st.markdown("### Top Locations")
        locations = top_entities.get("locations", [])[:10]
        if locations:
            for i, entity in enumerate(locations, 1):
                st.markdown(
                    f"{i}. **{entity.get('entity', 'N/A')}** - "
                    f"{entity.get('mentions', 0)} mentions"
                )
        else:
            st.info("No location entities found")

st.markdown("---")

# Top Keywords
st.markdown("## Top Keywords")

top_keywords = analytics.get("top_keywords", [])[:20]

if top_keywords:
    # Filter out invalid keywords (like URLs)
    valid_keywords = [
        kw for kw in top_keywords 
        if not kw.get('keyword', '').startswith('href=') and len(kw.get('keyword', '')) > 2
    ][:15]
    
    if valid_keywords:
        df_keywords = pd.DataFrame(valid_keywords)
        
        fig_keywords = px.bar(
            df_keywords,
            x='frequency',
            y='keyword',
            orientation='h',
            title="Most Frequent Keywords",
            color='frequency',
            color_continuous_scale='Viridis',
            text='frequency'
        )
        
        fig_keywords.update_traces(textposition='outside')
        fig_keywords.update_layout(
            showlegend=False,
            height=500,
            xaxis_title="Frequency",
            yaxis_title="",
            yaxis={'categoryorder': 'total ascending'}
        )
        
        st.plotly_chart(fig_keywords, use_container_width=True)
    else:
        st.info("No valid keywords found")
else:
    st.info("No keyword data available")

# Footer
st.markdown("---")
st.caption("NewsLens Dashboard - Overview | Data updates every 5 minutes")
