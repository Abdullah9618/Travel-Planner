#!/usr/bin/env python3
"""Test script for TripAdvisor API integration"""

import os
import sys
from dotenv import load_dotenv

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Load environment variables
load_dotenv()

from integration_services import get_traveladvisor_places

def test_tripadvisor_api():
    """Test the TripAdvisor API integration"""
    print("Testing TripAdvisor API Integration...")
    print(f"API Key loaded: {'Yes' if os.getenv('TRAVELADVISOR_API_KEY') else 'No'}")

    # Test with Lahore attractions
    places = get_traveladvisor_places('Lahore Pakistan', 'attractions', 3)
    print(f"\nTripAdvisor API Test Results for 'Lahore Pakistan attractions':")
    print(f"Found {len(places)} places")

    if places:
        for i, place in enumerate(places, 1):
            print(f"{i}. {place.get('name', 'Unknown')}")
            print(f"   Address: {place.get('address', 'No address')}")
            print(f"   Location ID: {place.get('location_id', 'N/A')}")
            print()
    else:
        print("No places found - API might be failing or returning empty results")

    # Test with restaurants
    restaurants = get_traveladvisor_places('Karachi Pakistan', 'restaurants', 2)
    print(f"\nTripAdvisor API Test Results for 'Karachi Pakistan restaurants':")
    print(f"Found {len(restaurants)} restaurants")

    if restaurants:
        for i, restaurant in enumerate(restaurants, 1):
            print(f"{i}. {restaurant.get('name', 'Unknown')}")
            print(f"   Address: {restaurant.get('address', 'No address')}")
    else:
        print("No restaurants found - API might be failing or returning empty results")

if __name__ == "__main__":
    test_tripadvisor_api()