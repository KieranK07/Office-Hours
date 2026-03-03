"""
Core data models for the Office Hours Triage System
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User roles for authentication"""
    STUDENT = "student"
    TA = "ta"
    STAFF = "staff"


class SkillSet(str, Enum):
    """Available skill sets for help requests"""
    CPP = "C++"
    PYTHON = "Python"
    JAVA = "Java"
    JAVASCRIPT = "JavaScript"
    DATA_STRUCTURES = "Data Structures"
    ALGORITHMS = "Algorithms"
    WEB_DEV = "Web Development"
    DATABASE = "Database"


class QueueType(str, Enum):
    """Queue types in the system"""
    ARRIVAL = "arrival"
    SKILL_SET = "skill_set"
    ASSIGNED = "assigned"


class Student(BaseModel):
    """Student model with validation"""
    id: str = Field(..., description="Unique student identifier")
    name: str = Field(..., min_length=1, max_length=100)
    severity: int = Field(..., ge=1, le=5, description="Problem severity (1=low, 5=high)")
    skill_set: str = Field(..., description="Required skill set for help")
    problem_description: str = Field(..., min_length=1, max_length=500)
    arrival_time: datetime = Field(default_factory=datetime.now)
    ticket_number: Optional[int] = None
    assigned_ta_id: Optional[str] = None
    queue_type: QueueType = Field(default=QueueType.ARRIVAL)
    
    @field_validator('skill_set')
    @classmethod
    def validate_skill_set(cls, v: str) -> str:
        """Normalize and validate skill set"""
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "student_001",
                "name": "Alice Johnson",
                "severity": 4,
                "skill_set": "Python",
                "problem_description": "Debugging recursive function causing stack overflow",
                "arrival_time": "2026-03-02T14:30:00",
                "ticket_number": 1
            }
        }


class TA(BaseModel):
    """Teaching Assistant model"""
    id: str = Field(..., description="Unique TA identifier")
    name: str = Field(..., min_length=1, max_length=100)
    skills: list[str] = Field(..., min_length=1, description="List of skill sets")
    current_student_id: Optional[str] = None
    is_available: bool = Field(default=True)
    students_helped: int = Field(default=0)
    total_wait_time_minutes: int = Field(default=0)
    
    def has_skill(self, skill: str) -> bool:
        """Check if TA has a specific skill"""
        return skill in self.skills
    
    def calculate_average_wait_time(self) -> float:
        """Calculate average wait time for students helped"""
        if self.students_helped == 0:
            return 0.0
        return self.total_wait_time_minutes / self.students_helped
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "ta_001",
                "name": "Bob Smith",
                "skills": ["Python", "Java", "Data Structures"],
                "current_student_id": None,
                "is_available": True,
                "students_helped": 5,
                "total_wait_time_minutes": 75
            }
        }


class User(BaseModel):
    """User model for authentication"""
    username: str = Field(..., min_length=3, max_length=50)
    role: UserRole
    hashed_password: str
    full_name: Optional[str] = None
    disabled: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "ta_bob",
                "role": "ta",
                "full_name": "Bob Smith",
                "disabled": False
            }
        }
