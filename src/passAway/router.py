from typing import List
from fastapi import APIRouter, Depends, Request,UploadFile, Form
from src.utils.response import create_success_response
from src.exceptions import handle_exceptions
from src.models import get_error_response_model
from src.schemas import ApiSuccessResponseModel
from src.database import get_db
from sqlalchemy.orm import Session

from src.secertBase.service import get_dead_user_permission_trx

import json
from src.passAway.service import (create_pass_away_trx, bind_passaway_file)

from typing import List

router = APIRouter()
# Delete

# Edit


# Get
@router.get("/get_dead_user_permission", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def get_dead_user_permission(request: Request,db:Session = Depends(get_db),deaduserID: str | None = None):
    # 1. Prepare the data
    user_id = request.state.user_id
    dead_user_id = deaduserID
    # log_info(f'userId-{user_id}')
    res = await get_dead_user_permission_trx(user_id=user_id,dead_user_id=dead_user_id,db=db)
    # log_info(f'permissions----->{res}')
    return create_success_response(res)    

# Create

@router.post("/bind_passaway_file/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def bind_passaway_file_endpoint(id:str, request: Request, files: List[UploadFile], oss_data:str=Form(...), db:Session = Depends(get_db)):
    user_id = request.state.user_id
    id = int(id)
    # req_data = json.loads(req_data)
    oss_data = json.loads(oss_data)
    res = await bind_passaway_file(id, user_id, db, files, oss_data)
    return create_success_response(res)


@router.post("/create_pass_away/{ui_id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def create_pass_away(ui_id:str,request: Request,req_data:str=Form(...),payment_data:str=Form(...),db:Session = Depends(get_db)):
    
    inheritor_id = request.state.user_id
    ui_id = int(ui_id)
    req_data = json.loads(req_data)
    payment_data = json.loads(payment_data)
    res = await create_pass_away_trx(ui_id,inheritor_id, db,req_data,payment_data)
    return create_success_response({"pai_id":res})