"""Pydantic schemas for request/response validation"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


# User Profile Schemas
class UserProfileCreate(BaseModel):
    """Create user profile"""
    user_id: str
    email: EmailStr
    full_name: str
    target_roles: Optional[List[str]] = []
    target_companies: Optional[List[str]] = []
    blacklist_companies: Optional[List[str]] = []
    min_salary: Optional[int] = None
    preferred_locations: Optional[List[str]] = []
    auto_apply_threshold: float = 0.75
    generate_cover_letters: bool = True
    use_custom_resume: bool = False


class UserProfileUpdate(BaseModel):
    """Update user profile"""
    full_name: Optional[str] = None
    target_roles: Optional[List[str]] = None
    target_companies: Optional[List[str]] = None
    blacklist_companies: Optional[List[str]] = None
    min_salary: Optional[int] = None
    preferred_locations: Optional[List[str]] = None
    auto_apply_threshold: Optional[float] = None
    generate_cover_letters: Optional[bool] = None
    use_custom_resume: Optional[bool] = None


class UserProfileResponse(BaseModel):
    """User profile response"""
    id: int
    user_id: str
    email: str
    full_name: str
    resume_file_name: Optional[str]
    resume_uploaded_at: Optional[datetime]
    target_roles: List[str]
    target_companies: List[str]
    blacklist_companies: List[str]
    min_salary: Optional[int]
    preferred_locations: List[str]
    auto_apply_threshold: float
    generate_cover_letters: bool
    use_custom_resume: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Job Posting Schemas
class JobPostingCreate(BaseModel):
    """Create job posting"""
    external_id: str
    title: str
    company: str
    description: str
    location: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    currency: str = "USD"
    job_type: Optional[str] = None
    source: str
    source_url: str
    posted_date: Optional[datetime] = None


class JobPostingResponse(BaseModel):
    """Job posting response"""
    id: int
    external_id: str
    title: str
    company: str
    description: str
    location: Optional[str]
    salary_min: Optional[int]
    salary_max: Optional[int]
    currency: str
    job_type: Optional[str]
    source: str
    source_url: str
    posted_date: Optional[datetime]
    scraped_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


# Job Match Schemas
class JobMatchResponse(BaseModel):
    """Job match response"""
    id: int
    user_id: int
    job_id: int
    match_score: float
    match_reasons: List[str]
    required_skills_match: Optional[float]
    preferred_skills_match: Optional[float]
    salary_match: Optional[float]
    location_match: Optional[float]
    user_status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Application Schemas
class ApplicationCreate(BaseModel):
    """Create application"""
    job_id: int
    application_method: str = "DIRECT"
    auto_applied: bool = False


class ApplicationResponse(BaseModel):
    """Application response"""
    id: int
    user_id: int
    job_id: int
    status: str
    application_method: str
    auto_applied: bool
    applied_date: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Resume Upload Schemas
class ResumeUploadResponse(BaseModel):
    """Resume upload response"""
    file_name: str
    uploaded_at: datetime
    text_extracted: bool
    embedding_created: bool


# AI Matching Request/Response
class MatchJobRequest(BaseModel):
    """Request to match user with job"""
    user_id: int
    job_id: int


class MatchJobResponse(BaseModel):
    """Job match result"""
    match_score: float
    match_reasons: List[str]
    cover_letter: Optional[str]
    should_apply: bool


# Bulk Operations
class BulkJobPostingCreate(BaseModel):
    """Bulk create job postings"""
    jobs: List[JobPostingCreate]


class BulkApplicationCreate(BaseModel):
    """Bulk create applications"""
    applications: List[ApplicationCreate]


# Stats & Analytics
class UserStatsResponse(BaseModel):
    """User statistics"""
    total_jobs_applied: int
    pending_interviews: int
    offers_received: int
    average_match_score: float
    total_matches_found: int
