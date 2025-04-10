import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base

class User(Base):
    """Core user identity and authentication"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    # Remove this line
    # country = Column(String(100), nullable=True)
    phone = Column(String(20), unique=True, index=True, nullable=True)
    
    # Status flags
    is_active = Column(Boolean, default=False, index=True)
    is_verified = Column(Boolean, default=False, index=True)
    profile_completed = Column(Boolean, default=False, index=True)
    
    # Verification system
    verification_code = Column(String(6), nullable=True)
    verification_code_expires = Column(DateTime, nullable=True)
    
    # Password reset system
    reset_password_otp = Column(String(6), nullable=True)
    reset_password_otp_expires = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), index=True)
    updated_at = Column(DateTime, onupdate=func.now(), index=True)
    last_login = Column(DateTime, nullable=True, index=True)
    
    # Role management
    role = Column(String(20), default='user', index=True)
    
    # Relationship to profile
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
class UserProfile(Base):
    """Simplified user profile with only country information"""
    __tablename__ = "user_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    
    
    # Profile image kept (assuming you still want this)
    profile_image = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), index=True)
    updated_at = Column(DateTime, onupdate=func.now(), index=True)
    
    # Relationship to user
    user = relationship("User", back_populates="profile")

    reset_password_otp = Column(String(6), nullable=True)
    reset_password_otp_expires = Column(DateTime, nullable=True)