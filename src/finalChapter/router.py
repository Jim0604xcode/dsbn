from typing import List
from fastapi import APIRouter, Depends, Request
from src.exceptions import DatabaseErrorException, handle_exceptions
from src.schemas import ApiSuccessResponseModel
from src.models import get_error_response_model
from src.database import get_db
from sqlalchemy.orm import Session
from src.utils.response import create_success_response
from src.finalChapter.schemas import AshesBaseInputRequest, CeremonyPreferenceBaseInputRequest, CoffinBaseInputRequest, EnduringPowerOfAttorneyBaseInputRequest, FuneralBaseInputRequest, MedicalPreferenceBaseInputRequest, PalliativeCareBaseInputRequest
from src.finalChapter.service import create_ashes_trx, create_ceremony_preference_trx, create_coffin_trx, create_enduring_power_of_attorney_trx, create_funeral_trx, create_medical_preference_trx, create_palliative_care_trx, get_ashes_trx, get_ceremony_preference_trx, get_coffin_trx, get_enduring_power_of_attorney_trx, get_final_chapter_trx, get_funeral_trx, get_medical_preference_trx, get_palliative_care_trx
from src.finalChapter.models import Ashes, CeremonyPreference, Coffin, EnduringPowerOfAttorney, Funeral, MedicalPreference, PalliativeCare
from src.loggerServices import log_info
from src.secertBase.service import check_dead_user_permission
router = APIRouter()


# Edit
# @router.put("/edit_push_notification", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
# @handle_exceptions
# async def edit_push_notification(request: Request,reqBody:PushNotificationBaseInputRequest,db:Session = Depends(get_db)):
#     # 1. Prepare the data
#     user_id = request.state.user_id # userId from Middleware
#     # 2. Create Transaction to DB 
#     res = await edit_push_notification_trx(user_id=user_id,updates=reqBody,db=db)
#     return create_success_response(res)

# Get
@router.get("/get_final_chapter", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def get_final_chapter(request: Request,db:Session = Depends(get_db),deaduserID: str | None = None):
    # 1. Prepare the data
    user_id = deaduserID if deaduserID else request.state.user_id
    # 2. Create Transaction to DB
    res = await get_final_chapter_trx(user_id, db,cb=check_dead_user_permission(user_id=request.state.user_id,dead_user_id=user_id,db=db,key="FC")) if deaduserID else await get_final_chapter_trx(user_id, db)
    return create_success_response(res)
    

@router.get("/get_palliative_care", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def get_palliative_care(request: Request,db:Session = Depends(get_db)):
    # 1. Prepare the data
    user_id = request.state.user_id # userId from Middleware
    
    fl:List = [PalliativeCare.user_id == user_id]
    # 2. Create Transaction to DB
    res = await get_palliative_care_trx(fl, db=db)
    return create_success_response(res)

@router.get("/get_medical_preference", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def get_medical_preference(request: Request,db:Session = Depends(get_db)):
    # 1. Prepare the data
    user_id = request.state.user_id # userId from Middleware
    fl:List = [MedicalPreference.user_id == user_id]
    # 2. Create Transaction to DB
    res = await get_medical_preference_trx(fl, db=db)
    return create_success_response(res)

@router.get("/get_enduring_power_of_attorney", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def get_enduring_power_of_attorney(request: Request,db:Session = Depends(get_db)):
    # 1. Prepare the data
    user_id = request.state.user_id # userId from Middleware
    fl:List = [EnduringPowerOfAttorney.user_id == user_id]
    # 2. Create Transaction to DB
    res = await get_enduring_power_of_attorney_trx(fl, db=db)
    return create_success_response(res)



@router.get("/get_ceremony_preference", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def get_ceremony_preference(request: Request,db:Session = Depends(get_db)):
    # 1. Prepare the data
    user_id = request.state.user_id # userId from Middleware
    fl:List = [CeremonyPreference.user_id == user_id]
    # 2. Create Transaction to DB
    res = await get_ceremony_preference_trx(fl, db=db)
    return create_success_response(res)

@router.get("/get_coffin", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def get_coffin(request: Request,db:Session = Depends(get_db)):
    # 1. Prepare the data
    user_id = request.state.user_id # userId from Middleware
    fl:List = [Coffin.user_id == user_id]
    # 2. Create Transaction to DB
    res = await get_coffin_trx(fl, db=db)
    return create_success_response(res)

@router.get("/get_funeral", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def get_funeral(request: Request,db:Session = Depends(get_db)):
    # 1. Prepare the data
    user_id = request.state.user_id # userId from Middleware
    fl:List = [Funeral.user_id == user_id]
    # 2. Create Transaction to DB
    res = await get_funeral_trx(fl, db=db)
    return create_success_response(res)

@router.get("/get_ashes", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def get_ashes(request: Request,db:Session = Depends(get_db)):
    # 1. Prepare the data
    user_id = request.state.user_id # userId from Middleware
    fl:List = [Ashes.user_id == user_id]
    # 2. Create Transaction to DB
    res = await get_ashes_trx(fl, db=db)
    return create_success_response(res)



# Create

@router.post("/create_palliative_care", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def create_palliative_care(request: Request,req_data:PalliativeCareBaseInputRequest,db:Session = Depends(get_db)):
    user_id = request.state.user_id # userId from Middleware
    res = await create_palliative_care_trx(req_data,user_id, db)
    return create_success_response({'id':res})

@router.post("/create_medical_preference", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def create_medical_preference(request: Request,req_data:MedicalPreferenceBaseInputRequest,db:Session = Depends(get_db)):
    user_id = request.state.user_id # userId from Middleware
    res = await create_medical_preference_trx(req_data,user_id, db)
    return create_success_response({'id':res})

@router.post("/create_enduring_power_of_attorney", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def create_enduring_power_of_attorney(request: Request,req_data:EnduringPowerOfAttorneyBaseInputRequest,db:Session = Depends(get_db)):
    user_id = request.state.user_id # userId from Middleware
    res = await create_enduring_power_of_attorney_trx(req_data,user_id, db)
    return create_success_response({'id':res})


@router.post("/create_ceremony_preference", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def create_ceremony_preference(request: Request,req_data:CeremonyPreferenceBaseInputRequest,db:Session = Depends(get_db)):
    user_id = request.state.user_id # userId from Middleware
    res = await create_ceremony_preference_trx(req_data,user_id, db)
    return create_success_response({'id':res})


@router.post("/create_coffin", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def create_coffin(request: Request,req_data:CoffinBaseInputRequest,db:Session = Depends(get_db)):
    user_id = request.state.user_id # userId from Middleware
    res = await create_coffin_trx(req_data,user_id, db)
    return create_success_response({'id':res})
    

@router.post("/create_funeral", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def create_funeral(request: Request,req_data:FuneralBaseInputRequest,db:Session = Depends(get_db)):
    user_id = request.state.user_id # userId from Middleware
    res = await create_funeral_trx(req_data,user_id, db)
    return create_success_response({'id':res})


@router.post("/create_ashes", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def create_ashes(request: Request,req_data:AshesBaseInputRequest,db:Session = Depends(get_db)):
    user_id = request.state.user_id # userId from Middleware
    res = await create_ashes_trx(req_data,user_id, db)
    return create_success_response({'id':res})
