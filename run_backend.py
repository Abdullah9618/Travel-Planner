#!/usr/bin/env python3
"""
Travel Planner Backend - Startup Script
Installs dependencies and starts the Flask application
"""

import subprocess
import sys
import os

def main():
    backend_dir = os.path.dirname(__file__)
    
    print("=" * 60)
    print("Travel Planner - Backend Server")
    print("=" * 60)
    print()
    
    # Install requirements
    print("Installing dependencies...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"],
        cwd=backend_dir,
        capture_output=False
    )
    
    if result.returncode != 0:
        print("Warning: Some dependencies may not have installed correctly")
    else:
        print("Dependencies installed successfully!")
    
    print()
    print("=" * 60)
    print("Starting Flask application...")
    print("=" * 60)
    print()
    
    # Start Flask app
    result = subprocess.run(
        [sys.executable, "app.py"],
        cwd=backend_dir
    )
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())
