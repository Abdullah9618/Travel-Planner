# MongoDB Setup Guide

Your Travel Planner backend has been migrated from SQLAlchemy (SQL-based) to **MongoDB** with a real connection (no abstraction layer).

## What Changed

- ✅ Removed SQLAlchemy dependency
- ✅ Added pymongo for direct MongoDB connection
- ✅ Replaced `persistence.py` (SQL abstraction) with `mongodb_persistence.py` (real connection)
- ✅ Updated `app.py` to use MongoDB collections instead of JSON file fallback

## Setup Instructions

### Option 1: MongoDB Atlas (Cloud - Recommended)

1. **Create a MongoDB Atlas account:**
   - Go to https://www.mongodb.com/cloud/atlas
   - Sign up for a free account
   - Create a new project

2. **Create a cluster:**
   - Select "Build a Cluster"
   - Choose the free tier (M0)
   - Select your region
   - Create the cluster

3. **Get your connection string:**
   - Go to "Connect" → "Drivers"
   - Copy the connection string (looks like: `mongodb+srv://username:password@cluster.mongodb.net/travelplanner`)

4. **Update `.env` file:**
   ```
   MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/travelplanner
   ```

### Option 2: Local MongoDB with Docker

If you want to run MongoDB locally using Docker:

```bash
docker-compose up -d mongo
```

This will start MongoDB on `mongodb://localhost:27017`

Your `.env` should have:
```
MONGO_URI=mongodb://localhost:27017
```

### Option 3: Local MongoDB Installation

1. **Install MongoDB locally** from https://www.mongodb.com/try/download/community
2. **Start MongoDB service:**
   - On Windows: MongoDB should start automatically
   - Verify it's running at `mongodb://localhost:27017`

3. **Update `.env`:**
   ```
   MONGO_URI=mongodb://localhost:27017
   ```

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the backend:**
   ```bash
   python app.py
   ```

On startup, you should see:
```
✓ Connected to MongoDB: travelplanner
✓ Seeded destinations from data/destinations.json
✓ Seeded users from data/users.json
✓ Seeded cost_rates from data/cost_rates.json
```

## Database Structure

### Collections

The MongoDB database uses these collections:

| Collection | Purpose | Data |
|-----------|---------|------|
| `destinations` | Travel destinations | destinations.json |
| `users` | User accounts | users.json |
| `cost_rates` | Travel cost rates | cost_rates.json |

Each collection stores documents with the following structure:
```json
{
  "_id": "collection_name",
  "payload": { /* actual data */ }
}
```

## How It Works

### Direct Connection (No Layer)

Instead of an abstraction layer like SQLAlchemy:

```python
# OLD WAY (SQL with abstraction):
# db_load_json(persistence, filepath)
# db_save_json(persistence, filepath, data)

# NEW WAY (Direct MongoDB):
load_json(DESTINATIONS_COLLECTION)      # Loads from MongoDB
save_json(DESTINATIONS_COLLECTION, data) # Saves to MongoDB
```

The new `mongodb_persistence.py` provides:
- Direct `MongoClient` connection
- Simple `load_json()` and `save_json()` methods
- Automatic fallback to JSON files if MongoDB is empty

### Data Flow

1. **On startup:** JSON files are automatically seeded into MongoDB collections (if empty)
2. **During operation:** All reads/writes go to MongoDB
3. **Backup:** Data is also saved to JSON files for backup

## Testing Connection

To verify your MongoDB setup is working:

```python
from mongodb_persistence import build_mongodb_persistence

db = build_mongodb_persistence()
print("Connected successfully!")
```

## Migration Status

- ✅ Database layer replaced with MongoDB
- ✅ All imports updated
- ✅ Collection names configured
- ✅ Data seeding implemented
- ✅ API endpoints updated
- ✅ Requirements.txt updated

## Troubleshooting

### Connection Failed

```
✗ Failed to connect to MongoDB: [Connection error]
```

**Solutions:**
1. Verify your `MONGO_URI` in `.env` is correct
2. Check MongoDB is running
3. Verify network access (if using Atlas, check IP whitelist)
4. Check username/password if using authentication

### Empty Collections

If collections appear empty:
1. Delete `travelbuddy.db` if it exists (old SQLite database)
2. Restart the app - JSON files will be seeded

### Import Errors

```
ModuleNotFoundError: No module named 'pymongo'
```

Run:
```bash
pip install pymongo==4.6.1
```

## Performance Notes

- Direct MongoDB queries are faster than SQLAlchemy ORM
- No N+1 query problems
- Suitable for JSON-like data structures
- Consider adding indexes for frequently queried fields in production

## Next Steps

1. Update your MongoDB connection string in `.env`
2. Run `pip install -r requirements.txt`
3. Start the backend: `python app.py`
4. Test an API endpoint to verify it's working
