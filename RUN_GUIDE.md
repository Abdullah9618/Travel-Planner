# How to Run Travel Planner

## Quick Start

### Option 1: Direct Run (Simplest)

```bash
cd c:\Users\AB\Desktop\FYP\backend
python app.py
```

Expected output:
```
[OK] Connected to MongoDB: travelplanner
[OK] Seeded destinations from ...\destinations.json
[OK] Seeded users from ...\users.json
[OK] Seeded cost_rates from ...\cost_rates.json
 * Running on http://127.0.0.1:5000
```

### Option 2: Using Run Script

```bash
python c:\Users\AB\Desktop\FYP\run_server.py
```

## Testing the Backend

Once the server is running, test it:

```bash
# In another terminal, test an API endpoint:
curl http://127.0.0.1:5000/api/destinations
```

## Prerequisites

### 1. MongoDB Must Be Running

The app needs MongoDB. Choose one:

**Option A: Local MongoDB**
- Ensure MongoDB is installed and running
- Server connects to: `mongodb://localhost:27017`

**Option B: MongoDB Atlas (Cloud)**
- Update `backend/.env` with your connection string:
  ```
  MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/travelplanner
  ```

**Option C: Docker**
- Run: `docker-compose up -d mongo`
- This starts MongoDB in a Docker container

### 2. Python Dependencies

Dependencies are installed automatically on first run, but you can pre-install them:

```bash
pip install -r backend/requirements.txt
```

## Available Endpoints

Once running, test these endpoints:

- `GET /api/destinations` - List all destinations
- `GET /api/destinations/<id>` - Get single destination
- `POST /api/search` - Search destinations
- `POST /api/auth/register` - Register user
- `POST /api/auth/login` - Login user
- `GET /api/recommendations` - Get recommendations

Example:
```bash
# Get all destinations
curl http://127.0.0.1:5000/api/destinations | python -m json.tool

# Get recommendations
curl http://127.0.0.1:5000/api/recommendations | python -m json.tool
```

## Troubleshooting

### MongoDB Connection Error
```
[ERROR] Failed to connect to MongoDB
```
**Solution:** 
- Start MongoDB service or Docker: `docker-compose up -d mongo`
- Verify `MONGO_URI` in `backend/.env`

### Port Already in Use
```
OSError: [Errno 10048] Address already in use
```
**Solution:**
- Change Flask port: `flask run --port 5001`
- Or kill existing process

### Import Errors
```
ModuleNotFoundError: No module named 'pymongo'
```
**Solution:**
```bash
pip install -r backend/requirements.txt
```

## Project Structure

```
Travel-Planner/
├── backend/
│   ├── app.py                  # Main Flask app
│   ├── mongodb_persistence.py  # MongoDB handler
│   ├── requirements.txt         # Dependencies
│   ├── .env                     # Configuration
│   ├── data/                    # Initial data JSON files
│   ├── *.py                     # Other modules
│   └── ...
├── frontend/                    # React frontend
├── run_server.py               # Run script
└── README.md                   # Documentation
```

## Next Steps

1. **Start the server**: `python backend/app.py`
2. **Test endpoints**: `curl http://127.0.0.1:5000/api/destinations`
3. **Run frontend**: Navigate to frontend directory and run development server
4. **Access web UI**: Open http://localhost:3000 (or configured frontend port)

## Notes

- Backend runs on port 5000 by default
- MongoDB data persists between restarts
- JSON files in `backend/data/` are automatically synced to MongoDB
- To reset data, delete documents in MongoDB or JSON files and restart

## Need Help?

- Check `MONGODB_SETUP.md` for MongoDB setup details
- Check `QUICK_START.md` for quick reference
- Check `ARCHITECTURE.md` for system architecture
