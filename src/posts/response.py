from datetime import datetime
from pydantic import BaseModel
from src.posts.constants import POST_OWNER_IS_REQUESTER
from src.posts.schemas import ( CustomLifePostTypeBase,
    LifeMomentBase, LifeTrajectoryBase, MessageToYouBaseInputRequest, PermissionsUserBase,
    PostMasterBase)
from typing import List, Optional
from src.auth.schemas import PostAuthgearUserInfo
class MediaResponseModel(BaseModel):
    images_url: Optional[List[str]]
    videos_url: Optional[List[str]]
    voices_url: Optional[List[str]]

class PostMasterBaseWithoutAI(BaseModel):
    title: Optional[str]
    content: str
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    motion_rate: Optional[int]
    class Config:
        from_attributes = True


class PermissionsUserResponseModel(PermissionsUserBase):
    id:int
    user_id: str | None
    class Config:
        from_attributes = True
            
class LifeMomentResponseModel(LifeMomentBase, PostMasterBase, MediaResponseModel):
    id: int 
    post_master_id: int
    shared_to_list: List[PermissionsUserResponseModel] | None
    total_replies: int = 0
    shared_replies_count: int = 0
    postOwner: PostAuthgearUserInfo | str = POST_OWNER_IS_REQUESTER
    updated_at: datetime
    created_at: datetime

# excluding the ai_feddback related fields
class SharedLifeMomentResponseModel(LifeMomentBase, PostMasterBaseWithoutAI, MediaResponseModel):
    id: int 
    post_master_id: int
    shared_to_list: List[PermissionsUserResponseModel] | None
    total_replies: int = 0
    shared_replies_count: int = 0
    postOwner: PostAuthgearUserInfo | str = POST_OWNER_IS_REQUESTER
    updated_at: datetime
    created_at: datetime
    is_life_moment: bool = True
    is_life_trajectory: bool = False
    
class LifeTrajectoryResponseModel(LifeTrajectoryBase,PostMasterBase,MediaResponseModel):
    id: int
    shared_to_list: List[PermissionsUserResponseModel] | None
    total_replies: int = 0
    shared_replies_count: int = 0
    updated_at: datetime
    postOwner: PostAuthgearUserInfo | str = POST_OWNER_IS_REQUESTER
    created_at: datetime

# excluding the ai_feddback related fields
class SharedLifeTrajectoryResponseModel(LifeTrajectoryBase, PostMasterBaseWithoutAI, MediaResponseModel):
    id: int
    shared_to_list: List[PermissionsUserResponseModel] | None
    total_replies: int = 0
    shared_replies_count: int = 0
    postOwner: PostAuthgearUserInfo | str = POST_OWNER_IS_REQUESTER
    updated_at: datetime
    created_at: datetime
    is_life_moment: bool = False
    is_life_trajectory: bool = True

class MessageToYouResponseModel(MessageToYouBaseInputRequest,MediaResponseModel):
    id: int
    shared_to_list: List[PermissionsUserResponseModel] | None
    total_replies: int = 0
    shared_replies_count: int = 0
    postOwner: PostAuthgearUserInfo | str = POST_OWNER_IS_REQUESTER
    updated_at: datetime
class PermissionsGroupResponse(BaseModel):
    id: int
    group_name: str
    created_at: datetime
    class Config:
        from_attributes = True    
            
class GetPermissionsGroupResponseModel(BaseModel):
    group: PermissionsGroupResponse
    members: List[PermissionsUserResponseModel]
    class Config:
        from_attributes = True

class PermissionsGroupsListResponseModel(BaseModel):
    groups: List[GetPermissionsGroupResponseModel]
    class Config:
        from_attributes = True

class CustomLifePostTypeResponse(BaseModel):
    id: int
    type_name: str
    type_description: str
    updated_at: datetime
    class Config:
        from_attributes = True
class DefaultPostTypeBaseResponse(BaseModel):
    type_code: str
    zh_hk_type_name: str
    zh_hk_type_description: str
    en_type_name: str
    en_type_description: str    
    zh_hans_type_name: str
    zh_hans_type_description: str
    class Config:
        from_attributes = True

# Response model for default post types
# Container model for the combined response
class AllPostTypesResponse(BaseModel):
    default_types: List[DefaultPostTypeBaseResponse]
    custom_types: List[CustomLifePostTypeResponse]

class ReplierInfoResponse(BaseModel):
    first_name: str
    last_name: str
    picture: str

class ReplyResponse(BaseModel):
    reply_master_id: int
    user_id: str
    content: str
    created_at: datetime
    is_deleted: bool
    parent_reply_master_id: Optional[int]
    children: List['ReplyResponse'] = []

class PostRepliesResponse(BaseModel):
    replies: List[ReplyResponse]
    replier_info: dict[str, ReplierInfoResponse]

# Enable forward references for recursive model
ReplyResponse.model_rebuild()