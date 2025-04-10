from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User, UserProfile
from ..schemas.profile import ProfileUpdate, ProfileResponse

router = APIRouter(
    prefix="/profile",
    tags=["Profile"],
    responses={401: {"description": "Unauthorized"}},
)


@router.put("/update", response_model=ProfileResponse)
async def update_profile(
    profile_data: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update user profile information"""
    # Find the user profile or create it if it doesn't exist
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()

    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)

    # Update user info
    if profile_data.first_name:
        current_user.first_name = profile_data.first_name

    if profile_data.last_name:
        current_user.last_name = profile_data.last_name

    if profile_data.phone:
        current_user.phone = profile_data.phone

    # Update profile fields if provided
    for field in ["bio", "skills", "zip", "website", "linkedin", "github", "twitter"]:
        if hasattr(profile_data, field) and getattr(profile_data, field) is not None:
            setattr(profile, field, getattr(profile_data, field))

    # Mark profile as completed if we have the minimum required fields
    if all([current_user.first_name, current_user.last_name, profile.bio, profile.skills]):
        current_user.profile_completed = True

    db.commit()

    return ProfileResponse(
        message="Profile updated successfully",
        success=True,
        user_id=str(current_user.id),
    )