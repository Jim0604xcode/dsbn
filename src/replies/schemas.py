from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CreateReplyRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000, description="The reply content")
    reply_master_id: Optional[int] = Field(None, description="The reply_master_id this reply is responding to")
    
    class Config:
        from_attributes = True

class EditReplyRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000, description="The new reply content")
    
    class Config:
        from_attributes = True

class ReplyResponse(BaseModel):
    id: int
    post_master_id: int
    user_id: str
    parent_reply_master_id: Optional[int]
    content: str
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True