from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from src.database import get_db
from src.ai_feedback.service import generate_ai_feedback
from src.ai_feedback.schemas import AIFeedbackResponse
from src.exceptions import BadReqExpection, handle_exceptions
from src.utils.response import create_success_response
from src.models import get_error_response_model

router = APIRouter()

@router.get("/generate_ai_feedback/life_moment/{post_id}", response_model=AIFeedbackResponse,responses=get_error_response_model)
@handle_exceptions
async def generate_ai_feedback_for_life_moment(
    request: Request,
    post_id: int,
    db: Session = Depends(get_db)
):
    """
    Generate AI feedback for a life moment post
    
    Args:
        request: FastAPI request object
        post_id: The ID of the life moment post
        db: Database session
    
    Returns:
        AI feedback response with status and content
    """
    
    try:
        user_id = request.state.user_id
    except AttributeError:
        raise BadReqExpection("User not authenticated")
    
    if not user_id:
        raise BadReqExpection("User not authenticated")
    
    # Get user info from request state for nickname
    user_info = getattr(request.state, 'user_info', None)
    
    result = await generate_ai_feedback(user_id, post_id, db, user_info)
    
    return AIFeedbackResponse(
        data=result
    )
