# Travel Planner Pakistan - AI-Powered Trip Planning

A comprehensive web application for planning trips in Pakistan with AI-powered destination recommendations, budget estimation, and personalized travel suggestions.

## 🌟 Features

### Home Page
- **Intelligent Search Bar**: Natural language queries like "Plan a 3-day trip to northern Pakistan under 25,000 PKR"
- **NLP Query Parsing**: Automatically extracts destination, days, budget, and travel type
- **Recommended Destinations**: Dynamic cards with personalized recommendations
- **Guest User Access**: Browse and use the app without registration
- **Real-time Travel Suggestions**: 
  - "Top Adventure Spots under 20,000 PKR"
  - "Best Weekend Destinations Near You"
  - "Highest Rated Destinations"

### User Registration & Profile Management
- Email-based registration and login
- Profile page with travel preferences:
  - Budget range (min/max)
  - Travel style (Adventure, Relaxation, Family, Cultural, etc.)
  - Preferred trip duration
  - Weather preferences
  - Preferred activities

### Destination Recommendation System
- **Content-Based Filtering**: Matches destinations to user preferences
- **Collaborative Filtering**: Recommends based on similar users' behavior
- **Cold-Start Handling**: Popular destinations for new users
- 20+ destinations with rich data including:
  - Type, Region, Cost
  - Weather, Best Season
  - Activities, Safety Rating
  - User Ratings, Images

### Budget Estimation & Cost Optimization
- Detailed cost breakdown:
  - Hotel (per night)
  - Travel/Transport
  - Meals (per day)
  - Activities
- Region-based pricing
- Visual budget breakdown with charts
- Budget optimization tips

### Admin Dashboard
- **Statistics Overview**: Total destinations, users, ratings
- **Destination Management**: Add, edit, delete destinations
- **Cost Rates Management**: Update regional pricing
- **Visual Analytics**: Charts for destinations by type/region

## 🛠️ Technology Stack

### Frontend
- **React.js 18** - UI Framework
- **React Router 6** - Navigation
- **React Icons** - Icon library
- **React Toastify** - Notifications
- **Axios** - HTTP client
- **CSS3** - Custom styling (no frameworks)

### Backend
- **Python 3.10+** - Server language
- **Flask** - Web framework
- **Flask-CORS** - Cross-origin support
- **Flask-JWT-Extended** - JWT authentication
- **Werkzeug** - Password hashing

### AI/ML
- **NumPy** - Numerical computing
- **Custom NLP Parser** - Query understanding
- **Custom Recommendation Engine**:
  - Content-based filtering
  - Collaborative filtering
  - Similarity calculations

### Database
- **JSON Files** - Data storage (prototype)
  - destinations.json
  - users.json
  - cost_rates.json

## 📁 Project Structure

```
FYP/
├── backend/
│   ├── app.py                    # Main Flask application
│   ├── nlp_parser.py             # NLP query parser
│   ├── recommendation_engine.py  # ML recommendation system
│   ├── requirements.txt          # Python dependencies
│   └── data/
│       ├── destinations.json     # Destination data
│       ├── users.json            # User data
│       └── cost_rates.json       # Regional pricing
│
└── frontend/
    ├── package.json
    ├── public/
    │   └── index.html
    └── src/
        ├── index.js
        ├── App.js
        ├── context/
        │   └── AuthContext.js    # Authentication state
        ├── services/
        │   └── api.js            # API service
        ├── components/
        │   ├── Navbar.js
        │   ├── Footer.js
        │   ├── SearchBar.js
        │   ├── DestinationCard.js
        │   ├── BudgetTable.js
        │   └── ProtectedRoute.js
        ├── pages/
        │   ├── Home.js
        │   ├── Login.js
        │   ├── Register.js
        │   ├── Profile.js
        │   ├── SearchResults.js
        │   ├── Destination.js
        │   └── AdminDashboard.js
        └── styles/
            ├── index.css
            ├── App.css
            ├── Navbar.css
            ├── Footer.css
            ├── SearchBar.css
            ├── DestinationCard.css
            ├── BudgetTable.css
            ├── Home.css
            ├── Auth.css
            ├── Profile.css
            ├── SearchResults.css
            ├── Destination.css
            └── AdminDashboard.css
```

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Run the Flask server:
```bash
python app.py
```

The backend will run on `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The frontend will run on `http://localhost:3000`

## 🔐 Demo Credentials

### Admin Account
- **Email**: admin@travelplanner.com
- **Password**: admin123

### Guest Access
- Browse and search without login
- Register to save trips and preferences

## 📡 API Endpoints

### Public Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/search` | Search with natural language query |
| GET | `/api/destinations` | Get all destinations |
| GET | `/api/destinations/:id` | Get single destination |
| GET/POST | `/api/recommendations` | Get recommendations |
| GET | `/api/travel-suggestions` | Get travel suggestions |
| POST | `/api/budget/estimate` | Estimate trip budget |

### Auth Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login user |
| GET | `/api/auth/profile` | Get user profile |
| PUT | `/api/auth/profile` | Update profile |
| POST | `/api/auth/save-trip` | Save trip to profile |

### Admin Endpoints (Protected)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/destinations` | Get all destinations |
| POST | `/api/admin/destinations` | Add new destination |
| PUT | `/api/admin/destinations/:id` | Update destination |
| DELETE | `/api/admin/destinations/:id` | Delete destination |
| GET | `/api/admin/stats` | Get dashboard stats |
| GET | `/api/admin/cost-rates` | Get cost rates |
| PUT | `/api/admin/cost-rates` | Update cost rates |

## 🧠 ML Recommendation Algorithm

### Content-Based Filtering
- Calculates similarity between user preferences and destination features
- Features considered:
  - Budget matching (20% weight)
  - Travel style (25% weight)
  - Weather preference (10% weight)
  - Activities overlap (15% weight)
  - Ratings (15% weight)

### Collaborative Filtering
- Finds similar destinations based on user's travel history
- Uses destination similarity metrics:
  - Type similarity
  - Region matching
  - Weather similarity
  - Activity overlap
  - Cost similarity

### Cold-Start Handling
- New users receive popular destinations
- Scoring based on user ratings and safety ratings

## 🎨 Sample Destinations

The app includes 20 pre-configured destinations:

| Destination | Type | Region | Cost (PKR) |
|-------------|------|--------|------------|
| Hunza Valley | Adventure | Gilgit Baltistan | 25,000 |
| Skardu | Adventure | Gilgit Baltistan | 35,000 |
| Murree | Family | Punjab | 15,000 |
| Swat Valley | Cultural | KPK | 20,000 |
| Gwadar Beach | Relaxation | Balochistan | 18,000 |
| Lahore | Cultural | Punjab | 12,000 |
| Fairy Meadows | Adventure | Gilgit Baltistan | 28,000 |
| Taxila | Historical | Punjab | 8,000 |
| And more... | | | |

## 🔮 Future Enhancements

- [ ] Real API integrations (Google Places, Weather API)
- [ ] MongoDB/PostgreSQL database
- [ ] Real-time chat support
- [ ] Trip itinerary generation
- [ ] Social sharing features
- [ ] Review and rating system
- [ ] Mobile app (React Native)
- [ ] Multi-language support
- [ ] Payment integration

## 📝 License

This project is created for educational purposes as part of a Final Year Project (FYP).

## 👥 Contributors

- Student: [Your Name]
- Supervisor: [Supervisor Name]

---

Made with ❤️ for exploring the beauty of Pakistan
