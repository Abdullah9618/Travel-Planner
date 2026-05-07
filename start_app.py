#!/usr/bin/env python3
"""
Quick server starter - runs Flask backend and keeps it alive
"""
import subprocess
import sys
import os
import time

os.chdir(r"c:\Users\AB\Desktop\FYP\backend")

print("\n" + "="*70)
print("TRAVEL PLANNER - BACKEND SERVER")
print("="*70 + "\n")

print("Installing dependencies...")
subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"], timeout=120)

print("\nStarting server on http://127.0.0.1:5000...")
print("-"*70 + "\n")

# Run the Flask app
subprocess.run([sys.executable, "app.py"])
