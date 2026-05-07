# FRONTEND ERROR FIX GUIDE

## Error You Got
```
Unsafe attempt to load URL http://localhost:3000/ from frame with URL chrome-error://chromewebdata/
```

This means: **React dev server didn't start properly**

---

## SOLUTION (Try These Steps)

### Step 1: Close Everything
```bash
# Kill all Node processes
taskkill /IM node.exe /F
```

Then close all Command Prompt windows.

---

### Step 2: Open Fresh Command Prompt

**Method A: Windows + R (Easiest)**
1. Press `Windows + R`
2. Type: `cmd`
3. Press Enter

**Method B: Manual**
1. Start menu → Command Prompt
2. Or search for "cmd"

---

### Step 3: Navigate to Frontend

Copy and paste this:
```bash
cd C:\Users\AB\Desktop\FYP\frontend
```

Press Enter.

---

### Step 4: Clear and Reinstall

Copy and paste this:
```bash
npm install
```

Wait for it to complete (might take 1-2 minutes).

---

### Step 5: Start Frontend

Copy and paste this:
```bash
npm start
```

---

### Step 6: Wait for This Message

In your terminal, you should see:
```
Compiled successfully!

Local:            http://localhost:3000
```

**Don't do anything yet - wait about 5 seconds**

---

### Step 7: Open Browser

**One of these will happen:**
1. ✅ Browser opens automatically at http://localhost:3000
2. ❓ Browser doesn't open - you open it manually

If it doesn't open automatically:
- Open any browser
- Type: `http://localhost:3000`
- Press Enter

---

## If Still Getting Error

### Fix 1: Clear Browser Cache

1. Press `Ctrl + Shift + Delete`
2. Select "All time"
3. Check all boxes
4. Click "Clear data"
5. Refresh page

---

### Fix 2: Use Different Browser

Try:
- Edge
- Firefox
- Safari
- Brave

---

### Fix 3: Check if Backend is Running

The frontend needs backend to work!

Verify backend is running:
```bash
# Open another Command Prompt
python c:\Users\AB\Desktop\FYP\backend\app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
```

---

### Fix 4: Reinstall Everything

If nothing works:

```bash
# Go to frontend
cd C:\Users\AB\Desktop\FYP\frontend

# Delete node_modules
rmdir /s /q node_modules

# Delete package-lock.json
del package-lock.json

# Reinstall
npm install

# Start
npm start
```

This might take 3-5 minutes.

---

## Common Issues

### Issue: `npm is not recognized`

**Cause**: npm not in PATH

**Solution**:
1. Install Node.js from https://nodejs.org
2. Restart Command Prompt
3. Try again

### Issue: `Port 3000 already in use`

**Solution**:
```bash
taskkill /IM node.exe /F
```

### Issue: Blank white page

**Solution**:
1. Press F12 to open console
2. Look for red errors
3. Take screenshot of errors
4. Restart: Ctrl+C then npm start

### Issue: Can't connect to API

**Solution**:
- Make sure backend is running
- Check backend console shows: `Running on http://127.0.0.1:5000`

---

## Step-by-Step Quick Fix

**Copy and paste these commands one at a time:**

```bash
cd C:\Users\AB\Desktop\FYP\frontend
```
Press Enter, wait 2 seconds.

```bash
taskkill /IM node.exe /F
```
Press Enter, wait 2 seconds.

```bash
npm install
```
Press Enter, wait for completion (1-2 min).

```bash
npm start
```
Press Enter, wait for "Compiled successfully!"

Then open: http://localhost:3000

---

## What Should Happen

1. ✅ Command Prompt shows "Compiled successfully!"
2. ✅ Browser opens automatically (or you open it)
3. ✅ http://localhost:3000 loads
4. ✅ You see the Travel Planner homepage
5. ✅ No errors in browser console

---

## Verification

Once page loads, test:

1. **Search works** → Type destination name
2. **No red errors** → Press F12, check console
3. **Can navigate** → Click menu items
4. **Register button visible** → Look for signup button

---

## Still Not Working?

Try this exact process:

1. **Close everything**
   - Close all Command Prompts
   - Close all browsers
   - Press Windows key, type Task Manager, open it
   - Kill any "node.exe" or "npm" processes

2. **Start completely fresh**
   - Open Command Prompt
   - Copy each line, one at a time:

```bash
cd C:\Users\AB\Desktop\FYP\frontend
npm install
npm start
```

3. **Wait at least 1 minute** for "Compiled successfully!"

4. **Don't click anything** until you see that message

5. **Then open browser** to http://localhost:3000

---

## Alternative: Use Batch File

Instead of Command Prompt, try batch file:

```
C:\Users\AB\Desktop\FYP\frontend\START_FRONTEND.bat
```

Double-click it. Let it run.

---

## If Batch File Doesn't Work

The issue is likely npm PATH issue. To fix:

1. Restart your computer (seriously, this helps!)
2. Install Node.js again from https://nodejs.org
3. During install, make sure "Add to PATH" is checked
4. Restart computer again
5. Try npm start

---

## Summary

**The Error**: React dev server crashed or didn't start  
**The Fix**: Reinstall dependencies and restart

**Quick Commands**:
```bash
cd C:\Users\AB\Desktop\FYP\frontend
npm install
npm start
```

**What to expect**: 
- Compiles successfully
- Browser opens
- App loads at http://localhost:3000

---

**Try the fixes above and let me know if you hit any errors!**
