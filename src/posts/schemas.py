from pydantic import BaseModel,AfterValidator, Field
from typing import List, Optional
from datetime import datetime
from typing_extensions import Annotated
from src.posts.validators import (check_age, check_post_content, check_group_member_name,
    check_group_name, check_motion_rate, check_post_type_code, check_title,check_common_string)
from src.schemas import PaginatedRequestModel
import enum
from src.posts.models import MessageToYou
from fastapi import Query
from src.ai_feedback.constants import AIFeedbackLangEnum

class SharePostReadPermission(BaseModel):
    shared_to_group_member_id: Optional[List[int]] = None

class PostMasterBase(BaseModel):
    title: Optional[Annotated[str, AfterValidator(check_title)]]
    content: Annotated[str, AfterValidator(check_post_content)]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    motion_rate: Optional[Annotated[int, AfterValidator(check_motion_rate)]]
    images_name: Optional[List[str]]
    videos_name: Optional[List[str]]
    voices_name: Optional[List[str]]
    ai_feedback_content: Optional[str] = None
    ai_feedback_status: Optional[str] = None
    ai_feedback_count: Optional[int] = 0
    ai_feedback_hotline: Optional[bool] = False
    ai_feedback_lang: Optional[AIFeedbackLangEnum] = None  # Will contain 'en', 'sc', 'tc', or 'other'
    class Config:
        from_attributes = True
        
class LifeMomentBase(BaseModel):
    weather: Optional[Annotated[str, AfterValidator(check_common_string)]]
    participants: Optional[Annotated[str, AfterValidator(check_common_string)]]
    restaurant_name: Optional[Annotated[str, AfterValidator(check_common_string)]]
    food_name: Optional[Annotated[str, AfterValidator(check_common_string)]]
    academic_work_interest: Optional[Annotated[str, AfterValidator(check_common_string)]]
    school_score: Optional[Annotated[str, AfterValidator(check_common_string)]]
    age: Optional[Annotated[int, AfterValidator(check_age)]] 
    post_type_code: Optional[Annotated[str, AfterValidator(check_post_type_code)]]
    custom_post_type_id: Optional[int]
    location: Optional[str]
    class Config:
        from_attributes = True

class LifeMomentsBaseInputRequest(LifeMomentBase,PostMasterBase, SharePostReadPermission): 
    class Config:
        from_attributes = True

class LifeTrajectoryBase(BaseModel):
    post_type_code: Optional[Annotated[str, AfterValidator(check_post_type_code)]]
    age: Optional[Annotated[int, AfterValidator(check_age)]]
    custom_post_type_id: Optional[int]
    class Config:
        from_attributes = True        

class LifeTrajectoryBaseInputRequest(LifeTrajectoryBase, PostMasterBase, SharePostReadPermission):
    class Config:
        from_attributes = True


class MessageToYouBase(BaseModel):
    post_type_code: Annotated[str, AfterValidator(check_post_type_code)]
    when_can_read_the_post: Optional[datetime]
    class Config:
        from_attributes = True

class MessageToYouBaseInputRequest(MessageToYouBase, PostMasterBase, SharePostReadPermission):
    class Config:
        from_attributes = True

class LifeMomentAndLifeTrajectoryBaseQueryParams(PaginatedRequestModel):        
    create_from: Optional[str] = None
    create_to: Optional[str] = None
    min_motion_rate: Optional[float] = None
    max_motion_rate: Optional[float] = None
    post_type_code: Optional[List[str]] = None 
    custom_post_type_id: Optional[List[int]] = None
    search_text: Optional[str] = None
    class Config: 
        from_attributes = True

class GetMyCreatedMsgQueryParams(PaginatedRequestModel):        
    type_code: str
    class Config:
        from_attributes = True                

class PostFileType(enum.Enum):
    IMAGES = "images"
    VIDEOS = "videos"
    VOICES_MESSAGE = "voices_msg"
class CreatePermissionsGroupRequest(BaseModel):
    group_name: str

class EditPermissionsGroupRequest(BaseModel):
    group_name: Annotated[str, AfterValidator(check_group_name)]
class PermissionsUserBase(BaseModel):
    phone_number_prefix: str | int
    phone_number: str | int
    first_name:  Annotated[str, AfterValidator(check_group_member_name)]
    last_name:  Annotated[str, AfterValidator(check_group_member_name)]
    class Config:
        from_attributes = True 
class PermissionsGroupMember(PermissionsUserBase):
    user_id: str

class AddPermissionsGroupMembersRequest(BaseModel):
    members: List[PermissionsUserBase]

class EditPermissionsGroupMemberRequest(PermissionsUserBase):
    pass
class RemovePermissionsGroupMemberRequest(BaseModel):
    user_id: str    


class DefineWhichCustomLifePostType(BaseModel):
    is_life_moment: bool = Field(default=False)
    is_life_trajectory: bool = Field(default=False)
    class Config:
        from_attributes = True 

class CustomLifePostTypeBase(DefineWhichCustomLifePostType):
    type_name: str
    type_description: str
    class Config:
        from_attributes = True 

class SelectedUserBase(BaseModel):
    user_id: str
    first_name: str
    last_name: str
    phone_number_prefix: str | int
    phone_number: str | int

    class Config:
        from_attributes = True 
class GroupBase(BaseModel):
    pgm_row_id: int | None
    group_id: int
    selected_user_is_exist: bool
    class Config:
        from_attributes = True 
class ManageUserGroupBaseInputRequest(BaseModel):
    groupData:List[GroupBase]    
    selected_user_data:SelectedUserBase
    class Config:
        from_attributes = True 