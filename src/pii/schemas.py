from typing import List, Optional, Literal
from pydantic import BaseModel, Field

from .constants import (
    SUPPORTED_ENTITY_TYPES,
    DEFAULT_PHONE_REGIONS,
    DEFAULT_MASK_CHAR,
    MASK_STYLE_FULL,
    MASK_STYLE_PARTIAL_LAST4,
)


class MaskRequest(BaseModel):
    text: str = Field(..., description="Original text")
    locale: str = Field("auto", description="Language/region: auto/en/zh etc.")
    entity_types: List[str] = Field(
        default_factory=lambda: list(SUPPORTED_ENTITY_TYPES),
        description="Entity types to identify and mask",
    )
    phone_regions: List[str] = Field(
        default_factory=lambda: list(DEFAULT_PHONE_REGIONS),
        description="Phone region priority list (ISO 3166-1 alpha-2)",
    )
    mask_char: str = Field(DEFAULT_MASK_CHAR, min_length=1, max_length=1)
    mask_style: Literal["full", "partial_last4"] = Field(MASK_STYLE_FULL)
    preserve_length: bool = Field(True, description="Whether to keep the same length as the original text")


class EntityDetail(BaseModel):
    type: str
    text: str
    start: int
    end: int
    replacement: str
    region: Optional[str] = None  # Only phone may have region
    subtype: Optional[str] = None  # Subtype of certificate, etc.


class MaskResponse(BaseModel):
    masked_text: str
    entities: List[EntityDetail]


