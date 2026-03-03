# Office Hours Triage System - FastAPI Server

A robust, secure Python FastAPI server that manages student office hours queues with a three-layer triage system. Ported from the original C++ implementation with enterprise-grade security features.

## 🏗️ Architecture

### Three-Layer Queue System

1. **Arrival Queue** (FIFO) - Students initially enter here
2. **Skill-Set Priority Queues** - Students sorted by:
   - **Primary**: Severity (1-5, where 5 is critical)
   - **Secondary**: Arrival time (earlier = higher priority)
3. **TA Assignment** - Students matched with available TAs based on skill sets

### Separation of Concerns

```
api/
├── config.py          # Configuration and settings
├── models.py          # Core Pydantic data models
├── schemas.py         # Request/Response schemas
├── auth.py            # JWT authentication & security
├── service.py         # Business logic layer (triage system)
├── main.py            # FastAPI routes and app
└── requirements.txt   # Python dependencies
```

## 🔐 Security Features

- ✅ **JWT (JSON Web Tokens)** for stateless authentication
- ✅ **bcrypt password hashing** via passlib
- ✅ **Role-Based Access Control** (Student, TA, Staff)
- ✅ **CORS middleware** for frontend integration
- ✅ **Secure default credentials** (change in production!)

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Installation

1. **Navigate to the API directory:**
```bash
cd Office-Hours/api
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment (optional):**
Create a `.env` file for custom settings:
```env
SECRET_KEY=your-super-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=60
ALLOWED_ORIGINS=["http://localhost:3000"]
```

4. **Run the server:**
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

5. **Access the API:**
- **Interactive API Docs:** http://localhost:8000/docs
- **Alternative Docs:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

## 📡 API Endpoints

### 🔓 Public Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/student/request` | Student joins arrival queue |
| `GET`  | `/student/{id}` | Check student status by ID |
| `GET`  | `/stats` | View system statistics |
| `GET`  | `/health` | Health check |

### 🔐 Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/login` | Login and receive JWT token |
| `GET`  | `/auth/me` | Get current user info |

**Default Credentials:**
- **Username:** `admin`
- **Password:** `admin123`
- **Role:** `staff`

### 👥 Staff Endpoints (Requires STAFF role)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/staff/triage` | Process queues (arrival → skill → TA) |
| `POST` | `/staff/ta` | Add a new TA to the system |

### 🎓 TA Endpoints (Requires TA role)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/ta/claim` | Claim highest priority student |
| `POST` | `/ta/complete` | Mark student session complete |
| `GET`  | `/ta/all` | List all TAs and their status |

## 🧪 Testing the API

### Using cURL

**1. Student requests help:**
```bash
curl -X POST "http://localhost:8000/student/request" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice Johnson",
    "severity": 5,
    "skill_set": "Python",
    "problem_description": "Recursion causing stack overflow"
  }'
```

**2. Staff logs in:**
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

**3. Staff adds a TA:**
```bash
curl -X POST "http://localhost:8000/staff/ta" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Bob Smith",
    "skills": ["Python", "Java", "C++"],
    "username": "ta_bob",
    "password": "SecurePass123!"
  }'
```

**4. Staff processes triage:**
```bash
curl -X GET "http://localhost:8000/staff/triage" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**5. TA claims a student:**
```bash
curl -X POST "http://localhost:8000/ta/claim" \
  -H "Authorization: Bearer TA_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ta_id": "ta_ta_bob",
    "preferred_skill": "Python"
  }'
```

### Using Python requests

```python
import requests

BASE_URL = "http://localhost:8000"

# Student request
response = requests.post(f"{BASE_URL}/student/request", json={
    "name": "Alice Johnson",
    "severity": 4,
    "skill_set": "Python",
    "problem_description": "Need help with recursion"
})
print(response.json())

# Staff login
auth = requests.post(f"{BASE_URL}/auth/login", json={
    "username": "admin",
    "password": "admin123"
})
token = auth.json()["access_token"]

# Process triage
headers = {"Authorization": f"Bearer {token}"}
triage = requests.get(f"{BASE_URL}/staff/triage", headers=headers)
print(triage.json())
```

## 📊 Data Models

### Student
```json
{
  "id": "student_20260302143000",
  "name": "Alice Johnson",
  "severity": 4,
  "skill_set": "Python",
  "problem_description": "Debugging recursive function",
  "arrival_time": "2026-03-02T14:30:00",
  "ticket_number": 1,
  "queue_type": "skill_set",
  "assigned_ta_id": null
}
```

### TA
```json
{
  "id": "ta_001",
  "name": "Bob Smith",
  "skills": ["Python", "Java", "C++"],
  "current_student_id": "student_001",
  "is_available": false,
  "students_helped": 5,
  "average_wait_time": 15.3
}
```

## 🎯 Workflow Example

1. **Student submits help request** → Enters arrival queue
2. **Staff runs triage** → Student moves to Python skill queue
3. **TA logs in and claims student** → Automatic assignment based on priority
4. **TA helps student and marks complete** → TA becomes available again

## ⚙️ Configuration

Edit `config.py` or use environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | (change!) | JWT signing key |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 60 | Token expiration time |
| `ALLOWED_ORIGINS` | localhost | CORS allowed origins |
| `MAX_SEVERITY` | 5 | Maximum severity level |

## 🔧 Development

### PEP 8 Compliance
Code follows PEP 8 styling with full type hints:
```python
def add_student(self, name: str, severity: int, skill_set: str, 
                problem_description: str) -> Student:
    """Add a student to the arrival queue"""
    ...
```

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests (if test suite exists)
pytest tests/
```

### Hot Reload Development
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📦 Dependencies

- **FastAPI** - Modern async web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **python-jose** - JWT implementation
- **passlib[bcrypt]** - Password hashing
- **python-multipart** - Form data support

## 🚀 Production Deployment

**Security Checklist:**
- [ ] Change `SECRET_KEY` in production
- [ ] Use environment variables for secrets
- [ ] Change default admin password
- [ ] Configure proper CORS origins
- [ ] Enable HTTPS/TLS
- [ ] Set up proper logging
- [ ] Use a production ASGI server (Gunicorn + Uvicorn workers)

**Example production command:**
```bash
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

## 🔄 Differences from C++ Version

| Feature | C++ | Python FastAPI |
|---------|-----|----------------|
| **Authentication** | None | JWT with bcrypt |
| **API Protocol** | CLI Menu | RESTful HTTP/JSON |
| **Concurrency** | Single-threaded | Async/await support |
| **Storage** | In-memory | In-memory (DB-ready) |
| **Security** | N/A | CORS, RBAC, encryption |

## 🛣️ Future Enhancements

- [ ] PostgreSQL/SQLAlchemy integration
- [ ] WebSocket support for real-time updates
- [ ] Rate limiting and API throttling
- [ ] Comprehensive test suite
- [ ] Docker containerization
- [ ] Redis caching layer
- [ ] Prometheus metrics export
- [ ] Student notification system

## 📝 License

Educational project - free to use and modify.

## 🤝 Integration with Frontend

This API is designed to work with HTML/JavaScript frontends. Example CORS configuration allows:
- `http://localhost:3000` (React/Next.js dev server)
- `http://localhost:8000` (Same-origin)

Configure additional origins in `config.py` → `ALLOWED_ORIGINS`

## 🐛 Troubleshooting

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
Add your frontend URL to `ALLOWED_ORIGINS` in `config.py`

---

**Built with ❤️ and Python** | [FastAPI Documentation](https://fastapi.tiangolo.com/)
