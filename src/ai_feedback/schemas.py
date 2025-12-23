from pydantic import BaseModel
from typing import Optional
from src.posts.models import AIFeedbackStatusEnum
from src.ai_feedback.constants import AIFeedbackLangEnum

class AIFeedbackData(BaseModel):
    ai_feedback_content: Optional[str] = None
    ai_feedback_hotline: Optional[bool] = False
    ai_feedback_lang: Optional[AIFeedbackLangEnum] = None  
    ai_feedback_status: AIFeedbackStatusEnum

class AIFeedbackResponse(BaseModel):
    data: AIFeedbackData