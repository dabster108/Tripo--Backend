from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random
import string

from ..core.database import get_db
from ..core.security import get_password_hash
from ..models.user import User
from ..schemas.password import ForgotPasswordRequest, ResetPasswordRequest, StepCompletionResponse
from ..core.security import get_password_hash
from ..models.user import User

from ..core.database import get_db
from ..core.security import verify_password, create_access_token, get_password_hash, get_current_user
from ..core.config import settings
from ..models.user import User, UserProfile
from ..schemas.auth import LoginResponse, TokenData
from ..schemas.user import (
    UserResponseData, 
    UserResponse, 
    UserCreate, 
    InitialSignup, 
    VerifyEmail, 
    StepCompletionResponse,
    ResendVerification,
    EmailCheck,
    EmailExists
)


# reset password added 

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={401: {"description": "Unauthorized"}}
)

@router.post(
    "/signup/initial", 
    response_model=StepCompletionResponse,
    status_code=status.HTTP_201_CREATED,
    description="Step 1: Initial signup with email, name, and password"
)
async def initial_signup(user_data: InitialSignup, db: Session = Depends(get_db)):
    """First step: Create an account with email, name, and password"""
    try:
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Extract username from email
        email_parts = user_data.email.split('@')
        username = email_parts[0]
        
        # Check if username already exists
        username_count = 0
        base_username = username
        
        while db.query(User).filter(User.username == username).first():
            username_count += 1
            username = f"{base_username}{username_count}"
            
        # Create new user with the provided information
        user = User(
            email=user_data.email,
            username=username,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            hashed_password=get_password_hash(user_data.password),
            is_active=False,  # Will be true after OTP verification
            is_verified=False,
            profile_completed=False
        )
        
        # Generate verification code
        verification_code = ''.join(random.choices(string.digits, k=6))
        user.verification_code = verification_code
        user.verification_code_expires = datetime.utcnow() + timedelta(minutes=30)
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Send verification email/SMS (mock implementation for now)
        print(f"VERIFICATION CODE for {user.email}: {verification_code}")
        
        return StepCompletionResponse(
            message="Account created. Please verify your email.",
            success=True,
            next_step="verify_email",
            user_id=str(user.id)
        )

    except Exception as e:
        db.rollback()
        print(f"Error in initial_signup: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )
    
@router.post("/verify-email", response_model=StepCompletionResponse)
async def verify_email(verification: VerifyEmail, db: Session = Depends(get_db)):
    """Verify user's email with OTP code"""
    user = db.query(User).filter(User.id == verification.user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
        
    if user.verification_code != verification.verification_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code"
        )
        
    if user.verification_code_expires and user.verification_code_expires < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code expired. Please request a new code.",
            headers={"X-Error-Code": "EXPIRED_CODE"}
        )
        
    # Mark user as active and clear verification code
    user.is_active = True
    user.verification_code = None
    user.verification_code_expires = None
    
    # Create an empty profile record if one doesn't exist yet
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if not profile:
        profile = UserProfile(user_id=user.id)
        db.add(profile)
    
    db.commit()
    
    return StepCompletionResponse(
        message="Email verified successfully.",
        success=True,
        next_step="complete_profile",
        user_id=str(user.id)
    )

@router.post("/login", response_model=LoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    try:
        print(f"Attempting login for username: {form_data.username}")
        
        # Try to find user by username or email
        user = db.query(User).filter(
            (User.email == form_data.username) | 
            (User.username == form_data.username)
        ).first()
        
        # If phone is provided, also check that
        if not user and form_data.username.replace('+', '').isdigit():
            user = db.query(User).filter(User.phone == form_data.username).first()
        
        if not user:
            print(f"User not found: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        if not verify_password(form_data.password, user.hashed_password):
            print(f"Password verification failed for: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Update last login time
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Create access token (without referencing role which doesn't exist in your model)
        access_token = create_access_token(
            data={
                "sub": user.username,
                "email": user.email
            }
        )
        
        # Create full name from first and last name if both exist
        full_name = None
        if user.first_name or user.last_name:
            first_name = user.first_name or ""
            last_name = user.last_name or ""
            full_name = f"{first_name} {last_name}".strip() or None
        
        print(f"Login successful for user: {user.username}")
        
        # Return user information based on your actual model
        return LoginResponse(
    message="Login successful",
    token=TokenData(
        access_token=access_token,
        token_type="bearer",
        username=user.username
    ),
    user={
        "id": str(user.id),
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "full_name": full_name,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "profile_completed": user.profile_completed,
        "phone": user.phone
        # REMOVED country from here since it's in UserProfile
    }
)
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Login error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login"
        )

@router.get("/me", response_model=dict)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get profile data
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    
    user_data = {
        "id": str(current_user.id),
        "username": current_user.username,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "phone": current_user.phone,
        "is_verified": current_user.is_verified,
        "profile_completed": current_user.profile_completed,
    }
    
    # Add profile data if available
    if profile:
        user_data["profile"] = {
            "bio": profile.bio,
            "skills": profile.skills,
            "years_experience": profile.years_experience,
            "education": profile.education,
            "address": {
                "street": profile.street,
                "city": profile.city,
                "state": profile.state,
                "country": profile.country,
                "zip": profile.zip,
                "full_address": profile.full_address
            } if profile.street else None,
            "social": {
                "website": profile.website,
                "linkedin": profile.linkedin,
                "github": profile.github
            },
            "languages": profile.languages,
            "availability": profile.availability
        }
    
    return {"user": user_data}

@router.post("/resend-verification", response_model=StepCompletionResponse)
async def resend_verification(resend_data: ResendVerification, db: Session = Depends(get_db)):
    """Resend verification code to the user's email"""
    user = db.query(User).filter(User.id == resend_data.user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if user is already verified
    if user.is_active:
        return StepCompletionResponse(
            message="User is already verified.",
            success=True,
            next_step="complete_profile",
            user_id=str(user.id)
        )
    
    # Generate new verification code
    verification_code = ''.join(random.choices(string.digits, k=6))
    user.verification_code = verification_code
    user.verification_code_expires = datetime.utcnow() + timedelta(minutes=30)
    
    db.commit()
    
    # Print the verification code to terminal (for development purposes)
    print("=" * 50)
    print(f"RESENT VERIFICATION CODE for {user.email}: {verification_code}")
    print("=" * 50)
    
    # In a real implementation, you would send an email here
    # send_email(user.email, "Your verification code", f"Your code is {verification_code}")
    
    return StepCompletionResponse(
        message="Verification code resent. Please check your email.",
        success=True,
        next_step="verify_email",
        user_id=str(user.id)
    )

@router.post("/check-email", response_model=EmailExists)
async def check_email_exists(data: EmailCheck, db: Session = Depends(get_db)):
    """Check if an email is already registered"""
    try:
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == data.email).first()
        
        if existing_user:
            return EmailExists(
                exists=True,
                message="Email is already registered. Please login instead."
            )
        
        return EmailExists(
            exists=False,
            message="Email is available for registration."
        )
    except Exception as e:
        print(f"Error in check_email_exists: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

# Generate OTP
def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

# Forgot password 
@router.post("/forgot-password", response_model=StepCompletionResponse)
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Request a password reset by providing the email address"""
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        # For security reasons, don't tell the client if the email exists or not
        return StepCompletionResponse(
            message="If your email is registered, you will receive a password reset link.",
            success=True,
            next_step="check_email",
            user_id=None
        )
    
    # Generate OTP and save it to the user record
    otp = generate_otp()
    user.reset_password_otp = otp
    user.reset_password_otp_expires = datetime.utcnow() + timedelta(minutes=30)
    db.commit()
    
    # Send OTP to user's email (for now, print to console)
    print(f"OTP for password reset: {otp}")
    # Uncomment the following line to send email using emailjs
    # send_reset_password_email(user.email, otp)
    
    return StepCompletionResponse(
        message="If your email is registered, you will receive a password reset link.",
        success=True,
        next_step="check_email",
        user_id=user.id
    )

# Reset password
@router.post("/reset-password", response_model=StepCompletionResponse)
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset the password using the OTP"""
    user = db.query(User).filter(User.email == request.email, User.reset_password_otp == request.otp).first()
    
    if not user or user.reset_password_otp_expires < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    
    if request.new_password != request.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    user.hashed_password = get_password_hash(request.new_password)
    user.reset_password_otp = None  # Clear the OTP after successful reset
    user.reset_password_otp_expires = None
    db.commit()
    
    return StepCompletionResponse(
        message="Password has been reset successfully. You can now log in with your new password.",
        success=True,
        next_step="login",
        user_id=user.id
    )