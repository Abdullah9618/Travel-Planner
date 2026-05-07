@echo off
setlocal enabledelayedexpansion

echo.
echo ======================================================================
echo AUTO-FIXING FRONTEND - Travel Planner
echo ======================================================================
echo.

REM Change to frontend directory
cd /d "c:\Users\AB\Desktop\FYP\frontend"

echo Checking npm installation...
npm --version
if errorlevel 1 (
    echo ERROR: npm not installed
    echo Please install Node.js from https://nodejs.org
    pause
    exit /b 1
)

echo.
echo Installing dependencies... (this may take 2-5 minutes)
echo.
call npm install

if errorlevel 1 (
    echo ERROR: npm install failed
    pause
    exit /b 1
)

echo.
echo ======================================================================
echo Dependencies installed successfully!
echo Starting React development server...
echo ======================================================================
echo.
echo Please wait for: "Compiled successfully!"
echo.

call npm start

pause
