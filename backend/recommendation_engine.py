"""
Model-driven recommendation engine for travel destinations.

This version fits a TF-IDF model on destination documents and combines:
 - content-based similarity from learned text features
 - collaborative-style signals from travel history similarity
 - cold-start popularity heuristics
"""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Dict, List, Optional, Tuple

import math
import re

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine_similarity
except Exception:  # pragma: no cover - fallback when sklearn is unavailable
    TfidfVectorizer = None
    sklearn_cosine_similarity = None


class RecommendationEngine:
    """Hybrid recommender using fitted text features and travel history."""

    def __init__(self):
        self.feature_weights = {
            "content": 0.55,
            "history": 0.25,
            "popularity": 0.10,
            "exact_match": 0.10,
        }

        self.type_similarity = {
            "Adventure": {"Adventure": 1.0, "Family": 0.3, "Relaxation": 0.2, "Cultural": 0.4, "Historical": 0.3, "Religious": 0.2},
            "Family": {"Adventure": 0.3, "Family": 1.0, "Relaxation": 0.6, "Cultural": 0.5, "Historical": 0.4, "Religious": 0.3},
            "Relaxation": {"Adventure": 0.2, "Family": 0.6, "Relaxation": 1.0, "Cultural": 0.3, "Historical": 0.3, "Religious": 0.4},
            "Cultural": {"Adventure": 0.4, "Family": 0.5, "Relaxation": 0.3, "Cultural": 1.0, "Historical": 0.8, "Religious": 0.6},
            "Historical": {"Adventure": 0.3, "Family": 0.4, "Relaxation": 0.3, "Cultural": 0.8, "Historical": 1.0, "Religious": 0.5},
            "Religious": {"Adventure": 0.2, "Family": 0.3, "Relaxation": 0.4, "Cultural": 0.6, "Historical": 0.5, "Religious": 1.0},
        }

        self.weather_similarity = {
            "Cold": {"Cold": 1.0, "Cool": 0.7, "Moderate": 0.4, "Warm": 0.2, "Hot": 0.1},
            "Cool": {"Cold": 0.7, "Cool": 1.0, "Moderate": 0.6, "Warm": 0.3, "Hot": 0.2},
            "Moderate": {"Cold": 0.4, "Cool": 0.6, "Moderate": 1.0, "Warm": 0.6, "Hot": 0.4},
            "Warm": {"Cold": 0.2, "Cool": 0.3, "Moderate": 0.6, "Warm": 1.0, "Hot": 0.7},
            "Hot": {"Cold": 0.1, "Cool": 0.2, "Moderate": 0.4, "Warm": 0.7, "Hot": 1.0},
        }

        self.user_interactions = defaultdict(dict)
        self._destination_vectors: List[Dict[str, float]] = []
        self._idf: Dict[str, float] = {}
        self._fitted_signature: Optional[Tuple] = None
        self._vectorizer = None
        self._destination_matrix = None
        self._use_sklearn = TfidfVectorizer is not None and sklearn_cosine_similarity is not None

    def _destination_text(self, destination: Dict) -> str:
        activities = " ".join(destination.get("activities", []))
        return " ".join(
            str(part)
            for part in [
                destination.get("name", ""),
                destination.get("type", ""),
                destination.get("region", ""),
                destination.get("weather", ""),
                destination.get("best_season", ""),
                destination.get("description", ""),
                activities,
                f"cost {destination.get('cost', '')}",
                f"safety {destination.get('safety_rating', '')}",
                f"rating {destination.get('user_rating', '')}",
            ]
            if part
        )

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r"[a-z0-9]+", (text or "").lower())

    def _vector_from_tokens(self, tokens: List[str]) -> Dict[str, float]:
        if not tokens:
            return {}

        counts = Counter(tokens)
        length = sum(counts.values()) or 1
        vector: Dict[str, float] = {}
        for term, count in counts.items():
            if term in self._idf:
                tf = count / length
                vector[term] = tf * self._idf[term]
        return vector

    def _vector_norm(self, vector: Dict[str, float]) -> float:
        return math.sqrt(sum(value * value for value in vector.values()))

    def _cosine_similarity(self, vector_a: Dict[str, float], vector_b: Dict[str, float]) -> float:
        if not vector_a or not vector_b:
            return 0.0

        smaller, larger = (vector_a, vector_b) if len(vector_a) < len(vector_b) else (vector_b, vector_a)
        dot_product = sum(value * larger.get(term, 0.0) for term, value in smaller.items())
        norm_a = self._vector_norm(vector_a)
        norm_b = self._vector_norm(vector_b)
        if not norm_a or not norm_b:
            return 0.0
        return dot_product / (norm_a * norm_b)

    def _build_signature(self, destinations: List[Dict]) -> Tuple:
        return tuple(
            (
                dest.get("id"),
                dest.get("name"),
                dest.get("saved_count", 0),
                dest.get("view_count", 0),
                dest.get("user_rating", 0),
                dest.get("safety_rating", 0),
            )
            for dest in destinations
        )

    def _fit_model(self, destinations: List[Dict]):
        signature = self._build_signature(destinations)
        if signature == self._fitted_signature and (
            (self._use_sklearn and self._destination_matrix is not None)
            or (not self._use_sklearn and self._destination_vectors)
        ):
            return

        raw_documents = [self._destination_text(dest) for dest in destinations]
        if self._use_sklearn:
            self._vectorizer = TfidfVectorizer(
                stop_words="english",
                ngram_range=(1, 2),
                min_df=1,
                lowercase=True,
            )
            self._destination_matrix = self._vectorizer.fit_transform(raw_documents)
            self._destination_vectors = []
            self._idf = {}
            self._fitted_signature = signature
            return

        documents = [self._tokenize(doc) for doc in raw_documents]
        self._vectorizer = None
        self._destination_matrix = None

        document_frequencies = Counter()
        for tokens in documents:
            document_frequencies.update(set(tokens))

        total_documents = len(documents) or 1
        self._idf = {
            term: math.log((1 + total_documents) / (1 + df)) + 1.0
            for term, df in document_frequencies.items()
        }

        self._destination_vectors = [self._vector_from_tokens(tokens) for tokens in documents]
        self._fitted_signature = signature

    def _vectorize_text(self, text: str):
        if self._use_sklearn and self._vectorizer is not None:
            return self._vectorizer.transform([text or ""])
        return self._vector_from_tokens(self._tokenize(text))

    def _similarity_scores(self, query_vector):
        if query_vector is None:
            return None

        if self._use_sklearn and self._destination_matrix is not None:
            return sklearn_cosine_similarity(query_vector, self._destination_matrix).flatten().tolist()

        return [self._cosine_similarity(query_vector, vector) for vector in self._destination_vectors]

    def _preference_document(self, preferences: Optional[Dict], history: Optional[List[Dict]], all_destinations: List[Dict]) -> str:
        parts: List[str] = []
        preferences = preferences or {}

        if preferences.get("budget_range"):
            budget_range = preferences["budget_range"]
            parts.append(f"budget {budget_range.get('min', 0)} to {budget_range.get('max', '')}")

        if preferences.get("travel_style"):
            parts.extend(str(item) for item in preferences["travel_style"])

        if preferences.get("weather_preference"):
            parts.append(str(preferences["weather_preference"]))

        if preferences.get("preferred_activities"):
            parts.extend(str(item) for item in preferences["preferred_activities"])

        if preferences.get("preferred_regions"):
            parts.extend(str(item) for item in preferences["preferred_regions"])

        if preferences.get("season"):
            parts.append(str(preferences["season"]))

        if preferences.get("destination"):
            parts.append(str(preferences["destination"]))

        if preferences.get("duration"):
            parts.append(f"{preferences['duration']} day trip")

        if history:
            parts.append(self._history_document(history, all_destinations))

        return " ".join(parts).strip()

    def _history_document(self, history: List[Dict], all_destinations: List[Dict]) -> str:
        texts: List[str] = []
        for item in history:
            if not isinstance(item, dict):
                continue

            destination_name = item.get("destination", "")
            destination = next((d for d in all_destinations if d.get("name") == destination_name), None)
            if destination:
                texts.append(self._destination_text(destination))
            elif destination_name:
                texts.append(destination_name)

            if item.get("notes"):
                texts.append(str(item["notes"]))

        return " ".join(texts).strip()

    def get_recommendations(
        self,
        destinations: List[Dict],
        preferences: Dict = None,
        history: List[Dict] = None,
        num_recommendations: int = 6,
    ) -> List[Dict]:
        if not destinations:
            return []

        self._fit_model(destinations)

        preference_document = self._preference_document(preferences, history, destinations)
        preference_vector = self._vectorize_text(preference_document) if preference_document else None

        history_vector = None
        if history:
            history_document = self._history_document(history, destinations)
            if history_document:
                history_vector = self._vectorize_text(history_document)

        content_scores = self._similarity_scores(preference_vector)
        history_scores = self._similarity_scores(history_vector)

        scored_destinations = []
        for index, dest in enumerate(destinations):
            if preferences and "budget_range" in preferences:
                budget_max = preferences["budget_range"].get("max", float("inf"))
                if dest.get("cost", 0) > budget_max:
                    continue

            score = 0.0
            content_score = float(content_scores[index]) if content_scores is not None else 0.0
            history_score = float(history_scores[index]) if history_scores is not None else 0.0

            if preference_vector is not None:
                score += content_score * self.feature_weights["content"]

            if history_vector is not None:
                score += history_score * self.feature_weights["history"]
            else:
                score += (dest.get("user_rating", 4.0) / 5.0) * 0.18
                score += (dest.get("safety_rating", 4) / 5.0) * 0.06

            score += self._exact_feature_boost(dest, preferences)

            popularity = dest.get("saved_count", 0) + dest.get("view_count", 0)
            if popularity:
                score += min(0.12, math.log1p(popularity) / 22)

            scored_destinations.append(
                {
                    **dest,
                    "recommendation_score": round(score, 3),
                    "match_reason": self._get_match_reason(dest, preferences, content_score, history_score, popularity),
                }
            )

        scored_destinations.sort(key=lambda item: item["recommendation_score"], reverse=True)
        return scored_destinations[:num_recommendations]

    def _exact_feature_boost(self, destination: Dict, preferences: Optional[Dict]) -> float:
        if not preferences:
            return 0.0

        boost = 0.0
        if preferences.get("travel_style"):
            dest_type = (destination.get("type") or "").lower()
            for style in preferences["travel_style"]:
                if dest_type == str(style).lower():
                    boost += 0.05
                    break

        if preferences.get("weather_preference"):
            pref_weather = str(preferences["weather_preference"])
            dest_weather = destination.get("weather", "Moderate")
            if pref_weather in self.weather_similarity and dest_weather in self.weather_similarity.get(pref_weather, {}):
                boost += self.weather_similarity[pref_weather][dest_weather] * 0.03

        if preferences.get("preferred_activities"):
            dest_activities = {str(activity).lower() for activity in destination.get("activities", [])}
            pref_activities = {str(activity).lower() for activity in preferences["preferred_activities"]}
            if dest_activities and pref_activities:
                overlap = len(dest_activities & pref_activities)
                boost += min(0.05, overlap * 0.015)

        if preferences.get("budget_range"):
            budget_min = preferences["budget_range"].get("min", 0)
            budget_max = preferences["budget_range"].get("max", float("inf"))
            dest_cost = destination.get("cost", 0)
            if budget_min <= dest_cost <= budget_max:
                boost += 0.05

        return boost

    def _get_match_reason(
        self,
        destination: Dict,
        preferences: Optional[Dict],
        content_score: float,
        history_score: float,
        popularity: int,
    ) -> str:
        reasons = []
        preferences = preferences or {}

        if preferences.get("budget_range"):
            budget_max = preferences["budget_range"].get("max", float("inf"))
            if destination.get("cost", 0) <= budget_max:
                reasons.append("Within your budget")

        if preferences.get("travel_style"):
            dest_type = (destination.get("type") or "").lower()
            if any(dest_type == str(style).lower() for style in preferences["travel_style"]):
                reasons.append(f"Matches your {destination.get('type', '').lower()} preference")

        if preferences.get("preferred_activities"):
            dest_activities = {str(activity).lower() for activity in destination.get("activities", [])}
            pref_activities = {str(activity).lower() for activity in preferences["preferred_activities"]}
            overlap = sorted(dest_activities & pref_activities)
            if overlap:
                reasons.append(f"Shares {len(overlap)} preferred activities")

        if preferences.get("weather_preference") and destination.get("weather") == preferences["weather_preference"]:
            reasons.append(f"Matches your {str(preferences['weather_preference']).lower()} weather preference")

        if preferences.get("season") and destination.get("best_season") == preferences["season"]:
            reasons.append(f"Good for {preferences['season'].lower()}")

        if history_score >= 0.15:
            reasons.append("Similar to places you've liked before")
        elif content_score >= 0.18:
            reasons.append("Strong semantic match to your query")

        if destination.get("user_rating", 0) >= 4.5:
            reasons.append("Highly rated by travelers")

        if destination.get("safety_rating", 0) >= 4:
            reasons.append("Safe destination")

        if popularity:
            reasons.append("Popular with travelers")

        if not reasons:
            reasons.append("Popular destination")

        return " | ".join(reasons[:4])

    def get_popular_destinations(self, destinations: List[Dict], num: int = 6) -> List[Dict]:
        if not destinations:
            return []

        scored = []
        for dest in destinations:
            popularity = dest.get("saved_count", 0) + dest.get("view_count", 0)
            score = (dest.get("user_rating", 4.0) * 0.6 + dest.get("safety_rating", 4) * 0.4) / 5.0
            if popularity:
                score += min(0.2, math.log1p(popularity) / 18)

            scored.append(
                {
                    **dest,
                    "recommendation_score": round(score, 3),
                    "match_reason": "Popular with travelers",
                }
            )

        scored.sort(key=lambda item: item["recommendation_score"], reverse=True)
        return scored[:num]

    def get_similar_destinations(self, destination_name: str, all_destinations: List[Dict], num: int = 4) -> List[Dict]:
        target = next((dest for dest in all_destinations if dest.get("name") == destination_name), None)
        if not target:
            return []

        self._fit_model(all_destinations)
        target_index = next((index for index, dest in enumerate(all_destinations) if dest.get("name") == destination_name), None)
        if target_index is None:
            return []

        if self._use_sklearn and self._destination_matrix is not None:
            target_vector = self._destination_matrix[target_index]
        else:
            target_vector = self._destination_vectors[target_index]

        results = []
        for index, dest in enumerate(all_destinations):
            if dest.get("name") == destination_name:
                continue
            if self._use_sklearn and self._destination_matrix is not None:
                similarity = float(sklearn_cosine_similarity(target_vector, self._destination_matrix[index]).flatten()[0])
            else:
                similarity = float(self._cosine_similarity(target_vector, self._destination_vectors[index]))
            results.append(
                {
                    **dest,
                    "similarity_score": round(similarity, 3),
                }
            )

        results.sort(key=lambda item: item["similarity_score"], reverse=True)
        return results[:num]

    def update_user_interaction(self, user_id: str, destination_name: str, rating: float):
        self.user_interactions[user_id][destination_name] = rating


if __name__ == "__main__":
    engine = RecommendationEngine()

    destinations = [
        {"name": "Hunza Valley", "type": "Adventure", "region": "Gilgit Baltistan", "cost": 25000, "weather": "Cool", "best_season": "Summer", "activities": ["Hiking", "Sightseeing"], "user_rating": 4.8, "safety_rating": 5, "description": "Mountains and forts."},
        {"name": "Gwadar Beach", "type": "Relaxation", "region": "Balochistan", "cost": 18000, "weather": "Warm", "best_season": "Winter", "activities": ["Swimming", "Sunbathing"], "user_rating": 4.5, "safety_rating": 4, "description": "Beach destination."},
        {"name": "Murree", "type": "Family", "region": "Punjab", "cost": 15000, "weather": "Cold", "best_season": "All Year", "activities": ["Shopping", "Cable Car"], "user_rating": 4.3, "safety_rating": 4, "description": "Hill station."},
    ]

    preferences = {
        "budget_range": {"min": 10000, "max": 30000},
        "travel_style": ["Adventure"],
        "weather_preference": "Cool",
        "preferred_activities": ["Hiking"],
    }

    recommendations = engine.get_recommendations(destinations, preferences)
    print("Recommendations:")
    for rec in recommendations:
        print(f"  {rec['name']}: {rec['recommendation_score']} - {rec['match_reason']}")
