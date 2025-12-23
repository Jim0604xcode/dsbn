from typing import Optional
from pydantic import BaseModel, Field, AfterValidator,BeforeValidator
from datetime import datetime
from typing_extensions import Annotated
from src.schemas import ApiSuccessResponseModel
from src.auth.validators import check_gender, check_language, check_phone_number
from src.auth.models import LanguageEnum


class LanguageBaseInputRequest(BaseModel):
    language:Annotated[LanguageEnum,AfterValidator(check_language)]
    
    
    class Config:
        from_attributes = True
        extra = extra='forbid'


class AuthgearStandardAttributes(BaseModel):    
    family_name: str = Field(..., min_length=1, max_length=50)
    given_name: str = Field(..., min_length=1, max_length=50)
    nickname: Optional[str] = Field(None, min_length=1, max_length=50)
    birthdate: str
    gender:  Annotated[str, BeforeValidator(check_gender)]
    picture: str | None = None
    phone_number: Optional[str] = None
    phone_number_verified:Optional[bool] = None

class PostAuthgearUserInfo(BaseModel):
    formattedName: str
    standardAttributes: AuthgearStandardAttributes
    authgear_id: str
    class Config:
        from_attributes = True

class AuthgearCustomAttributes(BaseModel):
    is_deceased: int
    pending_confirm_decease: int



class UserUpdateMobileInputRequest(BaseModel):
    old_phone_number:str
    new_phone_number: str
class UserUpdateMobileVerifyInputRequest(BaseModel):
    otp_code:str
    password: str    
    new_phone_number: str

class UserFullyRegisterInputRequest(BaseModel):
    standardAttributes: AuthgearStandardAttributes
    customAttributes: AuthgearCustomAttributes



class UserOut(BaseModel):
    id: str
    authgear_id: str
    created_at: datetime
    class Config:
        from_attributes = True

class UserProfileImageResponse(BaseModel):
    url: str      
      
class UserProfileImageUploadSuccessModel(ApiSuccessResponseModel):
    data: UserProfileImageResponse


class validionRequest(BaseModel):
    device_uuid: str
    class Config:
        from_attributes = True