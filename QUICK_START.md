# Quick Start - MongoDB Setup

## ⚡ 30-Second Setup

### Step 1: Configure MongoDB
Edit `.env` in the `backend` folder:

**Option A - Local MongoDB:**
```
MONGO_URI=mongodb://localhost:27017
```

**Option B - MongoDB Atlas (Cloud):**
```
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/travelplanner
```

### Step 2: Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 3: Run Your App
```bash
python app.py
```

You should see:
```
✓ Connected to MongoDB: travelplanner
✓ Seeded destinations from data/destinations.json
✓ Seeded users from data/users.json
✓ Seeded cost_rates from data/cost_rates.json
```

## 🐳 Docker Setup (Optional)

If you want MongoDB in Docker:

```bash
# Make sure docker-compose.yml includes mongo service
docker-compose up -d mongo

# Then start your app
python app.py
```

## ✅ Verify It Works

```bash
# Test MongoDB connection
python test_mongodb.py
```

## 📝 What Changed?

- ❌ Removed: SQLAlchemy, SQLite database
- ✅ Added: Direct MongoDB connection
- ✅ Result: Real MongoDB connection (no abstraction layer)

## 🔗 MongoDB Connection Options

| Type | Connection String |
|------|-------------------|
| Local | `mongodb://localhost:27017` |
| Atlas Cloud | `mongodb+srv://user:pass@cluster.mongodb.net` |
| Docker | `mongodb://mongo:27017` |

## 📚 Full Documentation

See `MONGODB_SETUP.md` for complete setup guide with troubleshooting.
