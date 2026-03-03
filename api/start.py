#!/usr/bin/env python3
"""
Quick start script for Office Hours API
Checks dependencies and starts the server
"""
import sys
import subprocess
import os


def check_python_version():
    """Ensure Python 3.10+"""
    if sys.version_info < (3, 10):
        print("❌ Error: Python 3.10 or higher required")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")


def check_dependencies():
    """Check if required packages are installed"""
    try:
        import fastapi
        import uvicorn
        import pydantic
        import jose
        import passlib
        print("✅ All dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e.name}")
        print("\n📦 Installing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return False


def start_server():
    """Start the FastAPI server"""
    print("\n" + "="*60)
    print("🚀 Starting Office Hours Triage API Server")
    print("="*60)
    print("\n📚 Documentation: http://localhost:8000/docs")
    print("🔐 Default login: username=admin, password=admin123")
    print("\n⏹️  Press CTRL+C to stop the server\n")
    print("="*60 + "\n")
    
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "main:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8000"
    ])


def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("Office Hours Triage API - Setup")
    print("="*60 + "\n")
    
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    check_python_version()
    check_dependencies()
    
    try:
        start_server()
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
