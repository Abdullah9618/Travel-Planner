# Architecture Comparison

## Old Architecture (SQLAlchemy)

```
Flask API
    ↓
app.py (helpers: load_json, save_json)
    ↓
persistence.py (SQLAlchemy Abstraction Layer)
    ↓
SQL Layer (SQLAlchemy ORM)
    ↓
Database Drivers (PyMySQL/SQLite)
    ↓
Database (MySQL/SQLite)
    
Alternative Fallback:
    ↓
JSON Files (destinations.json, users.json, cost_rates.json)
```

**Problems:**
- ❌ Abstraction layer overhead
- ❌ ORM complexity for simple JSON data
- ❌ Multiple driver dependencies
- ❌ Mixed storage (DB + Files)

---

## New Architecture (MongoDB Direct)

```
Flask API
    ↓
app.py (helpers: load_json, save_json)
    ↓
mongodb_persistence.py (Direct MongoDB Handler)
    ↓
pymongo (Native MongoDB Driver)
    ↓
MongoDB Database
    
Alternative Fallback:
    ↓
JSON Files (destinations.json, users.json, cost_rates.json)
```

**Benefits:**
- ✅ Direct connection (no abstraction layer)
- ✅ Native JSON handling
- ✅ Simpler dependencies
- ✅ Better performance
- ✅ Cloud-ready (MongoDB Atlas)
- ✅ Type flexibility with MongoDB

---

## Data Flow

### Reading Data

**Old Way:**
```
load_json(filepath)
  → Check DB via SQLAlchemy
    → Parse SQL result
    → Convert to Python object
  → Fallback to file
```

**New Way:**
```
load_json(collection_name)
  → Query MongoDB collection
    → Get document payload
    → Return JSON
  → Fallback to file
```

### Writing Data

**Old Way:**
```
save_json(filepath, data)
  → Convert to SQL via SQLAlchemy
  → Write to database
  → Write to file as backup
```

**New Way:**
```
save_json(collection_name, data)
  → Write directly to MongoDB collection
  → Write to file as backup
```

---

## Collection Structure

```json
{
  "_id": "destinations",
  "payload": [
    {
      "id": 1,
      "name": "Swat",
      "region": "Khyber Pakhtunkhwa",
      "cost": 15000,
      "type": "Adventure",
      ...
    },
    ...
  ]
}
```

Three collections:
- `destinations` - Travel destinations
- `users` - User accounts and preferences
- `cost_rates` - Travel cost rates

---

## Deployment Options

### Option 1: Local MongoDB
```
Your Computer
  ↓
MongoDB (localhost:27017)
  ↓
Flask App connects locally
```

### Option 2: Docker (Recommended for Dev)
```
Docker Container (mongo:latest)
  ↓
localhost:27017 or mongo:27017
  ↓
Flask App in container or host
```

### Option 3: MongoDB Atlas (Cloud - Recommended for Production)
```
MongoDB Atlas Cloud
  ↓
mongodb+srv://user:pass@cluster.mongodb.net
  ↓
Flask App connects over internet
```

---

## File Organization

```
backend/
├── app.py                      ← Updated with MongoDB
├── mongodb_persistence.py      ← NEW: Direct MongoDB handler
├── test_mongodb.py             ← NEW: Connection test
├── requirements.txt            ← Updated (pymongo added)
├── .env                        ← Updated (MONGO_URI added)
├── persistence.py              ← OLD: No longer used
├── data/
│   ├── destinations.json       ← Seeded into MongoDB
│   ├── users.json              ← Seeded into MongoDB
│   └── cost_rates.json         ← Seeded into MongoDB
└── ... (other files unchanged)
```

---

## Performance Comparison

| Metric | SQLAlchemy | MongoDB Direct |
|--------|-----------|-----------------|
| Query Speed | Slower (ORM overhead) | Faster (direct) |
| Connection Setup | Complex | Simple |
| Data Conversion | ORM → Python → JSON | Direct JSON |
| Cloud Ready | Limited | Native (Atlas) |
| JSON Handling | Not optimized | Native support |
| Learning Curve | Steep | Gentle |

---

## API Compatibility

All existing API endpoints work **exactly the same**:

✅ `/api/search` - Search destinations  
✅ `/api/destinations` - Get all destinations  
✅ `/api/auth/login` - User login  
✅ `/api/auth/register` - User registration  
✅ `/api/itinerary/generate` - Generate travel plans  
... and all other endpoints

**No frontend changes needed!**

---

## Migration Summary

**What changed:**
- Database driver: SQLAlchemy → pymongo
- Storage: SQL → MongoDB
- Connection type: Abstraction → Direct

**What stayed the same:**
- API endpoints and responses
- Data structure and format
- Frontend code
- Business logic

**Result:**
- Simpler codebase
- Better performance
- Cloud-ready
- More scalable
