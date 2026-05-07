@echo off
REM Travel Planner Backend Startup Script

echo ==========================================
echo Travel Planner Backend - Starting
echo ==========================================
echo.

REM Change to backend directory
cd /d C:\Users\AB\Desktop\FYP\backend

REM Check Python
python --version
echo.

REM Install pymongo if needed
echo Installing/Checking dependencies...
python -m pip install -r requirements.txt --quiet
echo Dependencies ready.
echo.

REM Start the Flask app
echo Starting Flask application...
echo ==========================================
echo.
python app.py
