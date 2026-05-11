"""
ML-Based Recommendation Engine
Implements Content-Based Filtering and Collaborative Filtering
"""

from typing import List, Dict, Optional
from collections import defaultdict

class RecommendationEngine:
    """
    Machine Learning based recommendation engine for travel destinations
    Uses Content-Based Filtering and Collaborative Filtering
    """
    
    def __init__(self):
        # Feature weights for content-based filtering
        self.feature_weights = {
            'type': 0.25,
            'region': 0.15,
            'cost': 0.20,
            'weather': 0.10,
            'activities': 0.15,
            'user_rating': 0.10,
            'safety_rating': 0.05
        }
        
        # Type similarity matrix
        self.type_similarity = {
            'Adventure': {'Adventure': 1.0, 'Family': 0.3, 'Relaxation': 0.2, 'Cultural': 0.4, 'Historical': 0.3, 'Religious': 0.2},
            'Family': {'Adventure': 0.3, 'Family': 1.0, 'Relaxation': 0.6, 'Cultural': 0.5, 'Historical': 0.4, 'Religious': 0.3},
            'Relaxation': {'Adventure': 0.2, 'Family': 0.6, 'Relaxation': 1.0, 'Cultural': 0.3, 'Historical': 0.3, 'Religious': 0.4},
            'Cultural': {'Adventure': 0.4, 'Family': 0.5, 'Relaxation': 0.3, 'Cultural': 1.0, 'Historical': 0.8, 'Religious': 0.6},
            'Historical': {'Adventure': 0.3, 'Family': 0.4, 'Relaxation': 0.3, 'Cultural': 0.8, 'Historical': 1.0, 'Religious': 0.5},
            'Religious': {'Adventure': 0.2, 'Family': 0.3, 'Relaxation': 0.4, 'Cultural': 0.6, 'Historical': 0.5, 'Religious': 1.0}
        }
        
        # Weather similarity
        self.weather_similarity = {
            'Cold': {'Cold': 1.0, 'Cool': 0.7, 'Moderate': 0.4, 'Warm': 0.2, 'Hot': 0.1},
            'Cool': {'Cold': 0.7, 'Cool': 1.0, 'Moderate': 0.6, 'Warm': 0.3, 'Hot': 0.2},
            'Moderate': {'Cold': 0.4, 'Cool': 0.6, 'Moderate': 1.0, 'Warm': 0.6, 'Hot': 0.4},
            'Warm': {'Cold': 0.2, 'Cool': 0.3, 'Moderate': 0.6, 'Warm': 1.0, 'Hot': 0.7},
            'Hot': {'Cold': 0.1, 'Cool': 0.2, 'Moderate': 0.4, 'Warm': 0.7, 'Hot': 1.0}
        }
        
        # User-destination interaction matrix (simulated for collaborative filtering)
        self.user_interactions = defaultdict(dict)
    
    def get_recommendations(self, 
                          destinations: List[Dict],
                          preferences: Dict = None,
                          history: List[Dict] = None,
                          num_recommendations: int = 6) -> List[Dict]:
        """
        Get personalized destination recommendations
        
        Args:
            destinations: List of all available destinations
            preferences: User preferences (budget_range, travel_style, etc.)
            history: User's travel history
            num_recommendations: Number of recommendations to return
            
        Returns:
            List of recommended destinations with scores
        """
        if not destinations:
            return []
        
        # Calculate scores for each destination
        scored_destinations = []
        
        for dest in destinations:
            # Strict filtering: exclude destinations that exceed maximum budget
            if preferences and 'budget_range' in preferences:
                budget_max = preferences['budget_range'].get('max', float('inf'))
                if dest.get('cost', 0) > budget_max:
                    continue # Do not recommend over budget

            score = 0.0
            
            # Content-based filtering score
            if preferences:
                content_score = self._calculate_content_score(dest, preferences)
                score += content_score * 0.6
            
            # Collaborative filtering score (based on similar users)
            if history:
                collab_score = self._calculate_collaborative_score(dest, history, destinations)
                score += collab_score * 0.4
            else:
                # Cold start: boost popular destinations
                score += (dest.get('user_rating', 4.0) / 5.0) * 0.3
                score += (dest.get('safety_rating', 4) / 5.0) * 0.1
            
            scored_destinations.append({
                **dest,
                'recommendation_score': round(score, 3),
                'match_reason': self._get_match_reason(dest, preferences)
            })
        
        # Sort by score and return top recommendations
        scored_destinations.sort(key=lambda x: x['recommendation_score'], reverse=True)
        
        return scored_destinations[:num_recommendations]
    
    def _calculate_content_score(self, destination: Dict, preferences: Dict) -> float:
        """
        Calculate content-based filtering score
        Compares destination features with user preferences
        """
        score = 0.0
        
        # Budget matching
        if 'budget_range' in preferences:
            budget_min = preferences['budget_range'].get('min', 0)
            budget_max = preferences['budget_range'].get('max', float('inf'))
            dest_cost = destination.get('cost', 0)
            
            if budget_min <= dest_cost <= budget_max:
                # Higher score for destinations in the middle of budget range
                budget_score = 1.0 - abs(dest_cost - (budget_min + budget_max) / 2) / (budget_max - budget_min + 1)
                score += budget_score * self.feature_weights['cost']
            else:
                # Penalty for out of budget
                score -= 0.2
        
        # Travel style matching
        if 'travel_style' in preferences and preferences['travel_style']:
            dest_type = destination.get('type', '')
            style_scores = []
            
            for style in preferences['travel_style']:
                if style in self.type_similarity and dest_type in self.type_similarity.get(style, {}):
                    style_scores.append(self.type_similarity[style][dest_type])
            
            if style_scores:
                score += max(style_scores) * self.feature_weights['type']
        
        # Weather preference
        if 'weather_preference' in preferences:
            dest_weather = destination.get('weather', 'Moderate')
            pref_weather = preferences['weather_preference']
            
            if pref_weather in self.weather_similarity and dest_weather in self.weather_similarity.get(pref_weather, {}):
                score += self.weather_similarity[pref_weather][dest_weather] * self.feature_weights['weather']
        
        # Activity matching
        if 'preferred_activities' in preferences:
            dest_activities = set(a.lower() for a in destination.get('activities', []))
            pref_activities = set(a.lower() for a in preferences['preferred_activities'])
            
            if dest_activities and pref_activities:
                intersection = len(dest_activities & pref_activities)
                activity_score = intersection / max(len(pref_activities), 1)
                score += activity_score * self.feature_weights['activities']
        
        # Rating bonus
        user_rating = destination.get('user_rating', 4.0)
        safety_rating = destination.get('safety_rating', 4)
        
        score += (user_rating / 5.0) * self.feature_weights['user_rating']
        score += (safety_rating / 5.0) * self.feature_weights['safety_rating']
        
        return min(score, 1.0)
    
    def _calculate_collaborative_score(self, 
                                       destination: Dict, 
                                       history: List[Dict],
                                       all_destinations: List[Dict]) -> float:
        """
        Calculate collaborative filtering score
        Based on similarity to previously visited/liked destinations
        """
        if not history:
            return 0.0
        
        # Calculate similarity with each destination in history
        similarities = []
        
        for hist_item in history:
            hist_dest_name = hist_item.get('destination', '')
            hist_dest = next((d for d in all_destinations if d['name'] == hist_dest_name), None)
            
            if hist_dest:
                similarity = self._calculate_destination_similarity(destination, hist_dest)
                # Weight by user rating of historical destination
                rating_weight = hist_item.get('rating', 4.0) / 5.0
                similarities.append(similarity * rating_weight)
        
        if similarities:
            return sum(similarities) / len(similarities)
        
        return 0.0
    
    def _calculate_destination_similarity(self, dest1: Dict, dest2: Dict) -> float:
        """Calculate similarity between two destinations"""
        if dest1.get('name') == dest2.get('name'):
            return 0.0  # Don't recommend already visited
        
        similarity = 0.0
        
        # Type similarity
        type1, type2 = dest1.get('type', ''), dest2.get('type', '')
        if type1 in self.type_similarity and type2 in self.type_similarity.get(type1, {}):
            similarity += self.type_similarity[type1][type2] * 0.3
        
        # Region similarity (same region = bonus)
        if dest1.get('region') == dest2.get('region'):
            similarity += 0.2
        
        # Weather similarity
        weather1, weather2 = dest1.get('weather', 'Moderate'), dest2.get('weather', 'Moderate')
        if weather1 in self.weather_similarity and weather2 in self.weather_similarity.get(weather1, {}):
            similarity += self.weather_similarity[weather1][weather2] * 0.2
        
        # Activity overlap
        activities1 = set(a.lower() for a in dest1.get('activities', []))
        activities2 = set(a.lower() for a in dest2.get('activities', []))
        
        if activities1 and activities2:
            overlap = len(activities1 & activities2) / len(activities1 | activities2)
            similarity += overlap * 0.2
        
        # Cost similarity
        cost1, cost2 = dest1.get('cost', 0), dest2.get('cost', 0)
        if cost1 > 0 and cost2 > 0:
            cost_similarity = 1 - abs(cost1 - cost2) / max(cost1, cost2)
            similarity += cost_similarity * 0.1
        
        return min(similarity, 1.0)
    
    def _get_match_reason(self, destination: Dict, preferences: Dict) -> str:
        """Generate a human-readable reason for the recommendation"""
        reasons = []
        
        if preferences:
            if 'travel_style' in preferences:
                for style in preferences['travel_style']:
                    if destination.get('type', '').lower() == style.lower():
                        reasons.append(f"Matches your {style.lower()} preference")
                        break
            
            if 'budget_range' in preferences:
                budget_max = preferences['budget_range'].get('max', float('inf'))
                if destination.get('cost', 0) <= budget_max:
                    reasons.append("Within your budget")
        
        if destination.get('user_rating', 0) >= 4.5:
            reasons.append("Highly rated by travelers")
        
        if destination.get('safety_rating', 0) >= 4:
            reasons.append("Safe destination")
        
        if not reasons:
            reasons.append("Popular destination")
        
        return " • ".join(reasons)
    
    def get_popular_destinations(self, destinations: List[Dict], num: int = 6) -> List[Dict]:
        """
        Get popular destinations for guest users (cold start problem)
        Uses heuristics based on ratings and safety
        """
        if not destinations:
            return []
        
        # Score based on ratings and safety
        scored = []
        for dest in destinations:
            score = (
                dest.get('user_rating', 4.0) * 0.6 +
                dest.get('safety_rating', 4) * 0.4
            ) / 5.0
            
            scored.append({
                **dest,
                'recommendation_score': round(score, 3),
                'match_reason': 'Popular with travelers'
            })
        
        scored.sort(key=lambda x: x['recommendation_score'], reverse=True)
        return scored[:num]
    
    def get_similar_destinations(self, 
                                destination_name: str, 
                                all_destinations: List[Dict],
                                num: int = 4) -> List[Dict]:
        """Find destinations similar to a given destination"""
        target = next((d for d in all_destinations if d['name'] == destination_name), None)
        
        if not target:
            return []
        
        similarities = []
        for dest in all_destinations:
            if dest['name'] != destination_name:
                sim_score = self._calculate_destination_similarity(target, dest)
                similarities.append({
                    **dest,
                    'similarity_score': round(sim_score, 3)
                })
        
        similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
        return similarities[:num]
    
    def update_user_interaction(self, user_id: str, destination_name: str, rating: float):
        """Update user-destination interaction for collaborative filtering"""
        self.user_interactions[user_id][destination_name] = rating


# Example usage
if __name__ == '__main__':
    engine = RecommendationEngine()
    
    # Sample destinations
    destinations = [
        {"name": "Hunza Valley", "type": "Adventure", "region": "Gilgit Baltistan", 
         "cost": 25000, "weather": "Cool", "activities": ["Hiking", "Sightseeing"], 
         "user_rating": 4.8, "safety_rating": 5},
        {"name": "Gwadar Beach", "type": "Relaxation", "region": "Balochistan",
         "cost": 18000, "weather": "Warm", "activities": ["Swimming", "Sunbathing"],
         "user_rating": 4.5, "safety_rating": 4},
        {"name": "Murree", "type": "Family", "region": "Punjab",
         "cost": 15000, "weather": "Cold", "activities": ["Shopping", "Cable Car"],
         "user_rating": 4.3, "safety_rating": 4}
    ]
    
    # User preferences
    preferences = {
        "budget_range": {"min": 10000, "max": 30000},
        "travel_style": ["Adventure"],
        "weather_preference": "Cool"
    }
    
    recommendations = engine.get_recommendations(destinations, preferences)
    print("Recommendations:")
    for rec in recommendations:
        print(f"  {rec['name']}: {rec['recommendation_score']} - {rec['match_reason']}")
