@echo off
setlocal enabledelayedexpansion

echo ================================================
echo Contract Analysis System - Backend
echo ================================================
echo.

REM Activate virtual environment and run backend
cd backend

if not exist ".venv" (
    echo ❌ Virtual environment not found at backend\.venv
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat
echo ✓ Virtual environment activated
echo.
echo Starting API server...
echo API will be available at http://localhost:8000
echo API Docs at http://localhost:8000/docs
echo.

python main.py
pause
