"""
Sidebar filter components for the NewsLens dashboard.

Each function renders Streamlit sidebar widgets and returns the chosen
values, so page scripts can stay focused on layout and visualisation.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import streamlit as st


def sentiment_filter(key: str = "sentiment_filter") -> Optional[str]:
    """
    Radio selector for a single sentiment label.

    Returns:
        ``'positive'``, ``'neutral'``, ``'negative'``, or ``None`` (All).
    """
    options = ["All", "Positive", "Neutral", "Negative"]
    choice = st.sidebar.radio("Sentiment", options, key=key)
    return None if choice == "All" else choice.lower()


def source_filter(
    available_sources: List[str], key: str = "source_filter"
) -> List[str]:
    """
    Multi-select for news sources.

    Returns:
        Selected source names; empty list means "all sources".
    """
    selected = st.sidebar.multiselect(
        "Sources",
        options=sorted(available_sources),
        default=[],
        key=key,
        placeholder="All sources",
    )
    return selected


def date_range_filter(
    min_date: Optional[datetime] = None,
    max_date: Optional[datetime] = None,
    key_prefix: str = "date",
) -> Tuple[datetime, datetime]:
    """
    Two date inputs (start / end) rendered in the sidebar.

    Returns:
        ``(start_date, end_date)`` as ``datetime`` objects.
    """
    today = datetime.utcnow().date()
    default_start = (datetime.utcnow() - timedelta(days=7)).date()

    start = st.sidebar.date_input(
        "From",
        value=min_date.date() if min_date else default_start,
        max_value=today,
        key=f"{key_prefix}_start",
    )
    end = st.sidebar.date_input(
        "To",
        value=max_date.date() if max_date else today,
        max_value=today,
        key=f"{key_prefix}_end",
    )

    # Ensure chronological order
    if start > end:
        start, end = end, start

    return (
        datetime.combine(start, datetime.min.time()),
        datetime.combine(end, datetime.max.time()),
    )


def confidence_threshold_filter(key: str = "conf_threshold") -> float:
    """
    Slider for minimum sentiment-confidence threshold.

    Returns:
        Float in ``[0.0, 1.0]``.
    """
    return st.sidebar.slider(
        "Min confidence",
        min_value=0.0,
        max_value=1.0,
        value=0.0,
        step=0.05,
        key=key,
        help="Only show articles where the model confidence is at or above this value.",
    )


def keyword_search_filter(key: str = "keyword_search") -> str:
    """
    Text input for keyword search.

    Returns:
        Stripped search string (may be empty).
    """
    return st.sidebar.text_input(
        "Search keyword",
        value="",
        key=key,
        placeholder="e.g. climate",
    ).strip()


def apply_article_filters(
    articles: List[Dict[str, Any]],
    sentiment: Optional[str] = None,
    sources: Optional[List[str]] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    min_confidence: float = 0.0,
    keyword: str = "",
) -> List[Dict[str, Any]]:
    """
    Apply a set of filters to a list of article dicts.

    Args:
        articles: Full list of article dicts.
        sentiment: Filter to this sentiment label, or ``None`` for all.
        sources: Keep only these sources; ``None`` / empty list means all.
        start_date: Keep articles published on or after this datetime.
        end_date: Keep articles published on or before this datetime.
        min_confidence: Minimum ``sentiment_confidence`` value.
        keyword: Case-insensitive substring match against title + description.

    Returns:
        Filtered list.
    """
    result = articles

    if sentiment:
        result = [a for a in result if a.get("sentiment", "").lower() == sentiment]

    if sources:
        sources_lower = {s.lower() for s in sources}
        result = [a for a in result if a.get("source", "").lower() in sources_lower]

    if min_confidence > 0:
        result = [
            a for a in result if a.get("sentiment_confidence", 0.0) >= min_confidence
        ]

    if keyword:
        kw = keyword.lower()
        result = [
            a
            for a in result
            if kw in a.get("title", "").lower()
            or kw in a.get("description", "").lower()
        ]

    # Date filtering is best-effort; many RSS dates are plain strings
    if start_date or end_date:
        filtered = []
        for article in result:
            pub = article.get("published", "")
            try:
                dt = _parse_date(pub)
                if start_date and dt < start_date:
                    continue
                if end_date and dt > end_date:
                    continue
                filtered.append(article)
            except Exception:
                filtered.append(article)  # keep if unparseable
        result = filtered

    return result


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _parse_date(s: str) -> datetime:
    for fmt in (
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ):
        try:
            return datetime.strptime(s.strip(), fmt)
        except (ValueError, AttributeError):
            continue
    raise ValueError(f"Cannot parse date: {s!r}")
