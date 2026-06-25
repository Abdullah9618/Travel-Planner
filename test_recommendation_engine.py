#!/usr/bin/env python3
"""Smoke test for the recommendation engine."""

from backend.recommendation_engine import RecommendationEngine


def main():
    engine = RecommendationEngine()

    destinations = [
        {
            "name": "Hunza Valley",
            "type": "Adventure",
            "region": "Gilgit Baltistan",
            "cost": 25000,
            "weather": "Cool",
            "best_season": "Summer",
            "activities": ["Hiking", "Sightseeing"],
            "user_rating": 4.8,
            "safety_rating": 5,
            "description": "Mountains, lakes, and forts.",
        },
        {
            "name": "Gwadar Beach",
            "type": "Relaxation",
            "region": "Balochistan",
            "cost": 18000,
            "weather": "Warm",
            "best_season": "Winter",
            "activities": ["Swimming", "Sunbathing"],
            "user_rating": 4.5,
            "safety_rating": 4,
            "description": "Beach destination.",
        },
        {
            "name": "Murree",
            "type": "Family",
            "region": "Punjab",
            "cost": 15000,
            "weather": "Cold",
            "best_season": "All Year",
            "activities": ["Shopping", "Cable Car"],
            "user_rating": 4.3,
            "safety_rating": 4,
            "description": "Hill station.",
        },
    ]

    preferences = {
        "budget_range": {"min": 10000, "max": 30000},
        "travel_style": ["Adventure"],
        "weather_preference": "Cool",
        "preferred_activities": ["Hiking"],
    }

    recommendations = engine.get_recommendations(destinations, preferences)
    assert recommendations, "Expected at least one recommendation"
    assert recommendations[0]["name"] == "Hunza Valley", recommendations[0]
    assert recommendations[0]["recommendation_score"] >= recommendations[-1]["recommendation_score"]

    similar = engine.get_similar_destinations("Hunza Valley", destinations)
    assert similar, "Expected similar destinations"
    assert similar[0]["name"] != "Hunza Valley"

    print("Recommendation engine smoke test passed.")
    print("Top recommendation:", recommendations[0]["name"], recommendations[0]["match_reason"])
    print("Most similar destination:", similar[0]["name"], similar[0]["similarity_score"])


if __name__ == "__main__":
    main()
