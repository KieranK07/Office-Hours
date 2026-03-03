"""
Request and Response schemas for API endpoints
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from models import UserRole, QueueType


# ============================================================================
# Request Schemas
# ============================================================================

class StudentRequest(BaseModel):
    """Request to add a student to the queue"""
    name: str = Field(..., min_length=1, max_length=100)
    severity: int = Field(..., ge=1, le=5)
    skill_set: str = Field(..., min_length=1)
    problem_description: str = Field(..., min_length=1, max_length=500)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Alice Johnson",
                "severity": 4,
                "skill_set": "Python",
                "problem_description": "Need help with recursion and base cases"
            }
        }


class TARequest(BaseModel):
    """Request to add a TA"""
    name: str = Field(..., min_length=1, max_length=100)
    skills: list[str] = Field(..., min_length=1)
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Bob Smith",
                "skills": ["Python", "Java", "C++"],
                "username": "ta_bob",
                "password": "SecurePass123!"
            }
        }


class TAClaimRequest(BaseModel):
    """Request for TA to claim a student"""
    ta_id: str = Field(..., description="TA identifier")
    preferred_skill: Optional[str] = Field(None, description="Preferred skill set to help with")
    
    class Config:
        json_schema_extra = {
            "example": {
                "ta_id": "ta_001",
                "preferred_skill": "Python"
            }
        }


class CompleteStudentRequest(BaseModel):
    """Request to mark a student as helped"""
    ta_id: str = Field(..., description="TA identifier")
    student_id: str = Field(..., description="Student identifier")
    
    class Config:
        json_schema_extra = {
            "example": {
                "ta_id": "ta_001",
                "student_id": "student_123"
            }
        }


class LoginRequest(BaseModel):
    """Login credentials"""
    username: str
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "ta_bob",
                "password": "SecurePass123!"
            }
        }


class StaffCreateUserRequest(BaseModel):
    """Staff request to create a user account"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    role: UserRole
    full_name: Optional[str] = Field(None, max_length=100)
    ta_skills: Optional[list[str]] = Field(
        default=None,
        description="Required when creating a TA user"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "username": "ta_amy",
                "password": "SecurePass123!",
                "role": "ta",
                "full_name": "Amy Chen",
                "ta_skills": ["Python", "Data Structures"]
            }
        }


# ============================================================================
# Response Schemas
# ============================================================================

class StudentResponse(BaseModel):
    """Response with student information"""
    id: str
    name: str
    severity: int
    skill_set: str
    problem_description: str
    arrival_time: datetime
    ticket_number: int
    queue_type: QueueType
    assigned_ta_id: Optional[str] = None
    wait_time_minutes: Optional[float] = None


class TAResponse(BaseModel):
    """Response with TA information"""
    id: str
    name: str
    skills: list[str]
    current_student_id: Optional[str] = None
    current_student_name: Optional[str] = None
    is_available: bool
    students_helped: int
    average_wait_time: float


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    role: UserRole
    username: str


class TriageResponse(BaseModel):
    """Response from triage operation"""
    students_moved: int
    students_assigned: int
    message: str


class QueueStatsResponse(BaseModel):
    """Statistics for a specific queue"""
    queue_type: str
    size: int
    students: list[StudentResponse]


class SystemStatsResponse(BaseModel):
    """Overall system statistics"""
    current_time: datetime
    arrival_queue_size: int
    skill_queues: dict[str, int]
    total_students_in_system: int
    total_students_processed: int
    available_tas: int
    busy_tas: int
    average_wait_time_minutes: float
    queue_details: list[QueueStatsResponse]


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    success: bool = True
    data: Optional[dict] = None


class UserSummaryResponse(BaseModel):
    """Response with non-sensitive user account details"""
    username: str
    role: UserRole
    full_name: Optional[str] = None
    disabled: bool


class StudentLineStatusResponse(BaseModel):
    """Live-friendly queue status for a student"""
    student_id: str
    student_name: str
    queue_type: QueueType
    students_ahead_count: int
    students_ahead: list[str]
    assigned_ta_id: Optional[str] = None


class TAUpcomingStudentsResponse(BaseModel):
    """TA portal response with assigned and upcoming students"""
    ta_id: str
    ta_name: str
    current_student_id: Optional[str] = None
    current_student_name: Optional[str] = None
    upcoming_students: list[StudentResponse]
