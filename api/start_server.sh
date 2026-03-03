#!/bin/bash
# Linux/Mac Shell Script to Start the FastAPI Server

echo "============================================================"
echo "Office Hours Triage API - Startup Script"
echo "============================================================"
echo

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python 3 is not installed"
    echo "   Please install Python 3.10 or higher"
    exit 1
fi

echo "✅ Python detected:"
python3 --version
echo

# Navigate to script directory
cd "$(dirname "$0")"

# Check if virtual environment should be used
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
fi

# Check if requirements are installed
echo "🔍 Checking dependencies..."
python3 -c "import fastapi, uvicorn, pydantic, jose, passlib" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Installing dependencies..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ ERROR: Failed to install dependencies"
        exit 1
    fi
fi

echo "✅ Dependencies OK"
echo

# Start the server
echo "============================================================"
echo "🚀 Starting FastAPI Server..."
echo "============================================================"
echo
echo "📚 Documentation: http://localhost:8000/docs"
echo "🔐 Default Login: username=admin, password=admin123"
echo
echo "⏹️  Press CTRL+C to stop the server"
echo "============================================================"
echo

python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
