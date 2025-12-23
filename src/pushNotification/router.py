from typing import List
from fastapi import APIRouter, Depends, Request
from src.exceptions import DatabaseErrorException, handle_exceptions
from src.schemas import ApiSuccessResponseModel
from src.models import get_error_response_model
from src.database import get_db
from sqlalchemy.orm import Session
from src.utils.response import create_success_response
from src.pushNotification.schemas import PushNotificationBaseInputRequest
from src.pushNotification.service import get_push_notification_trx, register_push_notification_token_trx
from src.pushNotification.models import PushNotification
from src.loggerServices import log_info
router = APIRouter()



# Get

@router.get("/get_push_notification/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def get_push_notification(id:str,request: Request,db:Session = Depends(get_db)):
    
    # 1. Prepare the data
    user_id = request.state.user_id # userId from Middleware
    fl:List = [PushNotification.user_id == user_id,PushNotification.device_uuid == id]
    # 2. Create Transaction to DB
    res = await get_push_notification_trx(fl, db=db)
    return create_success_response(res)



# Create / Edit

@router.post("/register_push_notification_token", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def register_push_notification_token(request: Request,req_data:PushNotificationBaseInputRequest,db:Session = Depends(get_db)):
    user_id = request.state.user_id # userId from Middleware
    res = await register_push_notification_token_trx(req_data,user_id, db)
    return create_success_response(res)



