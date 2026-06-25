"""
Travel Planning Web Application - Backend
Flask server with REST API endpoints
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from google.oauth2 import id_token
from google.auth.transport import requests as grequests
import json
import os
from datetime import datetime, timedelta
from collections import Counter
from uuid import uuid4
from dotenv import load_dotenv
from recommendation_engine import RecommendationEngine
from nlp_parser import QueryParser
from mongodb_persistence import build_mongodb_persistence
from integration_services import (
    generate_itinerary,
    get_live_weather,
    get_weather_advisories,
    get_traveladvisor_places,
)

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(__file__)
load_dotenv(os.path.join(BASE_DIR, '.env'))

@app.route('/favicon.ico')
def favicon():
    return '', 204  # Return empty response with No Content status

# Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)
jwt = JWTManager(app)

# Initialize components
recommendation_engine = RecommendationEngine()
query_parser = QueryParser()

# Initialize MongoDB persistence (fallback to JSON files if unavailable)
try:
    MONGO_DB = build_mongodb_persistence()
except Exception as exc:
    MONGO_DB = None
    print(
        "[WARN] MongoDB unavailable; running with JSON file storage only. "
        f"Reason: {exc}"
    )

# Data collection names in MongoDB
DESTINATIONS_COLLECTION = "destinations"
USERS_COLLECTION = "users"
COST_RATES_COLLECTION = "cost_rates"
FEEDBACK_COLLECTION = "feedback"
ANALYTICS_COLLECTION = "analytics"
MODELS_COLLECTION = "models"

# Data file paths (kept for backward compatibility / seeding)
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
DESTINATIONS_FILE = os.path.join(DATA_DIR, 'destinations.json')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
COST_RATES_FILE = os.path.join(DATA_DIR, 'cost_rates.json')
FEEDBACK_FILE = os.path.join(DATA_DIR, 'feedback.json')
ANALYTICS_FILE = os.path.join(DATA_DIR, 'analytics.json')
MODELS_FILE = os.path.join(DATA_DIR, 'models.json')

DEFAULT_MODELS = [
    {
        'id': 1,
        'name': 'Content-Based Filtering',
        'version': '1.2.0',
        'status': 'active',
        'accuracy': 87,
        'last_trained': '2024-01-15',
        'description': 'Recommends destinations based on activity preferences and user history',
    },
    {
        'id': 2,
        'name': 'Collaborative Filtering',
        'version': '2.0.1',
        'status': 'active',
        'accuracy': 92,
        'last_trained': '2024-01-20',
        'description': 'Uses user similarity patterns for recommendations',
    },
    {
        'id': 3,
        'name': 'NLP Query Parser',
        'version': '1.5.0',
        'status': 'active',
        'accuracy': 95,
        'last_trained': '2024-01-18',
        'description': 'Parses natural language queries for destination search',
    },
    {
        'id': 4,
        'name': 'Budget Optimizer',
        'version': '1.0.0',
        'status': 'inactive',
        'accuracy': 78,
        'last_trained': '2024-01-10',
        'description': 'Optimizes trip costs based on user budget constraints',
    },
]

# Seed MongoDB from JSON files if collections are empty
def seed_mongodb():
    """Load initial data from JSON files into MongoDB if collections are empty."""
    if MONGO_DB is None:
        print("[INFO] Skipping MongoDB seeding (MongoDB not available).")
        return
    for filepath, collection_name in [
        (DESTINATIONS_FILE, DESTINATIONS_COLLECTION),
        (USERS_FILE, USERS_COLLECTION),
        (COST_RATES_FILE, COST_RATES_COLLECTION)
    ]:
        if os.path.exists(filepath):
            collection = MONGO_DB.get_collection(collection_name)
            if collection.count_documents({}) == 0:
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    collection.insert_one({"_id": collection_name, "payload": data})
                    print(f"[OK] Seeded {collection_name} from {filepath}")
                except Exception as e:
                    print(f"[ERROR] Error seeding {collection_name}: {e}")

seed_mongodb()

# Helper functions
def load_json(collection_name):
    """Load JSON data from MongoDB collection.
    
    Args:
        collection_name: Name of MongoDB collection to load from
    """
    if MONGO_DB is not None:
        data = MONGO_DB.load_json(collection_name, collection_name)
        if data is not None:
            return data
    
    # Fallback to file if collection is empty
    filepath_map = {
        DESTINATIONS_COLLECTION: DESTINATIONS_FILE,
        USERS_COLLECTION: USERS_FILE,
        COST_RATES_COLLECTION: COST_RATES_FILE,
        FEEDBACK_COLLECTION: FEEDBACK_FILE,
        ANALYTICS_COLLECTION: ANALYTICS_FILE,
        MODELS_COLLECTION: MODELS_FILE,
    }
    filepath = filepath_map.get(collection_name)
    if filepath and os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            pass
    
    return [] if collection_name in [USERS_COLLECTION, DESTINATIONS_COLLECTION, FEEDBACK_COLLECTION, ANALYTICS_COLLECTION, MODELS_COLLECTION] else {}

def save_json(collection_name, data):
    """Save data to MongoDB collection.
    
    Args:
        collection_name: Name of MongoDB collection to save to
        data: Data to save
    """
    if MONGO_DB is not None:
        success = MONGO_DB.save_json(collection_name, collection_name, data)
        if not success:
            print(f"Warning: Failed to save to MongoDB collection {collection_name}")
    
    # Also save to file for backup
    filepath_map = {
        DESTINATIONS_COLLECTION: DESTINATIONS_FILE,
        USERS_COLLECTION: USERS_FILE,
        COST_RATES_COLLECTION: COST_RATES_FILE,
        FEEDBACK_COLLECTION: FEEDBACK_FILE,
        ANALYTICS_COLLECTION: ANALYTICS_FILE,
        MODELS_COLLECTION: MODELS_FILE,
    }
    filepath = filepath_map.get(collection_name)
    if filepath:
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Failed to save backup file {filepath}: {e}")


def utc_now_iso():
    return datetime.utcnow().isoformat() + "Z"


def append_collection_item(collection_name, item):
    records = load_json(collection_name)
    if not isinstance(records, list):
        records = []
    records.append(item)
    save_json(collection_name, records)
    return item


def log_activity(event_type, payload=None):
    event = {
        'id': len(load_json(ANALYTICS_COLLECTION) or []) + 1,
        'event_type': event_type,
        'timestamp': utc_now_iso(),
    }
    if payload:
        event.update(payload)
    append_collection_item(ANALYTICS_COLLECTION, event)
    return event


def get_destination_by_name(destinations, name):
    if not name:
        return None
    name_lower = name.lower()
    return next((d for d in destinations if d.get('name', '').lower() == name_lower), None)


def get_feedback_items():
    feedback = load_json(FEEDBACK_COLLECTION)
    return feedback if isinstance(feedback, list) else []


def get_model_items():
    models = load_json(MODELS_COLLECTION)
    if not isinstance(models, list) or not models:
        models = DEFAULT_MODELS.copy()
        save_json(MODELS_COLLECTION, models)
    return models


def save_model_items(models):
    save_json(MODELS_COLLECTION, models)
    return models


def build_activity_summary():
    analytics = load_json(ANALYTICS_COLLECTION)
    if not isinstance(analytics, list):
        analytics = []

    feedback = get_feedback_items()
    search_events = [item for item in analytics if item.get('event_type') == 'search']
    itinerary_events = [item for item in analytics if item.get('event_type') == 'itinerary_generated']
    save_events = [item for item in analytics if item.get('event_type') == 'save_trip']

    query_counter = Counter(
        item.get('query') or item.get('parsed_query', {}).get('original_query', '')
        for item in search_events
        if (item.get('query') or item.get('parsed_query', {}).get('original_query', ''))
    )
    destination_counter = Counter(
        item.get('destination')
        for item in save_events
        if item.get('destination')
    )

    daily_counter = Counter()
    for item in analytics:
        timestamp = item.get('timestamp', '')
        if timestamp:
            daily_counter[timestamp[:10]] += 1

    return {
        'total_searches': len(search_events),
        'total_itineraries': len(itinerary_events),
        'total_bookmarks': len(save_events),
        'total_feedback': len(feedback),
        'pending_feedback': len([item for item in feedback if item.get('status', 'new') == 'new']),
        'average_session_time': 'Tracked via activity logs',
        'popular_searches': [
            {'query': query, 'count': count} for query, count in query_counter.most_common(5)
        ],
        'top_destinations': [
            {'name': destination, 'views': count} for destination, count in destination_counter.most_common(5)
        ],
        'daily_activity': [
            {'date': date, 'events': count} for date, count in sorted(daily_counter.items(), reverse=True)[:7]
        ],
        'recent_activity': list(reversed(analytics[-10:])),
    }


def _find_user_saved_trip(user, trip_id):
    try:
        trip_id = int(trip_id)
    except Exception:
        return None, None

    saved_trips = user.get('saved_trips', [])
    for index, trip in enumerate(saved_trips):
        if int(trip.get('id', -1)) == trip_id:
            return index, trip
    return None, None


def get_user_by_email(users, email):
    return next((u for u in users if u['email'] == email), None)


def get_current_user_and_users():
    current_user_email = get_jwt_identity()
    users = load_json(USERS_COLLECTION)
    return get_user_by_email(users, current_user_email), users


def require_admin():
    user, users = get_current_user_and_users()
    if not user or user.get('role') != 'admin':
        return None, users, (jsonify({'error': 'Admin access required'}), 403)

    return user, users, None


def get_destination_by_id(destinations, dest_id):
    destination = next((d for d in destinations if d.get('id') == dest_id), None)
    if destination is not None:
        return destination

    if 0 <= dest_id < len(destinations):
        return destinations[dest_id]

    return None


def serialize_user(user):
    return {
        'id': user['id'],
        'email': user['email'],
        'name': user['name'],
        'preferences': user.get('preferences', {}),
        'saved_trips': user.get('saved_trips', []),
        'history': user.get('history', []),
        'role': user.get('role', 'user')
    }

# ==================== HOME PAGE ROUTES ====================

@app.route('/api/search', methods=['POST'])
def search_trips():
    """
    Parse search query and return matching destinations
    Example: "Plan a 3-day trip to northern Pakistan under 25,000 PKR"
    """
    data = request.json
    query = data.get('query', '')
    
    # Parse the query using NLP module
    parsed = query_parser.parse(query)
    
    # Get destinations matching criteria
    destinations = load_json(DESTINATIONS_COLLECTION)
    
    # Filter destinations based on parsed parameters
    filtered = []
    for dest in destinations:
        match = True
        if parsed.get('budget') and dest['cost'] > parsed['budget']:
            match = False
        if parsed.get('region') and parsed['region'].lower() not in dest['region'].lower():
            match = False
        if parsed.get('type') and parsed['type'].lower() != dest['type'].lower():
            match = False
        if match:
            filtered.append(dest)
    
    # Generate budget estimation for each destination
    cost_rates = load_json(COST_RATES_COLLECTION)
    days = parsed.get('days', 3)
    
    results = []
    for dest in filtered:
        budget_estimate = calculate_budget(dest, days, cost_rates)
        results.append({
            **dest,
            'budget_estimate': budget_estimate,
            'days': days
        })

    log_activity('search', {
        'query': query,
        'parsed_query': parsed,
        'result_count': len(results),
        'intent': parsed.get('intent'),
        'destination': parsed.get('destination'),
        'region': parsed.get('region'),
    })
    
    return jsonify({
        'parsed_query': parsed,
        'destinations': results,
        'total_results': len(results)
    })

@app.route('/api/destinations', methods=['GET'])
def get_destinations():
    """Get all destinations or filter by parameters"""
    destinations = load_json(DESTINATIONS_COLLECTION)
    
    # Optional filtering
    region = request.args.get('region')
    travel_type = request.args.get('type')
    max_cost = request.args.get('max_cost', type=int)
    
    filtered = destinations
    
    if region:
        filtered = [d for d in filtered if region.lower() in d['region'].lower()]
    if travel_type:
        filtered = [d for d in filtered if travel_type.lower() == d['type'].lower()]
    if max_cost:
        filtered = [d for d in filtered if d['cost'] <= max_cost]
    
    return jsonify(filtered)

@app.route('/api/destinations/<int:dest_id>', methods=['GET'])
def get_destination(dest_id):
    """Get single destination by ID"""
    destinations = load_json(DESTINATIONS_COLLECTION)
    destination = get_destination_by_id(destinations, dest_id)
    if destination:
        destination['view_count'] = int(destination.get('view_count', 0)) + 1
        destination['last_viewed_at'] = utc_now_iso()
        save_json(DESTINATIONS_COLLECTION, destinations)
        log_activity('destination_view', {
            'destination': destination.get('name'),
            'region': destination.get('region'),
            'destination_id': dest_id,
        })
        return jsonify(destination)
    return jsonify({'error': 'Destination not found'}), 404

@app.route('/api/recommendations', methods=['GET', 'POST'])
def get_recommendations():
    """
    Get personalized destination recommendations
    Uses ML-based content filtering and collaborative filtering
    """
    destinations = load_json(DESTINATIONS_COLLECTION)
    request_data = request.get_json(silent=True) or {}
    
    if request.method == 'POST':
        user_preferences = request_data.get('preferences', {})
        user_history = request_data.get('history', [])
        
        # Get ML-based recommendations
        recommendations = recommendation_engine.get_recommendations(
            destinations=destinations,
            preferences=user_preferences,
            history=user_history
        )
    else:
        # For guest users - recommend popular destinations
        recommendations = recommendation_engine.get_popular_destinations(destinations)

    log_activity('recommendations', {
        'mode': request.method.lower(),
        'result_count': len(recommendations),
        'has_preferences': bool(request.method == 'POST' and request_data.get('preferences')),
    })
    
    return jsonify(recommendations)

@app.route('/api/travel-suggestions', methods=['GET'])
def get_travel_suggestions():
    """Get real-time travel suggestions for homepage"""
    destinations = load_json(DESTINATIONS_COLLECTION)
    
    suggestions = [
        {
            'title': 'Top Adventure Spots under 20,000 PKR',
            'destinations': [d for d in destinations if d['type'] == 'Adventure' and d['cost'] <= 20000][:3]
        },
        {
            'title': 'Best Weekend Destinations Near You',
            'destinations': sorted(destinations, key=lambda x: x['cost'])[:3]
        },
        {
            'title': 'Highest Rated Destinations',
            'destinations': sorted(destinations, key=lambda x: x['user_rating'], reverse=True)[:3]
        },
        {
            'title': 'Family-Friendly Getaways',
            'destinations': [d for d in destinations if d['type'] == 'Family'][:3]
        }
    ]
    
    return jsonify(suggestions)


@app.route('/api/home/insights', methods=['GET'])
def get_home_insights():
    """Get featured destinations, weather highlights, and travel advisories for the home page."""
    destinations = load_json(DESTINATIONS_COLLECTION)
    featured = recommendation_engine.get_popular_destinations(destinations, num=4)
    analytics = load_json(ANALYTICS_COLLECTION)

    trend_scores = Counter()
    for dest in destinations:
        score = int(dest.get('saved_count', 0)) * 3 + int(dest.get('view_count', 0))
        trend_scores[dest['name']] += score

    for item in analytics if isinstance(analytics, list) else []:
        if item.get('destination'):
            trend_scores[item['destination']] += 2 if item.get('event_type') == 'save_trip' else 1

    weather_highlights = []
    advisories = []
    seen_titles = set()  # Track seen advisory titles to avoid duplicates
    
    for dest in featured[:3]:
        live_weather = get_live_weather(dest.get('region', ''), dest.get('name', ''))
        weather_highlights.append({
            'destination': dest['name'],
            'region': dest['region'],
            'temperature': live_weather.get('temperature'),
            'condition': live_weather.get('condition'),
            'description': live_weather.get('description'),
            'updated_at': live_weather.get('updated_at')
        })
        # Add advisories but skip duplicates based on title
        for advisory in get_weather_advisories(live_weather, dest):
            if advisory['title'] not in seen_titles:
                advisories.append(advisory)
                seen_titles.add(advisory['title'])

    return jsonify({
        'featured_destinations': featured,
        'trending_destinations': [
            next((d for d in destinations if d.get('name') == name), {'name': name})
            for name, _ in trend_scores.most_common(4)
        ],
        'weather_highlights': weather_highlights,
        'travel_advisories': advisories[:5],
        'ai_suggestions': [
            'Ideal weekend destinations this month',
            'Best budget trips under 20,000 PKR',
            'Top-rated adventure places near you'
        ]
    })


@app.route('/api/weather/highlights', methods=['GET'])
def get_weather_highlights():
    """Return live weather snapshots for a region or all featured destinations."""
    destinations = load_json(DESTINATIONS_COLLECTION)
    region = request.args.get('region')

    if region:
        matched = [d for d in destinations if region.lower() in d.get('region', '').lower()]
    else:
        matched = recommendation_engine.get_popular_destinations(destinations, num=3)

    highlights = []
    for dest in matched[:5]:
        live_weather = get_live_weather(dest.get('region', ''), dest.get('name', ''))
        highlights.append({
            'destination': dest['name'],
            'region': dest['region'],
            'weather': live_weather,
            'advisories': get_weather_advisories(live_weather, dest)
        })

    return jsonify(highlights)


@app.route('/api/explore/places', methods=['GET'])
def get_explore_places():
    """Fetch points of interest from TravelAdvisor API with fallback."""
    query = request.args.get('query', '')
    category = request.args.get('category', 'attractions')
    limit = request.args.get('limit', default=5, type=int)

    places = get_traveladvisor_places(query=query, category=category, limit=limit)
    return jsonify({
        'query': query,
        'category': category,
        'source': places[0].get('source', 'fallback') if places else 'fallback',
        'places': places
    })


@app.route('/api/itinerary/generate', methods=['POST'])
def generate_itinerary_route():
    """Generate a day-by-day trip plan using NLP, recommendation logic, and live weather."""
    data = request.json or {}
    query = data.get('query', '')
    
    parsed = query_parser.parse(query) if query else {}
    
    destination_name = data.get('destination')
    if not destination_name and parsed.get('destination'):
        destination_name = parsed['destination']

    # Use explicitly provided days/budget, fallback to NLP parsed values, then defaults
    try:
        days = int(data.get('days')) if data.get('days') else (parsed.get('days') or 3)
    except Exception:
        days = parsed.get('days') or 3

    try:
        budget = float(data.get('budget')) if data.get('budget') else parsed.get('budget')
    except Exception:
        budget = parsed.get('budget')

    preferences = data.get('preferences') or {}

    destinations = load_json(DESTINATIONS_COLLECTION)
    cost_rates = load_json(COST_RATES_COLLECTION)

    candidates = destinations
    if parsed.get('budget'):
        candidates = [d for d in candidates if d.get('cost', 0) <= parsed['budget']]
    if parsed.get('region'):
        candidates = [d for d in candidates if parsed['region'].lower() in d.get('region', '').lower()]
    if parsed.get('type'):
        candidates = [d for d in candidates if d.get('type', '').lower() == parsed['type'].lower()]

    import difflib

    destination = None
    if destination_name:
        # Exact match first
        destination = next((d for d in destinations if d['name'].lower() == destination_name.lower()), None)
        # Fuzzy match fallback
        if not destination:
            dest_names = [d['name'] for d in destinations]
            matches = difflib.get_close_matches(destination_name, dest_names, n=1, cutoff=0.6)
            if matches:
                matched_name = matches[0]
                destination = next((d for d in destinations if d['name'] == matched_name), None)

    if not destination and candidates:
        ranked = recommendation_engine.get_recommendations(candidates, preferences=preferences, num_recommendations=1)
        destination = ranked[0] if ranked else candidates[0]
    if not destination:
        destination = recommendation_engine.get_popular_destinations(destinations, num=1)[0]

    budget_breakdown = calculate_budget(destination, days, cost_rates)
    itinerary = generate_itinerary(
        destination=destination,
        days=days,
        budget=budget,
        preferences=preferences,
        budget_breakdown=budget_breakdown,
    )

    itinerary['parsed_query'] = parsed
    itinerary['recommendation_score'] = destination.get('recommendation_score')
    itinerary['match_reason'] = destination.get('match_reason')
    itinerary['budget_status'] = (
        'over_budget' if budget and itinerary['budget_breakdown']['total'] > budget else 'within_budget'
    )

    if budget and itinerary['budget_status'] == 'over_budget':
        cheaper = [d for d in destinations if d.get('cost', 0) <= budget]
        itinerary['budget_alternative'] = recommendation_engine.get_popular_destinations(cheaper, num=1)[:1]

    place_query = f"{destination.get('name', '')} {destination.get('region', '')}".strip()
    itinerary['recommended_places'] = {
        'attractions': get_traveladvisor_places(place_query, category='attractions', limit=5),
        'restaurants': get_traveladvisor_places(place_query, category='restaurants', limit=5),
    }

    log_activity('itinerary_generated', {
        'destination': itinerary['destination'].get('name'),
        'region': itinerary['destination'].get('region'),
        'days': itinerary.get('days'),
        'budget': budget,
        'budget_status': itinerary.get('budget_status'),
        'intent': parsed.get('intent'),
    })

    return jsonify(itinerary)

# ==================== USER AUTHENTICATION ROUTES ====================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.json
    email = data.get('email')
    name = data.get('name')
    password = data.get('password')
    
    if not all([email, name, password]):
        return jsonify({'error': 'All fields are required'}), 400
    
    users = load_json(USERS_COLLECTION)
    
    # Check if user already exists
    if any(u['email'] == email for u in users):
        return jsonify({'error': 'Email already registered'}), 400
    
    # Create new user
    new_user = {
        'id': len(users) + 1,
        'email': email,
        'name': name,
        'password': generate_password_hash(password),
        'preferences': {
            'budget_range': {'min': 10000, 'max': 50000},
            'travel_style': [],
            'duration': 3
        },
        'saved_trips': [],
        'history': [],
        'role': 'user'
    }
    
    users.append(new_user)
    save_json(USERS_COLLECTION, users)
    
    # Generate token
    access_token = create_access_token(identity=email)
    
    return jsonify({
        'message': 'Registration successful',
        'token': access_token,
        'user': serialize_user(new_user)
    }), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    users = load_json(USERS_COLLECTION)
    user = get_user_by_email(users, email)
    
    if not user or not check_password_hash(user['password'], password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    access_token = create_access_token(identity=email)
    
    return jsonify({
        'message': 'Login successful',
        'token': access_token,
        'user': serialize_user(user)
    })


@app.route('/api/auth/google', methods=['POST'])
def google_login():
    """Login or register with Google OAuth ID token."""
    data = request.json or {}
    token = data.get('id_token')
    google_client_id = os.getenv('GOOGLE_CLIENT_ID')

    if not google_client_id:
        return jsonify({'error': 'Google OAuth is not configured on server'}), 400

    if not token:
        return jsonify({'error': 'id_token is required'}), 400

    try:
        id_info = id_token.verify_oauth2_token(token, grequests.Request(), google_client_id)
    except Exception:
        return jsonify({'error': 'Invalid Google token'}), 401

    email = id_info.get('email')
    name = id_info.get('name') or email.split('@')[0]
    if not email:
        return jsonify({'error': 'Google account email is unavailable'}), 400

    users = load_json(USERS_COLLECTION)
    user = get_user_by_email(users, email)

    if not user:
        user = {
            'id': len(users) + 1,
            'email': email,
            'name': name,
            'password': generate_password_hash(os.urandom(24).hex()),
            'preferences': {
                'budget_range': {'min': 10000, 'max': 50000},
                'travel_style': [],
                'duration': 3
            },
            'saved_trips': [],
            'history': [],
            'role': 'user',
            'auth_provider': 'google'
        }
        users.append(user)
        save_json(USERS_COLLECTION, users)

    access_token = create_access_token(identity=email)
    return jsonify({
        'message': 'Google login successful',
        'token': access_token,
        'user': serialize_user(user)
    })

@app.route('/api/auth/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    current_user_email = get_jwt_identity()
    users = load_json(USERS_COLLECTION)
    user = get_user_by_email(users, current_user_email)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        **serialize_user(user)
    })


@app.route('/api/auth/history', methods=['GET'])
@jwt_required()
def get_history():
    """Get current user travel history"""
    current_user_email = get_jwt_identity()
    users = load_json(USERS_COLLECTION)
    user = get_user_by_email(users, current_user_email)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify(user.get('history', []))

@app.route('/api/auth/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile and preferences"""
    current_user_email = get_jwt_identity()
    data = request.json
    
    users = load_json(USERS_COLLECTION)
    user_index = next((i for i, u in enumerate(users) if u['email'] == current_user_email), None)
    
    if user_index is None:
        return jsonify({'error': 'User not found'}), 404
    
    # Update allowed fields
    if 'name' in data:
        users[user_index]['name'] = data['name']
    if 'preferences' in data:
        users[user_index]['preferences'].update(data['preferences'])
    
    save_json(USERS_COLLECTION, users)
    
    return jsonify({
        'message': 'Profile updated successfully',
        'user': serialize_user(users[user_index])
    })

@app.route('/api/auth/save-trip', methods=['POST'])
@jwt_required()
def save_trip():
    """Save a trip plan for the user"""
    current_user_email = get_jwt_identity()
    data = request.json
    
    users = load_json(USERS_COLLECTION)
    destinations = load_json(DESTINATIONS_COLLECTION)
    user_index = next((i for i, u in enumerate(users) if u['email'] == current_user_email), None)
    
    if user_index is None:
        return jsonify({'error': 'User not found'}), 404
    
    trip = {
        'id': len(users[user_index]['saved_trips']) + 1,
        'destination': data.get('destination'),
        'days': data.get('days'),
        'budget_estimate': data.get('budget_estimate'),
        'saved_at': data.get('saved_at') or utc_now_iso(),
        'daily_plan': data.get('daily_plan', []),
        'query': data.get('query', ''),
        'parsed_query': data.get('parsed_query', {}),
        'notes': data.get('notes', ''),
        'share_token': data.get('share_token') or uuid4().hex,
    }
    
    users[user_index]['saved_trips'].append(trip)
    users[user_index].setdefault('history', []).append({
        'destination': trip['destination'],
        'days': trip['days'],
        'budget_estimate': trip['budget_estimate'],
        'saved_at': trip['saved_at'],
        'action': 'saved_trip',
        'query': trip['query'],
        'daily_plan': trip['daily_plan'],
    })

    destination = get_destination_by_name(destinations, trip['destination'])
    if destination:
        destination['saved_count'] = int(destination.get('saved_count', 0)) + 1
        destination['last_saved_at'] = trip['saved_at']
        save_json(DESTINATIONS_COLLECTION, destinations)

    save_json(USERS_COLLECTION, users)

    log_activity('save_trip', {
        'user_email': current_user_email,
        'destination': trip['destination'],
        'days': trip['days'],
        'saved_at': trip['saved_at'],
    })
    
    return jsonify({
        'message': 'Trip saved successfully',
        'trip': trip,
        'user': serialize_user(users[user_index])
    })


@app.route('/api/auth/saved-trips/<int:trip_id>', methods=['PUT'])
@jwt_required()
def update_saved_trip(trip_id):
    """Update a saved trip plan for the current user."""
    current_user_email = get_jwt_identity()
    data = request.json or {}

    users = load_json(USERS_COLLECTION)
    user_index = next((i for i, u in enumerate(users) if u['email'] == current_user_email), None)

    if user_index is None:
        return jsonify({'error': 'User not found'}), 404

    trip_index, trip = _find_user_saved_trip(users[user_index], trip_id)
    if trip is None:
        return jsonify({'error': 'Saved trip not found'}), 404

    for field in ['destination', 'days', 'notes', 'query']:
        if field in data:
            trip[field] = data[field]

    if 'budget_estimate' in data:
        trip['budget_estimate'] = data['budget_estimate']
    if 'daily_plan' in data:
        trip['daily_plan'] = data['daily_plan']

    trip['updated_at'] = utc_now_iso()
    users[user_index]['saved_trips'][trip_index] = trip
    save_json(USERS_COLLECTION, users)

    log_activity('saved_trip_updated', {
        'user_email': current_user_email,
        'trip_id': trip_id,
        'destination': trip.get('destination'),
    })

    return jsonify({'message': 'Saved trip updated successfully', 'trip': trip, 'user': serialize_user(users[user_index])})


@app.route('/api/auth/saved-trips/<int:trip_id>', methods=['DELETE'])
@jwt_required()
def delete_saved_trip(trip_id):
    """Delete a saved trip for the current user."""
    current_user_email = get_jwt_identity()

    users = load_json(USERS_COLLECTION)
    user_index = next((i for i, u in enumerate(users) if u['email'] == current_user_email), None)

    if user_index is None:
        return jsonify({'error': 'User not found'}), 404

    trip_index, trip = _find_user_saved_trip(users[user_index], trip_id)
    if trip is None:
        return jsonify({'error': 'Saved trip not found'}), 404

    users[user_index]['saved_trips'].pop(trip_index)
    save_json(USERS_COLLECTION, users)

    log_activity('saved_trip_deleted', {
        'user_email': current_user_email,
        'trip_id': trip_id,
        'destination': trip.get('destination'),
    })

    return jsonify({'message': 'Saved trip deleted successfully', 'user': serialize_user(users[user_index])})


@app.route('/api/auth/saved-trips/<int:trip_id>/share', methods=['POST'])
@jwt_required()
def share_saved_trip(trip_id):
    """Create or return a shareable link for a saved trip."""
    current_user_email = get_jwt_identity()

    users = load_json(USERS_COLLECTION)
    user_index = next((i for i, u in enumerate(users) if u['email'] == current_user_email), None)

    if user_index is None:
        return jsonify({'error': 'User not found'}), 404

    trip_index, trip = _find_user_saved_trip(users[user_index], trip_id)
    if trip is None:
        return jsonify({'error': 'Saved trip not found'}), 404

    if not trip.get('share_token'):
        trip['share_token'] = uuid4().hex
        users[user_index]['saved_trips'][trip_index] = trip
        save_json(USERS_COLLECTION, users)

    share_url = f"{request.host_url.rstrip('/')}/shared-trip/{trip['share_token']}"

    log_activity('saved_trip_shared', {
        'user_email': current_user_email,
        'trip_id': trip_id,
        'destination': trip.get('destination'),
    })

    return jsonify({'share_url': share_url, 'trip': trip})


@app.route('/api/shared-trip/<string:share_token>', methods=['GET'])
def get_shared_trip(share_token):
    """Public endpoint for viewing a shared saved trip."""
    users = load_json(USERS_COLLECTION)
    for user in users:
        for trip in user.get('saved_trips', []):
            if trip.get('share_token') == share_token:
                return jsonify({
                    'trip': trip,
                    'owner': {
                        'name': user.get('name'),
                        'email': user.get('email') if user.get('share_profile', True) else None,
                    }
                })

    return jsonify({'error': 'Shared trip not found'}), 404

# ==================== BUDGET ESTIMATION ROUTES ====================

def calculate_budget(destination, days, cost_rates):
    """Calculate estimated budget for a trip"""
    region_rates = cost_rates.get(destination['region'], cost_rates.get('default', {}))
    
    hotel_cost = region_rates.get('hotel_per_day', 3000) * days
    travel_cost = region_rates.get('travel', 5000)
    meal_cost = region_rates.get('meals_per_day', 1500) * days
    activities_cost = region_rates.get('activities', 2000)
    
    total = hotel_cost + travel_cost + meal_cost + activities_cost
    
    return {
        'hotel': hotel_cost,
        'travel': travel_cost,
        'meals': meal_cost,
        'activities': activities_cost,
        'total': total,
        'days': days
    }

@app.route('/api/budget/estimate', methods=['POST'])
def estimate_budget():
    """Get detailed budget estimation for a trip"""
    data = request.json
    destination_name = data.get('destination')
    days = data.get('days', 3)
    
    destinations = load_json(DESTINATIONS_COLLECTION)
    cost_rates = load_json(COST_RATES_COLLECTION)
    
    destination = next((d for d in destinations if d['name'].lower() == destination_name.lower()), None)
    
    if not destination:
        return jsonify({'error': 'Destination not found'}), 404
    
    budget = calculate_budget(destination, days, cost_rates)
    
    return jsonify({
        'destination': destination['name'],
        'region': destination['region'],
        'budget_breakdown': budget,
        'tips': [
            'Book hotels in advance for better rates',
            'Consider local transport options',
            'Try local cuisine for authentic experience'
        ]
    })


@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """Store traveler feedback so admins can review real comments and ratings."""
    data = request.json or {}
    destination = (data.get('destination') or '').strip()
    rating = data.get('rating')
    comment = (data.get('comment') or '').strip()

    if not destination or not comment:
        return jsonify({'error': 'Destination and comment are required'}), 400

    try:
        rating_value = int(rating)
    except Exception:
        rating_value = 0

    if rating_value < 1 or rating_value > 5:
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400

    feedbacks = get_feedback_items()
    feedback = {
        'id': len(feedbacks) + 1,
        'user': data.get('user') or data.get('email') or 'Anonymous',
        'email': data.get('email') or '',
        'destination': destination,
        'rating': rating_value,
        'comment': comment,
        'date': data.get('date') or utc_now_iso(),
        'status': 'new',
        'source': data.get('source', 'itinerary'),
    }
    feedbacks.append(feedback)
    save_json(FEEDBACK_COLLECTION, feedbacks)

    log_activity('feedback_submitted', {
        'destination': destination,
        'rating': rating_value,
        'source': feedback['source'],
    })

    return jsonify({'message': 'Feedback submitted successfully', 'feedback': feedback}), 201

# ==================== ADMIN ROUTES ====================

@app.route('/api/admin/destinations', methods=['GET'])
@jwt_required()
def admin_get_destinations():
    """Admin: Get all destinations"""
    user, users, error_response = require_admin()
    if error_response:
        return error_response
    
    destinations = load_json(DESTINATIONS_COLLECTION)
    return jsonify(destinations)

@app.route('/api/admin/destinations', methods=['POST'])
@jwt_required()
def admin_add_destination():
    """Admin: Add new destination"""
    user, users, error_response = require_admin()
    if error_response:
        return error_response
    
    data = request.json
    destinations = load_json(DESTINATIONS_COLLECTION)
    next_id = max([d.get('id', 0) for d in destinations], default=0) + 1
    
    new_destination = {
        'id': next_id,
        'name': data.get('name'),
        'type': data.get('type'),
        'region': data.get('region'),
        'cost': data.get('cost'),
        'weather': data.get('weather'),
        'best_season': data.get('best_season'),
        'activities': data.get('activities', []),
        'safety_rating': data.get('safety_rating'),
        'user_rating': data.get('user_rating'),
        'image': data.get('image'),
        'description': data.get('description', '')
    }
    
    destinations.append(new_destination)
    save_json(DESTINATIONS_COLLECTION, destinations)
    
    return jsonify({'message': 'Destination added successfully', 'destination': new_destination}), 201

@app.route('/api/admin/destinations/<int:dest_id>', methods=['PUT'])
@jwt_required()
def admin_update_destination(dest_id):
    """Admin: Update destination"""
    user, users, error_response = require_admin()
    if error_response:
        return error_response
    
    data = request.json
    destinations = load_json(DESTINATIONS_COLLECTION)
    destination = get_destination_by_id(destinations, dest_id)

    if not destination:
        return jsonify({'error': 'Destination not found'}), 404
    
    # Update destination fields
    for key in ['name', 'type', 'region', 'cost', 'weather', 'best_season', 'activities', 'safety_rating', 'user_rating', 'image']:
        if key in data:
            destination[key] = data[key]

    if 'description' in data:
        destination['description'] = data['description']
    
    save_json(DESTINATIONS_COLLECTION, destinations)
    
    return jsonify({'message': 'Destination updated', 'destination': destination})

@app.route('/api/admin/destinations/<int:dest_id>', methods=['DELETE'])
@jwt_required()
def admin_delete_destination(dest_id):
    """Admin: Delete destination"""
    user, users, error_response = require_admin()
    if error_response:
        return error_response
    
    destinations = load_json(DESTINATIONS_COLLECTION)
    destination = get_destination_by_id(destinations, dest_id)

    if not destination:
        return jsonify({'error': 'Destination not found'}), 404
    
    deleted = destination
    destinations = [d for d in destinations if d.get('id') != deleted.get('id')]
    save_json(DESTINATIONS_COLLECTION, destinations)
    
    return jsonify({'message': 'Destination deleted', 'destination': deleted})

@app.route('/api/admin/stats', methods=['GET'])
@jwt_required()
def admin_get_stats():
    """Admin: Get user statistics and activity"""
    user, users, error_response = require_admin()
    if error_response:
        return error_response
    
    destinations = load_json(DESTINATIONS_COLLECTION)
    analytics = load_json(ANALYTICS_COLLECTION)
    feedback = get_feedback_items()
    
    stats = {
        'total_users': len(users),
        'total_destinations': len(destinations),
        'destinations_by_type': {},
        'destinations_by_region': {},
        'average_user_rating': sum(d['user_rating'] for d in destinations) / len(destinations) if destinations else 0,
        'total_searches': len([item for item in analytics if item.get('event_type') == 'search']),
        'total_bookmarks': len([item for item in analytics if item.get('event_type') == 'save_trip']),
        'total_itineraries': len([item for item in analytics if item.get('event_type') == 'itinerary_generated']),
        'total_feedback': len(feedback),
        'pending_feedback': len([item for item in feedback if item.get('status', 'new') == 'new']),
    }
    
    for dest in destinations:
        stats['destinations_by_type'][dest['type']] = stats['destinations_by_type'].get(dest['type'], 0) + 1
        stats['destinations_by_region'][dest['region']] = stats['destinations_by_region'].get(dest['region'], 0) + 1
    
    return jsonify(stats)


@app.route('/api/admin/activity', methods=['GET'])
@jwt_required()
def admin_get_activity():
    """Admin: Get live user activity summaries from stored analytics."""
    user, users, error_response = require_admin()
    if error_response:
        return error_response

    return jsonify(build_activity_summary())


@app.route('/api/admin/feedback', methods=['GET'])
@jwt_required()
def admin_get_feedback():
    """Admin: Get all submitted feedback entries."""
    user, users, error_response = require_admin()
    if error_response:
        return error_response

    feedback = sorted(get_feedback_items(), key=lambda item: item.get('date', ''), reverse=True)
    return jsonify(feedback)


@app.route('/api/admin/feedback/<int:feedback_id>', methods=['PATCH'])
@jwt_required()
def admin_update_feedback(feedback_id):
    """Admin: Update feedback status."""
    user, users, error_response = require_admin()
    if error_response:
        return error_response

    data = request.json or {}
    new_status = data.get('status')
    if new_status not in {'new', 'reviewed', 'resolved'}:
        return jsonify({'error': 'Invalid feedback status'}), 400

    feedback = get_feedback_items()
    feedback_item = next((item for item in feedback if item.get('id') == feedback_id), None)
    if not feedback_item:
        return jsonify({'error': 'Feedback not found'}), 404

    feedback_item['status'] = new_status
    save_json(FEEDBACK_COLLECTION, feedback)

    return jsonify({'message': 'Feedback updated successfully', 'feedback': feedback_item})


@app.route('/api/admin/models', methods=['GET'])
@jwt_required()
def admin_get_models():
    """Admin: Get AI model inventory and status metrics."""
    user, users, error_response = require_admin()
    if error_response:
        return error_response

    return jsonify({'models': get_model_items()})


@app.route('/api/admin/models/<int:model_id>', methods=['PATCH'])
@jwt_required()
def admin_update_model(model_id):
    """Admin: Update a model's status or retrain metadata."""
    user, users, error_response = require_admin()
    if error_response:
        return error_response

    data = request.json or {}
    models = get_model_items()
    model_index = next((i for i, model in enumerate(models) if int(model.get('id', -1)) == model_id), None)

    if model_index is None:
        return jsonify({'error': 'Model not found'}), 404

    model = models[model_index]

    if 'status' in data:
        model['status'] = data['status']

    if data.get('action') == 'retrain':
        model['last_trained'] = datetime.utcnow().strftime('%Y-%m-%d')
        model['accuracy'] = min(99, int(model.get('accuracy', 0)) + 1)
        if data.get('version'):
            model['version'] = data['version']

    model['updated_at'] = utc_now_iso()
    models[model_index] = model
    save_model_items(models)

    log_activity('model_admin_update', {
        'user_email': current_user_email,
        'model_id': model_id,
        'action': data.get('action', 'status_update'),
        'status': model.get('status'),
    })

    return jsonify({'message': 'Model updated successfully', 'model': model})

@app.route('/api/admin/cost-rates', methods=['GET'])
@jwt_required()
def admin_get_cost_rates():
    """Admin: Get cost rates"""
    current_user_email = get_jwt_identity()
    users = load_json(USERS_COLLECTION)
    user = get_user_by_email(users, current_user_email)
    
    if not user or user.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    cost_rates = load_json(COST_RATES_COLLECTION)
    return jsonify(cost_rates)

@app.route('/api/admin/cost-rates', methods=['PUT'])
@jwt_required()
def admin_update_cost_rates():
    """Admin: Update cost rates"""
    current_user_email = get_jwt_identity()
    users = load_json(USERS_COLLECTION)
    user = get_user_by_email(users, current_user_email)
    
    if not user or user.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.json
    save_json(COST_RATES_COLLECTION, data)
    
    return jsonify({'message': 'Cost rates updated successfully'})

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Ensure data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Initialize empty files if they don't exist
    if not os.path.exists(USERS_FILE):
        # Create admin user
        admin_user = {
            'id': 1,
            'email': 'admin@travelplanner.com',
            'name': 'Admin',
            'password': generate_password_hash('admin123'),
            'preferences': {},
            'saved_trips': [],
            'history': [],
            'role': 'admin'
        }
        save_json(USERS_COLLECTION, [admin_user])
    
    app.run(debug=True, port=5000)
