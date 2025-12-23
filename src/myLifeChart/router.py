from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.orm import Session
from src.secertBase.service import check_dead_user_permission
from typing import List, Optional
from datetime import datetime

from src.database import get_db
from src.utils.response import create_success_response
from src.exceptions import BadReqExpection, handle_exceptions
from src.models import get_error_response_model
from src.schemas import ApiSuccessResponseModel

from src.myLifeChart.schemas import MoodAnalyticsResponse
from src.myLifeChart.service import get_mood_analytics

router = APIRouter()

@router.get("/mood_analytics", response_model=ApiSuccessResponseModel[MoodAnalyticsResponse], responses=get_error_response_model)
@handle_exceptions
async def get_mood_analytics_route(
    request: Request,
    start_date: datetime,
    end_date: datetime,
    deaduserID: str | None = None,
    db: Session = Depends(get_db)
):
    user_id = request.state.user_id
    if deaduserID:
        analytics_data = await get_mood_analytics(start_date, end_date, deaduserID, db, cb=check_dead_user_permission(user_id=user_id,dead_user_id=deaduserID,db=db,key="LET"))
    else:
        analytics_data = await get_mood_analytics(start_date, end_date, user_id, db)
    
    return create_success_response(analytics_data)
