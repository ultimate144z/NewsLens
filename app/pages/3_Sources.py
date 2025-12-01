"""
NewsLens Dashboard - Sources Analysis Page

Source comparison, bias detection, and detailed source metrics.
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
    get_bias_color,
    format_large_number,
    create_metric_card
)

# Page configuration
st.set_page_config(
    page_title="Sources Analysis - NewsLens",
    page_icon="N",
    layout="wide"
)

st.title("Sources Analysis")
st.markdown("### Source Comparison, Bias Detection, and Detailed Metrics")

# Load data
analytics = load_analytics_summary()
articles = load_articles()

if not analytics:
    st.error("Unable to load analytics data. Please ensure the analytics files are available.")
    st.stop()

source_comparison = analytics.get("source_comparison", {})

if not source_comparison:
    st.warning("No source comparison data available")
    st.stop()

# Overview Metrics
st.markdown("## Source Overview")

cols = st.columns(len(source_comparison))

for col, (source_name, source_data) in zip(cols, source_comparison.items()):
    with col:
        total_articles = source_data.get("total_articles", 0)
        avg_confidence = source_data.get("avg_confidence", 0)
        
        st.markdown(
            create_metric_card(
                value=str(total_articles),
                label=source_name,
                color="#1e3a8a"
            ),
            unsafe_allow_html=True
        )
        st.markdown(f"**Avg Confidence:** {avg_confidence:.3f}")

st.markdown("---")

# Bias Analysis
st.markdown("## Sentiment Bias Analysis")

st.info(
    "Bias score indicates the tendency of a source towards positive or negative sentiment. "
    "Positive scores indicate positive bias, negative scores indicate negative bias, "
    "and scores near zero indicate neutral reporting."
)

# Prepare bias data
bias_data = []
for source_name, source_data in source_comparison.items():
    bias_info = source_data.get("sentiment_bias", {})
    bias_score = bias_info.get("score", 0)
    tendency = bias_info.get("tendency", "neutral")
    
    bias_data.append({
        'Source': source_name,
        'Bias Score': bias_score,
        'Tendency': tendency.capitalize(),
        'Positive %': bias_info.get('positive_ratio', 0) * 100,
        'Negative %': bias_info.get('negative_ratio', 0) * 100,
        'Neutral %': bias_info.get('neutral_ratio', 0) * 100
    })

df_bias = pd.DataFrame(bias_data)

col1, col2 = st.columns([2, 1])

with col1:
    # Bias score chart
    fig_bias = go.Figure()
    
    for _, row in df_bias.iterrows():
        color = get_bias_color(row['Bias Score'])
        fig_bias.add_trace(go.Bar(
            name=row['Source'],
            x=[row['Source']],
            y=[row['Bias Score']],
            marker_color=color,
            text=[f"{row['Bias Score']:.3f}"],
            textposition='outside',
            hovertemplate=(
                f"<b>{row['Source']}</b><br>"
                f"Bias Score: {row['Bias Score']:.3f}<br>"
                f"Tendency: {row['Tendency']}<br>"
                f"<extra></extra>"
            )
        ))
    
    fig_bias.update_layout(
        title="Sentiment Bias Score by Source",
        showlegend=False,
        height=400,
        xaxis_title="",
        yaxis_title="Bias Score",
        yaxis_range=[-1, 1],
        shapes=[
            dict(
                type="line",
                x0=-0.5,
                x1=len(df_bias) - 0.5,
                y0=0,
                y1=0,
                line=dict(color="gray", width=2, dash="dash")
            )
        ]
    )
    
    st.plotly_chart(fig_bias, use_container_width=True)

with col2:
    st.markdown("### Bias Interpretation")
    
    for _, row in df_bias.iterrows():
        bias_score = row['Bias Score']
        color = get_bias_color(bias_score)
        
        st.markdown(f"**{row['Source']}**")
        st.markdown(
            f"<div style='background-color: {color}; color: white; "
            f"padding: 8px; border-radius: 5px; margin-bottom: 10px;'>"
            f"Bias Score: {bias_score:.3f} ({row['Tendency']})</div>",
            unsafe_allow_html=True
        )

st.markdown("---")

# Sentiment Distribution Comparison
st.markdown("## Sentiment Distribution by Source")

col1, col2 = st.columns([2, 1])

with col1:
    # 100% stacked bar chart
    fig_dist = go.Figure()
    
    for sentiment_type in ['Positive', 'Neutral', 'Negative']:
        percentages = []
        sources = []
        
        for source_name, source_data in source_comparison.items():
            sources.append(source_name)
            sentiment_dist = source_data.get("sentiment_distribution", {})
            sentiment_info = sentiment_dist.get(sentiment_type.lower(), {})
            percentage = sentiment_info.get("percentage", 0)
            percentages.append(percentage)
        
        fig_dist.add_trace(go.Bar(
            name=sentiment_type,
            x=sources,
            y=percentages,
            marker_color=get_sentiment_color(sentiment_type.lower()),
            text=[f"{p:.1f}%" for p in percentages],
            textposition='inside',
            hovertemplate=(
                f"<b>%{{x}}</b><br>"
                f"{sentiment_type}: %{{y:.1f}}%<br>"
                f"<extra></extra>"
            )
        ))
    
    fig_dist.update_layout(
        title="Sentiment Distribution (%) by Source",
        barmode='stack',
        height=400,
        xaxis_title="",
        yaxis_title="Percentage",
        yaxis_range=[0, 100],
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig_dist, use_container_width=True)

with col2:
    st.markdown("### Distribution Details")
    
    for _, row in df_bias.iterrows():
        st.markdown(f"**{row['Source']}**")
        st.markdown(f"- Positive: {row['Positive %']:.1f}%")
        st.markdown(f"- Neutral: {row['Neutral %']:.1f}%")
        st.markdown(f"- Negative: {row['Negative %']:.1f}%")
        st.markdown("")

st.markdown("---")

# Detailed Source Metrics
st.markdown("## Detailed Source Metrics")

# Create comparison table
comparison_data = []

for source_name, source_data in source_comparison.items():
    sentiment_dist = source_data.get("sentiment_distribution", {})
    bias_info = source_data.get("sentiment_bias", {})
    
    comparison_data.append({
        'Source': source_name,
        'Total Articles': source_data.get("total_articles", 0),
        'Avg Confidence': f"{source_data.get('avg_confidence', 0):.3f}",
        'Positive %': f"{sentiment_dist.get('positive', {}).get('percentage', 0):.1f}%",
        'Neutral %': f"{sentiment_dist.get('neutral', {}).get('percentage', 0):.1f}%",
        'Negative %': f"{sentiment_dist.get('negative', {}).get('percentage', 0):.1f}%",
        'Bias Score': f"{bias_info.get('score', 0):.3f}",
        'Tendency': bias_info.get('tendency', 'neutral').capitalize()
    })

df_comparison = pd.DataFrame(comparison_data)

st.dataframe(
    df_comparison,
    use_container_width=True,
    hide_index=True
)

st.markdown("---")

# Top Entities by Source
st.markdown("## Top Entities by Source")

source_tabs = st.tabs(list(source_comparison.keys()))

for tab, (source_name, source_data) in zip(source_tabs, source_comparison.items()):
    with tab:
        st.markdown(f"### {source_name}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### Top Entities")
            top_entities = source_data.get("top_entities", [])[:10]
            if top_entities:
                for i, entity_data in enumerate(top_entities, 1):
                    entity = entity_data.get('entity', 'N/A')
                    count = entity_data.get('count', 0)
                    st.markdown(f"{i}. **{entity}** - {count} mentions")
            else:
                st.info("No entity data available")
        
        with col2:
            st.markdown("#### Top Keywords")
            top_keywords = source_data.get("top_keywords", [])[:10]
            if top_keywords:
                for i, keyword_data in enumerate(top_keywords, 1):
                    keyword = keyword_data.get('keyword', 'N/A')
                    count = keyword_data.get('count', 0)
                    st.markdown(f"{i}. **{keyword}** - {count} occurrences")
            else:
                st.info("No keyword data available")
        
        with col3:
            st.markdown("#### Metrics")
            st.metric("Total Articles", source_data.get("total_articles", 0))
            st.metric("Avg Confidence", f"{source_data.get('avg_confidence', 0):.3f}")
            
            sentiment_dist = source_data.get("sentiment_distribution", {})
            pos_count = sentiment_dist.get('positive', {}).get('count', 0)
            neu_count = sentiment_dist.get('neutral', {}).get('count', 0)
            neg_count = sentiment_dist.get('negative', {}).get('count', 0)
            
            st.markdown("**Sentiment Counts:**")
            st.markdown(f"- Positive: {pos_count}")
            st.markdown(f"- Neutral: {neu_count}")
            st.markdown(f"- Negative: {neg_count}")

st.markdown("---")

# Source Articles Sample
st.markdown("## Sample Articles by Source")

if articles:
    # Group articles by source
    articles_by_source = {}
    for article in articles:
        source = article.get('source', 'Unknown')
        if source not in articles_by_source:
            articles_by_source[source] = []
        articles_by_source[source].append(article)
    
    # Create selectbox for source selection
    selected_source = st.selectbox(
        "Select a source to view sample articles:",
        options=list(articles_by_source.keys())
    )
    
    if selected_source and selected_source in articles_by_source:
        source_articles = articles_by_source[selected_source][:5]
        
        st.markdown(f"### {selected_source} - Sample Articles ({len(source_articles)} shown)")
        
        for i, article in enumerate(source_articles, 1):
            sentiment = article.get('sentiment', 'unknown')
            confidence = article.get('sentiment_confidence', 0)
            title = article.get('title', 'No title')
            description = article.get('description', 'No description')
            link = article.get('link', '#')
            published = article.get('published', 'Unknown date')
            
            with st.expander(f"{i}. {title[:80]}..."):
                col_a, col_b = st.columns([3, 1])
                
                with col_a:
                    st.markdown(f"**Published:** {published}")
                    st.markdown(f"**Sentiment:** {sentiment.capitalize()}")
                    st.markdown(f"**Confidence:** {confidence:.3f}")
                
                with col_b:
                    sentiment_color = get_sentiment_color(sentiment)
                    st.markdown(
                        f"<div style='background-color: {sentiment_color}; "
                        f"color: white; padding: 10px; border-radius: 5px; "
                        f"text-align: center; font-weight: bold;'>"
                        f"{sentiment.upper()}</div>",
                        unsafe_allow_html=True
                    )
                
                st.markdown("---")
                st.markdown(f"**Description:** {description}")
                st.markdown(f"[Read full article]({link})")
else:
    st.warning("No articles data available")

# Footer
st.markdown("---")
st.caption("NewsLens Dashboard - Sources Analysis | Data updates every 5 minutes")
