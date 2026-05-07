@echo off
REM Travel Planner - Full Stack Starter
REM Starts Backend and Frontend together

setlocal enabledelayedexpansion

echo.
echo ======================================================================
echo TRAVEL PLANNER - FULL STACK STARTUP
echo ======================================================================
echo.
echo This script will:
echo   1. Start Backend on http://127.0.0.1:5000
echo   2. Start Frontend on http://localhost:3000
echo.
echo You may see TWO windows open:
echo   - Backend server terminal (Python)
echo   - Frontend development server (React)
echo.
pause

REM Start Backend in new window
echo Starting Backend...
start "Backend Server" cmd /k "cd /d C:\Users\AB\Desktop\FYP\backend && python app.py"

REM Wait for backend to start
echo Waiting for backend to start...
timeout /t 3 /nobreak

REM Start Frontend in new window
echo Starting Frontend...
start "Frontend Server" cmd /k "cd /d C:\Users\AB\Desktop\FYP\frontend && npm start"

echo.
echo ======================================================================
echo Both servers should be starting!
echo ======================================================================
echo.
echo Backend:  http://127.0.0.1:5000
echo Frontend: http://localhost:3000
echo.
echo Your browser should open automatically when ready.
echo.
pause
