from pydantic import BaseModel,AfterValidator
from typing import Optional
from datetime import date, datetime
from typing_extensions import Annotated
from src.shareLove.models import BeneficiaryTypeEnum,DidArrangeOrganDonorEnum, InviateStatusEnum


from src.shareLove.validators import check_beneficiary, check_contact_person, check_did_family_office, check_did_family_office_date, check_did_trust, check_did_trust_date, check_family_office_name, check_goods_info, check_inviate_status, check_invitation_expire_date, check_mobile, check_phone_number, check_platform_or_company,check_first_name,check_last_name, check_registeration_address,check_relation,check_contact_country_code,check_contact_number,check_beneficiary_type,check_did_testament,check_did_testament_date, check_settlor,check_testament_store_in,check_comment,check_image_url,check_goods_info,check_donor_organization,check_did_arrange_organ_donor,check_contact_organization,check_title,check_content, check_trust_name, check_user_inheritor_permission_meta

class UserInheritorMetaBaseInputRequest(BaseModel):
    LB:Annotated[bool,AfterValidator(check_user_inheritor_permission_meta)]
    OP:Annotated[bool,AfterValidator(check_user_inheritor_permission_meta)]
    LET:Annotated[bool,AfterValidator(check_user_inheritor_permission_meta)]
    SB:Annotated[bool,AfterValidator(check_user_inheritor_permission_meta)]
    HM:Annotated[bool,AfterValidator(check_user_inheritor_permission_meta)]
    MTS:Annotated[bool,AfterValidator(check_user_inheritor_permission_meta)]
    LS:Annotated[bool,AfterValidator(check_user_inheritor_permission_meta)]
    FC:Annotated[bool,AfterValidator(check_user_inheritor_permission_meta)]
    PE:Annotated[bool,AfterValidator(check_user_inheritor_permission_meta)]
    

class UserInheritorBaseInputRequest(UserInheritorMetaBaseInputRequest):
    sender_name:Annotated[str,AfterValidator(check_first_name)] # not save into DB
    phone_number:Annotated[str,AfterValidator(check_phone_number)]
    first_name:Annotated[str,AfterValidator(check_first_name)] # not save into DB
    last_name:Annotated[str,AfterValidator(check_last_name)] # not save into DB
    class Config:
        from_attributes = True
        extra = extra='forbid'
class ReSendSMSBaseInputRequest(BaseModel):
    sender_name:Annotated[str,AfterValidator(check_first_name)] # not save into DB
    class Config:
        from_attributes = True
        extra = extra='forbid'
    
class UserInheritorUpdateBaseInputRequest(BaseModel):
    inviate_status:Annotated[InviateStatusEnum,AfterValidator(check_inviate_status)]
    class Config:
        from_attributes = True
        extra = extra='forbid'


class UserBeneficiariesMetaBaseInputRequest(BaseModel):
    contact_country_code:Optional[Annotated[str, AfterValidator(check_contact_country_code)]]
    contact_number:Optional[Annotated[str, AfterValidator(check_contact_number)]]

class PhoneBeneficiariesBaseInputRequest(UserBeneficiariesMetaBaseInputRequest):
    beneficiary_type:Annotated[BeneficiaryTypeEnum,AfterValidator(check_beneficiary_type)]
    platform_or_company:Annotated[str,AfterValidator(check_platform_or_company)] # encrypt
    first_name:Annotated[str,AfterValidator(check_first_name)] # encrypt
    last_name:Annotated[str,AfterValidator(check_last_name)] # encrypt
    relation:Annotated[str,AfterValidator(check_relation)] # encrypt
    class Config:
        from_attributes = True
        extra = extra='forbid'

class InsuranceBeneficiariesBaseInputRequest(BaseModel):
    beneficiary_type:Annotated[BeneficiaryTypeEnum,AfterValidator(check_beneficiary_type)]
    platform_or_company:Annotated[str,AfterValidator(check_platform_or_company)] # encrypt
    first_name:Annotated[str,AfterValidator(check_first_name)] # encrypt
    last_name:Annotated[str,AfterValidator(check_last_name)] # encrypt
    relation:Annotated[str,AfterValidator(check_relation)] # encrypt
    class Config:
        from_attributes = True
        extra = extra='forbid'

class UserTestamentBaseInputRequest(BaseModel):
    did_testament:Annotated[bool,AfterValidator(check_did_testament)]
    did_testament_date: Annotated[str,AfterValidator(check_did_testament_date)]
    testament_store_in: Annotated[str,AfterValidator(check_testament_store_in)] # encrypt
    comment:Annotated[str,AfterValidator(check_comment)] # encrypt
    class Config:
        from_attributes = True
        extra = extra='forbid'

class UserTestamentEditBaseInputRequest(BaseModel):
    did_testament:Annotated[bool,AfterValidator(check_did_testament)]
    did_testament_date: Optional[str]
    testament_store_in: Optional[str] # encrypt
    comment:Optional[str] # encrypt
    class Config:
        from_attributes = True
        extra = extra='forbid'


class FamilyOfficeBaseInputRequest(BaseModel):
    did_family_office:Annotated[bool,AfterValidator(check_did_family_office)]
    did_family_office_date: Annotated[str,AfterValidator(check_did_family_office_date)]
    family_office_name: Annotated[str,AfterValidator(check_family_office_name)] # encrypt
    registeration_address: Annotated[str,AfterValidator(check_registeration_address)] # encrypt
    contact_person: Annotated[str,AfterValidator(check_contact_person)] # encrypt
    mobile: Annotated[str,AfterValidator(check_mobile)] # encrypt
    comment:Annotated[str,AfterValidator(check_comment)] # encrypt
    class Config:
        from_attributes = True
        extra = extra='forbid'

class FamilyOfficeEditBaseInputRequest(BaseModel):
    did_family_office:Annotated[bool,AfterValidator(check_did_family_office)]
    did_family_office_date: Optional[str]
    family_office_name: Optional[str] # encrypt
    registeration_address: Optional[str] # encrypt
    contact_person: Optional[str] # encrypt
    mobile: Optional[str] # encrypt
    comment:Optional[str] # encrypt
    class Config:
        from_attributes = True
        extra = extra='forbid'




class TrustBaseInputRequest(BaseModel):
    did_trust:Annotated[bool,AfterValidator(check_did_trust)]
    did_trust_date: Annotated[str,AfterValidator(check_did_trust_date)]
    trust_name: Annotated[str,AfterValidator(check_trust_name)] # encrypt
    contact_person: Annotated[str,AfterValidator(check_contact_person)] # encrypt
    mobile: Annotated[str,AfterValidator(check_mobile)] # encrypt
    settlor: Annotated[str,AfterValidator(check_settlor)] # encrypt
    beneficiary: Annotated[str,AfterValidator(check_beneficiary)] # encrypt
    comment:Annotated[str,AfterValidator(check_comment)] # encrypt
    class Config:
        from_attributes = True
        extra = extra='forbid'

class TrustEditBaseInputRequest(BaseModel):
    did_trust:Annotated[bool,AfterValidator(check_did_trust)]
    did_trust_date: Optional[str]
    trust_name: Optional[str] # encrypt
    contact_person: Optional[str] # encrypt
    mobile: Optional[str] # encrypt
    settlor: Optional[str] # encrypt
    beneficiary: Optional[str] # encrypt
    comment:Optional[str] # encrypt
    class Config:
        from_attributes = True
        extra = extra='forbid'


class GoodsDonorBaseInputRequest(BaseModel):
    image_url_1:str
    image_url_2:str
    image_url_3:str
    goods_info:Annotated[str,AfterValidator(check_goods_info)] # encrypt
    donor_organization:Annotated[str,AfterValidator(check_donor_organization)] # encrypt
    class Config:
        from_attributes = True
        extra = extra='forbid'


class OrgansDonorBaseInputRequest(BaseModel):
    did_arrange_organ_donor:Annotated[DidArrangeOrganDonorEnum,AfterValidator(check_did_arrange_organ_donor)]
    contact_organization:Annotated[str,AfterValidator(check_contact_organization)] # encrypt
    comment:Annotated[str,AfterValidator(check_comment)] # encrypt
    class Config:
        from_attributes = True
        extra = extra='forbid'
class LoveLeftInTheWorldBaseInputRequest(BaseModel):
    title:Annotated[str,AfterValidator(check_title)] # encrypt
    content:Annotated[str,AfterValidator(check_content)] # encrypt
    class Config:
        from_attributes = True
        extra = extra='forbid'
