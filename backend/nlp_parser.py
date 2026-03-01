"""
NLP Query Parser Module
Parses natural language travel queries to extract parameters
"""

import re
from typing import Dict, Optional, List

class QueryParser:
    """
    Parse natural language travel queries
    Example: "Plan a 3-day trip to northern Pakistan under 25,000 PKR"
    """
    
    def __init__(self):
        # Region mappings
        self.regions = {
            'northern': ['Gilgit Baltistan', 'KPK', 'AJK'],
            'north': ['Gilgit Baltistan', 'KPK', 'AJK'],
            'southern': ['Sindh', 'Balochistan'],
            'south': ['Sindh', 'Balochistan'],
            'punjab': ['Punjab'],
            'sindh': ['Sindh'],
            'balochistan': ['Balochistan'],
            'kpk': ['KPK'],
            'gilgit': ['Gilgit Baltistan'],
            'kashmir': ['AJK'],
            'azad kashmir': ['AJK']
        }
        
        # Travel type keywords
        self.travel_types = {
            'adventure': 'Adventure',
            'adventurous': 'Adventure',
            'hiking': 'Adventure',
            'trekking': 'Adventure',
            'relaxation': 'Relaxation',
            'relaxing': 'Relaxation',
            'peaceful': 'Relaxation',
            'beach': 'Relaxation',
            'family': 'Family',
            'family-friendly': 'Family',
            'kids': 'Family',
            'children': 'Family',
            'cultural': 'Cultural',
            'culture': 'Cultural',
            'heritage': 'Cultural',
            'historical': 'Historical',
            'history': 'Historical',
            'religious': 'Religious',
            'spiritual': 'Religious'
        }
        
        # Season keywords
        self.seasons = {
            'summer': 'Summer',
            'winter': 'Winter',
            'spring': 'Spring',
            'autumn': 'Autumn',
            'fall': 'Autumn',
            'monsoon': 'Monsoon'
        }
        
        # Activity keywords
        self.activities = [
            'hiking', 'trekking', 'camping', 'photography', 'sightseeing',
            'swimming', 'boating', 'skiing', 'shopping', 'rafting',
            'paragliding', 'rock climbing', 'fishing', 'bird watching'
        ]
    
    def parse(self, query: str) -> Dict:
        """
        Parse a natural language query and extract travel parameters
        
        Args:
            query: Natural language search query
            
        Returns:
            Dictionary with extracted parameters
        """
        query_lower = query.lower()
        
        result = {
            'original_query': query,
            'days': self._extract_days(query_lower),
            'budget': self._extract_budget(query_lower),
            'region': self._extract_region(query_lower),
            'type': self._extract_type(query_lower),
            'season': self._extract_season(query_lower),
            'activities': self._extract_activities(query_lower),
            'destination': self._extract_destination(query_lower)
        }
        
        # Clean None values
        result = {k: v for k, v in result.items() if v is not None}
        result['original_query'] = query
        
        return result
    
    def _extract_days(self, query: str) -> Optional[int]:
        """Extract number of days from query"""
        # Patterns: "3-day", "3 day", "3 days", "three days", "a week"
        patterns = [
            r'(\d+)\s*-?\s*days?',
            r'(\d+)\s*-?\s*nights?',
            r'for\s+(\d+)\s*days?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                return int(match.group(1))
        
        # Word numbers
        word_numbers = {
            'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'a week': 7, 'weekend': 2
        }
        
        for word, num in word_numbers.items():
            if word in query:
                return num
        
        return None
    
    def _extract_budget(self, query: str) -> Optional[int]:
        """Extract budget from query"""
        # Patterns: "25,000 PKR", "under 25000", "budget 25k"
        patterns = [
            r'(?:under|below|within|budget\s+of?|less\s+than|max(?:imum)?)\s*(?:pkr|rs\.?)?\s*([\d,]+)\s*(?:pkr|rs\.?)?',
            r'([\d,]+)\s*(?:pkr|rs\.?|rupees?)',
            r'(?:pkr|rs\.?)\s*([\d,]+)',
            r'(\d+)\s*k\b',  # 25k format
        ]
        
        for i, pattern in enumerate(patterns):
            match = re.search(pattern, query)
            if match:
                amount = match.group(1).replace(',', '')
                try:
                    budget = int(amount)
                    # Handle "k" format (25k = 25000)
                    if i == 3:  # The 'k' pattern
                        budget *= 1000
                    return budget
                except ValueError:
                    continue
        
        return None
    
    def _extract_region(self, query: str) -> Optional[str]:
        """Extract region from query"""
        for keyword, regions in self.regions.items():
            if keyword in query:
                return regions[0]  # Return first matching region
        
        # Check for specific place names
        place_regions = {
            'hunza': 'Gilgit Baltistan',
            'skardu': 'Gilgit Baltistan',
            'naran': 'KPK',
            'kaghan': 'KPK',
            'swat': 'KPK',
            'murree': 'Punjab',
            'lahore': 'Punjab',
            'karachi': 'Sindh',
            'gwadar': 'Balochistan',
            'quetta': 'Balochistan',
            'neelum': 'AJK',
            'muzaffarabad': 'AJK'
        }
        
        for place, region in place_regions.items():
            if place in query:
                return region
        
        return None
    
    def _extract_type(self, query: str) -> Optional[str]:
        """Extract travel type from query"""
        for keyword, travel_type in self.travel_types.items():
            if keyword in query:
                return travel_type
        return None
    
    def _extract_season(self, query: str) -> Optional[str]:
        """Extract preferred season from query"""
        for keyword, season in self.seasons.items():
            if keyword in query:
                return season
        return None
    
    def _extract_activities(self, query: str) -> List[str]:
        """Extract mentioned activities from query"""
        found_activities = []
        for activity in self.activities:
            if activity in query:
                found_activities.append(activity.title())
        return found_activities if found_activities else None
    
    def _extract_destination(self, query: str) -> Optional[str]:
        """Extract specific destination name if mentioned"""
        destinations = [
            'hunza', 'skardu', 'fairy meadows', 'naran', 'kaghan',
            'swat', 'murree', 'nathia gali', 'lahore', 'karachi',
            'gwadar', 'quetta', 'neelum valley', 'malam jabba',
            'taxila', 'mohenjo daro', 'khunjerab', 'deosai',
            'saif ul malook', 'attabad lake', 'shangrila', 'chitral'
        ]
        
        for dest in destinations:
            if dest in query:
                return dest.title()
        
        return None


# Example usage and testing
if __name__ == '__main__':
    parser = QueryParser()
    
    test_queries = [
        "Plan a 3-day trip to northern Pakistan under 25,000 PKR",
        "Looking for adventure spots with budget 15k",
        "Family trip to Murree for weekend",
        "Best places for hiking in Gilgit under 30000 rupees",
        "Relaxing beach vacation in Gwadar for 5 days",
        "Cultural tour of Lahore under Rs. 20,000"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        result = parser.parse(query)
        for key, value in result.items():
            if key != 'original_query':
                print(f"  {key}: {value}")
