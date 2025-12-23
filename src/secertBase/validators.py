from src.exceptions import GeneralErrorExcpetion
from src.loggerServices import log_error, log_info
from src.secertBase.models import AssetTypeEnum
def string_common_check(v,less_than, more_than) -> bool:
    if not isinstance(v, str):
        raise GeneralErrorExcpetion("输入必须是字符串")
    length_of_string = len(v)
    if length_of_string > more_than or length_of_string < less_than:
        return True
    return False
    
def check_bank_account_name(v)->str:
    if string_common_check(v,1,100):
        raise GeneralErrorExcpetion('Bank account name exceeds 100 characters or less than 1 character')
    return v    
def check_bank_account_number(v)->str:
    if string_common_check(v,1,100):
        raise GeneralErrorExcpetion('Bank account number exceeds 100 characters or less than 1 character')
    return v    
def check_currency(v)->str:
    if string_common_check(v,1,3):
        raise GeneralErrorExcpetion('Currency exceeds 3 characters or less than 1 character')
    return v    
def check_property_name(v)->str:
    if string_common_check(v,1,100):
        raise GeneralErrorExcpetion('Property name exceeds 100 characters or less than 1 character')
    return v    
def check_property_address(v)->str:
    if string_common_check(v,1,500):
        raise GeneralErrorExcpetion('Property address exceeds 100 characters or less than 1 character')
    return v    
def check_remarks(v)->str:
    if string_common_check(v,0,1000):
        raise GeneralErrorExcpetion('Remarks exceeds 1000 characters or less than 0 character')
    return v    
def check_safety_deposit_box_name(v)->str:
    if string_common_check(v,1,100):
        raise GeneralErrorExcpetion('Safety deposit box name exceeds 100 characters or less than 1 character')
    return v    
def check_safety_deposit_box_open_method(v)->str:
    if string_common_check(v,1,500):
        raise GeneralErrorExcpetion('Safety deposit box open method exceeds 100 characters or less than 1 character')
    return v    
def check_safety_deposit_box_address(v)->str:
    if string_common_check(v,1,500):
        raise GeneralErrorExcpetion('Safety deposit box address exceeds 100 characters or less than 1 character')
    return v    
def check_event_name(v)->str:
    if string_common_check(v,1,100):
        raise GeneralErrorExcpetion('Event name exceeds 100 characters or less than 1 character')
    return v    
def check_event_details(v)->str:
    if string_common_check(v,1,2000):
        raise GeneralErrorExcpetion('Event details exceeds 100 characters or less than 1 character')
    return v    
def check_asset_type(v)->str:
    if v not in {AssetTypeEnum.BANK_ACCOUNT, AssetTypeEnum.PROPERTY, AssetTypeEnum.SAFETY_DEPOSIT_BOX, AssetTypeEnum.CONFIDENTIAL_EVENT}:
        raise GeneralErrorExcpetion('Asset type only between BANK_ACCOUNT and PROPERTY AND SAFETY_DEPOSIT_BOX AND CONFIDENTIAL_EVENT')
    return v.value
def check_user_id(v)->str:
    if string_common_check(v,36,36):
        raise GeneralErrorExcpetion('User ID exceeds 36 characters or less than 36 character')
    return v    
def check_product_id(v)->str:
    if string_common_check(v,1,100):
        raise GeneralErrorExcpetion('Product ID exceeds 100 characters or less than 1 character')
    return v    