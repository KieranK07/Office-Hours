# Office Hours Triage System

A comprehensive three-layer queue management system for efficiently handling student help requests during office hours. Available as both a **C++ console application** and a **Python REST API** with JWT authentication.

## 📋 Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
  - [C++ Console Application](#c-console-application)
  - [Python API Server](#python-api-server)
- [Features](#features)
- [Architecture](#architecture)
- [Technical Details](#technical-details)
- [Usage Examples](#usage-examples)
- [Development](#development)
- [Future Enhancements](#future-enhancements)

## Overview

This system implements a priority-based triage system that sorts students based on their problem severity and arrival time, then matches them with available TAs based on skill sets.

### Three-Layer Architecture

1. **Arrival Queue** - All students enter here first (FIFO)
2. **Skill Set Queues** - Students are sorted by problem type and priority
   - **Primary**: Severity (1-5, where 5 is most urgent)
   - **Secondary**: Arrival time (earlier = higher priority)
3. **TA Assignment** - Students matched with available TAs by skill set

### Available Implementations

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Console App** | C++11 | Standalone CLI interface for local use |
| **REST API** | Python + FastAPI | Network-accessible service with authentication |

## Project Structure

```
Office-Hours/
├── src/                          # C++ Source Code
│   ├── Student.h                 # Student class declaration
│   ├── Student.cpp               # Student class implementation
│   ├── TA.h                      # TA class declaration
│   ├── TA.cpp                    # TA class implementation
│   ├── OfficeHoursSystem.h       # Main system manager declaration
│   ├── OfficeHoursSystem.cpp     # Main system manager implementation
│   └── officehours.cpp           # Main entry point with interactive CLI
│
├── api/                          # Python API Server
│   ├── main.py                   # FastAPI application and routes
│   ├── service.py                # Core business logic (triage system)
│   ├── models.py                 # Pydantic data models
│   ├── schemas.py                # Request/Response schemas
│   ├── auth.py                   # JWT authentication & security
│   ├── config.py                 # Configuration settings
│   ├── requirements.txt          # Python dependencies
│   ├── start_server.bat          # Windows server launcher
│   ├── start_server.sh           # Unix server launcher
│   ├── test_client.py            # Example API client
│   └── README.md                 # API-specific documentation
│
├── build.bat                     # Windows build script
├── Makefile                      # Unix build automation
└── README.md                     # This file
```

## Quick Start

### C++ Console Application

**Windows:**
```batch
build.bat
officehours.exe
```

**Linux/Mac:**
```bash
make
./officehours
```

### Python API Server

**Requirements:** Python 3.10+

```bash
cd api
pip install -r requirements.txt
python main.py
```

**Access:**
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

**Default Credentials:**
- Username: `admin`
- Password: `admin123`

## Features

### C++ Console Application

**Features:**
- ✅ Priority-based queuing (severity 1-5 + arrival time)
- ✅ Multiple skill set support for TAs
- ✅ Real-time statistics tracking
- ✅ Interactive menu-driven interface
- ✅ Professional data visualization
- ✅ Memory-safe implementation with proper cleanup

### Python API Server

**Features:**
- ✅ RESTful HTTP/JSON API
- ✅ JWT authentication with bcrypt password hashing
- ✅ Role-Based Access Control (Student, TA, Staff)
- ✅ CORS middleware for frontend integration
- ✅ Interactive Swagger documentation
- ✅ Async/await support for high performance
- ✅ PEP 8 compliant with full type hints

## Architecture

### Data Flow

```
Student Request
    ↓
Arrival Queue (FIFO)
    ↓
[Triage Process]
    ↓
Skill Set Queues (Priority: Severity → Time)
    ↓
TA Assignment (Match by skill)
    ↓
TA Helps Student
    ↓
Complete & Remove from System
```

### Priority Algorithm

Students are prioritized by:
1. **Severity** (1-5, where 5 is most urgent) - Primary factor
2. **Arrival Time** - Secondary factor (earlier = higher priority)

Example priority order:
- Student A: Severity 5, arrived 10:00 AM
- Student B: Severity 5, arrived 10:15 AM
- Student C: Severity 3, arrived 9:00 AM
- **Queue order:** A → B → C

## Technical Details

### C++ Implementation

**Compilation Requirements:**
- C++11 or higher
- Standard Template Library (STL)
- g++ or compatible compiler

**Build Process:**

*Windows:*
```batch
build.bat
```
Or manually:
```batch
g++ -std=c++11 -Wall -Wextra -pedantic -g -c src/Student.cpp src/TA.cpp src/OfficeHoursSystem.cpp src/officehours.cpp
g++ -std=c++11 -Wall -Wextra -pedantic -g -o officehours.exe Student.o TA.o OfficeHoursSystem.o officehours.o
```

*Linux/Mac:*
```bash
make
# or
make run  # build and run in one command
```

**Design Patterns:**
- **Encapsulation** - Private data members with public accessors
- **Separation of Concerns** - Each class has a single responsibility
- **RAII** - Resource management tied to object lifetime
- **STL Containers** - Priority queues, vectors, maps for robust data structures

**Memory Management:**
- All dynamically allocated memory is properly managed
- Students are deleted after being helped
- System destructor cleans up all remaining resources

### Python API Implementation

**Technology Stack:**
- **FastAPI** - Modern async web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation with type hints
- **python-jose** - JWT implementation
- **passlib[bcrypt]** - Secure password hashing

**Installation:**
```bash
cd api
pip install -r requirements.txt
```

**Running the Server:**
```bash
# Development mode (auto-reload)
python main.py

# Or with uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**API Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Usage Examples

### C++ Console Application - Main Menu

1. **Add Student** - Register a new student with problem details
   - Name, severity (1-5), skill set, problem description
2. **Add TA** - Add a teaching assistant with skill sets
   - Name, multiple skills (Python, Java, C++, etc.)
3. **Process System** - Move students through queues and assign to TAs
   - Automated triage from arrival → skill queues → TA assignment
4. **Complete Student** - Mark that a TA has finished helping a student
   - Frees up TA for next student
5. **Display All Queues** - View current queue status
6. **Display TA Status** - See all TAs and their availability
7. **Display System Statistics** - View performance metrics
8. **Advance Time** - Simulate time progression
9. **Exit** - Close the program
**Typical Workflow:**
1. Add TAs (Option 2) to staff the office hours
2. Students arrive and are added (Option 1)
3. Process system (Option 3) to move students into skill queues
4. Process again (Option 3) to assign students to available TAs
5. Complete student sessions (Option 4) as TAs finish
6. View statistics (Option 7) to see performance metrics

### Python API - Endpoint Reference

**Authentication:**
```bash
# Login and get JWT token
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

**Student Operations (Public):**
```bash
# Student requests help
curl -X POST "http://localhost:8000/student/request" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice Johnson",
    "severity": 5,
    "skill_set": "Python",
    "problem_description": "Recursion causing stack overflow"
  }'

# Check student status
curl "http://localhost:8000/student/{student_id}"
```

**Staff Operations (Requires Authentication):**
```bash
# Add a TA
curl -X POST "http://localhost:8000/staff/ta" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Bob Smith",
    "skills": ["Python", "Java", "C++"],
    "username": "ta_bob",
    "password": "SecurePass123!"
  }'

# Process triage (move students through queues)
curl -X GET "http://localhost:8000/staff/triage" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**TA Operations (Requires TA Authentication):**
```bash
# TA claims next student
curl -X POST "http://localhost:8000/ta/claim" \
  -H "Authorization: Bearer TA_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"ta_id": "ta_ta_bob", "preferred_skill": "Python"}'

# TA marks student complete
curl -X POST "http://localhost:8000/ta/complete" \
  -H "Authorization: Bearer TA_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"ta_id": "ta_ta_bob", "student_id": "student_123"}'
```

**System Statistics:**
```bash
# View stats (public)
curl "http://localhost:8000/stats"
```

For detailed API documentation, see [api/README.md](api/README.md)

## Development

### C++ Development

**Debugging:**
```bash
# Build with debug symbols
make debug

# Use with gdb/lldb
gdb ./officehours
```

**Testing:**
- Run with demo data to test functionality
- Verify memory safety with valgrind (Linux):
  ```bash
  valgrind --leak-check=full ./officehours
  ```

### Python API Development

**Hot Reload:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Testing:**
```bash
# Run test client
python test_client.py

# Or use pytest (if tests exist)
pytest tests/
```

**Configuration:**

Create `api/.env` file:
```env
SECRET_KEY=your-super-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=60
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
MAX_SEVERITY=5
```

### Code Quality

**C++:**
- Follows modern C++11 standards
- Comprehensive documentation comments
- Memory-safe with RAII patterns
- Proper const correctness

**Python:**
- PEP 8 compliant
- Full type hints throughout
- Comprehensive docstrings
- Async/await best practices

## Deployment

### C++ Console Application

**Distribution:**
1. Compile for target platform
2. Distribute executable
3. No external dependencies required

### Python API Server

**Production Checklist:**
- [ ] Change `SECRET_KEY` in production environment
- [ ] Use environment variables for all secrets
- [ ] Change default admin password
- [ ] Configure proper CORS origins for your frontend
- [ ] Enable HTTPS/TLS
- [ ] Set up proper logging and monitoring
- [ ] Use production ASGI server

**Production Command:**
```bash
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

**Docker (Optional):**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY api/ .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Comparison: C++ vs Python API

| Feature | C++ Console | Python API |
|---------|------------|------------|
| **Interface** | Interactive CLI | RESTful HTTP/JSON |
| **Authentication** | None | JWT with bcrypt |
| **Networking** | Local only | Network accessible |
| **Concurrency** | Single-threaded | Async/await |
| **Web Frontend** | No | Yes (CORS enabled) |
| **Security** | N/A | RBAC, encryption |
| **Documentation** | Code comments | Auto-generated Swagger |
| **Platform** | Native binary | Cross-platform |
| **Use Case** | Local testing, demos | Production web service |

## Future Enhancements

**Shared:**
- [ ] Database integration (SQLite/PostgreSQL)
- [ ] Estimated wait time calculations
- [ ] Student notification system
- [ ] Export statistics to CSV/JSON
- [ ] Multiple concurrent TA sessions
- [ ] Logging system for audit trail

**API-Specific:**
- [ ] WebSocket support for real-time updates
- [ ] Rate limiting and API throttling
- [ ] Comprehensive test suite
- [ ] Docker containerization
- [ ] Redis caching layer
- [ ] Prometheus metrics export

**C++-Specific:**
- [ ] Configuration file support
- [ ] GUI interface (Qt/wxWidgets)
- [ ] Network server capabilities
- [ ] Plugin system for extensions

**Integration:**
- [ ] Bridge between C++ and Python implementations
- [ ] Shared data format for interoperability
- [ ] Web frontend that uses API backend

## Troubleshooting

### C++ Issues

**Compilation errors:**
- Ensure g++ or compatible compiler is installed
- Check C++11 support: `g++ --version`
- Verify all source files are in `src/` directory

**Runtime issues:**
- Enable debug symbols: `make debug`
- Use valgrind for memory leaks (Linux)

### API Issues

**Port already in use:**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

**Module not found:**
```bash
pip install -r requirements.txt --upgrade
```

**CORS errors:**
- Add your frontend URL to `ALLOWED_ORIGINS` in `api/config.py`

**Authentication errors:**
- Verify token format: `Bearer YOUR_JWT_TOKEN`
- Check token expiration time
- Ensure proper role for endpoint access

## Contributing

This is an educational project demonstrating:
- Data structures (queues, priority queues, maps)
- Object-oriented design
- REST API development
- Authentication and security
- Multi-language system design

## License

Educational project - free to use and modify.

## Resources

- **C++ Documentation**: See code comments in `src/` files
- **API Documentation**: [api/README.md](api/README.md)
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **C++ Reference**: https://cppreference.com/

---

**Built with dedication for efficient office hours management** 🎓 
