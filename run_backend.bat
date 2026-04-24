@echo off
echo ================================================
echo Starting Backend API
echo ================================================
echo.

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
echo API: http://localhost:8000
echo Docs: http://localhost:8000/docs
echo.

python main.py
pause
