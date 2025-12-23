from pydantic import BaseModel
from typing import List, Optional

class AIFeedbackRequest(BaseModel):
    weather: Optional[str] = None
    participants: Optional[List[str]] = None
    restaurant_name: Optional[str] = None
    food_name: Optional[str] = None
    location: Optional[str] = None
    academic_work_interest: Optional[str] = None
    school_score: Optional[str] = None
    nickname: Optional[str] = None
    motion_rate: Optional[float] = None
    content: str
    title: Optional[str] = None
    lang: Optional[str] = None