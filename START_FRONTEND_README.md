# FRONTEND QUICK START

## Prerequisites

⚠️ **IMPORTANT: Backend Must Be Running First!**

Before starting frontend, ensure:

1. **Backend is running** on http://127.0.0.1:5000
2. **MongoDB Atlas connected** (you'll see [OK] messages)
3. **Data seeded** (destinations, users, cost_rates)

---

## How to Run Frontend

### **EASIEST: Double-click Batch File**

```
C:\Users\AB\Desktop\FYP\frontend\START_FRONTEND.bat
```

Browser will open automatically at http://localhost:3000

---

### Alternative: Command Line

```bash
cd C:\Users\AB\Desktop\FYP\frontend
npm start
```

Then open: http://localhost:3000

---

## What You'll See

✅ React Travel Planner app loads  
✅ Search bar visible  
✅ Destinations displayed  
✅ Navigation menu working  

---

## If It Doesn't Work

### Error: Can't connect to backend
```
Check: Is backend running on port 5000?
If not: python backend/app.py (in another terminal)
```

### Error: Port 3000 in use
```
Kill: taskkill /IM node.exe /F
Or: PORT=3001 npm start
```

### Error: npm not found
```
Install Node.js: https://nodejs.org
Restart Command Prompt
Try again
```

### Error: Blank page
```
Press F12 to open console
Check for errors
Restart: Ctrl+C then npm start
```

---

## Full Stack Status

| Component | Status | Port | Command |
|-----------|--------|------|---------|
| Backend | Running | 5000 | `python backend/app.py` |
| Frontend | Ready | 3000 | `npm start` |
| Database | Connected | Cloud | MongoDB Atlas |

---

## Test After Starting

1. **Homepage loads** ✓
2. **Search works** ✓
3. **Register user** ✓
4. **Login works** ✓
5. **View destinations** ✓

---

**Start frontend now!** 🚀
