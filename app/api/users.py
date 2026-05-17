"""API routes for user profile and resume management"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import os

from app.database import get_db
from app.models import UserProfile
from app.schemas import UserProfileCreate, UserProfileUpdate, UserProfileResponse, ResumeUploadResponse

router = APIRouter(prefix="/api/users", tags=["users"])

# Allowed file extensions
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


@router.post("/profile", response_model=UserProfileResponse)
async def create_user_profile(
    profile: UserProfileCreate,
    db: AsyncSession = Depends(get_db)
) -> UserProfileResponse:
    """Create a new user profile"""
    # Check if user already exists
    existing = await db.execute(
        select(UserProfile).where(UserProfile.user_id == profile.user_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User already exists")
    
    db_user = UserProfile(**profile.model_dump())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return UserProfileResponse.model_validate(db_user)


@router.get("/profile/{user_id}", response_model=UserProfileResponse)
async def get_user_profile(
    user_id: str,
    db: AsyncSession = Depends(get_db)
) -> UserProfileResponse:
    """Get user profile by ID"""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserProfileResponse.model_validate(user)


@router.put("/profile/{user_id}", response_model=UserProfileResponse)
async def update_user_profile(
    user_id: str,
    profile: UserProfileUpdate,
    db: AsyncSession = Depends(get_db)
) -> UserProfileResponse:
    """Update user profile"""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update fields
    update_data = profile.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    
    user.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(user)
    return UserProfileResponse.model_validate(user)


@router.post("/profile/{user_id}/resume", response_model=ResumeUploadResponse)
async def upload_resume(
    user_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
) -> ResumeUploadResponse:
    """Upload resume for user"""
    # Validate file
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 5MB)")
    
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_ext}")
    
    # Get user
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Read file content
    content = await file.read()
    
    # Simple text extraction (would use pdf2image or similar in production)
    resume_text = content.decode("utf-8", errors="ignore")
    
    # Update user profile
    user.resume_text = resume_text
    user.resume_file_name = file.filename
    user.resume_uploaded_at = datetime.utcnow()
    user.updated_at = datetime.utcnow()
    
    await db.commit()
    
    return ResumeUploadResponse(
        file_name=file.filename,
        uploaded_at=user.resume_uploaded_at,
        text_extracted=len(resume_text) > 0,
        embedding_created=False  # Will be created by background task
    )


@router.delete("/profile/{user_id}")
async def delete_user_profile(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete user profile"""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await db.delete(user)
    await db.commit()
    return {"message": "User profile deleted"}
