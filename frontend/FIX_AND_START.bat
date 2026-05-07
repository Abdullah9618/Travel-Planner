@echo off
REM Travel Planner - Frontend Fixer
REM This script fixes the npm/frontend startup issue

echo.
echo ======================================================================
echo TRAVEL PLANNER - FRONTEND FIX & START
echo ======================================================================
echo.

echo Killing existing Node processes...
taskkill /IM node.exe /F 2>nul
timeout /t 2 /nobreak

echo.
cd /d C:\Users\AB\Desktop\FYP\frontend

echo Checking npm...
call npm --version
if errorlevel 1 (
    echo.
    echo ERROR: npm not found!
    echo Please install Node.js from: https://nodejs.org
    echo Then restart this script.
    pause
    exit /b 1
)

echo.
echo Reinstalling dependencies...
call npm install

echo.
echo ======================================================================
echo Starting React Frontend
echo ======================================================================
echo.
echo Waiting for it to compile...
echo.

call npm start

pause
