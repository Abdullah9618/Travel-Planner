# Travel Planner Pakistan

An AI-assisted travel planning web app for discovering destinations in Pakistan, generating itineraries, estimating budgets, and saving shareable trip plans.

## What this project does

This app helps users:

- search destinations using natural language
- get personalized recommendations
- generate day-by-day itineraries
- estimate trip budgets
- view live weather highlights and travel advisories
- save, edit, delete, and share travel plans
- manage destinations and analytics from an admin dashboard

## Core features

### Home page

- natural-language search bar for queries like `Plan a 3-day trip to northern Pakistan under 25,000 PKR`
- AI-powered featured and trending destination cards
- live weather highlights and travel advisories
- dynamic travel suggestion chips
- personalized greeting for logged-in users
- quick access to the itinerary planner and saved trips

### Authentication and profiles

- email/password registration and login
- Google sign-in support
- profile management for:
  - budget range
  - travel style
  - preferred duration
  - weather preference
  - preferred activities
- saved trips and travel history

### Recommendation engine

- spaCy-based NLP parsing for travel queries
- sklearn TF-IDF and cosine similarity when available
- pure-Python fallback for resilient local development
- content-based ranking
- travel-history-aware similarity scoring
- cold-start popularity fallback for new users

### Itinerary planner

- generates day-by-day trip plans
- includes live weather context
- includes budget breakdowns
- includes recommended attractions and restaurants when available
- provides route summary and Google Maps link
- lets users edit daily plans before saving

### Budget and cost planning

- hotel, travel, meals, and activities cost breakdown
- budget-aware recommendation filtering
- over-budget alternative suggestions

### Weather and events

- live OpenWeather lookup when API key and coordinates are available
- curated fallback weather data for development/offline use
- weather advisories based on conditions
- fallback local event suggestions when live event API is unavailable

### Maps and navigation

- interactive Leaflet map in the itinerary planner
- Google Maps search and embed links
- destination route summary with estimated travel distance/time

### Destination and shared trip pages

- destination detail page with similar destinations
- live weather on destination detail pages
- save trip from a destination page
- public shareable trip pages

### Admin dashboard

- manage destination records
- manage cost rates
- inspect activity analytics
- review and moderate feedback
- view and retrain/toggle AI models

## Technology stack

### Frontend

- React 18
- React Router
- React Icons
- React Toastify
- Axios
- React Leaflet
- plain CSS

### Backend

- Flask
- Flask-CORS
- Flask-JWT-Extended
- Google OAuth token verification
- MongoDB persistence layer with JSON fallback
- Python-based itinerary and weather integration helpers

### AI and NLP

- spaCy for query parsing and entity extraction
- pure-Python TF-IDF destination recommender
- cosine similarity scoring
- travel-history-aware matching

### Data storage

- JSON seed/backup files in `backend/data/`
- MongoDB-backed persistence when available

## Project structure

```text
FYP/
├── backend/
│   ├── app.py
│   ├── integration_services.py
│   ├── mongodb_persistence.py
│   ├── nlp_parser.py
│   ├── recommendation_engine.py
│   ├── persistence.py
│   ├── requirements.txt
│   └── data/
│       ├── analytics.json
│       ├── cost_rates.json
│       ├── destinations.json
│       ├── models.json
│       └── users.json
└── frontend/
    ├── package.json
    └── src/
        ├── App.js
        ├── index.js
        ├── components/
        ├── context/
        ├── pages/
        ├── services/
        └── styles/
```

## Key pages

- `/` — Home page
- `/login` — Login page
- `/register` — Registration page
- `/search` — Search results page
- `/planner` — AI itinerary planner
- `/destination/:id` — Destination detail page
- `/profile` — User profile and saved trips
- `/shared-trip/:token` — Public shared itinerary view
- `/admin/*` — Admin dashboard

## API overview

### Public endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/search` | Parse a natural-language travel query |
| GET | `/api/destinations` | List destinations |
| GET | `/api/destinations/:id` | Get one destination |
| GET/POST | `/api/recommendations` | Get recommended destinations |
| GET | `/api/travel-suggestions` | Homepage suggestion cards |
| GET | `/api/home/insights` | Featured/trending/weather/advisories |
| GET | `/api/weather/highlights` | Live weather snapshots |
| GET | `/api/explore/places` | Attraction/restaurant suggestions |
| POST | `/api/itinerary/generate` | Generate a full itinerary |
| POST | `/api/budget/estimate` | Estimate budget |
| POST | `/api/feedback` | Submit feedback |
| GET | `/api/shared-trip/:token` | Load a shared trip |

### Authentication endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register` | Create an account |
| POST | `/api/auth/login` | Sign in |
| POST | `/api/auth/google` | Google sign-in |
| GET | `/api/auth/profile` | Load profile |
| PUT | `/api/auth/profile` | Update profile |
| POST | `/api/auth/save-trip` | Save itinerary to profile |
| GET | `/api/auth/history` | View travel history |

### Saved-trip endpoints

| Method | Endpoint | Description |
|---|---|---|
| PUT | `/api/auth/saved-trips/:id` | Update a saved trip |
| DELETE | `/api/auth/saved-trips/:id` | Delete a saved trip |
| POST | `/api/auth/saved-trips/:id/share` | Generate share link |

### Admin endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/admin/destinations` | List all destinations |
| POST | `/api/admin/destinations` | Add destination |
| PUT | `/api/admin/destinations/:id` | Update destination |
| DELETE | `/api/admin/destinations/:id` | Delete destination |
| GET | `/api/admin/stats` | Dashboard stats |
| GET | `/api/admin/activity` | Activity summary |
| GET | `/api/admin/feedback` | Feedback list |
| PATCH | `/api/admin/feedback/:id` | Update feedback status |
| GET | `/api/admin/models` | View model list |
| PATCH | `/api/admin/models/:id` | Retrain/toggle model |
| GET | `/api/admin/cost-rates` | View cost rates |
| PUT | `/api/admin/cost-rates` | Update cost rates |

## Environment variables

### Backend `backend/.env`

- `JWT_SECRET_KEY`
- `DATABASE_URL` (optional)
- `OPENWEATHER_API_KEY` (optional, for live weather)
- `MAPTILER_API_KEY` (optional, for map tiles)
- `TRAVELADVISOR_API_KEY` (optional, for places search; RapidAPI key if available)
- `GOOGLE_CLIENT_ID` (optional, for Google sign-in)

TripAdvisor place suggestions use this order:

1. TripAdvisor Content API when the configured provider responds
2. TripAdvisor public page parsing when available
3. OpenStreetMap live lookup via Nominatim/Overpass
4. curated fallback places as a last resort

### Frontend `frontend/.env`

- `REACT_APP_API_URL`
- `REACT_APP_GOOGLE_CLIENT_ID`
- `REACT_APP_MAPTILER_API_KEY`

## Getting started

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

The backend runs on `http://localhost:5000`.

### Frontend

```bash
cd frontend
npm install
npm start
```

The frontend runs on `http://localhost:3000`.

### Smoke tests

Run the provided validation scripts from the project root:

```bash
python test_tripadvisor.py
python test_recommendation_engine.py
```

### AI/ML note

The destination recommender uses sklearn TF-IDF and cosine similarity when available, with a pure-Python fallback to keep development resilient.

## Docker

Run the full stack from the project root:

```bash
docker compose up --build
```

## Demo credentials

### Admin

- email: `admin@travelplanner.com`
- password: `admin123`

## Notes for the report

- The NLP layer is spaCy-based, not regex-only.
- The recommender uses a fitted TF-IDF model with cosine similarity.
- Live APIs are used when configured, but the app still works with fallback data.
- MongoDB is supported, with JSON files used as seed/backup storage.

## Future improvements

- deeper real-time API coverage
- stronger event discovery integration
- more advanced model training with user interaction data
- multi-language support
- mobile app version

## License

Educational project for a final year project.

---

Made with ❤️ for exploring the beauty of Pakistan
