#!/usr/bin/env python3
"""
Frontend Starter - Starts React development server
"""
import subprocess
import sys
import os

os.chdir(r"c:\Users\AB\Desktop\FYP\frontend")

print("\n" + "="*70)
print("TRAVEL PLANNER - REACT FRONTEND")
print("="*70 + "\n")

print("Installing/updating npm dependencies...")
result = subprocess.run([sys.executable, "-m", "npm", "install"], capture_output=True)

# Try with npm directly
print("Starting React development server...")
print("Expected to open at http://localhost:3000\n")
print("-"*70 + "\n")

# Run npm start
subprocess.run(["npm", "start"])
