# FRONTEND STARTUP GUIDE

Your React frontend is ready to run!

## Prerequisites

✅ Node.js installed (required for npm)
✅ Backend running on http://localhost:5000
✅ npm dependencies already installed

---

## How to Start Frontend

### **METHOD 1: Batch File (Windows - EASIEST)**

1. **Double-click this file**:
   ```
   C:\Users\AB\Desktop\FYP\frontend\START_FRONTEND.bat
   ```

2. **It will**:
   - Install any missing dependencies
   - Start the React development server
   - Open http://localhost:3000 in browser

3. **Leave it running** in the background

---

### **METHOD 2: Command Line (Manual)**

Open Command Prompt and run:

```bash
cd C:\Users\AB\Desktop\FYP\frontend
npm start
```

Expected output:
```
Compiled successfully!

Local:            http://localhost:3000
On Your Network:  http://192.168.x.x:3000

You can now view travel-planner-frontend in the browser.
```

---

### **METHOD 3: Python Script**

```bash
python C:\Users\AB\Desktop\FYP\start_frontend.py
```

---

## What You'll See

### Browser Window Opens
- URL: http://localhost:3000
- Shows Travel Planner React App
- Fully functional web interface

### Console Output
```
Compiled successfully!

Local:            http://localhost:3000
On Your Network:  http://192.168.x.x:3000

You can now view travel-planner-frontend in the browser.
```

---

## Frontend Configuration

Your frontend is configured to:

```env
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_OPENWEATHER_API_KEY=<your-api-key>
REACT_APP_MAPTILER_API_KEY=<your-api-key>
REACT_APP_TRAVELADVISOR_API_KEY=<your-api-key>
```

**Backend Connection**: ✅ Ready (http://localhost:5000)

---

## Full Stack Setup

### **REQUIRED: Backend Must Be Running First!**

**Terminal 1 - Backend:**
```bash
cd C:\Users\AB\Desktop\FYP
python backend/app.py
```

Wait for:
```
* Running on http://127.0.0.1:5000
```

---

### **Terminal 2 - Frontend:**
```bash
cd C:\Users\AB\Desktop\FYP\frontend
npm start
```

Wait for:
```
Compiled successfully!
Local: http://localhost:3000
```

---

### **Browser**
Open: http://localhost:3000

---

## What to Test

Once frontend is running:

### 1. Homepage
- [ ] Loads without errors
- [ ] Shows destinations
- [ ] Navigation works
- [ ] Search bar visible

### 2. Search
- [ ] Search for destinations
- [ ] Filter by budget
- [ ] Filter by region
- [ ] Results display

### 3. Destination Details
- [ ] Click destination
- [ ] See details page
- [ ] View on map
- [ ] Read description

### 4. User Registration
- [ ] Register new account
- [ ] Email validation
- [ ] Password requirements
- [ ] Success message

### 5. User Login
- [ ] Login with credentials
- [ ] JWT token received
- [ ] Redirect to dashboard
- [ ] Profile visible

### 6. Itinerary Generation
- [ ] Generate itinerary
- [ ] Select duration
- [ ] Set budget
- [ ] View day-by-day plan

### 7. Weather Integration
- [ ] See weather for destination
- [ ] Display advisories
- [ ] Show temperature/conditions

### 8. API Integration
- [ ] All API calls successful
- [ ] No CORS errors
- [ ] Data displays correctly

---

## Troubleshooting

### Port 3000 Already in Use
```
Error: Something is already running on port 3000
```
**Solution**:
```bash
# Find process using port 3000
netstat -ano | findstr :3000

# Kill process (replace PID)
taskkill /PID <PID> /F

# Or use different port
PORT=3001 npm start
```

### npm not found
```
Error: 'npm' is not recognized
```
**Solution**:
1. Install Node.js from https://nodejs.org
2. Restart Command Prompt
3. Try again

### Can't connect to backend
```
Error: API_URL http://localhost:5000 not responding
```
**Solution**:
1. Ensure backend is running: `python backend/app.py`
2. Check backend is on port 5000
3. Check `.env` has correct API_URL

### Module not found
```
Error: Module 'react' not found
```
**Solution**:
```bash
cd frontend
npm install
npm start
```

### Blank page or white screen
**Solution**:
1. Check browser console for errors (F12)
2. Restart frontend: Ctrl+C then npm start
3. Clear browser cache: Ctrl+Shift+Delete

---

## Features Included

✅ **Destination Search**
- Search by name
- Filter by budget
- Filter by region
- View results

✅ **User Authentication**
- User registration
- User login
- Google OAuth (if configured)
- JWT token storage

✅ **Destination Details**
- View full information
- See on map
- Weather information
- Travel advisories
- Recommended places

✅ **Itinerary Generation**
- Create trip plan
- Day-by-day schedule
- Budget breakdown
- Activity suggestions

✅ **Weather Integration**
- Real-time weather
- Climate advisories
- Best travel season

✅ **Map Display**
- Interactive maps
- Destination locations
- Route planning

---

## File Structure

```
frontend/
├── public/
│   ├── index.html
│   └── favicon
├── src/
│   ├── App.js              # Main app
│   ├── components/         # React components
│   ├── pages/             # Page components
│   ├── services/          # API services
│   └── styles/            # CSS files
├── .env                   # Environment config
├── package.json           # Dependencies
└── START_FRONTEND.bat     # Quick starter
```

---

## Environment Variables

Edit `frontend/.env` to configure:

```env
# Backend API URL (required)
REACT_APP_API_URL=http://localhost:5000/api

# API Keys (optional)
REACT_APP_GOOGLE_CLIENT_ID=<your-google-client-id>
REACT_APP_GOOGLE_MAPS_API_KEY=<your-maps-key>
REACT_APP_OPENWEATHER_API_KEY=<your-openweather-key>
REACT_APP_MAPTILER_API_KEY=<your-maptiler-key>
REACT_APP_TRAVELADVISOR_API_KEY=<your-traveladvisor-key>
REACT_APP_TICKETMASTER_API_KEY=<your-ticketmaster-key>
```

---

## Performance Tips

- **Development**: npm start (with hot reload)
- **Production**: npm run build (optimized)
- **Testing**: npm test (run tests)

### Build for Production
```bash
cd frontend
npm run build
```

Creates optimized build in `build/` folder.

---

## Development Workflow

1. **Make changes** to React components
2. **Save file** - auto-reloads in browser
3. **Check browser console** for errors
4. **Backend must be running** for API calls

---

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Blank page | Check console (F12), restart npm |
| API errors | Verify backend running on :5000 |
| Port in use | Kill process or use PORT=3001 |
| Modules not found | Run npm install |
| Styling broken | Clear cache, restart |
| Maps not showing | Check API keys in .env |

---

## Quick Reference

```bash
# Start frontend
npm start

# Install dependencies
npm install

# Build for production
npm run build

# Run tests
npm test

# Update dependencies
npm update
```

---

## Complete Full Stack

### Terminal 1 - Backend
```bash
cd C:\Users\AB\Desktop\FYP
python backend/app.py
```

### Terminal 2 - Frontend
```bash
cd C:\Users\AB\Desktop\FYP\frontend
npm start
```

### Browser
```
http://localhost:3000
```

---

**Frontend is ready! Start it now!** 🚀
