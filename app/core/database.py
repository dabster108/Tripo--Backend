from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from .config import settings

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")


if not DATABASE_URL:
    raise ValueError("No DATABASE_URL set in environment variables")

# Check if using SQLite and add appropriate connection arguments
connect_args = {}
if settings.DATABASE_URL.startswith('sqlite'):
    connect_args = {"check_same_thread": False}

# Create engine with optimized settings for Neon
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,  # Only enable for debugging
    pool_pre_ping=True,
    pool_size=10,  # Increased for better performance
    max_overflow=20,  # Increased for peak loads
    pool_timeout=30,
    pool_recycle=1800,  # Recycle connections every 30 minutes
    connect_args=connect_args
)

# Create session with optimized settings
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # Better performance for read-heavy operations
)

Base = declarative_base()

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()