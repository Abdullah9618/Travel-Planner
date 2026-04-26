"""External API helpers for weather, map, and itinerary generation.

The app uses live APIs when keys are available and falls back to curated
local data so the web app remains functional during development.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from urllib.error import URLError, HTTPError
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

REGION_COORDINATES: Dict[str, Tuple[float, float]] = {
    "Gilgit Baltistan": (35.9202, 74.3083),
    "KPK": (34.0151, 71.5249),
    "Punjab": (31.5204, 74.3587),
    "Sindh": (24.8607, 67.0011),
    "Balochistan": (30.1798, 66.9750),
    "AJK": (34.3753, 73.4716),
}

REGION_CITIES: Dict[str, str] = {
    "Gilgit Baltistan": "Gilgit",
    "KPK": "Peshawar",
    "Punjab": "Lahore",
    "Sindh": "Karachi",
    "Balochistan": "Quetta",
    "AJK": "Muzaffarabad",
}

FALLBACK_EVENTS: Dict[str, List[Dict[str, str]]] = {
    "Gilgit Baltistan": [
        {"name": "Mountain Photography Walk", "date": "This weekend", "venue": "Hunza"},
        {"name": "Local Culture Evening", "date": "This week", "venue": "Gilgit"},
    ],
    "Punjab": [
        {"name": "Food Street Night Tour", "date": "This weekend", "venue": "Lahore"},
        {"name": "Heritage Walk", "date": "This week", "venue": "Taxila"},
    ],
    "KPK": [
        {"name": "Valley Trekking Meetup", "date": "This weekend", "venue": "Swat"},
        {"name": "Cultural Festival Preview", "date": "This week", "venue": "Peshawar"},
    ],
}


def _http_get_json(url: str, timeout: int = 10) -> Optional[Dict[str, Any]]:
    request = Request(url, headers={"User-Agent": "TravelPlannerPakistan/1.0"})
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = response.read().decode("utf-8")
            return json.loads(payload)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
        return None


def get_google_maps_embed_url(destination_name: str, region: str = "") -> str:
    query = quote_plus(f"{destination_name}, {region}".strip(", "))
    return f"https://www.google.com/maps?q={query}&output=embed"


def get_google_maps_search_url(destination_name: str, region: str = "") -> str:
    query = quote_plus(f"{destination_name}, {region}".strip(", "))
    return f"https://www.google.com/maps/search/?api=1&query={query}"


def get_maptiler_tile_url() -> str:
    key = os.getenv("MAPTILER_API_KEY", "")
    if key:
        return f"https://api.maptiler.com/maps/streets/{{z}}/{{x}}/{{y}}.png?key={key}"
    return "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"


def get_coordinates(region: str) -> Optional[Tuple[float, float]]:
    return REGION_COORDINATES.get(region)


def get_live_weather(region: str, destination_name: str = "") -> Dict[str, Any]:
    api_key = os.getenv("OPENWEATHER_API_KEY")
    coords = get_coordinates(region)

    if api_key and coords:
        lat, lon = coords
        url = (
            "https://api.openweathermap.org/data/2.5/weather"
            f"?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        )
        data = _http_get_json(url)
        if data:
            weather = data.get("weather", [{}])[0]
            main = data.get("main", {})
            wind = data.get("wind", {})
            return {
                "source": "openweather",
                "region": region,
                "destination": destination_name,
                "temperature": round(main.get("temp", 0), 1),
                "feels_like": round(main.get("feels_like", 0), 1),
                "humidity": main.get("humidity"),
                "wind_speed": wind.get("speed"),
                "condition": weather.get("main", "Unknown"),
                "description": weather.get("description", "Live weather data"),
                "updated_at": datetime.utcnow().isoformat() + "Z",
            }

    # fallback keeps the app working without keys
    fallback_profiles = {
        "Gilgit Baltistan": {"temperature": 16, "condition": "Cool", "description": "Pleasant mountain weather"},
        "KPK": {"temperature": 20, "condition": "Moderate", "description": "Good for road trips and hiking"},
        "Punjab": {"temperature": 24, "condition": "Warm", "description": "Comfortable city travel weather"},
        "Sindh": {"temperature": 30, "condition": "Hot", "description": "Best for early morning activities"},
        "Balochistan": {"temperature": 22, "condition": "Dry", "description": "Clear skies and open roads"},
        "AJK": {"temperature": 18, "condition": "Cool", "description": "Refreshing valley climate"},
    }
    profile = fallback_profiles.get(region, {"temperature": 22, "condition": "Moderate", "description": "Stable travel weather"})
    return {
        "source": "fallback",
        "region": region,
        "destination": destination_name,
        "temperature": profile["temperature"],
        "feels_like": profile["temperature"],
        "humidity": 55,
        "wind_speed": 8,
        "condition": profile["condition"],
        "description": profile["description"],
        "updated_at": datetime.utcnow().isoformat() + "Z",
    }


def get_weather_advisories(weather: Dict[str, Any], destination: Optional[Dict[str, Any]] = None) -> List[Dict[str, str]]:
    advisories: List[Dict[str, str]] = []
    condition = (weather.get("condition") or "").lower()
    temperature = weather.get("temperature")
    region = weather.get("region") or (destination or {}).get("region", "")

    if any(term in condition for term in ["rain", "storm", "thunder", "snow"]):
        advisories.append({
            "level": "warning",
            "title": "Weather disruption possible",
            "message": "Carry a backup plan and check road conditions before departure.",
        })
    elif any(term in condition for term in ["hot", "dry"]):
        advisories.append({
            "level": "info",
            "title": "Heat advisory",
            "message": "Start sightseeing early and keep extra water during the day.",
        })
    elif any(term in condition for term in ["cold", "cool"]):
        advisories.append({
            "level": "info",
            "title": "Cool weather expected",
            "message": "Pack warm layers, especially for evening activities.",
        })

    if temperature is not None and temperature <= 5:
        advisories.append({
            "level": "warning",
            "title": "Very low temperature",
            "message": "Some mountain passes may be affected; confirm road access before travelling.",
        })

    if region == "Gilgit Baltistan":
        advisories.append({
            "level": "info",
            "title": "Mountain travel note",
            "message": "Allow buffer time for road travel and keep offline maps ready.",
        })

    if not advisories:
        advisories.append({
            "level": "success",
            "title": "Travel conditions look good",
            "message": "No major weather concern detected for your trip.",
        })

    return advisories


def get_event_suggestions(region: str, destination_name: str = "") -> List[Dict[str, str]]:
    api_key = os.getenv("TICKETMASTER_API_KEY")
    city = REGION_CITIES.get(region, destination_name)

    if api_key and city:
        url = (
            "https://app.ticketmaster.com/discovery/v2/events.json"
            f"?apikey={api_key}&city={quote_plus(city)}&size=5"
        )
        data = _http_get_json(url)
        if data:
            events = []
            embedded = data.get("_embedded", {}).get("events", [])
            for event in embedded[:5]:
                dates = event.get("dates", {}).get("start", {})
                venue = event.get("_embedded", {}).get("venues", [{}])[0].get("name", city)
                events.append({
                    "name": event.get("name", "Event"),
                    "date": dates.get("localDate", "Upcoming"),
                    "venue": venue,
                    "url": event.get("url", ""),
                })
            if events:
                return events

    return FALLBACK_EVENTS.get(region, [
        {"name": f"{destination_name or region} Cultural Visit", "date": "This week", "venue": city or region},
        {"name": f"{destination_name or region} Local Market", "date": "This weekend", "venue": city or region},
    ])


def get_traveladvisor_places(query: str, category: str = "attractions", limit: int = 5) -> List[Dict[str, Any]]:
    """Fetch attractions/restaurants from TravelAdvisor Content API when key is available."""
    api_key = os.getenv("TRAVELADVISOR_API_KEY")
    if not api_key or not query:
        return []

    search_url = (
        "https://api.content.tripadvisor.com/api/v1/location/search"
        f"?key={api_key}&searchQuery={quote_plus(query)}&category={quote_plus(category)}&language=en"
    )
    data = _http_get_json(search_url)
    if not data:
        return []

    results: List[Dict[str, Any]] = []
    for item in data.get("data", [])[:limit]:
        results.append({
            "location_id": item.get("location_id"),
            "name": item.get("name", "Unknown"),
            "address": item.get("address_obj", {}).get("address_string", ""),
            "latitude": item.get("latitude"),
            "longitude": item.get("longitude"),
        })

    return results


def build_daily_plan(destination: Dict[str, Any], days: int, preferences: Optional[Dict[str, Any]] = None, weather: Optional[Dict[str, Any]] = None, events: Optional[List[Dict[str, str]]] = None) -> List[Dict[str, Any]]:
    activities = destination.get("activities", []) or []
    weather_condition = (weather or {}).get("condition", "Moderate").lower()
    budget_style = (preferences or {}).get("travel_style", [])

    indoor_friendly = any(term in weather_condition for term in ["rain", "storm", "hot"])
    daily_plan: List[Dict[str, Any]] = []

    for day in range(1, max(days, 1) + 1):
        activity_index = (day - 1) % max(len(activities), 1)
        primary_activity = activities[activity_index] if activities else "Sightseeing"
        secondary_activity = activities[(activity_index + 1) % len(activities)] if len(activities) > 1 else "Local exploration"
        event_note = None
        if events and day == 2:
            event_note = events[0]["name"]

        morning = f"Arrival and breakfast" if day == 1 else f"Start with {primary_activity}"
        afternoon = primary_activity if not indoor_friendly else f"Indoor-friendly {primary_activity.lower()}"
        evening = secondary_activity if not indoor_friendly else "Local market visit and dinner"

        daily_plan.append({
            "day": day,
            "title": f"Day {day}",
            "morning": morning,
            "afternoon": afternoon,
            "evening": evening,
            "activity_focus": primary_activity,
            "event": event_note,
            "travel_style_match": budget_style[0] if budget_style else destination.get("type", "General"),
        })

    return daily_plan


def generate_itinerary(destination: Dict[str, Any], days: int, budget: Optional[int] = None, preferences: Optional[Dict[str, Any]] = None, weather: Optional[Dict[str, Any]] = None, budget_breakdown: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    region = destination.get("region", "")
    live_weather = weather or get_live_weather(region, destination.get("name", ""))
    events = get_event_suggestions(region, destination.get("name", ""))
    daily_plan = build_daily_plan(destination, days, preferences=preferences, weather=live_weather, events=events)

    estimated_budget = budget_breakdown or {
        "hotel": destination.get("cost", 0) * max(days, 1) * 0.35,
        "travel": destination.get("cost", 0) * 0.30,
        "meals": destination.get("cost", 0) * 0.20,
        "activities": destination.get("cost", 0) * 0.15,
    }
    if "total" not in estimated_budget:
        estimated_budget["total"] = sum(v for k, v in estimated_budget.items() if isinstance(v, (int, float)))

    map_embed_url = get_google_maps_embed_url(destination.get("name", ""), region)
    map_search_url = get_google_maps_search_url(destination.get("name", ""), region)
    map_tiler_url = get_maptiler_tile_url()

    advisories = get_weather_advisories(live_weather, destination)

    return {
        "destination": destination,
        "days": days,
        "budget_limit": budget,
        "weather": live_weather,
        "events": events,
        "advisories": advisories,
        "budget_breakdown": estimated_budget,
        "daily_plan": daily_plan,
        "map": {
            "embed_url": map_embed_url,
            "search_url": map_search_url,
            "tile_url": map_tiler_url,
            "center": {
                "lat": get_coordinates(region)[0] if get_coordinates(region) else 30.3753,
                "lng": get_coordinates(region)[1] if get_coordinates(region) else 69.3451,
            },
        },
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }
