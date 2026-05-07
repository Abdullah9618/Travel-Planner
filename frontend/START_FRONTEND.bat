@echo off
REM Travel Planner - Frontend Starter
REM Starts React frontend on http://localhost:3000

echo.
echo ======================================================================
echo TRAVEL PLANNER - FRONTEND SERVER
echo ======================================================================
echo.

cd /d C:\Users\AB\Desktop\FYP\frontend

echo Installing/updating dependencies...
call npm install

echo.
echo ======================================================================
echo Starting React Frontend on http://localhost:3000
echo ======================================================================
echo.
echo A browser window should open automatically.
echo Press Ctrl+C to stop the server.
echo.

call npm start
