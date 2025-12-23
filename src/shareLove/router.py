from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, Request,UploadFile, Form
from pydantic import BaseModel
from src.utils.response import create_success_response
from src.exceptions import handle_exceptions
from src.models import get_error_response_model
from src.schemas import ApiSuccessResponseModel
from src.database import get_db
from sqlalchemy.orm import Session
# from src.loggerServices import log_info
from src.shareLove.schemas import (FamilyOfficeBaseInputRequest, FamilyOfficeEditBaseInputRequest, InsuranceBeneficiariesBaseInputRequest,PhoneBeneficiariesBaseInputRequest, ReSendSMSBaseInputRequest, TrustBaseInputRequest, TrustEditBaseInputRequest, UserInheritorBaseInputRequest, UserInheritorMetaBaseInputRequest, UserInheritorUpdateBaseInputRequest,UserTestamentBaseInputRequest,GoodsDonorBaseInputRequest,OrgansDonorBaseInputRequest,LoveLeftInTheWorldBaseInputRequest, UserTestamentEditBaseInputRequest)
from src.shareLove.models import (FamilyOffice, Trust, UserBeneficiaries, UserInheritor, UserTestament,GoodsDonor,OrgansDonor,LoveLeftInTheWorld)
from src.shareLove.service import (create_family_office_trx, create_insurance_beneficiaries_trx, create_phone_beneficiaries_trx, create_trust_trx, create_user_inheritor_trx, create_user_testament_trx, create_goods_donor_trx,create_organs_donor_trx,create_love_left_in_the_world_trx, edit_family_office_trx, edit_goods_donor_trx, edit_insurance_beneficiaries_trx, edit_love_left_in_the_world_trx, edit_organs_donor_trx, edit_phone_beneficiaries_trx, edit_trust_trx, edit_user_inheritor_meta_trx, edit_user_inheritor_trx, get_family_office_trx, get_single_user_inheritor_trx, get_trust_trx, get_user_beneficiaries_trx, get_user_inheritor_to_claim_user_dead_or_access_dead_usertrx, get_user_inheritor_trx,get_user_testament_trx,get_goods_donor_trx,get_organs_donor_trx,get_love_left_in_the_world_trx,edit_user_testament_trx, remove_goods_donor, remove_love_left_in_the_world, remove_user_beneficiaries, remove_user_inheritor)
import json
from src.secertBase.service import check_dead_user_permission
router = APIRouter()
# Delete
@router.delete("/del/user_inheritor/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def del_user_inheritor(id:str,request: Request,db:Session = Depends(get_db)):
    # 1. Prepare the data
    id = int(id) 
    user_id = request.state.user_id
    
    # user_id = 'e2749e29-1e01-4896-ae71-95f2474092aa'
    # 2. Create Transaction to DB 
    res = await remove_user_inheritor(id, user_id, db)
    return create_success_response(res)

@router.delete("/del/love_left_in_the_world/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def del_love_left_in_the_world(id:str,request: Request,db:Session = Depends(get_db)):
    # 1. Prepare the data
    id = int(id) 
    user_id = request.state.user_id
    
    # user_id = 'e2749e29-1e01-4896-ae71-95f2474092aa'
    # 2. Create Transaction to DB 
    res = await remove_love_left_in_the_world(id, user_id, db)
    return create_success_response(res)

@router.delete("/del/goods_donor/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def del_goods_donor(id:str,request: Request,db:Session = Depends(get_db)):
    # 1. Prepare the data
    id = int(id) 
    user_id = request.state.user_id
    
    # user_id = 'e2749e29-1e01-4896-ae71-95f2474092aa'
    # 2. Create Transaction to DB 
    res = await remove_goods_donor(id, user_id, db)
    return create_success_response(res)

@router.delete("/del/user_beneficiaries/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def del_user_beneficiaries(id:str,request: Request,db:Session = Depends(get_db)):
    # 1. Prepare the data
    id = int(id) 
    user_id = request.state.user_id
    
    # user_id = 'e2749e29-1e01-4896-ae71-95f2474092aa'
    # 2. Create Transaction to DB 
    await remove_user_beneficiaries(id, user_id, db)
    return create_success_response({})

# @router.delete("/del/family_office/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
# @handle_exceptions
# async def del_family_office(id:str,request: Request,db:Session = Depends(get_db)):
    
#     # 1. Prepare the data
#     id = int(id)
#     user_id = request.state.user_id
#     # 2. Create Transaction to DB 
#     res = await remove_family_office_trx(id,user_id,db)
#     return create_success_response(res)


# @router.delete("/del/trust/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
# @handle_exceptions
# async def del_trust(id:str,request: Request,db:Session = Depends(get_db)):
    
#     # 1. Prepare the data
#     id = int(id)
#     user_id = request.state.user_id
#     # 2. Create Transaction to DB 
#     res = await remove_trust_trx(id,user_id,db)
#     return create_success_response(res)


# @router.delete("/del/user_testament/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
# @handle_exceptions
# async def del_user_testament(id:str,request: Request,db:Session = Depends(get_db)):
    
#     # 1. Prepare the data
#     id = int(id)
#     user_id = request.state.user_id
#     # 2. Create Transaction to DB 
#     res = await remove_user_testament_trx(id,user_id,db)
#     return create_success_response(res)


# Edit
@router.put("/edit/user_inheritor/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def edit_user_inheritor(id:str,request: Request,reqBody:UserInheritorUpdateBaseInputRequest,db:Session = Depends(get_db)):
    
    # 1. Prepare the data
    id = int(id)  
    inheritor_id = request.state.user_id
    # user_id = 'e2749e29-1e01-4896-ae71-95f2474092aa'
    # 2. Create Transaction to DB 
    res = await edit_user_inheritor_trx(inheritor_id=inheritor_id,uid=id,updates=reqBody,db=db)
    return create_success_response({'uid':res})

@router.put("/edit/user_inheritor_meta/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def edit_user_inheritor_meta(id:str,request: Request,reqBody:UserInheritorMetaBaseInputRequest,db:Session = Depends(get_db)):
    # 1. Prepare the data
    id = int(id)
    user_id = request.state.user_id
    # user_id = '1c0b6935-598f-426b-a785-4279f50b37c5' # inheritor_user_id from Middleware
    # 2. Create Transaction to DB 
    res = await edit_user_inheritor_meta_trx(user_id=user_id,id=id,updates=reqBody,db=db)
    return create_success_response(res)


@router.put("/edit/family_office/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def edit_family_office(id:str,request: Request,reqBody:FamilyOfficeEditBaseInputRequest,db:Session = Depends(get_db)):
    
    # 1. Prepare the data
    id = int(id)
    user_id = request.state.user_id
    # 2. Create Transaction to DB 
    res = await edit_family_office_trx(user_id=user_id,id=id,updates=reqBody,db=db)
    return create_success_response(res)


@router.put("/edit/trust/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def edit_trust(id:str,request: Request,reqBody:TrustEditBaseInputRequest,db:Session = Depends(get_db)):
    
    # 1. Prepare the data
    id = int(id)
    user_id = request.state.user_id
    # 2. Create Transaction to DB 
    res = await edit_trust_trx(user_id=user_id,id=id,updates=reqBody,db=db)
    return create_success_response(res)


@router.put("/edit/user_testament/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def edit_user_testament(id:str,request: Request,reqBody:UserTestamentEditBaseInputRequest,db:Session = Depends(get_db)):
    
    # 1. Prepare the data
    id = int(id)
    user_id = request.state.user_id
    # 2. Create Transaction to DB 
    res = await edit_user_testament_trx(user_id=user_id,id=id,updates=reqBody,db=db)
    return create_success_response(res)

@router.put("/edit/phone_beneficiaries/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def edit_phone_beneficiaries(id:str,request: Request,reqBody:PhoneBeneficiariesBaseInputRequest,db:Session = Depends(get_db)):
    # required_keys = {"beneficiary_type","platform_or_company","first_name","last_name","relation","contact_country_code","contact_number"}
    # if set(reqBody.keys()) == required_keys:
    # 1. Prepare the data
    # 使用字典推導式移除值為 None 的鍵
    # reqBody = {k: v for k, v in reqBody.items() if v is not None}
    user_id = request.state.user_id
    id = int(id)
    # 2. Create Transaction to DB 
    res = await edit_phone_beneficiaries_trx(user_id=user_id,id=id,updates=reqBody,db=db)
    return create_success_response(res)


@router.put("/edit/insurance_beneficiaries/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def edit_insurance_beneficiaries(id:str,request: Request,reqBody:InsuranceBeneficiariesBaseInputRequest,db:Session = Depends(get_db)):
    # required_keys = {"beneficiary_type","platform_or_company","first_name","last_name","relation","contact_country_code","contact_number"}
    # if set(reqBody.keys()) == required_keys:
    # 1. Prepare the data
    # 使用字典推導式移除值為 None 的鍵
    # reqBody = {k: v for k, v in reqBody.items() if v is not None}
    user_id = request.state.user_id
    id = int(id)
    # 2. Create Transaction to DB 
    res = await edit_insurance_beneficiaries_trx(user_id=user_id,id=id,updates=reqBody,db=db)
    return create_success_response(res)



@router.put("/edit/goods_donor/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def edit_goods_donor(id:str,request: Request,files: List[UploadFile] = None,req_data:str=Form(...),oss_data:str=Form(...),db:Session = Depends(get_db)):
    # 1. Prepare the data
    id = int(id)
    req_data = json.loads(req_data)
    oss_data = json.loads(oss_data)
    user_id = request.state.user_id
    # 2. Create Transaction to DB 
    res = await edit_goods_donor_trx(user_id=user_id,id=id,req_data=req_data,oss_data=oss_data,files=files,db=db)
    return create_success_response(res)

@router.put("/edit/organs_donor/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def edit_organs_donor(id:str,request: Request,reqBody:OrgansDonorBaseInputRequest,db:Session = Depends(get_db)):
    # 1. Prepare the data
    id = int(id)
    user_id = request.state.user_id
    # 2. Create Transaction to DB 
    res = await edit_organs_donor_trx(user_id=user_id,id=id,updates=reqBody,db=db)
    return create_success_response(res)

@router.put("/edit/love_left_in_the_world/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def edit_love_left_in_the_world(id:str,request: Request,reqBody:LoveLeftInTheWorldBaseInputRequest,db:Session = Depends(get_db)):
    # 1. Prepare the data
    id = int(id)
    user_id = request.state.user_id
    # 2. Create Transaction to DB 
    res = await edit_love_left_in_the_world_trx(user_id=user_id,id=id,updates=reqBody,db=db)
    return create_success_response(res)

@router.get("/get/user_inheritor_by_id/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def get_single_user_inheritor(id:str,request: Request,db:Session = Depends(get_db)):
    # 1. Prepare the data
    user_id = request.state.user_id
    id = int(id)
    fl:List = [UserInheritor.user_id == user_id,UserInheritor.id == id]
    # 2. Create Transaction to DB
    res = await get_single_user_inheritor_trx(fl, db=db)
    return create_success_response(res)


@router.get("/get/user_inheritor", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def get_user_inheritor(request: Request,db:Session = Depends(get_db)):
    # 1. Prepare the data
    user_id = request.state.user_id
    # fl:List = [UserInheritor.user_id == user_id,UserInheritor.inheritor_user_id != None]
    fl:List = [UserInheritor.user_id == user_id]
    # user_id = 'e2749e29-1e01-4896-ae71-95f2474092aa' # userId from Middleware
    
    # 2. Create Transaction to DB 
    # for user to view inheritor invite status, expected return ----> inviate_status enum('WIP','ACCEPT','REJECT','EXPIRE') and who did not register deepsoul app account.
    res = await get_user_inheritor_trx(fl=fl, db=db,user_id=user_id)
    return create_success_response(res)


@router.get("/get/user_inheritor_by_accept", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def get_user_inheritor_by_accept(request: Request,db:Session = Depends(get_db),deaduserID: str | None = None):
    # log_info(f'deaduserID----->{deaduserID}')
    # 1. Prepare the data
    if deaduserID:
        user_id = deaduserID
        fl:List = [UserInheritor.inheritor_user_id == user_id,UserInheritor.inviate_status == "ACCEPT"]
        # for inheritor to view dead user, expected return pass away info meta ----> approval_status enum('VERIFY','APPROVAL','REJECT')
        res = await get_user_inheritor_to_claim_user_dead_or_access_dead_usertrx(fl=fl, db=db) 
    else:
        user_id = request.state.user_id
        fl:List = [UserInheritor.inheritor_user_id == user_id,UserInheritor.inviate_status == "ACCEPT"]
        # after inheritor accepted user invite via sms ulink, for inheritor to view all user what is status such as ('WIP','ACCEPT','REJECT','EXPIRE')
        # expected return user_inheritor inviate_status ('WIP','ACCEPT','REJECT','EXPIRE')
        res = await get_user_inheritor_to_claim_user_dead_or_access_dead_usertrx(fl=fl, db=db)
    # inheritor_id = request.state.user_id
    
    
    
    
    # 2. Create Transaction to DB 
    
    return create_success_response(res)


@router.get("/get/user_beneficiaries_by_id/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def get_user_beneficiaries(id:str,request: Request,db:Session = Depends(get_db),deaduserID: str | None = None):
    # 1. Prepare the data
    user_id = deaduserID if deaduserID else request.state.user_id
    id = int(id)
    fl:List = [UserBeneficiaries.user_id == user_id,UserBeneficiaries.id == id]
    
    # res = await get_user_beneficiaries_trx(fl=fl, db=db)
    res = await get_user_beneficiaries_trx(fl=fl, db=db,cb=check_dead_user_permission(user_id=request.state.user_id,dead_user_id=user_id,db=db,key="LB")) if deaduserID else await get_user_beneficiaries_trx(fl=fl, db=db)
    return create_success_response(res)



@router.get("/get/user_beneficiaries_by_cate/{cate}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def get_user_beneficiaries(cate:str,request: Request,db:Session = Depends(get_db),deaduserID: str | None = None):
    # 1. Prepare the data
    user_id = deaduserID if deaduserID else request.state.user_id
    fl:List = [UserBeneficiaries.user_id == user_id,UserBeneficiaries.beneficiary_type == cate]
    
    # res = await get_user_beneficiaries_trx(fl=fl, db=db)
    res = await get_user_beneficiaries_trx(fl=fl, db=db,cb=check_dead_user_permission(user_id=request.state.user_id,dead_user_id=user_id,db=db,key="LB")) if deaduserID else await get_user_beneficiaries_trx(fl=fl, db=db)
    return create_success_response(res)
    
    

@router.get("/get/family_office", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def get_family_office(request: Request,db:Session = Depends(get_db),deaduserID: str | None = None):
    # 1. Prepare the data
    user_id = deaduserID if deaduserID else request.state.user_id

    fl:List = [FamilyOffice.user_id == user_id]
    
    # res = await get_user_testament_trx(fl=fl, db=db)
    res = await get_family_office_trx(fl=fl, db=db,cb=check_dead_user_permission(user_id=request.state.user_id,dead_user_id=user_id,db=db,key="LB")) if deaduserID else await get_family_office_trx(fl=fl, db=db)
    return create_success_response(res)

@router.get("/get/trust", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def get_trust(request: Request,db:Session = Depends(get_db),deaduserID: str | None = None):
    # 1. Prepare the data
    user_id = deaduserID if deaduserID else request.state.user_id

    fl:List = [Trust.user_id == user_id]
    
    # res = await get_user_testament_trx(fl=fl, db=db)
    res = await get_trust_trx(fl=fl, db=db,cb=check_dead_user_permission(user_id=request.state.user_id,dead_user_id=user_id,db=db,key="LB")) if deaduserID else await get_trust_trx(fl=fl, db=db)
    return create_success_response(res)


@router.get("/get/user_testament", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def get_user_testament(request: Request,db:Session = Depends(get_db),deaduserID: str | None = None):
    # 1. Prepare the data
    user_id = deaduserID if deaduserID else request.state.user_id

    fl:List = [UserTestament.user_id == user_id]
    
    # res = await get_user_testament_trx(fl=fl, db=db)
    res = await get_user_testament_trx(fl=fl, db=db,cb=check_dead_user_permission(user_id=request.state.user_id,dead_user_id=user_id,db=db,key="LB")) if deaduserID else await get_user_testament_trx(fl=fl, db=db)
    return create_success_response(res)


@router.get("/get/goods_donor_by_id/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def get_user_testament(id:str,request: Request,db:Session = Depends(get_db),deaduserID: str | None = None):
    # 1. Prepare the data
    user_id = deaduserID if deaduserID else request.state.user_id
    id = int(id)
    fl:List = [GoodsDonor.user_id == user_id,GoodsDonor.id == id]
    # 2. Create Transaction to DB 
    # res = await get_goods_donor_trx(fl=fl, db=db)
    res = await get_goods_donor_trx(fl=fl, db=db,cb=check_dead_user_permission(user_id=request.state.user_id,dead_user_id=user_id,db=db,key="LB")) if deaduserID else await get_goods_donor_trx(fl=fl, db=db)
    return create_success_response(res)

@router.get("/get/goods_donor", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def get_goods_donor(request: Request,db:Session = Depends(get_db),deaduserID: str | None = None):
    # 1. Prepare the data
    user_id = deaduserID if deaduserID else request.state.user_id
    fl:List = [GoodsDonor.user_id == user_id]
    # 2. Create Transaction to DB 
    # res = await get_goods_donor_trx(fl=fl, db=db)
    res = await get_goods_donor_trx(fl=fl, db=db,cb=check_dead_user_permission(user_id=request.state.user_id,dead_user_id=user_id,db=db,key="LB")) if deaduserID else await get_goods_donor_trx(fl=fl, db=db)
    return create_success_response(res)

@router.get("/get/organs_donor", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def get_user_testament(request: Request,db:Session = Depends(get_db),deaduserID: str | None = None):
    # 1. Prepare the data
    user_id = deaduserID if deaduserID else request.state.user_id
    fl:List = [OrgansDonor.user_id == user_id]
    # 2. Create Transaction to DB 
    # res = await get_organs_donor_trx(fl=fl, db=db)
    res = await get_organs_donor_trx(fl=fl, db=db,cb=check_dead_user_permission(user_id=request.state.user_id,dead_user_id=user_id,db=db,key="LB")) if deaduserID else await get_organs_donor_trx(fl=fl, db=db)
    return create_success_response(res)

@router.get("/get/love_left_in_the_world/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def get_user_love_left_in_the_world(id:str,request: Request,db:Session = Depends(get_db),deaduserID: str | None = None):
    # 1. Prepare the data
    user_id = deaduserID if deaduserID else request.state.user_id
    id=int(id)
    # 2. Create Transaction to DB 
    fl:List = [LoveLeftInTheWorld.user_id == user_id, LoveLeftInTheWorld.id==id]
    # res = await get_love_left_in_the_world_trx(fl=fl, db=db)
    res = await get_love_left_in_the_world_trx(fl=fl, db=db,cb=check_dead_user_permission(user_id=request.state.user_id,dead_user_id=user_id,db=db,key="LB")) if deaduserID else await get_love_left_in_the_world_trx(fl=fl, db=db)
    return create_success_response(res)


@router.get("/get/love_left_in_the_world", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def get_user_love_left_in_the_world(request: Request,db:Session = Depends(get_db),deaduserID: str | None = None):
    # 1. Prepare the data
    user_id = deaduserID if deaduserID else request.state.user_id
    fl:List = [LoveLeftInTheWorld.user_id == user_id]
    # 2. Create Transaction to DB 
    # res = await get_love_left_in_the_world_trx(fl=fl, db=db)
    res = await get_love_left_in_the_world_trx(fl=fl, db=db,cb=check_dead_user_permission(user_id=request.state.user_id,dead_user_id=user_id,db=db,key="LB")) if deaduserID else await get_love_left_in_the_world_trx(fl=fl, db=db)
    return create_success_response(res)

@router.post("/create/user_inheritor", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def create_user_inheritor(request: Request,reqBody:UserInheritorBaseInputRequest,db:Session = Depends(get_db)):
    # 1. Prepare the data
    # 如果要拎黎user id 應該要用 phone_num-> authgear -> authgear_id -> userTable-> id
    user_id = request.state.user_id # userId from Middleware
    # user_id = "1c0b6935-598f-426b-a785-4279f50b37c5" # auth gear - +85251823007 user id
    # 2. Create Transaction to DB 
    res = await create_user_inheritor_trx(reqData=reqBody, user_id=user_id,db=db)

    return create_success_response(res)

@router.post("/create/phone_beneficiaries", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def create_user_beneficiaries(request: Request,user_beneficiaries:PhoneBeneficiariesBaseInputRequest,db:Session = Depends(get_db)):
    # 1. Prepare the data
    user_id = request.state.user_id # userId from Middleware
    # user_id = 'e2749e29-1e01-4896-ae71-95f2474092aa' # userId from Middleware
    # 2. Create Transaction to DB 
    res = await create_phone_beneficiaries_trx(reqData=user_beneficiaries, user_id=user_id, db=db)
    return create_success_response({"id":res})

@router.post("/create/insurance_beneficiaries", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def create_user_beneficiaries(request: Request,user_beneficiaries:InsuranceBeneficiariesBaseInputRequest,db:Session = Depends(get_db)):
    # 1. Prepare the data
    user_id = request.state.user_id # userId from Middleware
    # user_id = 'e2749e29-1e01-4896-ae71-95f2474092aa' # userId from Middleware
    # 2. Create Transaction to DB 
    res = await create_insurance_beneficiaries_trx(reqData=user_beneficiaries, user_id=user_id, db=db)

    return create_success_response({"id":res})

@router.post("/create/user_testament", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def create_user_testament(request: Request,user_testament:UserTestamentBaseInputRequest,db:Session = Depends(get_db)):
    
    # 1. Prepare the data
    user_id = request.state.user_id # userId from Middleware
    # 2. Create Transaction to DB
    # log_info(user_testament) 
    res = await create_user_testament_trx(reqData=user_testament, user_id=user_id, db=db)
    return create_success_response({"id":res})
    # return create_success_response(user_testament)

@router.post("/create/family_office", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def create_family_office(request: Request,family_office:FamilyOfficeBaseInputRequest,db:Session = Depends(get_db)):
    
    # 1. Prepare the data
    user_id = request.state.user_id # userId from Middleware
    # 2. Create Transaction to DB
    # log_info(user_testament) 
    res = await create_family_office_trx(reqData=family_office, user_id=user_id, db=db)
    return create_success_response({"id":res})
    # return create_success_response(user_testament)

@router.post("/create/trust", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def create_trust(request: Request,trust:TrustBaseInputRequest,db:Session = Depends(get_db)):
    
    # 1. Prepare the data
    user_id = request.state.user_id # userId from Middleware
    # 2. Create Transaction to DB
    # log_info(user_testament) 
    res = await create_trust_trx(reqData=trust, user_id=user_id, db=db)
    return create_success_response({"id":res})
    # return create_success_response(user_testament)



@router.post("/create/goods_donor", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def create_goods_donor(request: Request,files: List[UploadFile] = None,req_data:str=Form(...),oss_data:str=Form(...),db:Session = Depends(get_db)):
    # 1. Prepare the data
    user_id = request.state.user_id # userId from Middleware
    req_data = json.loads(req_data)
    oss_data = json.loads(oss_data)
    
    # user_id = 'e2749e29-1e01-4896-ae71-95f2474092aa' # userId from Middleware
    # 2. Create Transaction to DB 
    res = await create_goods_donor_trx(reqData=req_data,ossData=oss_data,files=files,user_id=user_id, db=db)
    return create_success_response({"id":res})



@router.post("/create/organs_donor", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def create_organs_donor(request: Request,organs_donor:OrgansDonorBaseInputRequest,db:Session = Depends(get_db)):
    # 1. Prepare the data
    user_id = request.state.user_id # userId from Middleware
    # user_id = 'e2749e29-1e01-4896-ae71-95f2474092aa' # userId from Middleware
    # 2. Create Transaction to DB 
    
    res = await create_organs_donor_trx(reqData=organs_donor, user_id=user_id, db=db)
    return create_success_response({"id":res})



# Pydantic model for response

@router.post("/create/love_left_in_the_world", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def create_love_left_in_the_world(request: Request,love_left_in_the_world:LoveLeftInTheWorldBaseInputRequest,db:Session = Depends(get_db)):
    
    # 1. Prepare the data
    user_id = request.state.user_id # userId from Middleware
    # user_id = 'e2749e29-1e01-4896-ae71-95f2474092aa' # userId from Middleware
    # 2. Create Transaction to DB 
    res = await create_love_left_in_the_world_trx(reqData=love_left_in_the_world, user_id=user_id, db=db)
    return create_success_response({"id":res})



