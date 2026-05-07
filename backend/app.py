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
from datetime import timedelta
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

# Initialize MongoDB persistence
MONGO_DB = build_mongodb_persistence()

# Data collection names in MongoDB
DESTINATIONS_COLLECTION = "destinations"
USERS_COLLECTION = "users"
COST_RATES_COLLECTION = "cost_rates"

# Data file paths (kept for backward compatibility / seeding)
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
DESTINATIONS_FILE = os.path.join(DATA_DIR, 'destinations.json')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
COST_RATES_FILE = os.path.join(DATA_DIR, 'cost_rates.json')

# Seed MongoDB from JSON files if collections are empty
def seed_mongodb():
    """Load initial data from JSON files into MongoDB if collections are empty."""
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
    data = MONGO_DB.load_json(collection_name, collection_name)
    if data is not None:
        return data
    
    # Fallback to file if collection is empty
    filepath_map = {
        DESTINATIONS_COLLECTION: DESTINATIONS_FILE,
        USERS_COLLECTION: USERS_FILE,
        COST_RATES_COLLECTION: COST_RATES_FILE,
    }
    filepath = filepath_map.get(collection_name)
    if filepath and os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            pass
    
    return [] if collection_name in [USERS_COLLECTION, DESTINATIONS_COLLECTION] else {}

def save_json(collection_name, data):
    """Save data to MongoDB collection.
    
    Args:
        collection_name: Name of MongoDB collection to save to
        data: Data to save
    """
    success = MONGO_DB.save_json(collection_name, collection_name, data)
    if not success:
        print(f"Warning: Failed to save to MongoDB collection {collection_name}")
    
    # Also save to file for backup
    filepath_map = {
        DESTINATIONS_COLLECTION: DESTINATIONS_FILE,
        USERS_COLLECTION: USERS_FILE,
        COST_RATES_COLLECTION: COST_RATES_FILE,
    }
    filepath = filepath_map.get(collection_name)
    if filepath:
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Failed to save backup file {filepath}: {e}")


def get_user_by_email(users, email):
    return next((u for u in users if u['email'] == email), None)


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
        return jsonify(destination)
    return jsonify({'error': 'Destination not found'}), 404

@app.route('/api/recommendations', methods=['GET', 'POST'])
def get_recommendations():
    """
    Get personalized destination recommendations
    Uses ML-based content filtering and collaborative filtering
    """
    destinations = load_json(DESTINATIONS_COLLECTION)
    
    if request.method == 'POST':
        data = request.json
        user_preferences = data.get('preferences', {})
        user_history = data.get('history', [])
        
        # Get ML-based recommendations
        recommendations = recommendation_engine.get_recommendations(
            destinations=destinations,
            preferences=user_preferences,
            history=user_history
        )
    else:
        # For guest users - recommend popular destinations
        recommendations = recommendation_engine.get_popular_destinations(destinations)
    
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
        'source': 'traveladvisor' if places else 'fallback',
        'places': places
    })


@app.route('/api/itinerary/generate', methods=['POST'])
def generate_itinerary_route():
    """Generate a day-by-day trip plan using NLP, recommendation logic, and live weather."""
    data = request.json or {}
    query = data.get('query', '')
    destination_name = data.get('destination')
    days = int(data.get('days') or 3)
    budget = data.get('budget')
    preferences = data.get('preferences') or {}

    destinations = load_json(DESTINATIONS_COLLECTION)
    cost_rates = load_json(COST_RATES_COLLECTION)

    parsed = query_parser.parse(query) if query else {}
    if not destination_name and parsed.get('destination'):
        destination_name = parsed['destination']

    candidates = destinations
    if parsed.get('budget'):
        candidates = [d for d in candidates if d.get('cost', 0) <= parsed['budget']]
    if parsed.get('region'):
        candidates = [d for d in candidates if parsed['region'].lower() in d.get('region', '').lower()]
    if parsed.get('type'):
        candidates = [d for d in candidates if d.get('type', '').lower() == parsed['type'].lower()]

    destination = None
    if destination_name:
        destination = next((d for d in destinations if d['name'].lower() == destination_name.lower()), None)
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
    user_index = next((i for i, u in enumerate(users) if u['email'] == current_user_email), None)
    
    if user_index is None:
        return jsonify({'error': 'User not found'}), 404
    
    trip = {
        'id': len(users[user_index]['saved_trips']) + 1,
        'destination': data.get('destination'),
        'days': data.get('days'),
        'budget_estimate': data.get('budget_estimate'),
        'saved_at': data.get('saved_at')
    }
    
    users[user_index]['saved_trips'].append(trip)
    users[user_index].setdefault('history', []).append({
        'id': len(users[user_index]['history']) + 1,
        'destination': data.get('destination'),
        'days': data.get('days'),
        'budget_estimate': data.get('budget_estimate'),
        'saved_at': data.get('saved_at'),
        'action': 'saved'
    })
    save_json(USERS_COLLECTION, users)
    
    return jsonify({
        'message': 'Trip saved successfully',
        'trip': trip,
        'user': serialize_user(users[user_index])
    })

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

# ==================== ADMIN ROUTES ====================

@app.route('/api/admin/destinations', methods=['GET'])
@jwt_required()
def admin_get_destinations():
    """Admin: Get all destinations"""
    current_user_email = get_jwt_identity()
    users = load_json(USERS_COLLECTION)
    user = get_user_by_email(users, current_user_email)
    
    if not user or user.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    destinations = load_json(DESTINATIONS_COLLECTION)
    return jsonify(destinations)

@app.route('/api/admin/destinations', methods=['POST'])
@jwt_required()
def admin_add_destination():
    """Admin: Add new destination"""
    current_user_email = get_jwt_identity()
    users = load_json(USERS_COLLECTION)
    user = get_user_by_email(users, current_user_email)
    
    if not user or user.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
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
    current_user_email = get_jwt_identity()
    users = load_json(USERS_COLLECTION)
    user = get_user_by_email(users, current_user_email)
    
    if not user or user.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
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
    current_user_email = get_jwt_identity()
    users = load_json(USERS_COLLECTION)
    user = get_user_by_email(users, current_user_email)
    
    if not user or user.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
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
    current_user_email = get_jwt_identity()
    users = load_json(USERS_COLLECTION)
    user = get_user_by_email(users, current_user_email)
    
    if not user or user.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    destinations = load_json(DESTINATIONS_COLLECTION)
    
    stats = {
        'total_users': len(users),
        'total_destinations': len(destinations),
        'destinations_by_type': {},
        'destinations_by_region': {},
        'average_user_rating': sum(d['user_rating'] for d in destinations) / len(destinations) if destinations else 0
    }
    
    for dest in destinations:
        stats['destinations_by_type'][dest['type']] = stats['destinations_by_type'].get(dest['type'], 0) + 1
        stats['destinations_by_region'][dest['region']] = stats['destinations_by_region'].get(dest['region'], 0) + 1
    
    return jsonify(stats)

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
