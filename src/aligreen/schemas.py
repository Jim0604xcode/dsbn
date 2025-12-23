"""
AliGreen Pydantic Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum
from src.aligreen.constants import SERVICE_QUERY_SECURITY_CHECK_INTL, SERVICE_TEXT_MODERATION
from src.aligreen.constants import SERVICE_CHAT_DETECTION
from src.aligreen.constants import LABEL_NORMAL, LABEL_RISK
from src.aligreen.constants import SUGGESTION_PASS, SUGGESTION_REVIEW, SUGGESTION_BLOCK


class ServiceTypeEnum(str, Enum):
    """Detection service type enum"""
    QUERY_SECURITY_CHECK_INTL = SERVICE_QUERY_SECURITY_CHECK_INTL
    TEXT_MODERATION = SERVICE_TEXT_MODERATION
    CHAT_DETECTION = SERVICE_CHAT_DETECTION


class LabelEnum(str, Enum):
    """Labels enum"""
    NORMAL = LABEL_NORMAL
    RISK = LABEL_RISK


class SuggestionEnum(str, Enum):
    """Suggestion enum"""
    PASS = SUGGESTION_PASS
    REVIEW = SUGGESTION_REVIEW
    BLOCK = SUGGESTION_BLOCK


# ============== Request Schemas ==============

class TextSafetyCheckRequest(BaseModel):
    """text safety check request"""
    content: str = Field(..., description="Text content to be checked", min_length=1)
    service: Optional[ServiceTypeEnum] = Field(
        default=ServiceTypeEnum.QUERY_SECURITY_CHECK_INTL,
        description="Detection service type"
    )
    
# ============== Response Schemas ==============

class TextSafetyCheckResult(BaseModel):
    """Text safety check result (simplified version)"""
    is_safe: bool = Field(..., description="Is safe")
    labels: LabelEnum = Field(..., description="Labels")
    reason: Optional[str] = Field(default="", description="Reason for the result")
    suggestion: SuggestionEnum = Field(..., description="Suggestion (pass/review/block)")
    confidence: float = Field(default=1.0, description="Confidence (0-1)", ge=0, le=1)
    raw_response: Dict[str, Any] = Field(..., description="Raw response")
