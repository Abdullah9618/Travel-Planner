@echo off
REM Travel Planner - Quick Start
REM Starts backend server and displays test commands

echo.
echo ======================================================================
echo TRAVEL PLANNER - BACKEND SERVER
echo ======================================================================
echo.

cd /d C:\Users\AB\Desktop\FYP\backend

echo Installing dependencies...
python -m pip install -r requirements.txt -q

echo.
echo ======================================================================
echo Starting server on http://127.0.0.1:5000
echo ======================================================================
echo.

python app.py
