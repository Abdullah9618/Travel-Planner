# FRONTEND ERROR - COMPLETE TROUBLESHOOTING

## Error Message You Got
```
Unsafe attempt to load URL http://localhost:3000/ 
from frame with URL chrome-error://chromewebdata/
```

**This means**: React dev server didn't start or crashed

---

## IMMEDIATE FIX (Try This First!)

### **Double-click this:**
```
C:\Users\AB\Desktop\FYP\frontend\FIX_AND_START.bat
```

This will:
1. Kill existing processes
2. Reinstall dependencies
3. Start the dev server fresh

Then wait for "Compiled successfully!" message.

---

## Manual Fix (Step-by-Step)

### Step 1: Kill Everything
```bash
taskkill /IM node.exe /F
```

Close all Command Prompt windows.

---

### Step 2: Open Fresh Terminal

Press `Windows + R`, type `cmd`, press Enter.

---

### Step 3: Go to Frontend
```bash
cd C:\Users\AB\Desktop\FYP\frontend
```

---

### Step 4: Clean Install
```bash
npm install
```

Wait for completion (1-2 minutes).

---

### Step 5: Start
```bash
npm start
```

Wait for:
```
Compiled successfully!

Local: http://localhost:3000
```

---

### Step 6: Open Browser

Type in address bar:
```
http://localhost:3000
```

---

## Still Not Working?

### Check 1: Is Node.js Installed?

Open Command Prompt:
```bash
node --version
```

Should show version like `v24.10.0`

**If error**: Install from https://nodejs.org

---

### Check 2: Is npm Installed?

```bash
npm --version
```

Should show version like `10.2.0`

**If error**: Reinstall Node.js

---

### Check 3: Is Backend Running?

Open another Command Prompt:
```bash
python C:\Users\AB\Desktop\FYP\backend\app.py
```

Should show:
```
 * Running on http://127.0.0.1:5000
```

**If error**: Start backend first

---

### Check 4: Delete and Reinstall

```bash
cd C:\Users\AB\Desktop\FYP\frontend
rmdir /s /q node_modules
del package-lock.json
npm install
npm start
```

---

## Browser-Level Fixes

### Fix 1: Clear Cache

1. Press `Ctrl + Shift + Delete`
2. Select "All time"
3. Uncheck everything except "Cookies and other site data" and "Cached images"
4. Click "Clear data"
5. Go to http://localhost:3000

---

### Fix 2: Use Incognito Mode

1. Press `Ctrl + Shift + N`
2. Go to http://localhost:3000
3. This bypasses cache issues

---

### Fix 3: Try Different Browser

Try:
- Chrome
- Edge
- Firefox
- Safari

---

### Fix 4: Check Console for Errors

1. Open http://localhost:3000
2. Press `F12`
3. Click "Console" tab
4. Look for red error messages
5. Tell me what you see

---

## Complete Reset Process

If nothing works, try complete reset:

### In Command Prompt:

```bash
cd C:\Users\AB\Desktop\FYP\frontend
```

```bash
rmdir /s /q node_modules
```

```bash
del package-lock.json
```

```bash
npm cache clean --force
```

```bash
npm install
```

```bash
npm start
```

Wait for "Compiled successfully!" then open http://localhost:3000

---

## Restart Computer Option

Sometimes the simplest fix is:

1. **Close everything**
2. **Restart computer** (yes, really!)
3. **Open Command Prompt**
4. **Run**:
   ```bash
   cd C:\Users\AB\Desktop\FYP\frontend
   npm start
   ```

---

## Environment Check

Make sure `.env` exists in frontend folder:

```
C:\Users\AB\Desktop\FYP\frontend\.env
```

Should contain:
```
REACT_APP_API_URL=http://localhost:5000/api
```

If missing, create it with these contents.

---

## API Connection Issues

If frontend loads but shows errors:

### Make sure backend is running:
```bash
python C:\Users\AB\Desktop\FYP\backend\app.py
```

Should show:
```
 * Running on http://127.0.0.1:5000
```

### Then frontend should connect.

---

## Error Messages & Solutions

| Error | Solution |
|-------|----------|
| `npm not recognized` | Install Node.js, restart |
| `Port 3000 in use` | `taskkill /IM node.exe /F` |
| `Cannot find module` | `npm install` |
| `Blank page` | Check console (F12), look for errors |
| `Can't connect to API` | Start backend first |
| `Compiled successfully! but blank page` | Clear cache, hard refresh (Ctrl+F5) |

---

## Quick Checklist

Before declaring victory:

- [ ] No red errors in browser console (F12)
- [ ] Travel Planner logo/title visible
- [ ] Search bar present
- [ ] Navigation menu works
- [ ] Can navigate to different pages
- [ ] API calls working (no 404s in console)
- [ ] Page interactive, not blank

---

## Commands Reference

```bash
# Kill Node processes
taskkill /IM node.exe /F

# Check Node version
node --version

# Check npm version
npm --version

# Go to frontend
cd C:\Users\AB\Desktop\FYP\frontend

# Install dependencies
npm install

# Start dev server
npm start

# Clean install
npm cache clean --force
npm install
npm start

# Delete everything and reinstall
rmdir /s /q node_modules
del package-lock.json
npm install
npm start
```

---

## When to Restart Computer

Try restarting if:
- npm commands not found after install
- Port issues persist
- Multiple errors occurring
- Nothing else works

---

## GET HELP

If you still have errors:

1. **Take screenshot** of the error
2. **Check console** (F12) for red errors
3. **Tell me**:
   - What command you ran
   - What error you see
   - What's in the Command Prompt
   - What's in the browser console

---

## Summary

Most likely fixes (in order):

1. ✅ `taskkill /IM node.exe /F` then restart
2. ✅ `npm install` then `npm start`
3. ✅ Clear browser cache (Ctrl+Shift+Delete)
4. ✅ Use incognito mode
5. ✅ Restart computer
6. ✅ Reinstall Node.js

---

**Try the FIX_AND_START.bat first, then follow manual steps if needed!**
