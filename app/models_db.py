"""SQLAlchemy ORM models for Job Automation Bot"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
import enum

from app.database import Base


class UserProfile(Base):
    """User profile with resume and preferences"""
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    
    # Resume data
    resume_text = Column(Text, nullable=True)  # Extracted text from PDF/DOCX
    resume_embedding = Column(Vector(384), nullable=True)  # Sentence transformer embedding
    resume_file_name = Column(String(255), nullable=True)
    resume_uploaded_at = Column(DateTime, nullable=True)
    
    # Job preferences
    target_roles = Column(JSON, default=list)  # ["Software Engineer", "Full Stack Developer"]
    target_companies = Column(JSON, default=list)  # ["Google", "Microsoft"]
    blacklist_companies = Column(JSON, default=list)  # ["Company1", "Company2"]
    min_salary = Column(Integer, nullable=True)  # USD
    preferred_locations = Column(JSON, default=list)  # ["New York", "Remote"]
    
    # LLM preferences
    auto_apply_threshold = Column(Float, default=0.75)  # Match score threshold for auto-apply
    generate_cover_letters = Column(Boolean, default=True)
    use_custom_resume = Column(Boolean, default=False)  # Use tailored resume for each application
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    applications = relationship("Application", back_populates="user")
    resume_variants = relationship("ResumeVariant", back_populates="user")


class JobPosting(Base):
    """Job postings scraped from various sources"""
    __tablename__ = "job_postings"

    id = Column(Integer, primary_key=True)
    external_id = Column(String(255), unique=True, nullable=False, index=True)  # e.g., "linkedin_12345"
    
    # Job details
    title = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    description_embedding = Column(Vector(384), nullable=True)  # For semantic search
    
    # Location & salary
    location = Column(String(255), nullable=True)
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    currency = Column(String(10), default="USD")
    job_type = Column(String(50), nullable=True)  # "Full-time", "Contract", etc.
    
    # Metadata
    source = Column(String(50), nullable=False, index=True)  # "linkedin", "indeed", "builtin"
    source_url = Column(String(1024), nullable=False)
    posted_date = Column(DateTime, nullable=True)
    
    # Timestamps
    scraped_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)  # Mark as inactive if job closed
    
    # Relationships
    matches = relationship("JobMatch", back_populates="job")
    applications = relationship("Application", back_populates="job")


class JobMatch(Base):
    """AI-scored job matches for users"""
    __tablename__ = "job_matches"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("job_postings.id"), nullable=False, index=True)
    
    # Match scoring
    match_score = Column(Float, nullable=False)  # 0.0 - 1.0
    match_reasons = Column(JSON, default=list)  # ["Skill match: Python", "Location: Remote"]
    required_skills_match = Column(Float, nullable=True)
    preferred_skills_match = Column(Float, nullable=True)
    salary_match = Column(Float, nullable=True)
    location_match = Column(Float, nullable=True)
    
    # Generated content
    cover_letter = Column(Text, nullable=True)
    tailored_resume_id = Column(Integer, ForeignKey("resume_variants.id"), nullable=True)
    
    # Status
    user_status = Column(String(50), default="NEW")  # "NEW", "INTERESTED", "REJECTED", "APPLIED"
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("UserProfile")
    job = relationship("JobPosting", back_populates="matches")
    tailored_resume = relationship("ResumeVariant")


class ResumeVariant(Base):
    """Customized resume variants for specific jobs"""
    __tablename__ = "resume_variants"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("job_postings.id"), nullable=True)  # Null if template
    
    # Resume content
    title = Column(String(255), nullable=False)  # e.g., "Tailored for Google SDE"
    content = Column(Text, nullable=False)  # Markdown or HTML formatted
    embedding = Column(Vector(384), nullable=True)
    
    # Metadata
    is_template = Column(Boolean, default=False)  # True for reusable templates
    format_type = Column(String(50), default="markdown")  # "markdown", "html", "pdf"
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("UserProfile", back_populates="resume_variants")


class Application(Base):
    """Track job applications submitted"""
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("job_postings.id"), nullable=False, index=True)
    
    # Application details
    status = Column(String(50), default="SUBMITTED")  # "SUBMITTED", "REVIEWED", "INTERVIEW", "REJECTED", "OFFER"
    application_method = Column(String(50), nullable=False)  # "DIRECT", "EMAIL", "LINKEDIN_MESSAGE"
    
    # What was sent
    resume_variant_id = Column(Integer, ForeignKey("resume_variants.id"), nullable=True)
    cover_letter_used = Column(Text, nullable=True)
    auto_applied = Column(Boolean, default=False)
    
    # Tracking
    application_url = Column(String(1024), nullable=True)
    confirmation_email = Column(String(1024), nullable=True)
    tracking_number = Column(String(255), nullable=True)
    
    # Communication
    recruiter_name = Column(String(255), nullable=True)
    recruiter_email = Column(String(255), nullable=True)
    last_message_date = Column(DateTime, nullable=True)
    last_message_subject = Column(String(255), nullable=True)
    
    # Timestamps
    applied_date = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("UserProfile", back_populates="applications")
    job = relationship("JobPosting", back_populates="applications")


class ScraperJob(Base):
    """Track scraper execution status"""
    __tablename__ = "scraper_jobs"

    id = Column(Integer, primary_key=True)
    source = Column(String(50), nullable=False, index=True)  # "linkedin", "indeed"
    status = Column(String(50), default="PENDING")  # "PENDING", "RUNNING", "COMPLETED", "FAILED"
    
    # Results
    jobs_scraped = Column(Integer, default=0)
    jobs_added = Column(Integer, default=0)
    jobs_updated = Column(Integer, default=0)
    errors = Column(JSON, default=list)
    error_message = Column(Text, nullable=True)
    
    # Timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    # Scheduling
    created_at = Column(DateTime, default=datetime.utcnow)
    next_scheduled = Column(DateTime, nullable=True)
