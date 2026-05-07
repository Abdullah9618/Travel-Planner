#!/usr/bin/env python3
"""
Test if the Travel Planner backend can start
"""

import sys
import os

# Add backend to path
sys.path.insert(0, r"c:\Users\AB\Desktop\FYP\backend")
os.chdir(r"c:\Users\AB\Desktop\FYP\backend")

print("=" * 60)
print("Testing Travel Planner Backend Startup")
print("=" * 60)
print()

# Step 1: Check imports
print("Step 1: Checking imports...")
try:
    from flask import Flask
    print("  [OK] Flask imported")
except ImportError as e:
    print(f"  [FAIL] Flask import failed: {e}")
    sys.exit(1)

try:
    import pymongo
    print("  [OK] pymongo imported")
except ImportError as e:
    print(f"  [INFO] pymongo not installed. Installing...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "pymongo==4.6.1", "-q"])
    import pymongo
    print("  [OK] pymongo installed and imported")

try:
    from mongodb_persistence import build_mongodb_persistence
    print("  [OK] mongodb_persistence imported")
except ImportError as e:
    print(f"  [FAIL] mongodb_persistence import failed: {e}")
    sys.exit(1)

print()
print("Step 2: Testing MongoDB connection...")
try:
    db = build_mongodb_persistence()
    print("  [OK] MongoDB connection successful")
except Exception as e:
    print(f"  [WARN] MongoDB connection failed (will use JSON fallback): {e}")
    print("    Make sure MongoDB is running, or app will fall back to JSON files")

print()
print("Step 3: Attempting to load app...")
try:
    # Import app - this will try to start MongoDB and seed data
    from app import app as flask_app
    print("  [OK] Flask app loaded successfully")
except Exception as e:
    print(f"  [WARN] Error loading app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("=" * 60)
print("SUCCESS: Backend is ready!")
print("=" * 60)
print()
print("To start the server, run:")
print("  python -m flask run")
print("  or")
print("  python app.py")
print()
