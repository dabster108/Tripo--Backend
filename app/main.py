from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, EmailStr, Field, validator
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .core.config import settings
from .core.database import Base, engine
from .models import User
from typing import Optional
import re
from dotenv import load_dotenv
import os
from .routes import auth, health
from .core.logging import logger
from .core import database

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for Lanceraa freelancing platform",
    version="1.0.0"
)

# Alternative solution for main.py
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Password hashing
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # You can adjust this value (10-14 is common)
)

# Create database tables (comment out if using Alembic)
Base.metadata.create_all(bind=engine)

# Moving all schemas to proper files in the schemas directory
# Removed the UserCreate and UserResponse models from here

@app.get("/")
async def root():
    return {"message": "Welcome to Lanceraa API", "docs_url": "/docs"}

# Include routers with API prefix
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(health.router, prefix=settings.API_V1_STR)

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Starting Lanceraa API")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Lanceraa API")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)