@echo off
REM Windows Batch Script to Start the FastAPI Server
REM Usage: start_server.bat

echo ============================================================
echo Office Hours Triage API - Windows Startup Script
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10 or higher
    pause
    exit /b 1
)

echo Python detected: 
python --version
echo.

REM Navigate to the script directory
cd /d "%~dp0"

REM Check if requirements are installed
echo Checking dependencies...
python -c "import fastapi, uvicorn, pydantic, jose, passlib" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo Dependencies OK
echo.

REM Start the server
echo ============================================================
echo Starting FastAPI Server...
echo ============================================================
echo.
echo Documentation: http://localhost:8000/docs
echo Default Login: username=admin, password=admin123
echo.
echo Press CTRL+C to stop the server
echo ============================================================
echo.

python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

pause
