"""External API helpers for weather, map, and itinerary generation.

The app uses live APIs when keys are available and falls back to curated
local data so the web app remains functional during development.
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timedelta
from html.parser import HTMLParser
from typing import Any, Dict, List, Optional, Tuple
from urllib.error import URLError, HTTPError
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available, use system env vars

REGION_COORDINATES: Dict[str, Tuple[float, float]] = {
    "Gilgit Baltistan": (35.9202, 74.3083),
    "KPK": (34.0151, 71.5249),
    "Punjab": (31.5204, 74.3587),
    "Sindh": (24.8607, 67.0011),
    "Balochistan": (30.1798, 66.9750),
    "AJK": (34.3753, 73.4716),
    "Islamabad Capital Territory": (33.6844, 73.0479),
}

DESTINATION_COORDINATES: Dict[str, Tuple[float, float]] = {
    "Hunza Valley": (36.3167, 74.6500),
    "Gwadar Beach": (25.1216, 62.3254),
    "Murree": (33.9070, 73.3943),
    "Skardu": (35.2981, 75.6114),
    "Swat Valley": (35.2227, 72.4258),
    "Naran Kaghan": (34.9083, 73.6500),
    "Lahore": (31.5204, 74.3587),
    "Fairy Meadows": (35.3853, 74.5772),
    "Neelum Valley": (34.5805, 73.9030),
    "Karachi": (24.8607, 67.0011),
    "Taxila": (33.7463, 72.7843),
    "Malam Jabba": (34.7981, 72.5722),
    "Deosai National Park": (35.0500, 75.4667),
    "Mohenjo-daro": (27.3292, 68.1389),
    "Chitral": (35.8500, 71.7833),
    "Attabad Lake": (36.3101, 74.8329),
    "Ziarat": (30.3800, 67.7275),
    "Nathia Gali": (34.0700, 73.3833),
    "Khunjerab Pass": (36.8497, 75.4239),
    "Rawalpindi": (33.5984, 73.0441),
}

REGION_CITIES: Dict[str, str] = {
    "Gilgit Baltistan": "Gilgit",
    "KPK": "Peshawar",
    "Punjab": "Lahore",
    "Sindh": "Karachi",
    "Balochistan": "Quetta",
    "AJK": "Muzaffarabad",
}

def _build_query_name(destination_name: str, region: str = "") -> str:
    parts = [part.strip() for part in [destination_name, region] if part and part.strip()]
    return ", ".join(parts)

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

FALLBACK_PLACES: Dict[str, Dict[str, List[Dict[str, Any]]]] = {
    "lahore": {
        "attractions": [
            {"name": "Badshahi Mosque", "address": "Lahore, Punjab", "latitude": 31.5885, "longitude": 74.3080, "location_id": "https://www.tripadvisor.com/Attraction_Review-g295413-d548234-Reviews-Badshahi_Mosque-Lahore_Punjab_Province.html", "source": "tripadvisor_seed"},
            {"name": "Lahore Guided Tours", "address": "Lahore, Punjab", "latitude": 31.5204, "longitude": 74.3587, "location_id": "https://www.tripadvisor.com/Attraction_Review-g295413-d10475680-Reviews-Lahore_Guided_Tours-Lahore_Punjab_Province.html", "source": "tripadvisor_seed"},
            {"name": "Wagah Border", "address": "Lahore, Punjab", "latitude": 31.5902, "longitude": 74.3095, "location_id": "https://www.tripadvisor.com/Attraction_Review-g295413-d548236-Reviews-Wagah_Border-Lahore_Punjab_Province.html", "source": "tripadvisor_seed"},
        ],
        "restaurants": [
            {"name": "Asian Wok Raya Lahore", "address": "Lahore, Punjab", "latitude": 31.5204, "longitude": 74.3587, "location_id": "https://www.tripadvisor.com/Restaurant_Review-g295413-d27463556-Reviews-Asian_Wok_Raya_Lahore-Lahore_Punjab_Province.html", "source": "tripadvisor_seed"},
            {"name": "Arcadian Cafe Packages Mall", "address": "Lahore, Punjab", "latitude": 31.5204, "longitude": 74.3587, "location_id": "https://www.tripadvisor.com/Restaurant_Review-g295413-d12412787-Reviews-Arcadian_Cafe_Packages_Mall-Lahore_Punjab_Province.html", "source": "tripadvisor_seed"},
            {"name": "Monal Lahore", "address": "Lahore, Punjab", "latitude": 31.5204, "longitude": 74.3587, "location_id": "https://www.tripadvisor.com/Restaurant_Review-g295413-d9784331-Reviews-Monal_Lahore-Lahore_Punjab_Province.html", "source": "tripadvisor_seed"},
        ],
    },
    "karachi": {
        "attractions": [
            {"name": "Dolmen Mall Clifton", "address": "Karachi, Sindh", "latitude": 24.8100, "longitude": 67.0317, "location_id": "https://www.tripadvisor.com/Attraction_Review-g295414-d4600145-Reviews-Dolmen_Mall_Clifton-Karachi_Sindh_Province.html", "source": "tripadvisor_seed"},
            {"name": "Port Grand Pakistan", "address": "Karachi, Sindh", "latitude": 24.8100, "longitude": 67.0317, "location_id": "https://www.tripadvisor.com/Attraction_Review-g295414-d2419975-Reviews-Port_Grand_Pakistan-Karachi_Sindh_Province.html", "source": "tripadvisor_seed"},
            {"name": "Mohatta Palace Museum", "address": "Karachi, Sindh", "latitude": 24.8749, "longitude": 67.0368, "location_id": "https://www.tripadvisor.com/Attraction_Review-g295414-d553612-Reviews-Mohatta_Palace_Museum-Karachi_Sindh_Province.html", "source": "tripadvisor_seed"},
        ],
        "restaurants": [
            {"name": "Chef's Table", "address": "Karachi, Sindh", "latitude": 24.8122, "longitude": 67.0290, "location_id": "https://www.tripadvisor.com/Restaurant_Review-g295414-d20006153-Reviews-Chef_s_Table-Karachi_Sindh_Province.html", "source": "tripadvisor_seed"},
            {"name": "Asia Live - Avari Towers Karachi", "address": "Karachi, Sindh", "latitude": 24.8122, "longitude": 67.0290, "location_id": "https://www.tripadvisor.com/Restaurant_Review-g295414-d21210320-Reviews-Asia_Live_Avari_Towers_Karachi-Karachi_Sindh_Province.html", "source": "tripadvisor_seed"},
            {"name": "Kolachi Restaurant", "address": "Karachi, Sindh", "latitude": 24.8506, "longitude": 67.0156, "location_id": "https://www.tripadvisor.com/Restaurant_Review-g295414-d3568210-Reviews-Kolachi_Restaurant-Karachi_Sindh_Province.html", "source": "tripadvisor_seed"},
        ],
    },
    "islamabad": {
        "attractions": [
            {"name": "Faisal Mosque", "address": "Islamabad", "latitude": 33.7294, "longitude": 73.0379, "location_id": "https://www.tripadvisor.com/Attraction_Review-g293960-d450851-Reviews-Faisal_Mosque-Islamabad_Islamabad_Capital_Territory.html", "source": "tripadvisor_seed"},
            {"name": "Margalla Hills", "address": "Islamabad", "latitude": 33.7380, "longitude": 73.0849, "location_id": "https://www.tripadvisor.com/Attraction_Review-g293960-d555109-Reviews-Margalla_Hills-Islamabad_Islamabad_Capital_Territory.html", "source": "tripadvisor_seed"},
            {"name": "Daman-e-Koh", "address": "Islamabad", "latitude": 33.7380, "longitude": 73.0849, "location_id": "https://www.tripadvisor.com/Attraction_Review-g293960-d554849-Reviews-Daman_e_Koh-Islamabad_Islamabad_Capital_Territory.html", "source": "tripadvisor_seed"},
        ],
        "restaurants": [
            {"name": "Dawat", "address": "Islamabad", "latitude": 33.7330, "longitude": 73.0585, "location_id": "https://www.tripadvisor.com/Restaurant_Review-g293960-d9463107-Reviews-Dawat-Islamabad_Islamabad_Capital_Territory.html", "source": "tripadvisor_seed"},
            {"name": "The Carnivore", "address": "Islamabad", "latitude": 33.7152, "longitude": 73.0787, "location_id": "https://www.tripadvisor.com/Restaurant_Review-g293960-d26819870-Reviews-The_Carnivore-Islamabad_Islamabad_Capital_Territory.html", "source": "tripadvisor_seed"},
            {"name": "Burger In Town", "address": "Islamabad", "latitude": 33.7070, "longitude": 73.0510, "location_id": "https://www.tripadvisor.com/Restaurant_Review-g293960-d26658591-Reviews-Burger_In_Town-Islamabad_Islamabad_Capital_Territory.html", "source": "tripadvisor_seed"},
        ],
    },
}

TRIPADVISOR_TOURISM_PAGES: Dict[str, str] = {
    "lahore": "https://www.tripadvisor.com/Tourism-g295413-Lahore_Punjab_Province-Vacations.html",
    "karachi": "https://www.tripadvisor.com/Tourism-g295414-Karachi_Sindh_Province-Vacations.html",
    "islamabad": "https://www.tripadvisor.com/Tourism-g293960-Islamabad_Islamabad_Capital_Territory-Vacations.html",
}

_TRIPADVISOR_PUBLIC_CACHE: Dict[Tuple[str, str, int], List[Dict[str, Any]]] = {}
_OPENSTREETMAP_CACHE: Dict[Tuple[str, str, int], List[Dict[str, Any]]] = {}


class _TripadvisorAnchorParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.anchors: List[Dict[str, str]] = []
        self._current_href: Optional[str] = None
        self._current_text: List[str] = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "a":
            attrs_dict = dict(attrs)
            self._current_href = attrs_dict.get("href")
            self._current_text = []

    def handle_data(self, data):
        if self._current_href is not None:
            self._current_text.append(data)

    def handle_endtag(self, tag):
        if tag.lower() == "a" and self._current_href is not None:
            text = " ".join(part.strip() for part in self._current_text if part.strip()).strip()
            if text or self._current_href:
                self.anchors.append({"href": self._current_href, "text": text})
            self._current_href = None
            self._current_text = []


def _http_get_text(url: str, timeout: int = 10) -> Optional[str]:
    request = Request(url, headers={"User-Agent": "TravelPlannerPakistan/1.0"})
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.read().decode("utf-8", errors="ignore")
    except (HTTPError, URLError, TimeoutError):
        return None


def _http_get_json(url: str, timeout: int = 10) -> Optional[Dict[str, Any]]:
    request = Request(url, headers={"User-Agent": "TravelPlannerPakistan/1.0"})
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = response.read().decode("utf-8")
            return json.loads(payload)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
        return None


def _openstreetmap_geocode(query: str) -> Optional[Tuple[float, float, str]]:
    if not query:
        return None

    url = (
        "https://nominatim.openstreetmap.org/search"
        f"?format=jsonv2&limit=1&q={quote_plus(query)}"
    )
    request = Request(url, headers={"User-Agent": "TravelPlannerPakistan/1.0"})
    try:
        with urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8", errors="ignore"))
            if isinstance(payload, list) and payload:
                first = payload[0]
                lat = first.get("lat")
                lon = first.get("lon")
                display_name = first.get("display_name", query)
                if lat is not None and lon is not None:
                    return float(lat), float(lon), display_name
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, ValueError):
        return None
    return None


def _openstreetmap_search(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    if not query:
        return []

    url = (
        "https://nominatim.openstreetmap.org/search"
        f"?format=jsonv2&namedetails=1&extratags=1&limit={max(limit, 1)}&q={quote_plus(query)}"
    )
    request = Request(url, headers={"User-Agent": "TravelPlannerPakistan/1.0"})
    try:
        with urlopen(request, timeout=12) as response:
            payload = json.loads(response.read().decode("utf-8", errors="ignore"))
            if isinstance(payload, list):
                return payload
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
        return []
    return []


def _openstreetmap_places(query: str, category: str, limit: int) -> List[Dict[str, Any]]:
    cache_key = (_normalize_tripadvisor_query(query).lower(), category, limit)
    cached = _OPENSTREETMAP_CACHE.get(cache_key)
    if cached is not None:
        return cached[:limit]

    results: List[Dict[str, Any]] = []
    seen = set()

    keyword_variants = ["attraction", "tourism", "museum", "monument", "mosque", "park"] if category != "restaurants" else ["restaurant", "restaurants", "cafe", "food", "dining"]
    for keyword in keyword_variants:
        search_query = f"{query} {keyword}".strip()
        for item in _openstreetmap_search(search_query, limit=limit):
            namedetails = item.get("namedetails") if isinstance(item.get("namedetails"), dict) else {}
            name = namedetails.get("name") or item.get("name") or item.get("display_name") or ""
            if not name:
                continue
            location_id = f"osm-search-{item.get('osm_type', 'result')}-{item.get('osm_id', name)}"
            if location_id in seen:
                continue
            seen.add(location_id)
            lat = item.get("lat")
            lon = item.get("lon")
            results.append({
                "location_id": location_id,
                "name": name.split(",")[0].strip(),
                "address": name,
                "latitude": float(lat) if lat is not None else None,
                "longitude": float(lon) if lon is not None else None,
                "category": category,
                "summary": name,
                "source": "openstreetmap",
                "url": f"https://www.openstreetmap.org/{item.get('osm_type', 'node')}/{item.get('osm_id', '')}",
            })
            if len(results) >= limit:
                _OPENSTREETMAP_CACHE[cache_key] = results
                return results

    geocoded = _openstreetmap_geocode(query)
    if geocoded:
        lat, lon, display_name = geocoded
        radius = 12000

        if category == "restaurants":
            osm_filter = '"amenity"~"restaurant|cafe|fast_food"'
        else:
            osm_filter = '"tourism"~"attraction|museum|zoo|theme_park"'

        overpass_query = (
            "[out:json][timeout:25];"
            f"(node(around:{radius},{lat},{lon})[{osm_filter}];"
            f"way(around:{radius},{lat},{lon})[{osm_filter}];"
            f"relation(around:{radius},{lat},{lon})[{osm_filter}];);"
            "out center 25;"
        )
        overpass_url = "https://overpass-api.de/api/interpreter?data=" + quote_plus(overpass_query)
        data = _http_get_json(overpass_url, timeout=25)
        elements = data.get("elements", []) if isinstance(data, dict) else []

        for element in elements:
            tags = element.get("tags", {}) if isinstance(element, dict) else {}
            name = tags.get("name") or tags.get("brand") or tags.get("operator")
            if not name:
                continue
            center = element.get("center", {}) if isinstance(element, dict) else {}
            el_lat = element.get("lat") if isinstance(element, dict) else None
            el_lon = element.get("lon") if isinstance(element, dict) else None
            if el_lat is None:
                el_lat = center.get("lat") if isinstance(center, dict) else None
            if el_lon is None:
                el_lon = center.get("lon") if isinstance(center, dict) else None
            location_id = f"osm-{element.get('type', 'node')}-{element.get('id', name)}"
            if location_id in seen:
                continue
            seen.add(location_id)
            results.append({
                "location_id": location_id,
                "name": name,
                "address": display_name,
                "latitude": float(el_lat) if el_lat is not None else None,
                "longitude": float(el_lon) if el_lon is not None else None,
                "category": category,
                "summary": tags.get("description") or tags.get("tourism") or tags.get("amenity") or name,
                "source": "openstreetmap",
                "url": f"https://www.openstreetmap.org/{element.get('type', 'node')}/{element.get('id')}",
            })
            if len(results) >= limit:
                break

    if results:
        _OPENSTREETMAP_CACHE[cache_key] = results
    return results


def _normalize_tripadvisor_query(query: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", " ", query or "")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def _tripadvisor_search_url(query: str) -> str:
    return f"https://www.tripadvisor.com/Search?q={quote_plus(query)}"


def _extract_tripadvisor_tourism_url(search_html: str) -> Optional[str]:
    if not search_html:
        return None

    match = re.search(r'href="(?P<href>/Tourism-g\d+-[^\"]+-Vacations\.html)"', search_html)
    if match:
        return f"https://www.tripadvisor.com{match.group('href')}"

    match = re.search(r'(https://www\.tripadvisor\.com/Tourism-g\d+-[^\s\"]+-Vacations\.html)', search_html)
    if match:
        return match.group(1)

    return None


def _extract_tripadvisor_places_from_html(page_html: str, category: str, limit: int) -> List[Dict[str, Any]]:
    if not page_html:
        return []

    parser = _TripadvisorAnchorParser()
    parser.feed(page_html)

    href_pattern = r"/Restaurant_Review-" if category == "restaurants" else r"/Attraction_Review-"
    results: List[Dict[str, Any]] = []
    seen = set()

    for anchor in parser.anchors:
        href = anchor.get("href", "")
        text = (anchor.get("text") or "").strip()
        if not href or not text:
            continue
        if href_pattern not in href:
            continue
        full_url = href if href.startswith("http") else f"https://www.tripadvisor.com{href}"
        key = full_url.split("?")[0]
        if key in seen:
            continue
        seen.add(key)
        results.append({
            "location_id": key,
            "name": text,
            "address": "",
            "latitude": None,
            "longitude": None,
            "category": category,
            "summary": text,
            "source": "tripadvisor_public",
            "url": full_url,
        })
        if len(results) >= limit:
            break

    return results


def _tripadvisor_query_variants(query: str, category: str) -> List[str]:
    normalized = _normalize_tripadvisor_query(query)
    if not normalized:
        return []

    variants = [normalized]
    category_term = category.rstrip("s")
    if category_term and category_term not in normalized.lower():
        variants.append(f"{normalized} {category_term}")
    if category and category not in normalized.lower():
        variants.append(f"{normalized} {category}")
    return variants


def _get_tripadvisor_public_places(query: str, category: str, limit: int) -> List[Dict[str, Any]]:
    cache_key = (_normalize_tripadvisor_query(query).lower(), category, limit)
    cached = _TRIPADVISOR_PUBLIC_CACHE.get(cache_key)
    if cached is not None:
        return cached[:limit]

    query_lower = query.lower()
    tourism_url = None
    tourism_html = None

    for candidate_query in _tripadvisor_query_variants(query, category):
        search_url = _tripadvisor_search_url(candidate_query)
        search_html = _http_get_text(search_url)
        if not search_html:
            continue

        direct_results = _extract_tripadvisor_places_from_html(search_html, category, limit)
        if len(direct_results) >= limit:
            _TRIPADVISOR_PUBLIC_CACHE[cache_key] = direct_results
            return direct_results[:limit]

        if not tourism_url:
            tourism_url = _extract_tripadvisor_tourism_url(search_html)

        if tourism_url and not tourism_html:
            tourism_html = _http_get_text(tourism_url)

        merged_results = list(direct_results)
        if tourism_html:
            merged_results.extend(_extract_tripadvisor_places_from_html(tourism_html, category, limit))

        deduped: List[Dict[str, Any]] = []
        seen = set()
        for item in merged_results:
            key = (item.get("location_id") or item.get("url") or item.get("name") or "").split("?")[0]
            if not key or key in seen:
                continue
            seen.add(key)
            deduped.append(item)
            if len(deduped) >= limit:
                _TRIPADVISOR_PUBLIC_CACHE[cache_key] = deduped
                return deduped

    if tourism_url and not tourism_html:
        tourism_html = _http_get_text(tourism_url)
    if tourism_html:
        tourism_results = _extract_tripadvisor_places_from_html(tourism_html, category, limit)
        if tourism_results:
            _TRIPADVISOR_PUBLIC_CACHE[cache_key] = tourism_results
            return tourism_results[:limit]

    if not tourism_url:
        for key, page_url in TRIPADVISOR_TOURISM_PAGES.items():
            if key in query_lower:
                tourism_url = page_url
                break
        if tourism_url:
            tourism_html = _http_get_text(tourism_url)
            if tourism_html:
                tourism_results = _extract_tripadvisor_places_from_html(tourism_html, category, limit)
                if tourism_results:
                    _TRIPADVISOR_PUBLIC_CACHE[cache_key] = tourism_results
                    return tourism_results[:limit]

    return []


def get_google_maps_embed_url(destination_name: str, region: str = "") -> str:
    query = quote_plus(f"{destination_name}, {region}".strip(", "))
    return f"https://www.google.com/maps?q={query}&output=embed"


def get_google_maps_search_url(destination_name: str, region: str = "") -> str:
    query = quote_plus(f"{destination_name}, {region}".strip(", "))
    return f"https://www.google.com/maps/search/?api=1&query={query}"


def get_maptiler_tile_url() -> str:
    key = os.getenv("MAPTILER_API_KEY", "")
    if key:
        return f"https://api.maptiler.com/maps/streets-v2/{{z}}/{{x}}/{{y}}.png?key={key}"
    # Better fallback with higher resolution tiles
    return "https://tile.openstreetmap.org/{z}/{x}/{y}.png"


def _resolve_coordinates(destination_name: str = "", region: str = "") -> Optional[Tuple[float, float]]:
    """Resolve coordinates using local lookup first, then live geocoding APIs."""
    normalized_destination = destination_name.strip()
    normalized_region = region.strip()

    if normalized_destination in DESTINATION_COORDINATES:
        return DESTINATION_COORDINATES[normalized_destination]

    if normalized_region in REGION_COORDINATES:
        return REGION_COORDINATES[normalized_region]

    if normalized_destination:
        query = _build_query_name(normalized_destination, normalized_region)

        openweather_key = os.getenv("OPENWEATHER_API_KEY")
        if openweather_key:
            geocode_url = (
                "https://api.openweathermap.org/geo/1.0/direct"
                f"?q={quote_plus(query)}&limit=1&appid={openweather_key}"
            )
            data = _http_get_json(geocode_url)
            if isinstance(data, list) and data:
                first = data[0]
                lat = first.get("lat")
                lon = first.get("lon")
                if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
                    return float(lat), float(lon)

        maptiler_key = os.getenv("MAPTILER_API_KEY")
        if maptiler_key:
            geocode_url = (
                "https://api.maptiler.com/geocoding/"
                f"{quote_plus(query)}.json?key={maptiler_key}&limit=1"
            )
            data = _http_get_json(geocode_url)
            features = data.get("features", []) if isinstance(data, dict) else []
            if features:
                center = features[0].get("center", [])
                if len(center) >= 2:
                    return float(center[1]), float(center[0])

    return None


def get_coordinates(region: str) -> Optional[Tuple[float, float]]:
    return _resolve_coordinates(region=region)


def _estimate_segment_time(distance_km: float, weather_condition: str = "") -> int:
    """Estimate local travel time in minutes using a simple city/road heuristic."""
    base_speed_kmh = 35.0
    if any(term in weather_condition.lower() for term in ["rain", "storm", "snow"]):
        base_speed_kmh *= 0.75
    elif any(term in weather_condition.lower() for term in ["hot", "dry"]):
        base_speed_kmh *= 0.9

    hours = distance_km / max(base_speed_kmh, 1)
    return max(8, int(round(hours * 60)))


def _build_navigation_plan(destination: Dict[str, Any], daily_plan: List[Dict[str, Any]], weather: Dict[str, Any]) -> Dict[str, Any]:
    """Build an easy-to-read navigation summary and route timings for the itinerary."""
    dest_name = destination.get("name", "")
    coords = _resolve_coordinates(dest_name, destination.get("region", "")) or (30.3753, 69.3451)
    route_points = []

    activities = destination.get("activities", []) or []
    for index, day in enumerate(daily_plan, start=1):
        activity_name = day.get("activity_focus") or (activities[(index - 1) % len(activities)] if activities else "Sightseeing")
        distance_km = round(4 + (index * 1.8), 1)
        travel_minutes = _estimate_segment_time(distance_km, weather.get("condition", ""))
        route_points.append({
            "day": index,
            "from": dest_name if index == 1 else f"Day {index - 1} hotel",
            "to": activity_name,
            "distance_km": distance_km,
            "travel_time_minutes": travel_minutes,
            "note": day.get("event") or "Optimized for local travel",
        })

    total_distance = round(sum(point["distance_km"] for point in route_points), 1)
    total_time = sum(point["travel_time_minutes"] for point in route_points)

    return {
        "center": {"lat": coords[0], "lng": coords[1]},
        "search_url": get_google_maps_search_url(dest_name, destination.get("region", "")),
        "embed_url": get_google_maps_embed_url(dest_name, destination.get("region", "")),
        "tile_url": get_maptiler_tile_url(),
        "summary": {
            "segments": len(route_points),
            "distance_km": total_distance,
            "travel_time_minutes": total_time,
        },
        "segments": route_points,
    }


def get_live_weather(region: str, destination_name: str = "") -> Dict[str, Any]:
    api_key = os.getenv("OPENWEATHER_API_KEY")
    coords = _resolve_coordinates(destination_name, region)

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
    if not query:
        return []

    data = None
    if api_key:
        search_url = (
            "https://api.content.tripadvisor.com/api/v1/location/search"
            f"?key={api_key}&searchQuery={quote_plus(query)}&category={quote_plus(category)}&language=en"
        )
        data = _http_get_json(search_url)

    results: List[Dict[str, Any]] = []
    raw_items: List[Dict[str, Any]] = []
    if isinstance(data, dict):
        for key in ("data", "results", "places", "locationSuggestions"):
            if isinstance(data.get(key), list):
                raw_items = data[key]
                break
    elif isinstance(data, list):
        raw_items = data

    for item in raw_items[:limit]:
        address = ""
        if isinstance(item.get("address_obj"), dict):
            address = item["address_obj"].get("address_string", "")
        elif isinstance(item.get("address"), str):
            address = item["address"]

        results.append({
            "location_id": item.get("location_id") or item.get("id") or item.get("placeId"),
            "name": item.get("name", "Unknown"),
            "address": address,
            "latitude": item.get("latitude") or item.get("lat"),
            "longitude": item.get("longitude") or item.get("lng") or item.get("lon"),
            "category": category,
            "summary": item.get("name", "Unknown"),
            "source": "traveladvisor",
        })

    if results:
        return results

    public_results = _get_tripadvisor_public_places(query, category, limit)
    if public_results:
        return public_results

    osm_results = _openstreetmap_places(query, category, limit)
    if osm_results:
        return osm_results

    query_lower = query.lower()
    fallback_bucket = None
    for key in FALLBACK_PLACES:
        if key in query_lower:
            fallback_bucket = key
            break

    if fallback_bucket:
        fallback_items = FALLBACK_PLACES[fallback_bucket].get(category, [])
        for index, item in enumerate(fallback_items[:limit], start=1):
            results.append({
                "location_id": f"fallback-{fallback_bucket}-{category}-{index}",
                "name": item.get("name", "Unknown"),
                "address": item.get("address", ""),
                "latitude": item.get("latitude"),
                "longitude": item.get("longitude"),
                "category": category,
                "summary": f"Curated fallback suggestion for {fallback_bucket.title()}",
                "source": "fallback",
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

    dest_name = destination.get("name", "")
    navigation = _build_navigation_plan(destination, daily_plan, live_weather)

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
        "navigation": navigation,
        "map": navigation,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }
