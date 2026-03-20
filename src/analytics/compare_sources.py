"""
Source Comparison Module

Compares news sources by sentiment profile, volume, entity focus, and
reporting overlap to surface potential media bias patterns.
"""

from collections import Counter, defaultdict
from typing import Any, Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class SourceComparison:
    """Compare sentiment profiles and entity coverage across news sources."""

    def __init__(self, articles: List[Dict[str, Any]]):
        """
        Args:
            articles: List of analysed article dictionaries.
        """
        self.articles = articles
        self._by_source: Dict[str, List[Dict]] = self._group_by_source()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def sentiment_profiles(self) -> Dict[str, Dict[str, Any]]:
        """
        Return per-source sentiment distribution and bias score.

        Returns:
            Mapping of source name → ``{total, positive_pct, neutral_pct,
            negative_pct, bias_score}``.
        """
        result = {}
        for source, arts in self._by_source.items():
            counts = Counter(
                a.get("sentiment", "unknown").lower() for a in arts
            )
            total = len(arts)
            pos = counts.get("positive", 0)
            neu = counts.get("neutral", 0)
            neg = counts.get("negative", 0)
            bias = round((pos - neg) / total, 4) if total else 0.0

            result[source] = {
                "total": total,
                "positive_pct": round(pos / total * 100, 2) if total else 0,
                "neutral_pct": round(neu / total * 100, 2) if total else 0,
                "negative_pct": round(neg / total * 100, 2) if total else 0,
                "bias_score": bias,
            }

        logger.info("sentiment_profiles computed for %d sources", len(result))
        return result

    def top_entities_per_source(
        self, entity_type: str = "people", top_n: int = 10
    ) -> Dict[str, List[Tuple[str, int]]]:
        """
        Most-mentioned entities for each source.

        Args:
            entity_type: One of ``'people'``, ``'organizations'``,
                ``'locations'``.
            top_n: How many entities to return per source.

        Returns:
            Mapping of source → list of ``(entity_text, count)`` tuples.
        """
        result = {}
        for source, arts in self._by_source.items():
            counter: Counter = Counter()
            for article in arts:
                for ent in article.get("entities", {}).get(entity_type, []):
                    text = ent.get("text", "").strip()
                    if text:
                        counter[text] += 1
            result[source] = counter.most_common(top_n)

        return result

    def coverage_overlap(self) -> Dict[str, Any]:
        """
        Identify stories (by title similarity) that multiple sources cover.

        Uses a simple keyword overlap heuristic: two articles are considered
        the same story if they share ≥3 unique title words (after filtering
        short words).

        Returns:
            ``{shared_stories: [...], overlap_matrix: {...}}``.
        """
        sources = list(self._by_source.keys())

        def _title_words(article: Dict) -> frozenset:
            title = article.get("title", "").lower()
            return frozenset(w for w in title.split() if len(w) > 3)

        # Build overlap matrix
        overlap_matrix: Dict[str, Dict[str, int]] = {
            s: {t: 0 for t in sources} for s in sources
        }

        shared_stories = []
        checked: set = set()

        all_arts = [(s, a) for s, arts in self._by_source.items() for a in arts]
        for i, (src_a, art_a) in enumerate(all_arts):
            words_a = _title_words(art_a)
            if len(words_a) < 3:
                continue
            for src_b, art_b in all_arts[i + 1 :]:
                if src_a == src_b:
                    continue
                words_b = _title_words(art_b)
                if len(words_a & words_b) >= 3:
                    overlap_matrix[src_a][src_b] += 1
                    overlap_matrix[src_b][src_a] += 1
                    story_key = frozenset([art_a.get("link", ""), art_b.get("link", "")])
                    if story_key not in checked:
                        checked.add(story_key)
                        shared_stories.append(
                            {
                                "source_a": src_a,
                                "title_a": art_a.get("title", ""),
                                "source_b": src_b,
                                "title_b": art_b.get("title", ""),
                            }
                        )

        return {"shared_stories": shared_stories[:50], "overlap_matrix": overlap_matrix}

    def confidence_comparison(self) -> Dict[str, Dict[str, float]]:
        """
        Compare average model confidence scores across sources.

        Returns:
            Mapping of source → ``{avg, min, max}``.
        """
        result = {}
        for source, arts in self._by_source.items():
            confs = [
                a.get("sentiment_confidence", 0.0)
                for a in arts
                if a.get("sentiment_confidence") is not None
            ]
            if not confs:
                result[source] = {"avg": 0.0, "min": 0.0, "max": 0.0}
            else:
                result[source] = {
                    "avg": round(sum(confs) / len(confs), 4),
                    "min": round(min(confs), 4),
                    "max": round(max(confs), 4),
                }

        return result

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _group_by_source(self) -> Dict[str, List[Dict]]:
        groups: Dict[str, List[Dict]] = defaultdict(list)
        for article in self.articles:
            source = article.get("source", "Unknown")
            groups[source].append(article)
        return dict(groups)
