"""
Trend Analysis Module

Analyses sentiment and topic trends over time from news articles.
"""

from collections import defaultdict, Counter
from datetime import datetime
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class TrendAnalysis:
    """Analyses temporal trends in news sentiment and topics."""

    def __init__(self, articles: List[Dict[str, Any]]):
        """
        Args:
            articles: List of analysed article dictionaries.
        """
        self.articles = articles

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def sentiment_over_time(self, interval: str = "day") -> List[Dict[str, Any]]:
        """
        Aggregate sentiment counts across equal time buckets.

        Args:
            interval: Grouping bucket – ``'hour'``, ``'day'`` (default), or
                ``'week'``.

        Returns:
            List of ``{timestamp, total, positive, neutral, negative}`` dicts
            sorted chronologically.
        """
        buckets: Dict[str, Counter] = defaultdict(Counter)

        for article in self.articles:
            dt = self._parse_date(article.get("published", ""))
            if dt is None:
                continue
            key = self._bucket_key(dt, interval)
            sentiment = article.get("sentiment", "unknown").lower()
            buckets[key][sentiment] += 1

        result = []
        for ts in sorted(buckets):
            counts = buckets[ts]
            result.append(
                {
                    "timestamp": ts,
                    "total": sum(counts.values()),
                    "positive": counts.get("positive", 0),
                    "neutral": counts.get("neutral", 0),
                    "negative": counts.get("negative", 0),
                }
            )

        logger.info("sentiment_over_time: %d buckets (%s interval)", len(result), interval)
        return result

    def top_keywords_over_time(
        self, top_n: int = 10, interval: str = "day"
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Return the most frequent keywords for each time bucket.

        Returns:
            Mapping of timestamp → list of ``{keyword, count}`` dicts.
        """
        buckets: Dict[str, Counter] = defaultdict(Counter)

        for article in self.articles:
            dt = self._parse_date(article.get("published", ""))
            if dt is None:
                continue
            key = self._bucket_key(dt, interval)
            for kw in article.get("keywords", []):
                word = kw.get("text", "").strip().lower()
                if word:
                    buckets[key][word] += kw.get("count", 1)

        result = {}
        for ts in sorted(buckets):
            result[ts] = [
                {"keyword": kw, "count": cnt}
                for kw, cnt in buckets[ts].most_common(top_n)
            ]

        return result

    def source_volume_over_time(
        self, interval: str = "day"
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Article volume per source per time bucket.

        Returns:
            Mapping of source name → list of ``{timestamp, count}`` dicts.
        """
        source_buckets: Dict[str, Counter] = defaultdict(Counter)

        for article in self.articles:
            dt = self._parse_date(article.get("published", ""))
            if dt is None:
                continue
            key = self._bucket_key(dt, interval)
            source = article.get("source", "Unknown")
            source_buckets[source][key] += 1

        result = {}
        for source, bucket in source_buckets.items():
            result[source] = [
                {"timestamp": ts, "count": cnt}
                for ts, cnt in sorted(bucket.items())
            ]

        return result

    def get_sentiment_momentum(self, window: int = 3) -> List[Dict[str, Any]]:
        """
        Calculate a simple rolling-average sentiment score over time.

        A score of +1 means all articles positive; –1 means all negative.

        Args:
            window: Number of consecutive days to average.

        Returns:
            List of ``{timestamp, score, direction}`` dicts.
        """
        daily = self.sentiment_over_time(interval="day")
        if not daily:
            return []

        scores = []
        for entry in daily:
            total = entry["total"]
            if total == 0:
                scores.append(0.0)
            else:
                scores.append(
                    (entry["positive"] - entry["negative"]) / total
                )

        result = []
        for i, entry in enumerate(daily):
            start = max(0, i - window + 1)
            avg_score = sum(scores[start : i + 1]) / (i - start + 1)
            prev = scores[i - 1] if i > 0 else avg_score
            direction = "up" if avg_score > prev else ("down" if avg_score < prev else "stable")
            result.append(
                {
                    "timestamp": entry["timestamp"],
                    "score": round(avg_score, 4),
                    "direction": direction,
                }
            )

        return result

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_date(date_string: str) -> Optional[datetime]:
        formats = [
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%a, %d %b %Y %H:%M:%S %z",
            "%a, %d %b %Y %H:%M:%S GMT",
        ]
        for fmt in formats:
            try:
                return datetime.strptime(date_string.strip(), fmt)
            except (ValueError, AttributeError):
                continue
        return None

    @staticmethod
    def _bucket_key(dt: datetime, interval: str) -> str:
        if interval == "hour":
            return dt.strftime("%Y-%m-%d %H:00")
        if interval == "week":
            return dt.strftime("%Y-W%U")
        return dt.strftime("%Y-%m-%d")
