# 🚀 RUN YOUR TRAVEL PLANNER NOW

## EASIEST WAY (Recommended)

### Step 1: Double-Click This File

```
C:\Users\AB\Desktop\FYP\START_ALL.bat
```

**That's it!**

Two windows will open:
1. Backend server (http://127.0.0.1:5000)
2. Frontend server (http://localhost:3000)

A browser will automatically open with your app.

---

## WHAT YOU'LL SEE

✅ Travel Planner homepage loads  
✅ Search bar for destinations  
✅ List of travel destinations  
✅ Login/Register buttons  
✅ Maps and weather info  

---

## MANUAL METHOD (If Batch File Doesn't Work)

### Terminal 1 - Backend
```bash
cd C:\Users\AB\Desktop\FYP
python backend/app.py
```

**Wait for this message:**
```
 * Running on http://127.0.0.1:5000
```

### Terminal 2 - Frontend
```bash
cd C:\Users\AB\Desktop\FYP\frontend
npm start
```

**Wait for this message:**
```
Compiled successfully!
Local: http://localhost:3000
```

Then your browser will open automatically.

---

## TEST THE APP

Once loaded, try:

1. **Search** → Type a destination name
2. **Register** → Create an account
3. **Login** → Login with your account
4. **Explore** → View destinations
5. **Plan** → Generate an itinerary

---

## TROUBLESHOOTING

### Backend won't start
```
python backend/app.py
(should show "Running on http://127.0.0.1:5000")
```

### Frontend won't start
```
npm start
(in frontend folder)
```

### Port in use
```
taskkill /IM node.exe /F
taskkill /IM python.exe /F
```

### Can't find npm
```
Install Node.js: https://nodejs.org
Restart Command Prompt
```

---

## WHAT'S INCLUDED

✅ Backend API (Flask + Python)  
✅ Frontend App (React)  
✅ Database (MongoDB Atlas - Cloud)  
✅ Search functionality  
✅ User authentication  
✅ Map integration  
✅ Weather API  
✅ Itinerary generation  

---

## QUICK REFERENCE

| What | Command | Port |
|------|---------|------|
| Backend | `python backend/app.py` | 5000 |
| Frontend | `npm start` (in frontend) | 3000 |
| Browser | http://localhost:3000 | - |
| API | http://127.0.0.1:5000/api | 5000 |

---

## THAT'S ALL!

Your complete Travel Planner is ready to use.

### 🎯 START NOW:

```
1. Double-click: START_ALL.bat
   OR
2. Open 2 terminals:
   - python backend/app.py
   - npm start
```

### 🌐 OPEN:

```
http://localhost:3000
```

---

## DOCUMENTATION

For more details, see:
- `FULL_STACK_GUIDE.md` - Complete setup
- `FRONTEND_GUIDE.md` - Frontend details
- `API_TESTING.md` - How to test APIs
- `SETUP_COMPLETE.md` - Full summary

---

**Enjoy your Travel Planner! 🎉**
