from fastapi import APIRouter
from ..core.config import settings

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)

@router.get("")
async def health_check():
    """
    Health check endpoint to verify that the API is running
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "app_name": settings.APP_NAME
    }