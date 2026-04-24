@echo off
echo ================================================
echo Starting Streamlit Frontend
echo ================================================
echo.

cd frontend

if not exist ".venv" (
    echo ❌ Virtual environment not found at frontend\.venv
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat
echo ✓ Virtual environment activated
echo.
echo Starting Streamlit app...
echo App: http://localhost:8501
echo.

streamlit run app.py
pause
