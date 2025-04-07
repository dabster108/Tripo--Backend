from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.schemas.chatbot.chat import UserInput
from app.core.groq_integration import GroqService
from typing import Optional

router = APIRouter(
    prefix="/chatbot",
    tags=["Chatbot"],
    responses={404: {"description": "Not found"}}
)

# Initialize service
try:
    groq_service = GroqService()
    print("✅ GroqService initialized successfully")  # Debug print
except Exception as e:
    print(f"❌ GroqService init failed: {e}")  # Debug print
    groq_service = None

@router.post(
    "/response",
    response_model=dict,
    summary="Get AI Chatbot Response",
    description="""Get responses for map and navigation questions.
    **Example Request:**
    ```json
    {
        "role": "user",
        "message": "How do I get to the nearest hospital?"
    }
    ```""",
    response_description="AI-generated response",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {"response": "Turn left on Main Street, then right after 200m 🏥"}
                }
            }
        },
        503: {
            "description": "Service Unavailable",
            "content": {
                "application/json": {
                    "example": {"detail": "Chatbot service unavailable"}
                }
            }
        }
    }
)
async def get_chat_response(user_input: UserInput):
    """
    Processes user queries and returns AI-generated responses.
    
    - **role**: Must be 'user'
    - **message**: Your location-related question
    """
    if not groq_service:
        raise HTTPException(
            status_code=503,
            detail="Chatbot service unavailable (check server logs)"
        )
    
    try:
        response = groq_service.get_response(user_input)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))