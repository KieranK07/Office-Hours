"""
FastAPI Main Application - Office Hours Triage System
Secure RESTful API with JWT authentication and CORS support
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import timedelta
from typing import Optional

from config import settings
from models import User, UserRole
from schemas import (
    StudentRequest, TARequest, TAClaimRequest, CompleteStudentRequest,
    LoginRequest, TokenResponse, MessageResponse, TriageResponse,
    SystemStatsResponse, StudentResponse, TAResponse,
    StaffCreateUserRequest, UserSummaryResponse,
    StudentLineStatusResponse, TAUpcomingStudentsResponse
)
from auth import (
    user_database, create_access_token, get_current_user, require_role
)
from service import office_hours_service


# ============================================================================
# FastAPI Application Setup
# ============================================================================

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc"
)


# ============================================================================
# CORS Middleware Configuration
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)


# ============================================================================
# Dependency Injection
# ============================================================================


# Use get_current_user from auth module as the authenticated user dependency
async def get_authenticated_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current authenticated user"""
    return current_user


def get_ta_id_for_username(username: str) -> str:
    """Build deterministic TA ID from username"""
    return f"ta_{username}"


# ============================================================================
# Authentication Endpoints
# ============================================================================

@app.post("/auth/login", response_model=TokenResponse, tags=["Authentication"])
async def login(credentials: LoginRequest):
    """
    Authenticate user and issue JWT token
    
    - **username**: User's username
    - **password**: User's password
    
    Returns JWT access token for API access
    """
    user = user_database.authenticate_user(credentials.username, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value}
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        role=user.role,
        username=user.username
    )


@app.get("/auth/me", response_model=dict, tags=["Authentication"])
async def get_current_user_info(current_user: User = Depends(get_authenticated_user)):
    """Get information about the currently authenticated user"""
    return {
        "username": current_user.username,
        "role": current_user.role,
        "full_name": current_user.full_name
    }


# ============================================================================
# Staff Portal Endpoints
# ============================================================================

@app.post("/portal/staff/users", response_model=UserSummaryResponse, tags=["Staff Portal"])
async def staff_create_user(
    request: StaffCreateUserRequest,
    current_user: User = Depends(get_authenticated_user)
):
    """Staff portal: create student/TA/staff user accounts"""
    if current_user.role != UserRole.STAFF:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff members can create users"
        )

    if request.role == UserRole.TA and (not request.ta_skills or len(request.ta_skills) == 0):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ta_skills is required when creating a TA account"
        )

    try:
        created_user = user_database.add_user(
            username=request.username,
            password=request.password,
            role=request.role,
            full_name=request.full_name
        )

        if request.role == UserRole.TA:
            ta_id = get_ta_id_for_username(request.username)
            if not office_hours_service.get_ta(ta_id):
                office_hours_service.add_ta(
                    ta_id=ta_id,
                    name=request.full_name or request.username,
                    skills=request.ta_skills or []
                )

        return UserSummaryResponse(
            username=created_user.username,
            role=created_user.role,
            full_name=created_user.full_name,
            disabled=created_user.disabled
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.get("/portal/staff/users", response_model=list[UserSummaryResponse], tags=["Staff Portal"])
async def staff_list_users(current_user: User = Depends(get_authenticated_user)):
    """Staff portal: list all user accounts"""
    if current_user.role != UserRole.STAFF:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff members can view users"
        )

    users = user_database.get_all_users().values()
    return [
        UserSummaryResponse(
            username=user.username,
            role=user.role,
            full_name=user.full_name,
            disabled=user.disabled
        )
        for user in users
    ]


@app.post("/portal/staff/students", response_model=StudentResponse, tags=["Staff Portal"])
async def staff_add_student(
    request: StudentRequest,
    current_user: User = Depends(get_authenticated_user)
):
    """Staff portal: add a student directly into the queue"""
    if current_user.role != UserRole.STAFF:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff members can add students"
        )

    student = office_hours_service.add_student(
        name=request.name,
        severity=request.severity,
        skill_set=request.skill_set,
        problem_description=request.problem_description
    )
    return office_hours_service._student_to_response(student)


# ============================================================================
# Student Endpoints
# ============================================================================

@app.post("/student/request", response_model=StudentResponse, tags=["Students"])
async def student_request_help(request: StudentRequest):
    """
    **Public Endpoint** - Students join the arrival queue
    
    - **name**: Student's name
    - **severity**: Problem severity (1=low, 5=critical)
    - **skill_set**: Required skill (e.g., Python, Java, C++)
    - **problem_description**: Description of the issue
    
    Returns student information with ticket number
    """
    try:
        student = office_hours_service.add_student(
            name=request.name,
            severity=request.severity,
            skill_set=request.skill_set,
            problem_description=request.problem_description
        )
        
        return office_hours_service._student_to_response(student)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to add student: {str(e)}"
        )


@app.get("/student/{student_id}", response_model=StudentResponse, tags=["Students"])
async def get_student_status(student_id: str):
    """
    **Public Endpoint** - Check student status by ID
    
    Returns current queue position and wait time
    """
    student = office_hours_service.get_student(student_id)
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    return office_hours_service._student_to_response(student)


@app.get("/portal/student/line/{student_id}", response_model=StudentLineStatusResponse, tags=["Student Portal"])
async def student_line_status(student_id: str):
    """Student portal: live-friendly line status (poll this endpoint for real-time updates)"""
    student = office_hours_service.get_student(student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    students_ahead = office_hours_service.get_students_ahead(student_id)
    return StudentLineStatusResponse(
        student_id=student.id,
        student_name=student.name,
        queue_type=student.queue_type,
        students_ahead_count=len(students_ahead),
        students_ahead=[ahead_student.name for ahead_student in students_ahead],
        assigned_ta_id=student.assigned_ta_id
    )


# ============================================================================
# Staff Endpoints (Triage Operations)
# ============================================================================

@app.get("/staff/triage", response_model=TriageResponse, tags=["Staff"])
async def staff_triage_queue(current_user: User = Depends(get_authenticated_user)):
    """
    **Staff Only** - Process arrival queue and assign students to skill queues
    
    Moves students from arrival queue → skill-set queues → available TAs
    
    Requires: STAFF role
    """
    if current_user.role != UserRole.STAFF:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff members can perform triage"
        )
    
    try:
        students_moved = office_hours_service.triage_arrival_queue()
        students_assigned = office_hours_service.assign_students_to_tas()
        
        return TriageResponse(
            students_moved=students_moved,
            students_assigned=students_assigned,
            message=f"Triage complete: {students_moved} moved to skill queues, {students_assigned} assigned to TAs"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Triage operation failed: {str(e)}"
        )


@app.post("/staff/ta", response_model=TAResponse, tags=["Staff"])
async def staff_add_ta(
    request: TARequest,
    current_user: User = Depends(get_authenticated_user)
):
    """
    **Staff Only** - Add a new TA to the system
    
    Creates both the TA entity and their authentication credentials
    
    Requires: STAFF role
    """
    if current_user.role != UserRole.STAFF:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff members can add TAs"
        )
    
    try:
        # Create user account for the TA
        user_database.add_user(
            username=request.username,
            password=request.password,
            role=UserRole.TA,
            full_name=request.name
        )
        
        # Create TA entity
        ta_id = f"ta_{request.username}"
        ta = office_hours_service.add_ta(
            ta_id=ta_id,
            name=request.name,
            skills=request.skills
        )
        
        return office_hours_service._ta_to_response(ta)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add TA: {str(e)}"
        )


# ============================================================================
# TA Endpoints
# ============================================================================

@app.post("/ta/claim", response_model=StudentResponse, tags=["TAs"])
async def ta_claim_student(
    request: TAClaimRequest,
    current_user: User = Depends(get_authenticated_user)
):
    """
    **TA Only** - Claim the highest priority student matching TA's skills
    
    - **ta_id**: TA identifier
    - **preferred_skill**: Optional skill preference
    
    Returns the claimed student or error if none available
    
    Requires: TA role
    """
    if current_user.role != UserRole.TA:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only TAs can claim students"
        )
    
    student = office_hours_service.ta_claim_student(
        ta_id=request.ta_id,
        preferred_skill=request.preferred_skill
    )
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No students available matching your skills"
        )
    
    return office_hours_service._student_to_response(student)


@app.post("/ta/complete", response_model=MessageResponse, tags=["TAs"])
async def ta_complete_student(
    request: CompleteStudentRequest,
    current_user: User = Depends(get_authenticated_user)
):
    """
    **TA Only** - Mark a student session as complete
    
    - **ta_id**: TA identifier
    - **student_id**: Student identifier
    
    Frees up the TA for the next student
    
    Requires: TA or STAFF role
    """
    if current_user.role not in [UserRole.TA, UserRole.STAFF]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only TAs and staff can complete student sessions"
        )
    
    success = office_hours_service.complete_student_session(
        ta_id=request.ta_id,
        student_id=request.student_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to complete student session. Verify TA and student IDs."
        )
    
    return MessageResponse(
        message="Student session completed successfully",
        success=True
    )


@app.get("/portal/ta/upcoming", response_model=TAUpcomingStudentsResponse, tags=["TA Portal"])
async def ta_portal_upcoming_students(current_user: User = Depends(get_authenticated_user)):
    """TA portal: see current assignment and upcoming students matching TA skills"""
    if current_user.role != UserRole.TA:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only TAs can access this portal"
        )

    ta_id = get_ta_id_for_username(current_user.username)
    ta = office_hours_service.get_ta(ta_id)

    if not ta:
        ta = office_hours_service.add_ta(
            ta_id=ta_id,
            name=current_user.full_name or current_user.username,
            skills=[]
        )

    current_student_name = None
    if ta.current_student_id:
        current_student = office_hours_service.get_student(ta.current_student_id)
        current_student_name = current_student.name if current_student else None

    upcoming_students = office_hours_service.get_ta_upcoming_students(ta_id)

    return TAUpcomingStudentsResponse(
        ta_id=ta.id,
        ta_name=ta.name,
        current_student_id=ta.current_student_id,
        current_student_name=current_student_name,
        upcoming_students=[office_hours_service._student_to_response(student) for student in upcoming_students]
    )


@app.get("/ta/all", response_model=list[TAResponse], tags=["TAs"])
async def get_all_tas(current_user: User = Depends(get_authenticated_user)):
    """
    **Authenticated** - Get all TAs and their status
    
    Returns list of all TAs with availability and statistics
    """
    tas = office_hours_service.get_all_tas()
    return [office_hours_service._ta_to_response(ta) for ta in tas]


# ============================================================================
# Statistics Endpoints
# ============================================================================

@app.get("/stats", response_model=SystemStatsResponse, tags=["Statistics"])
async def get_system_statistics():
    """
    **Public Endpoint** - Get comprehensive system statistics
    
    Returns:
    - Queue sizes and contents
    - TA availability
    - Average wait times
    - Total students processed
    """
    return office_hours_service.get_system_statistics()


# ============================================================================
# Health Check
# ============================================================================

@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Office Hours Triage API",
        "version": settings.API_VERSION
    }


@app.get("/", tags=["System"])
async def root():
    """Root endpoint with API information"""
    return {
        "service": settings.API_TITLE,
        "version": settings.API_VERSION,
        "docs": "/docs",
        "health": "/health",
        "description": settings.API_DESCRIPTION
    }


# ============================================================================
# Exception Handlers
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler for unexpected errors"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Internal server error occurred",
            "detail": str(exc) if settings.API_VERSION != "production" else None
        }
    )


# ============================================================================
# Startup/Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    print(f"🚀 {settings.API_TITLE} v{settings.API_VERSION} starting...")
    print(f"📚 Documentation available at: http://localhost:8000/docs")
    print(f"🔐 Default staff credentials: username=admin, password=admin123")
    print(f"🔐 Default TA credentials: username=ta_demo, password=ta123456")
    print(f"🔐 Default student credentials: username=student_demo, password=student123")

    default_ta_id = get_ta_id_for_username("ta_demo")
    if not office_hours_service.get_ta(default_ta_id):
        office_hours_service.add_ta(
            ta_id=default_ta_id,
            name="Demo Teaching Assistant",
            skills=["Python", "C++", "Data Structures"]
        )


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print(f"👋 {settings.API_TITLE} shutting down...")


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
