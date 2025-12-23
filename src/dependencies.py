from fastapi import Depends, Request
from sqlalchemy.orm import Session

from fastapi.security import HTTPBearer
from pydantic import BaseModel
from src.adminAuth.models import Staff
from src.loggerServices import log_error
from src.utils.jwtUtil import  parse_header,getJWTUserInfo
from src.utils.jwtUtilAdminPortal import  parse_header_admin_portal,getJWTUserInfo_admin_portal
from src.exceptions import BadReqExpection, GeneralErrorExcpetion, UserNotFoundErrorExpection,TokenInvalidExpection
from src.database import get_db
from typing import List, Optional, Dict, Any
from src.auth.models import PhoneMaster, User

from jwt import PyJWTError
# from src.payment.service import query_subscription_still_permission_valid
from src.transaction import wrap_insert_mapping_func
class StandardAttributes(BaseModel):
    # Do not enable these fields because first time user registration will not have these fields
    # family_name: Optional[str]
    gender: Optional[str] = None
    given_name: Optional[str] = None
    phone_number: Optional[str] = None
    phone_number_verified: Optional[bool] = None
    updated_at: Optional[int] = None
    nickname: Optional[str] = None


class TokenPayload(BaseModel):
    aud: List[str]
    client_id: str
    exp: int
    # https_authgear_com_claims_user_can_reauthenticate: bool
    # https_authgear_com_claims_user_is_anonymous: bool
    # https_authgear_com_claims_user_is_verified: bool
    # https_authgear_com_claims_user_roles: List[Any]
    iat: int
    iss: str
    jti: str
    standard_attributes: StandardAttributes | Optional[Dict[str, Any]] = {}
    sub: str

# Create a reusable HTTPBearer instance
security = HTTPBearer()

def verify_token(request: Request, db: Session = Depends(get_db)):
    headers = request.headers
    token_data = None
    
    try:
        authz_header = headers.get("X-JWT-Token")
        if authz_header is None:
            raise TokenInvalidExpection("JWT Token is missing")
        token = parse_header(authz_header)
        if token:
            # log_info(f"JWT token: {token}")
            user_info = getJWTUserInfo(token)
            if not user_info:
                raise UserNotFoundErrorExpection("JWT token is invalid")
            #Remark - user_id can be null when user just registered from authgear and call validation api
            user_sub = user_info.get("sub")
            user_id = get_user_id_from_db(user_sub, db)
            # dead_user_id = get_dead_user_id_from_db(user_id, db)
            request.state.user_info = TokenPayload(**user_info)
            request.state.user_id = user_id
            
            # request.state.dead_user_id = dead_user_id
            token_data = user_info
    except PyJWTError as e:
        log_error(f"JWT token is invalid: {e}")
        raise TokenInvalidExpection("Could not validate credentials")
    return token_data

def get_user_id_from_db(authgear_sub: str, db: Session):
    try:
        user = db.query(User).filter(User.authgear_id == authgear_sub).first()
        if not user:
            return ""
        return user.id        
    except Exception as e:
        log_error(f"get_user_id_from_db: {e}")
        raise UserNotFoundErrorExpection(f"JWT token is invalid: {e}")
    
def verify_admin_portal_token(request: Request, db: Session = Depends(get_db)):    
    headers = request.headers
    token_data = None
    
    try:
        authz_header = headers.get("X-JWT-Token")
        if authz_header is None:
            raise Exception("JWT Token is missing")
        token = parse_header_admin_portal(authz_header)
        if token:
            user_info = getJWTUserInfo_admin_portal(token)
            if not user_info:
                raise Exception("JWT token is invalid")
            user_sub = user_info.get("sub")
            user_id = get_user_id_from_staff_db(user_sub, db)
            
            request.state.user_info = TokenPayload(**user_info)
            request.state.user_id = user_id
            
            token_data = user_info
            return token_data
    except Exception as e:        
        log_error(f"JWT token is invalid-------->: {e}")
        raise GeneralErrorExcpetion(str(e))
    


def get_user_id_from_staff_db(authgear_sub: str, db: Session):
    try:
        user = db.query(Staff).filter(Staff.authgear_id == authgear_sub).first()
        if not user:
            insert_obj = Staff(authgear_id=authgear_sub,role="admin")
            wrap_insert_mapping_func(db, insert_obj)
            # TODO get phone number insert into PHONEMASTER table
            db.commit()
            return ""
        return user.id        
    except Exception as e:
        db.rollback()
        log_error(f"get_user_id_from_db: {e}")
        raise UserNotFoundErrorExpection(f"JWT token is invalid: {e}")
