"""
Reusable Plotly chart helpers for the NewsLens dashboard.

All functions return a ``plotly.graph_objects.Figure`` that can be passed
directly to ``st.plotly_chart()``.
"""

from typing import Any, Dict, List, Optional

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


# ---------------------------------------------------------------------------
# Colour helpers
# ---------------------------------------------------------------------------

SENTIMENT_COLORS = {
    "positive": "#10b981",
    "neutral": "#6b7280",
    "negative": "#ef4444",
    "unknown": "#9ca3af",
}


def sentiment_color(label: str) -> str:
    return SENTIMENT_COLORS.get(label.lower(), SENTIMENT_COLORS["unknown"])


# ---------------------------------------------------------------------------
# Sentiment charts
# ---------------------------------------------------------------------------


def sentiment_donut(
    labels: List[str],
    values: List[int],
    title: str = "Sentiment Distribution",
    height: int = 400,
) -> go.Figure:
    """Donut chart for sentiment distribution."""
    colors = [sentiment_color(lbl) for lbl in labels]
    fig = go.Figure(
        data=[
            go.Pie(
                labels=[lbl.capitalize() for lbl in labels],
                values=values,
                marker=dict(colors=colors),
                hole=0.45,
                textinfo="label+percent",
                hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>",
            )
        ]
    )
    fig.update_layout(
        title=title,
        height=height,
        showlegend=True,
        legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
    )
    return fig


def sentiment_bar(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    color_col: Optional[str] = None,
    title: str = "Sentiment",
    height: int = 400,
) -> go.Figure:
    """Simple vertical bar chart coloured by sentiment."""
    color_map = (
        {lbl.capitalize(): sentiment_color(lbl) for lbl in SENTIMENT_COLORS}
        if color_col
        else None
    )
    fig = px.bar(
        df,
        x=x_col,
        y=y_col,
        color=color_col,
        color_discrete_map=color_map,
        text=y_col,
        title=title,
        height=height,
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(showlegend=bool(color_col), xaxis_title="", yaxis_title=y_col)
    return fig


def stacked_sentiment_by_source(
    source_sentiment_df: pd.DataFrame,
    title: str = "Sentiment by Source",
    height: int = 420,
    use_percentage: bool = False,
) -> go.Figure:
    """
    Stacked bar chart of sentiment counts (or percentages) per source.

    Args:
        source_sentiment_df: DataFrame with columns
            ``[Source, Sentiment, Count, Percentage]``.
        use_percentage: If ``True`` stack percentages instead of raw counts.
    """
    fig = go.Figure()
    y_col = "Percentage" if use_percentage else "Count"

    for sentiment in ["Positive", "Neutral", "Negative"]:
        subset = source_sentiment_df[source_sentiment_df["Sentiment"] == sentiment]
        if subset.empty:
            continue
        fig.add_trace(
            go.Bar(
                name=sentiment,
                x=subset["Source"],
                y=subset[y_col],
                marker_color=sentiment_color(sentiment),
                text=subset[y_col].apply(
                    lambda v: f"{v:.1f}%" if use_percentage else str(int(v))
                ),
                textposition="inside",
                hovertemplate=f"<b>%{{x}}</b><br>{sentiment}: %{{y}}<extra></extra>",
            )
        )

    barmode = "stack"
    yaxis_title = "Percentage (%)" if use_percentage else "Number of Articles"
    fig.update_layout(
        title=title,
        barmode=barmode,
        height=height,
        xaxis_title="",
        yaxis_title=yaxis_title,
        legend=dict(orientation="h", y=1.05, x=1, xanchor="right"),
    )
    return fig


# ---------------------------------------------------------------------------
# Trend / timeline charts
# ---------------------------------------------------------------------------


def sentiment_timeline(
    timeline_data: List[Dict[str, Any]],
    title: str = "Sentiment Over Time",
    height: int = 420,
) -> go.Figure:
    """
    Line chart showing positive / neutral / negative counts over time.

    Args:
        timeline_data: List from ``TrendAnalysis.sentiment_over_time()``.
    """
    if not timeline_data:
        return go.Figure()

    df = pd.DataFrame(timeline_data)
    fig = go.Figure()

    for sentiment, color in [
        ("positive", SENTIMENT_COLORS["positive"]),
        ("neutral", SENTIMENT_COLORS["neutral"]),
        ("negative", SENTIMENT_COLORS["negative"]),
    ]:
        if sentiment not in df.columns:
            continue
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df[sentiment],
                mode="lines+markers",
                name=sentiment.capitalize(),
                line=dict(color=color, width=2),
                marker=dict(size=5),
                hovertemplate=f"<b>{sentiment.capitalize()}</b><br>%{{x}}<br>Count: %{{y}}<extra></extra>",
            )
        )

    fig.update_layout(
        title=title,
        height=height,
        xaxis_title="Date",
        yaxis_title="Article Count",
        hovermode="x unified",
        legend=dict(orientation="h", y=1.05, x=1, xanchor="right"),
    )
    return fig


def momentum_chart(
    momentum_data: List[Dict[str, Any]],
    title: str = "Sentiment Momentum",
    height: int = 300,
) -> go.Figure:
    """
    Area chart for rolling sentiment momentum score (–1 to +1).

    Args:
        momentum_data: List from ``TrendAnalysis.get_sentiment_momentum()``.
    """
    if not momentum_data:
        return go.Figure()

    df = pd.DataFrame(momentum_data)
    colors = ["#10b981" if s >= 0 else "#ef4444" for s in df["score"]]

    fig = go.Figure(
        go.Bar(
            x=df["timestamp"],
            y=df["score"],
            marker_color=colors,
            hovertemplate="<b>%{x}</b><br>Score: %{y:.3f}<extra></extra>",
        )
    )
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    fig.update_layout(
        title=title,
        height=height,
        xaxis_title="",
        yaxis_title="Score",
        yaxis_range=[-1, 1],
    )
    return fig


# ---------------------------------------------------------------------------
# Entity / keyword charts
# ---------------------------------------------------------------------------


def top_keywords_bar(
    keywords: List[Dict[str, Any]],
    keyword_col: str = "keyword",
    count_col: str = "frequency",
    title: str = "Top Keywords",
    top_n: int = 15,
    height: int = 480,
) -> go.Figure:
    """Horizontal bar chart of keyword frequencies."""
    if not keywords:
        return go.Figure()

    df = pd.DataFrame(keywords[:top_n])
    if keyword_col not in df.columns or count_col not in df.columns:
        return go.Figure()

    fig = px.bar(
        df.sort_values(count_col),
        x=count_col,
        y=keyword_col,
        orientation="h",
        color=count_col,
        color_continuous_scale="Blues",
        text=count_col,
        title=title,
        height=height,
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        showlegend=False,
        xaxis_title="Frequency",
        yaxis_title="",
        coloraxis_showscale=False,
    )
    return fig


def bias_score_chart(
    bias_df: pd.DataFrame,
    source_col: str = "Source",
    score_col: str = "Bias Score",
    title: str = "Sentiment Bias by Source",
    height: int = 380,
) -> go.Figure:
    """Bar chart of per-source bias scores with a zero baseline."""
    fig = go.Figure()
    for _, row in bias_df.iterrows():
        score = row[score_col]
        color = "#10b981" if score > 0.05 else ("#ef4444" if score < -0.05 else "#6b7280")
        fig.add_trace(
            go.Bar(
                x=[row[source_col]],
                y=[score],
                marker_color=color,
                text=[f"{score:.3f}"],
                textposition="outside",
                hovertemplate=f"<b>{row[source_col]}</b><br>Bias: {score:.3f}<extra></extra>",
            )
        )

    fig.add_hline(y=0, line_dash="dash", line_color="gray", line_width=1.5)
    fig.update_layout(
        title=title,
        showlegend=False,
        height=height,
        xaxis_title="",
        yaxis_title="Bias Score",
        yaxis_range=[-1.05, 1.05],
    )
    return fig
