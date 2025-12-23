from fastapi import APIRouter, Depends, Request
from src.exceptions import handle_exceptions
from src.schemas import ApiSuccessResponseModel
from src.models import get_error_response_model
from src.database import get_db
from sqlalchemy.orm import Session
from src.utils.response import create_success_response
from src.admin.service import edit_pass_away_meta_by_admin_trx, get_approval_user_table_by_id_trx, get_approval_user_table_trx, get_life_moment_table_trx, get_life_traj_table_trx, get_mess_to_you_table_trx, get_push_users_table_trx, get_user_life_moment_table_trx, get_user_life_traj_table_trx, get_user_message_to_you_table_trx, post_and_ai_total_summary_table_trx, send_push_notification_all_device_trx, send_push_notification_specific_device_trx, user_life_overview_chart_table_trx, user_pre_death_plan_table_trx, user_storage_usage_table_trx
from src.passAway.schemas import (PassAwayInfoMetaBaseInputRequest)
from src.admin.schemas import SendPushNotificationBaseInputRequest, SendPushNotificationToSpecificMemberBaseInputRequest, reqParam
from src.loggerServices import log_error, log_info
router = APIRouter()

# Get

@router.get("/get_push_users_table", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def get_push_users_table(request: Request,db:Session = Depends(get_db)):
    
    res = await get_push_users_table_trx(db=db)
    return create_success_response(res)


@router.get("/get_approval_user_table", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def get_approval_user_table(request: Request,db:Session = Depends(get_db)):
    
    # user_id = request.state.user_id # userId from Middleware
    res = await get_approval_user_table_trx(db=db)
    return create_success_response(res)


@router.get("/get_approval_user/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def get_approval_user(id:str,request: Request,db:Session = Depends(get_db)):
    id = int(id)    
    res = await get_approval_user_table_by_id_trx(id=id,db=db)
    return create_success_response(res)


@router.post("/edit_pass_away_meta_by_admin/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def edit_pass_away_meta_by_admin(id:str,request: Request,reqData:PassAwayInfoMetaBaseInputRequest,db:Session = Depends(get_db)):
    pass_away_info_id = int(id)
    admin_user_id = request.state.user_id # userId from Middleware
    
    res = await edit_pass_away_meta_by_admin_trx(pass_away_info_id=pass_away_info_id,updates=reqData,admin_user_id=admin_user_id,db=db)
    return create_success_response(res)



@router.post("/send_push_notification_all_device", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def send_push_notification_all_device(request: Request,reqData:SendPushNotificationBaseInputRequest,db:Session = Depends(get_db)):
    # user_id = request.state.user_id # userId from Middleware
    res = await send_push_notification_all_device_trx(reqData,db)

    return create_success_response(res)


@router.post("/send_push_notification_specific_device", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def send_push_notification_all_device(request: Request,reqData:SendPushNotificationToSpecificMemberBaseInputRequest,db:Session = Depends(get_db)):
    # user_id = request.state.user_id # userId from Middleware
    res = await send_push_notification_specific_device_trx(reqData,db)

    return create_success_response(res)


@router.post("/life_moment_table", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def get_life_moment_table(request: Request,reqData:reqParam,db:Session = Depends(get_db)):
    res = await get_life_moment_table_trx(reqData,db)
    # log_info(f'=====>{res}')
    return create_success_response(res)


@router.post("/life_traj_table", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def life_traj_table(request: Request,reqData:reqParam,db:Session = Depends(get_db)):
    res = await get_life_traj_table_trx(reqData,db)
    # log_info(f'=====>{res}')
    return create_success_response(res)


@router.post("/message_to_you_table", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def message_to_you_table(request: Request,reqData:reqParam,db:Session = Depends(get_db)):
    res = await get_mess_to_you_table_trx(reqData,db)
    # log_info(f'=====>{res}')
    return create_success_response(res)


@router.post("/user_life_moment_table", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def user_life_moment_table(request: Request,reqData:reqParam,db:Session = Depends(get_db)):
    res = await get_user_life_moment_table_trx(reqData,db)
    # log_info(f'=====>{res}')
    return create_success_response(res)


@router.post("/user_life_traj_table", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def user_life_traj_table(request: Request,reqData:reqParam,db:Session = Depends(get_db)):
    res = await get_user_life_traj_table_trx(reqData,db)
    # log_info(f'=====>{res}')
    return create_success_response(res)


@router.post("/user_message_to_you_table", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def user_message_to_you_table(request: Request,reqData:reqParam,db:Session = Depends(get_db)):
    res = await get_user_message_to_you_table_trx(reqData,db)
    # log_info(f'=====>{res}')
    return create_success_response(res)


@router.get("/post_and_ai_total_summary_table", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def post_and_ai_total_summary_table(request: Request,db:Session = Depends(get_db)):
    res = await post_and_ai_total_summary_table_trx(db)
    # log_info(f'=====>{res}')
    return create_success_response(res)

@router.post("/user_pre_death_plan_table", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def user_pre_death_plan_table(request: Request,reqData:reqParam,db:Session = Depends(get_db)):
    res = await user_pre_death_plan_table_trx(reqData,db)
    # log_info(f'=====>{res}')
    return create_success_response(res)

@router.post("/user_life_overview_chart_table", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def user_life_overview_chart_table(request: Request,reqData:reqParam,db:Session = Depends(get_db)):
    res = await user_life_overview_chart_table_trx(reqData,db)
    # log_info(f'=====>{res}')
    return create_success_response(res)

@router.post("/user_storage_usage_table", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def user_storage_usage_table(request: Request,reqData:reqParam,db:Session = Depends(get_db)):
    res = await user_storage_usage_table_trx(reqData,db)
    # log_info(f'=====>{res}')
    return create_success_response(res)

