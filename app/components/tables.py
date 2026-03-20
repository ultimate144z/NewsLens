"""
Reusable table display helpers for the NewsLens dashboard.

Functions in this module render Streamlit components directly (they call
``st.*`` internally) so callers only need to pass data.
"""

from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st

from app.utils import get_sentiment_color, truncate_text


# ---------------------------------------------------------------------------
# Article tables
# ---------------------------------------------------------------------------


def articles_table(
    articles: List[Dict[str, Any]],
    max_rows: int = 50,
    show_link: bool = True,
) -> None:
    """
    Display a paginated, colour-coded table of articles.

    Columns shown: Title, Source, Sentiment, Confidence, Published.
    """
    if not articles:
        st.info("No articles to display.")
        return

    rows = []
    for art in articles[:max_rows]:
        sentiment = art.get("sentiment", "unknown")
        rows.append(
            {
                "Title": truncate_text(art.get("title", ""), 90),
                "Source": art.get("source", "—"),
                "Sentiment": sentiment.capitalize(),
                "Confidence": f"{art.get('sentiment_confidence', 0):.2f}",
                "Published": art.get("published", "—")[:16],
                "_link": art.get("link", ""),
                "_sentiment": sentiment,
            }
        )

    df = pd.DataFrame(rows)

    # Colour-code sentiment column via pandas Styler
    def highlight_sentiment(val: str) -> str:
        color_map = {
            "Positive": "#d1fae5",
            "Neutral": "#f3f4f6",
            "Negative": "#fee2e2",
        }
        bg = color_map.get(val, "")
        return f"background-color: {bg};" if bg else ""

    display_cols = ["Title", "Source", "Sentiment", "Confidence", "Published"]
    styled = df[display_cols].style.applymap(highlight_sentiment, subset=["Sentiment"])

    st.dataframe(styled, use_container_width=True, hide_index=True)

    if len(articles) > max_rows:
        st.caption(f"Showing {max_rows} of {len(articles)} articles.")


def article_expanders(
    articles: List[Dict[str, Any]],
    max_shown: int = 10,
) -> None:
    """
    Render each article as a collapsible expander with full metadata.
    """
    if not articles:
        st.info("No articles to display.")
        return

    for i, article in enumerate(articles[:max_shown], 1):
        sentiment = article.get("sentiment", "unknown")
        title = article.get("title", "No title")
        confidence = article.get("sentiment_confidence", 0.0)

        with st.expander(f"{i}. {truncate_text(title, 100)}"):
            col_meta, col_badge = st.columns([3, 1])

            with col_meta:
                st.markdown(f"**Source:** {article.get('source', '—')}")
                st.markdown(f"**Published:** {article.get('published', '—')}")
                st.markdown(f"**Confidence:** {confidence:.3f}")

            with col_badge:
                color = get_sentiment_color(sentiment)
                st.markdown(
                    f"<div style='background:{color};color:white;padding:10px;"
                    f"border-radius:6px;text-align:center;font-weight:bold;'>"
                    f"{sentiment.upper()}</div>",
                    unsafe_allow_html=True,
                )

            st.markdown("---")
            description = article.get("description", "")
            if description:
                st.markdown(f"**Description:** {description}")

            link = article.get("link", "")
            if link:
                st.markdown(f"[Read full article ↗]({link})")

    if len(articles) > max_shown:
        st.info(f"Showing {max_shown} of {len(articles)} articles.")


# ---------------------------------------------------------------------------
# Summary / stats tables
# ---------------------------------------------------------------------------


def source_metrics_table(source_data: Dict[str, Dict[str, Any]]) -> None:
    """
    Render a comparative metrics table for multiple sources.

    Args:
        source_data: Mapping from source name → dict containing keys such as
            ``total_articles``, ``avg_confidence``, ``sentiment_bias``,
            ``sentiment_distribution``.
    """
    if not source_data:
        st.info("No source data available.")
        return

    rows = []
    for source, data in source_data.items():
        bias = data.get("sentiment_bias", {})
        dist = data.get("sentiment_distribution", {})
        rows.append(
            {
                "Source": source,
                "Articles": data.get("total_articles", 0),
                "Avg Confidence": f"{data.get('avg_confidence', 0):.3f}",
                "Positive %": f"{dist.get('positive', {}).get('percentage', 0):.1f}%",
                "Neutral %": f"{dist.get('neutral', {}).get('percentage', 0):.1f}%",
                "Negative %": f"{dist.get('negative', {}).get('percentage', 0):.1f}%",
                "Bias Score": f"{bias.get('score', 0):.3f}",
                "Tendency": bias.get("tendency", "neutral").capitalize(),
            }
        )

    df = pd.DataFrame(rows).sort_values("Articles", ascending=False)
    st.dataframe(df, use_container_width=True, hide_index=True)


def entity_ranking_table(
    entities: List[Dict[str, Any]],
    label: str = "Entity",
    count_label: str = "Mentions",
) -> None:
    """
    Simple ranked table for entities or keywords.

    Args:
        entities: List of dicts, each with ``'entity'`` and ``'mentions'``
            keys (or ``'keyword'`` / ``'frequency'`` for keywords).
    """
    if not entities:
        st.info("No data available.")
        return

    # Normalise key names
    rows = []
    for i, item in enumerate(entities, 1):
        name = item.get("entity") or item.get("keyword") or item.get("text", "—")
        count = item.get("mentions") or item.get("frequency") or item.get("count", 0)
        rows.append({"#": i, label: name, count_label: count})

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)
