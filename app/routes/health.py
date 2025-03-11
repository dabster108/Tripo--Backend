from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import platform
import time
from ..core.config import settings
from ..core.database import get_db

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)

@router.get("")
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint to verify that the API is running
    """
    start_time = time.time()
    
    # Try to make a simple database query to check DB connectivity
    db_healthy = True
    try:
        # Just execute a simple query that doesn't fetch data
        db.execute("SELECT 1")
    except Exception:
        db_healthy = False
    
    response_time = time.time() - start_time
    
    return {
        "status": "healthy",
        "version": "1.0.0",
        "app_name": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "database_connected": db_healthy,
        "system_info": {
            "python_version": platform.python_version(),
            "platform": platform.platform()
        },
        "response_time_ms": round(response_time * 1000, 2)
    }