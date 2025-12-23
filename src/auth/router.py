from fastapi import APIRouter, Depends, Request, UploadFile
from src.database import get_db
from sqlalchemy.orm import Session
from src.auth.schemas import LanguageBaseInputRequest, UserFullyRegisterInputRequest, UserOut, UserProfileImageUploadSuccessModel, UserUpdateMobileInputRequest, UserUpdateMobileVerifyInputRequest, validionRequest
from src.auth.service import create_user, edit_language_trx, do_new_user_after_full_register, update_user_mobile_trx
from src.exceptions import handle_exceptions
from src.utils.response import create_success_response
from src.models import get_error_response_model
from src.schemas import ApiSuccessResponseModel
from src.authgear.adminApi import updateUserInformation, update_user_profile_picture, query_users_by_authgear_ids
from src.loggerServices import log_info
from src.dependencies import verify_token 
from pydantic import BaseModel
from typing import List
router = APIRouter()

class QueryUsersByAuthgearIDsReqBody(BaseModel):
    authgear_ids: List[str]





@router.post("/validation", status_code=200 , response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def validation_route(request: Request,reqBoby:validionRequest, db: Session = Depends(get_db)):        
    device_uuid = reqBoby.device_uuid
    # log_info(f"Device UUID received: {device_uuid}")
    user_info = request.state.user_info
    db_user = create_user(db, user_info.sub,device_uuid) 
    user_out = UserOut.from_orm(db_user)
    return create_success_response(user_out) 

@router.put("/updateMobile", status_code=200 , response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def update_mobile(request: Request, reqBody: UserUpdateMobileInputRequest,db:Session = Depends(get_db)):
    # user_info = request.state.user_info
    # user_id = request.state.user_id
    result = await update_user_mobile_trx(reqBody,db)
    return create_success_response(result)    

# @router.post("/updateMobileVerifyFlow", status_code=200 , response_model=ApiSuccessResponseModel,responses=get_error_response_model)
# @handle_exceptions
# async def update_mobile(request: Request, reqBody: UserUpdateMobileVerifyInputRequest,db:Session = Depends(get_db)):
#     user_info = request.state.user_info
#     user_id = request.state.user_id
#     result = await update_mobile_verify_flow(
#         user_info.sub,
#         reqBody,
#         db

#     )
#     return create_success_response(result)

# @router.post("/updateMobileInitAuthenFlow", status_code=200 , response_model=ApiSuccessResponseModel,responses=get_error_response_model)
# @handle_exceptions
# async def update_mobile(request: Request, reqBody: UserUpdateMobileInputRequest):
#     user_info = request.state.user_info
#     user_id = request.state.user_id
#     result = await init_custom_authen_flow(
#         user_info.sub,
#         reqBody
#     )
#     return create_success_response(result)

@router.post("/profile/fullyRegister", status_code=200 , response_model=ApiSuccessResponseModel,responses=get_error_response_model)
async def fully_register_route(request: Request, user: UserFullyRegisterInputRequest,db:Session = Depends(get_db)):
    user_info = request.state.user_info
    user_id = request.state.user_id
    result = await updateUserInformation(
        user_info.sub,
        user.standardAttributes.model_dump(),
        user.customAttributes.model_dump()
    )
# Example:
# {
#    "updateUser":{
#       "user":{
#          "customAttributes":{
#             "is_deceased":0,
#             "pending_confirm_decease":0
#          },
#          "id":"VXNlcjpkZWIxOWIwMy0wZjI0LTRlYzItOGYwMi1iNjVkZTg4YjkxOGE",
#          "standardAttributes":{
#             "birthdate":"2025-09-08",
#             "family_name":"Wu",
#             "gender":"male",
#             "given_name":"Testing",
#             "phone_number":"+85259977197",
#             "phone_number_verified":true,
#             "updated_at":1757323684
#          }
#       }
#    }
# }
    do_new_user_after_full_register(user_id, result,db)
    return create_success_response(result)

    
@router.post("/profile/image/upload", status_code=200 , response_model=UserProfileImageUploadSuccessModel,responses=get_error_response_model)
@handle_exceptions
async def authgear_image_upload_route(request: Request, file: UploadFile):

    user_info = request.state.user_info
    result = await update_user_profile_picture(user_info.sub, file)
    return create_success_response({"url": result})

# @router.post("/get/usersByAuthGearIDs", status_code=200 , response_model=ApiSuccessResponseModel,responses=get_error_response_model)
# async def get_users_by_authgear_ids(request: Request, reqBody: QueryUsersByAuthgearIDsReqBody):
#     result = await query_users_by_authgear_ids(reqBody.authgear_ids)
#     return create_success_response(result)
    


@router.put("/editLanguage", status_code=200 , response_model=ApiSuccessResponseModel,responses=get_error_response_model)
async def editLanguage(request: Request, reqBody:LanguageBaseInputRequest,db:Session = Depends(get_db) ):
    user_id = request.state.user_id
    result = await edit_language_trx(user_id,reqBody,db)
    return create_success_response(result)


