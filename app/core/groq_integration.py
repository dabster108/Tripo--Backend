import logging
import time  # Add this import
from typing import Dict, List
from groq import Groq, APIStatusError
from app.models.chatbot.conversation import Conversation
from app.core.config import settings
from app.schemas.chatbot.chat import UserInput
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class GroqService:
    SYSTEM_PROMPT = {
        "role": "system",
        "content": (
            "You're a helpful map and navigation assistant for Tripo. "
            "Provide concise answers (2 sentences max) with emojis when appropriate. "
            "For non-map questions, politely respond: "
            "'I specialize in location assistance. For other queries, please contact Tripo support.' 🗺️"
        )
    }

    def __init__(self):
        self._validate_config()
        self.client = Groq(
            api_key=settings.GROQ_API_KEY,
            timeout=10.0
        )
        self.model = settings.GROQ_MODEL
        self.max_retries = 3
        logger.info("GroqService initialized with model: %s", self.model)

    def _validate_config(self):
        """Validate required configuration"""
        if not settings.GROQ_API_KEY:
            logger.error("Groq API key missing in configuration")
            raise ValueError("Groq API key not configured in settings")
        
        if not settings.GROQ_MODEL:
            logger.warning("Using default Groq model")
            settings.GROQ_MODEL = "llama3-8b-8192"

    def _initialize_conversation(self, user_message: str) -> List[Dict[str, str]]:
        """Create conversation context with system prompt"""
        return [
            self.SYSTEM_PROMPT,
            {"role": "user", "content": user_message}
        ]

    def get_response(self, user_input: UserInput) -> str:
        """
        Get AI response with error handling and retries
        Args:
            user_input: Validated user input containing message
        Returns:
            str: Generated response
        Raises:
            HTTPException: For client-facing errors
        """
        for attempt in range(self.max_retries):
            try:
                response = self._call_groq_api(user_input.message)
                logger.debug("Successfully generated response")
                return response
                
            except APIStatusError as e:
                if e.status_code == 429:  # Rate limit
                    wait_time = 2 ** attempt
                    logger.warning(f"Rate limited. Retry {attempt+1} in {wait_time}s")
                    time.sleep(wait_time)
                    continue
                logger.error(f"Groq API error: {str(e)}")
                raise HTTPException(
                    status_code=502,
                    detail="AI service temporarily unavailable"
                )
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail="Failed to generate response"
                )
        
        raise HTTPException(
            status_code=503,
            detail="AI service overloaded. Please try again later"
        )

    def _call_groq_api(self, message: str) -> str:
        """Make actual API call with streaming"""
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=self._initialize_conversation(message),
            temperature=settings.GROQ_TEMPERATURE,
            max_tokens=settings.GROQ_MAX_TOKENS,
            top_p=1,
            stream=True,
            stop=None,
        )
        return self._process_stream(completion)

    def _process_stream(self, completion) -> str:
        """Process streaming response efficiently"""
        response = []
        for chunk in completion:
            if content := chunk.choices[0].delta.content:
                response.append(content)
        return "".join(response)

    def health_check(self) -> bool:
        """Check if service is operational"""
        try:
            self.client.models.list()
            return True
        except Exception:
            return False