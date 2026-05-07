# QUICK TEST GUIDE

Your server is running! Here's how to test it.

## Option 1: Using Browser (Easiest)

Just open these URLs in your browser:

### Get All Destinations
```
http://127.0.0.1:5000/api/destinations
```

Expected: List of travel destinations in JSON format

### Get Recommendations
```
http://127.0.0.1:5000/api/recommendations
```

Expected: List of recommended destinations

### Get Home Insights
```
http://127.0.0.1:5000/api/home/insights
```

Expected: Featured destinations, weather, and advisories

---

## Option 2: Using curl (Command Line)

### Test 1: Get All Destinations
```bash
curl http://127.0.0.1:5000/api/destinations
```

### Test 2: Get Single Destination
```bash
curl http://127.0.0.1:5000/api/destinations/0
```

### Test 3: Search Destinations
```bash
curl -X POST http://127.0.0.1:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query":"budget trip 3 days under 20000"}'
```

### Test 4: Register User
```bash
curl -X POST http://127.0.0.1:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email":"test@example.com",
    "name":"Test User",
    "password":"testpass123"
  }'
```

### Test 5: Login User
```bash
curl -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email":"test@example.com",
    "password":"testpass123"
  }'
```

### Test 6: Get Travel Suggestions
```bash
curl http://127.0.0.1:5000/api/travel-suggestions
```

### Test 7: Get Weather Highlights
```bash
curl http://127.0.0.1:5000/api/weather/highlights
```

### Test 8: Generate Itinerary
```bash
curl -X POST http://127.0.0.1:5000/api/itinerary/generate \
  -H "Content-Type: application/json" \
  -d '{
    "destination":"Swat",
    "days":3,
    "budget":25000
  }'
```

---

## Option 3: Using Postman

1. Download Postman from https://www.postman.com/downloads/
2. Create requests to:
   - `GET http://127.0.0.1:5000/api/destinations`
   - `POST http://127.0.0.1:5000/api/auth/register`
   - etc.

---

## Expected Responses

### GET /api/destinations
```json
[
  {
    "id": 1,
    "name": "Swat",
    "region": "Khyber Pakhtunkhwa",
    "cost": 15000,
    "type": "Adventure",
    "user_rating": 4.5,
    "description": "Beautiful valley in northern Pakistan",
    "highlights": ["Mountains", "Rivers", "Hiking"],
    "best_season": "May-September"
  }
]
```

### POST /api/auth/register
```json
{
  "message": "Registration successful",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "test@example.com",
    "name": "Test User",
    "preferences": {...},
    "saved_trips": [],
    "history": [],
    "role": "user"
  }
}
```

---

## Troubleshooting Tests

### Connection Refused
**Error**: `curl: (7) Failed to connect to 127.0.0.1 port 5000`
**Fix**: 
- Ensure backend server is running
- Check terminal where you started it
- Restart the server

### Invalid JSON
**Error**: `ERR! Invalid JSON response body`
**Fix**:
- Check your curl command syntax
- Ensure Content-Type header is correct
- Verify endpoint URL

### 404 Not Found
**Error**: `{"error": "The requested URL was not found on the server"}`
**Fix**:
- Check endpoint spelling
- Verify HTTP method (GET vs POST)
- Check URL path

### 500 Server Error
**Error**: `500 Internal Server Error`
**Fix**:
- Check backend server console for errors
- Verify data is seeded in MongoDB
- Restart the server

---

## MongoDB Data Check

Your MongoDB Atlas has:
- **destinations**: Travel locations
- **users**: User accounts
- **cost_rates**: Travel costs

All data is automatically seeded from JSON files when server starts.

---

## API Endpoints Summary

| Method | Endpoint | Purpose | Auth |
|--------|----------|---------|------|
| GET | /api/destinations | List destinations | No |
| GET | /api/destinations/<id> | Get single destination | No |
| POST | /api/search | Search destinations | No |
| GET | /api/recommendations | Get recommendations | No |
| GET | /api/travel-suggestions | Get suggestions | No |
| GET | /api/home/insights | Home page data | No |
| GET | /api/weather/highlights | Weather data | No |
| POST | /api/itinerary/generate | Generate itinerary | No |
| POST | /api/auth/register | Register user | No |
| POST | /api/auth/login | Login user | No |
| POST | /api/auth/google | Google login | No |
| GET | /api/auth/profile | User profile | Yes |

---

## Postman Collection

If you want to save these tests, create a Postman collection with:

**Base URL**: http://127.0.0.1:5000

**Requests**:
1. GET /api/destinations
2. POST /api/auth/register
3. POST /api/auth/login
4. POST /api/search
5. POST /api/itinerary/generate
6. GET /api/recommendations

---

## Quick Test Script

Save this as `test_api.sh` (or `.bat` on Windows):

```bash
#!/bin/bash

echo "Testing Travel Planner API..."
echo ""

echo "1. Destinations:"
curl http://127.0.0.1:5000/api/destinations | python -m json.tool
echo ""

echo "2. Recommendations:"
curl http://127.0.0.1:5000/api/recommendations | python -m json.tool
echo ""

echo "3. Travel Suggestions:"
curl http://127.0.0.1:5000/api/travel-suggestions | python -m json.tool
```

---

## What to Check

✅ Server starts without errors
✅ MongoDB connects successfully
✅ Data seeds from JSON files
✅ API endpoints respond with data
✅ User registration works
✅ API returns JSON formatted responses

---

## Next Steps

1. **Test all endpoints** using curl or Postman
2. **Check responses** match expected format
3. **Create test user** via registration
4. **Generate itinerary** for a destination
5. **Start frontend** when backend is stable

---

**Server is running and ready to test!**
