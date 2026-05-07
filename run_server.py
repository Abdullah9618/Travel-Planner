#!/usr/bin/env python3
"""
Travel Planner Backend - Run Server
Starts the Flask development server
"""

import subprocess
import sys
import os
import time

backend_dir = r"c:\Users\AB\Desktop\FYP\backend"
os.chdir(backend_dir)

print("=" * 70)
print("Travel Planner - Flask Backend Server")
print("=" * 70)
print()

# Start server
print("Starting Flask application on http://127.0.0.1:5000")
print()
print("Press Ctrl+C to stop the server")
print()
print("=" * 70)
print()

# Run Flask app
subprocess.run([sys.executable, "app.py"])
