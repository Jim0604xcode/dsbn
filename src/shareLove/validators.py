from src.exceptions import GeneralErrorExcpetion
from src.loggerServices import log_error, log_info
from datetime import datetime
from src.shareLove.models import BeneficiaryTypeEnum,DidArrangeOrganDonorEnum, InviateStatusEnum
def datetime_common_check(v) -> bool:
    try:
        if isinstance(v, datetime):
            return isinstance(v, datetime)
        elif isinstance(v, str):
            return isinstance(datetime.fromisoformat(v),datetime)
        else:    
            return False
    except ValueError as e:
        log_error(v)
        return False
def string_common_check(v,less_than, more_than) -> bool:
    if not isinstance(v, str):
        raise GeneralErrorExcpetion("输入必须是字符串")
    length_of_string = len(v)
    if length_of_string > more_than or length_of_string < less_than:
        return True
    return False

def check_user_inheritor_permission_meta(v) -> str:
    if isinstance(v,bool) == False:
        raise GeneralErrorExcpetion('Field only between True and False')
    return v
def check_phone_number(v)->str:
    if string_common_check(v,1,100):
        raise GeneralErrorExcpetion('Phone number exceeds 100 characters or less than 1 character')
    return v
def check_invitation_expire_date(v)->str:
    if datetime_common_check(v) == False:
        raise GeneralErrorExcpetion('Invitation expire date type only dateTime')
    return v
def check_inviate_status(v) -> str:
    if v not in {InviateStatusEnum.WIP, InviateStatusEnum.ACCEPT, InviateStatusEnum.REJECT, InviateStatusEnum.EXPIRE}:
        raise GeneralErrorExcpetion('InviateStatusEnum type only between WIP and ACCEPT and REJECT and EXPIRE')
    return v


def check_platform_or_company(v)->str:
    if string_common_check(v,1,100):
        raise GeneralErrorExcpetion('Platform or Company exceeds 100 characters or less than 1 character')
    return v

def check_first_name(v)->str:
    if string_common_check(v,1,50):
        raise GeneralErrorExcpetion('First name exceeds 50 characters or less than 1 character')
    return v

def check_last_name(v)->str:
    if string_common_check(v,1,100):
        raise GeneralErrorExcpetion('Last name exceeds 100 characters or less than 1 character')
    return v

def check_relation(v)->str:
    if string_common_check(v,1,50):
        raise GeneralErrorExcpetion('Relation name exceeds 50 characters or less than 1 character')
    return v


def check_contact_country_code(v)->str:
    if string_common_check(v,1,100):
        raise GeneralErrorExcpetion('Contact country code exceeds 100 characters or less than 1 character')
    return v

def check_contact_number(v)->str:
    if string_common_check(v,1,100):
        raise GeneralErrorExcpetion('Contact number exceeds 100 characters or less than 1 character')
    return v


def check_beneficiary_type(v) -> str:
    if v not in {BeneficiaryTypeEnum.PHONE, BeneficiaryTypeEnum.INSURANCE}:
        raise GeneralErrorExcpetion('Beneficiary type only between PHONE and INSURANCE')
    return v

def check_did_testament(v)->str:
    if isinstance(v,bool) == False:
        raise GeneralErrorExcpetion('Did testament type only between True and False')
    return v

def check_did_family_office(v)->str:
    if isinstance(v,bool) == False:
        raise GeneralErrorExcpetion('Did family office type only between True and False')
    return v

def check_did_trust(v)->str:
    if isinstance(v,bool) == False:
        raise GeneralErrorExcpetion('Did trust type only between True and False')
    return v

def check_did_testament_date(v)->str:
    
    if v is None:
        return None  # Allow None
    if datetime_common_check(v) == False:
        raise GeneralErrorExcpetion('Did testament date type only dateTime')
    return v

def check_did_family_office_date(v)->str:
    
    if v is None:
        return None  # Allow None
    if datetime_common_check(v) == False:
        raise GeneralErrorExcpetion('Did family office date type only dateTime')
    return v

def check_did_trust_date(v)->str:
    
    if v is None:
        return None  # Allow None
    if datetime_common_check(v) == False:
        raise GeneralErrorExcpetion('Did trust date type only dateTime')
    return v
    
def check_testament_store_in(v)->str:
    if string_common_check(v,1,255):
        raise GeneralErrorExcpetion('Testament store in exceeds 255 characters or less than 1 character')
    return v

def check_family_office_name(v)->str:
    if string_common_check(v,1,100):
        raise GeneralErrorExcpetion('Family office name in exceeds 100 characters or less than 1 character')
    return v

def check_trust_name(v)->str:
    if string_common_check(v,1,100):
        raise GeneralErrorExcpetion('Trust name exceeds 100 characters or less than 1 character')
    return v

def check_registeration_address(v)->str:
    if string_common_check(v,0,1000):
        raise GeneralErrorExcpetion('Registeration ddress exceeds 1000 characters or less than 1 character')
    return v

def check_contact_person(v)->str:
    if string_common_check(v,1,100):
        raise GeneralErrorExcpetion('Contact person exceeds 100 characters or less than 1 character')
    return v

def check_mobile(v)->str:
    if string_common_check(v,0,100):
        raise GeneralErrorExcpetion('Mobile exceeds 100 characters or less than 1 character')
    return v

def check_settlor(v)->str:
    if string_common_check(v,0,100):
        raise GeneralErrorExcpetion('Settlor exceeds 100 characters or less than 1 character')
    return v

def check_beneficiary(v)->str:
    if string_common_check(v,1,100):
        raise GeneralErrorExcpetion('Beneficiary exceeds 100 characters or less than 1 character')
    return v


def check_comment(v)->str:
    if string_common_check(v,0,1000):
        raise GeneralErrorExcpetion('Comment exceeds 1000 characters or less than 1 character')
    return v

def check_image_url(v)->str:
    if string_common_check(v,1,6000):
        raise GeneralErrorExcpetion('Image url exceeds 6000 characters or less than 1 character')
    return v

def check_goods_info(v)->str:
    if string_common_check(v,1,255):
        raise GeneralErrorExcpetion('Goods info exceeds 255 characters or less than 1 character')
    return v

def check_donor_organization(v)->str:
    if string_common_check(v,1,100):
        raise GeneralErrorExcpetion('Donor organization exceeds 100 characters or less than 1 character')
    return v

def check_did_arrange_organ_donor(v)->str:
    
    if v not in {DidArrangeOrganDonorEnum.YES, DidArrangeOrganDonorEnum.NO, DidArrangeOrganDonorEnum.NOT_YET}:
        raise GeneralErrorExcpetion('Did arrange organ donor only between YES and NO and NOT_YET')
    return v

      
def check_contact_organization(v)->str:
    if string_common_check(v,0,100):
        raise GeneralErrorExcpetion('Contact organization exceeds 100 characters or less than 1 character')
    return v

def check_title(v)->str:
    if string_common_check(v,1,100):
        raise GeneralErrorExcpetion('Title exceeds 100 characters or less than 1 character')
    return v    
def check_content(v)->str:
    if string_common_check(v,1,1000):
        raise GeneralErrorExcpetion('Content exceeds 100 characters or less than 1 character')
    return v    
def check_transaction_id(v)->str:
    if string_common_check(v,1,100):
        raise GeneralErrorExcpetion('Transaction ID exceeds 100 characters or less than 1 character')
    return v    

