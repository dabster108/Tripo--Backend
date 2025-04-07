from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .routes import auth, health
from .core.logging import logger
from .core.database import Base, engine
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for Tripo with Integrated Chatbot",
    version="1.0.0",
    openapi_tags=[  # Explicit tags definition
        {
            "name": "Chatbot",
            "description": "AI-powered map and navigation assistance",
        },
        {
            "name": "Authentication",
            "description": "User registration and login endpoints",
        }
    ]
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
Base.metadata.create_all(bind=engine)

@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Tripo API Service - See /docs for API documentation"}

# Include routers with explicit prefix configuration
from app.routers.chatbot.endpoints import router as chatbot_router

app.include_router(
    chatbot_router,
    prefix=f"{settings.API_V1_STR}/chatbot",  # Fixed combined prefix
    tags=["Chatbot"]
)

app.include_router(auth.router, prefix=settings.API_V1_STR, tags=["Authentication"])
app.include_router(health.router, prefix=settings.API_V1_STR, tags=["Health"])

# Event handlers with error logging
@app.on_event("startup")
async def startup_event():
    try:
        logger.info(f"Starting {settings.APP_NAME}")
        logger.info(f"Environment: {settings.ENVIRONMENT}")
        logger.info(f"Allowed Origins: {settings.ALLOWED_ORIGINS}")
        logger.info(f"Chatbot Model: {settings.GROQ_MODEL}")
    except Exception as e:
        logger.error(f"Startup error: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Gracefully shutting down Tripo API")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=settings.ENVIRONMENT == "development",
        log_level="debug" if settings.ENVIRONMENT == "development" else "info"
    )