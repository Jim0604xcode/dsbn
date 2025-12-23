from typing import List
from fastapi import APIRouter, Depends, Request
from src.exceptions import handle_exceptions
from src.schemas import ApiSuccessResponseModel
from src.models import get_error_response_model
from src.database import get_db
from sqlalchemy.orm import Session
from src.utils.response import create_success_response
from src.secertBase.schemas import BankAccountBaseInputRequest, ConfidentialEventBaseInputRequest, PropertyBaseInputRequest, SafetyDepositBoxBaseInputRequest, SecretBaseInputRequest
from src.secertBase.service import check_dead_user_permission, create_bank_account_trx, create_confidential_event_trx, create_property_trx, create_safety_deposit_box_trx, create_secret_base, delete_bank_account_trx, delete_confidential_event_trx, delete_property_trx, delete_safety_deposit_box_trx, edit_bank_account_trx, edit_confidential_event_trx, edit_property_trx, edit_safety_deposit_box_trx, get_bank_account_trx, get_confidential_event_trx, get_dead_user_permission_trx, get_property_trx, get_safety_deposit_box_trx
from src.secertBase.models import (BankAccount, ConfidentialEvent, Property, SafetyDepositBox,SecretBase)
from src.loggerServices import log_info
from src.config import IN_APP_PURCHASE_NO_NEED_TO_PAY_SUBSCRIPTION
router = APIRouter()

# Delete
@router.delete("/delete_bank_account/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def delete_bank_account(id:str,request: Request,db:Session = Depends(get_db)):
    id = int(id) 
    user_id = request.state.user_id
    res = await delete_bank_account_trx(id, user_id, db)
    return create_success_response(res)
    
@router.delete("/delete_property/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def delete_property(id:str,request: Request,db:Session = Depends(get_db)):
    id = int(id) 
    user_id = request.state.user_id # userId from Middleware
    res = await delete_property_trx(id, user_id, db)
    return create_success_response(res)

@router.delete("/delete_safety_deposit_box/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def delete_safety_deposit_box(id:str,request: Request,db:Session = Depends(get_db)):
    id = int(id) 
    user_id = request.state.user_id # userId from Middleware
    res = await delete_safety_deposit_box_trx(id, user_id, db)
    return create_success_response(res)

@router.delete("/delete_confidential_event/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def delete_safety_deposit_box(id:str,request: Request,db:Session = Depends(get_db)):
    id = int(id) 
    user_id = request.state.user_id # userId from Middleware
    res = await delete_confidential_event_trx(id, user_id, db)
    return create_success_response(res)



# Edit
@router.put("/edit_bank_account/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def edit_bank_account(id:str,request: Request,req_data:BankAccountBaseInputRequest,db:Session = Depends(get_db)):
# 1. Prepare the data
    id = int(id) 
    user_id = request.state.user_id
    # user_id = 'e2749e29-1e01-4896-ae71-95f2474092aa'
    # 2. Create Transaction to DB 
    res = await edit_bank_account_trx(user_id=user_id,id=id,updates=req_data,db=db)
    return create_success_response(res)

@router.put("/edit_property/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def edit_property(id:str,request: Request,req_data:PropertyBaseInputRequest,db:Session = Depends(get_db)):
# 1. Prepare the data
    id = int(id) 
    user_id = request.state.user_id
    # user_id = 'e2749e29-1e01-4896-ae71-95f2474092aa'
    # 2. Create Transaction to DB 
    res = await edit_property_trx(user_id=user_id,id=id,updates=req_data,db=db)
    return create_success_response(res)

@router.put("/edit_safety_deposit_box/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def edit_safety_deposit_box(id:str,request: Request,req_data:SafetyDepositBoxBaseInputRequest,db:Session = Depends(get_db)):
# 1. Prepare the data
    id = int(id) 
    user_id = request.state.user_id
    # user_id = 'e2749e29-1e01-4896-ae71-95f2474092aa'
    # 2. Create Transaction to DB 
    res = await edit_safety_deposit_box_trx(user_id=user_id,id=id,updates=req_data,db=db)
    return create_success_response(res)

@router.put("/edit_confidential_event/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def edit_confidential_event(id:str,request: Request,req_data:ConfidentialEventBaseInputRequest,db:Session = Depends(get_db)):
# 1. Prepare the data
    id = int(id) 
    user_id = request.state.user_id
    # user_id = 'e2749e29-1e01-4896-ae71-95f2474092aa'
    # 2. Create Transaction to DB 
    res = await edit_confidential_event_trx(user_id=user_id,id=id,updates=req_data,db=db)
    return create_success_response(res)






# Get

@router.get("/get_bank_account_by_id/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def get_bank_account(id:str,request: Request,db:Session = Depends(get_db),deaduserID: str | None = None):
    # 1. Prepare the data
    user_id = deaduserID if deaduserID else request.state.user_id
    id = int(id)
    fl:List = [SecretBase.user_id == user_id,BankAccount.id == id]
    # 2. Create Transaction to DB 
    res = await get_bank_account_trx(fl=fl, db=db,cb=check_dead_user_permission(user_id=request.state.user_id,dead_user_id=user_id,db=db,key="SB")) if deaduserID else await get_bank_account_trx(fl=fl, db=db)
    return create_success_response(res)

@router.get("/get_bank_account", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def get_bank_account(request: Request,db:Session = Depends(get_db),deaduserID: str | None = None):
    # 1. Prepare the data
    user_id = deaduserID if deaduserID else request.state.user_id
    fl:List = [SecretBase.user_id == user_id]
    
    res = await get_bank_account_trx(fl=fl, db=db,cb=check_dead_user_permission(user_id=request.state.user_id,dead_user_id=user_id,db=db,key="SB")) if deaduserID else await get_bank_account_trx(fl=fl, db=db)
    return create_success_response(res)

@router.get("/get_property/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def get_property(id:str,request: Request,db:Session = Depends(get_db),deaduserID: str | None = None):
    # 1. Prepare the data
    user_id = deaduserID if deaduserID else request.state.user_id
    fl:List = [SecretBase.user_id == user_id,Property.id == id]
    ql:List = [Property.id.label("property_id"),Property.property_name,Property.property_address,Property.remarks]
    # 2. Create Transaction to DB 
    res = await get_property_trx(fl=fl, db=db,ql=ql,cb=check_dead_user_permission(user_id=request.state.user_id,dead_user_id=user_id,db=db,key="SB")) if deaduserID else await get_property_trx(fl=fl, db=db,ql=ql)
    return create_success_response(res)

@router.get("/get_property", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def get_property(request: Request,db:Session = Depends(get_db),deaduserID: str | None = None):
    # 1. Prepare the data
    user_id = deaduserID if deaduserID else request.state.user_id
    fl:List = [SecretBase.user_id == user_id]
    ql:List = [Property.id.label("property_id"),Property.property_name,Property.property_address,Property.remarks]
    # 2. Create Transaction to DB 
    res = await get_property_trx(fl=fl, db=db,ql=ql,cb=check_dead_user_permission(user_id=request.state.user_id,dead_user_id=user_id,db=db,key="SB")) if deaduserID else await get_property_trx(fl=fl, db=db,ql=ql)
    return create_success_response(res)

@router.get("/get_safety_deposit_box/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def get_safety_deposit_box(id:str,request: Request,db:Session = Depends(get_db),deaduserID: str | None = None):
    # 1. Prepare the data
    user_id = deaduserID if deaduserID else request.state.user_id
    fl:List = [SecretBase.user_id == user_id,SafetyDepositBox.id == id]
    # 2. Create Transaction to DB 
    res = await get_safety_deposit_box_trx(fl=fl, db=db,cb=check_dead_user_permission(user_id=request.state.user_id,dead_user_id=user_id,db=db,key="SB")) if deaduserID else await get_safety_deposit_box_trx(fl=fl, db=db)
    return create_success_response(res)

@router.get("/get_safety_deposit_box", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def get_safety_deposit_box(request: Request,db:Session = Depends(get_db),deaduserID: str | None = None):
    # 1. Prepare the data
    user_id = deaduserID if deaduserID else request.state.user_id
    fl:List = [SecretBase.user_id == user_id]
    # 2. Create Transaction to DB 
    res = await get_safety_deposit_box_trx(fl=fl, db=db,cb=check_dead_user_permission(user_id=request.state.user_id,dead_user_id=user_id,db=db,key="SB")) if deaduserID else await get_safety_deposit_box_trx(fl=fl, db=db)
    return create_success_response(res)

@router.get("/get_confidential_event/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def get_confidential_event(id:str,request: Request,db:Session = Depends(get_db),deaduserID: str | None = None):
    # 1. Prepare the data
    user_id = deaduserID if deaduserID else request.state.user_id
    fl:List = [SecretBase.user_id == user_id,ConfidentialEvent.id == id]
    # 2. Create Transaction to DB 
    res = await get_confidential_event_trx(fl=fl, db=db,cb=check_dead_user_permission(user_id=request.state.user_id,dead_user_id=user_id,db=db,key="SB")) if deaduserID else await get_confidential_event_trx(fl=fl, db=db)
    return create_success_response(res)

@router.get("/get_confidential_event", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def get_confidential_event(request: Request,db:Session = Depends(get_db),deaduserID: str | None = None):
    # 1. Prepare the data
    user_id = deaduserID if deaduserID else request.state.user_id
    fl:List = [SecretBase.user_id == user_id]
    # 2. Create Transaction to DB 
    res = await get_confidential_event_trx(fl=fl, db=db,cb=check_dead_user_permission(user_id=request.state.user_id,dead_user_id=user_id,db=db,key="SB")) if deaduserID else await get_confidential_event_trx(fl=fl, db=db)
    return create_success_response(res)








# Create

@router.post("/create_bank_account", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def create_bank_account(request: Request,req_data:BankAccountBaseInputRequest,db:Session = Depends(get_db)):
    
    user_id = request.state.user_id # userId from Middleware
    # product_id = request.state.product_id
    product_id = IN_APP_PURCHASE_NO_NEED_TO_PAY_SUBSCRIPTION
    # secert_data:SecretBaseInputRequest = SecretBaseInputRequest(asset_type="BANK_ACCOUNT",user_id=user_id,product_id="abc123abc123abc123abc123abc123abc123")
    secert_data:SecretBaseInputRequest = SecretBaseInputRequest(asset_type="BANK_ACCOUNT",user_id=user_id,product_id=product_id)
    res = await create_bank_account_trx(req_data, db,create_secret_base(secert_data,db))
    return create_success_response({"id":res})

@router.post("/create_property", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def create_property(request: Request,req_data:PropertyBaseInputRequest,db:Session = Depends(get_db)):
    
    user_id = request.state.user_id # userId from Middleware
    # product_id = request.state.product_id
    product_id = IN_APP_PURCHASE_NO_NEED_TO_PAY_SUBSCRIPTION
    # secert_data:SecretBaseInputRequest = SecretBaseInputRequest(asset_type="PROPERTY",user_id=user_id,product_id="abc123abc123abc123abc123abc123abc123")
    secert_data:SecretBaseInputRequest = SecretBaseInputRequest(asset_type="PROPERTY",user_id=user_id,product_id=product_id)
    res = await create_property_trx(req_data, db,create_secret_base(secert_data,db))
    return create_success_response({"id":res})

@router.post("/create_safety_deposit_box", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def create_safety_deposit_box(request: Request,req_data:SafetyDepositBoxBaseInputRequest,db:Session = Depends(get_db)):
    
    user_id = request.state.user_id # userId from Middleware
    # product_id = request.state.product_id
    product_id = IN_APP_PURCHASE_NO_NEED_TO_PAY_SUBSCRIPTION
    # secert_data:SecretBaseInputRequest = SecretBaseInputRequest(asset_type="SAFETY_DEPOSIT_BOX",user_id=user_id,product_id="abc123abc123abc123abc123abc123abc123")
    secert_data:SecretBaseInputRequest = SecretBaseInputRequest(asset_type="SAFETY_DEPOSIT_BOX",user_id=user_id,product_id=product_id)
    res = await create_safety_deposit_box_trx(req_data, db,create_secret_base(secert_data,db))
    
    return create_success_response({"id":res})

@router.post("/create_confidential_event", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def create_confidential_event(request: Request,req_data:ConfidentialEventBaseInputRequest,db:Session = Depends(get_db)):
    
    user_id = request.state.user_id # userId from Middleware
    # product_id = request.state.product_id
    product_id = IN_APP_PURCHASE_NO_NEED_TO_PAY_SUBSCRIPTION
    # secert_data:SecretBaseInputRequest = SecretBaseInputRequest(asset_type="CONFIDENTIAL_EVENT",user_id=user_id,product_id="abc123abc123abc123abc123abc123abc123")
    secert_data:SecretBaseInputRequest = SecretBaseInputRequest(asset_type="CONFIDENTIAL_EVENT",user_id=user_id,product_id=product_id)
    res = await create_confidential_event_trx(req_data, db,create_secret_base(secert_data,db))
    
    return create_success_response({"id":res})
