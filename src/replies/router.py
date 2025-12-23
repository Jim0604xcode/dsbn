from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from src.database import get_db
from src.replies.schemas import CreateReplyRequest, EditReplyRequest
from src.replies.service import create_reply, delete_reply, edit_reply
from src.posts.models import PostSourceEnum
from src.utils.response import create_success_response
from src.exceptions import handle_exceptions
from src.models import get_error_response_model
from src.schemas import ApiSuccessResponseModel

router = APIRouter()

@router.post("/create/life_moment/{id}", response_model=ApiSuccessResponseModel, responses=get_error_response_model)
@handle_exceptions
async def create_reply_to_life_moment(
    request: Request,
    id: int,
    reply_data: CreateReplyRequest,
    db: Session = Depends(get_db)
):
    """Create Reply to a Life Moment Route"""
    user_id = request.state.user_id
    
    result = await create_reply(
        post_source=PostSourceEnum.LIFE_MOMENT,
        shared_post_id=id,
        user_id=user_id,
        content=reply_data.content,
        parent_reply_master_id=reply_data.reply_master_id,
        db=db
    )
    return create_success_response(result)

@router.post("/create/life_trajectory/{id}", response_model=ApiSuccessResponseModel, responses=get_error_response_model)
@handle_exceptions
async def create_reply_to_life_trajectory(
    request: Request,
    id: int,
    reply_data: CreateReplyRequest,
    db: Session = Depends(get_db)
):
    """Create Reply to a Life Trajectory Route"""
    user_id = request.state.user_id
    
    result = await create_reply(
        post_source=PostSourceEnum.LIFE_TRAJECTORY,
        shared_post_id=id,
        user_id=user_id,
        content=reply_data.content,
        parent_reply_master_id=reply_data.reply_master_id,
        db=db
    )
    
    return create_success_response(result)

@router.post("/create/message_to_you/{id}", response_model=ApiSuccessResponseModel, responses=get_error_response_model)
@handle_exceptions
async def create_reply_to_message_to_you(
    request: Request,
    id: int,
    reply_data: CreateReplyRequest,
    db: Session = Depends(get_db)
):
    """Create Reply to a Message to You Route"""
    user_id = request.state.user_id
    
    result = await create_reply(
        post_source=PostSourceEnum.MESSAGE_TO_YOU,
        shared_post_id=id,
        user_id=user_id,
        content=reply_data.content,
        parent_reply_master_id=reply_data.reply_master_id,
        db=db
    )
    
    return create_success_response(result)

@router.delete("/{reply_master_id}", response_model=ApiSuccessResponseModel, responses=get_error_response_model)
@handle_exceptions
async def delete_reply_route(
    request: Request,
    reply_master_id: int,
    db: Session = Depends(get_db)
):
    """Delete a reply by marking it as deleted"""
    user_id = request.state.user_id
    
    result = delete_reply(reply_master_id, user_id, db)
    
    return create_success_response(result)

@router.put("/{reply_master_id}", response_model=ApiSuccessResponseModel, responses=get_error_response_model)
@handle_exceptions
async def edit_reply_route(
    request: Request,
    reply_master_id: int,
    reply_data: EditReplyRequest,
    db: Session = Depends(get_db)
):
    """Edit a reply's content"""
    user_id = request.state.user_id
    
    result = edit_reply(reply_master_id, reply_data.content, user_id, db)
    
    return create_success_response(result)