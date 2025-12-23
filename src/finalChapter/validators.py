from src.exceptions import GeneralErrorExcpetion
from src.loggerServices import log_error, log_info
from src.finalChapter.models import ADidArrangeTypeEnum, CDidArrangeTypeEnum,CPDidArrangeTypeEnum, EPOADidArrangeTypeEnum, FDidArrangeTypeEnum, MPDidArrangeTypeEnum, PCDidArrangeTypeEnum
from datetime import datetime
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
    
def check_custom(v)->str:
    if string_common_check(v,0,100):
        raise GeneralErrorExcpetion('Custom name exceeds 100 characters or less than 1 character')
    return v        
def check_notes(v)->str:
    if string_common_check(v,0,1000):
        raise GeneralErrorExcpetion('Notes exceeds 1000 characters or less than 1 character')
    return v    

def check_pc_did_arrange(v)->str:
    if v not in {PCDidArrangeTypeEnum.AGREE,PCDidArrangeTypeEnum.NOT_AGREE,PCDidArrangeTypeEnum.NOT_YET}:
        raise GeneralErrorExcpetion('Asset type only between BANK_ACCOUNT and PROPERTY AND SAFETY_DEPOSIT_BOX AND CONFIDENTIAL_EVENT')
    return v.value


def check_mp_did_arrange(v)->str:
    if v not in {MPDidArrangeTypeEnum.DID,MPDidArrangeTypeEnum.NOT_DID,MPDidArrangeTypeEnum.NOT_YET}:
        raise GeneralErrorExcpetion('Asset type only between BANK_ACCOUNT and PROPERTY AND SAFETY_DEPOSIT_BOX AND CONFIDENTIAL_EVENT')
    return v.value

def check_epoa_did_arrange(v)->str:
    if v not in {EPOADidArrangeTypeEnum.DID,EPOADidArrangeTypeEnum.NOT_DID,EPOADidArrangeTypeEnum.NOT_YET}:
        raise GeneralErrorExcpetion('Asset type only between BANK_ACCOUNT and PROPERTY AND SAFETY_DEPOSIT_BOX AND CONFIDENTIAL_EVENT')
    return v.value


def check_cp_did_arrange(v)->str:
    if v not in {CPDidArrangeTypeEnum.BUDDHISM,CPDidArrangeTypeEnum.TAOISM,CPDidArrangeTypeEnum.CHRISTIANITY,CPDidArrangeTypeEnum.NOT_YET,CPDidArrangeTypeEnum.CUSTOM}:
        raise GeneralErrorExcpetion('Asset type only between BANK_ACCOUNT and PROPERTY AND SAFETY_DEPOSIT_BOX AND CONFIDENTIAL_EVENT')
    return v.value

def check_c_did_arrange(v)->str:
    if v not in {CDidArrangeTypeEnum.CHINESE, CDidArrangeTypeEnum.WEST, CDidArrangeTypeEnum.EF, CDidArrangeTypeEnum.NOT_YET, CDidArrangeTypeEnum.CUSTOM}:
        raise GeneralErrorExcpetion('Asset type only between BANK_ACCOUNT and PROPERTY AND SAFETY_DEPOSIT_BOX AND CONFIDENTIAL_EVENT')
    return v.value

def check_f_did_arrange(v)->str:
    if v not in {FDidArrangeTypeEnum.BURIAL, FDidArrangeTypeEnum.CREMATION, FDidArrangeTypeEnum.NOT_YET,FDidArrangeTypeEnum.CUSTOM}:
        raise GeneralErrorExcpetion('Asset type only between BANK_ACCOUNT and PROPERTY AND SAFETY_DEPOSIT_BOX AND CONFIDENTIAL_EVENT')
    return v.value

def check_a_did_arrange(v)->str:
    if v not in {ADidArrangeTypeEnum.CB, ADidArrangeTypeEnum.CR, ADidArrangeTypeEnum.SAITGOR,ADidArrangeTypeEnum.SAOTS,ADidArrangeTypeEnum.NOT_YET,ADidArrangeTypeEnum.CUSTOM}:
        raise GeneralErrorExcpetion('Asset type only between BANK_ACCOUNT and PROPERTY AND SAFETY_DEPOSIT_BOX AND CONFIDENTIAL_EVENT')
    return v.value
 

def check_true_false(v) -> str:
    if isinstance(v,bool) == False:
        raise GeneralErrorExcpetion('Field only between True and False')
    return v

def check_date(v)->str:
    if datetime_common_check(v) == False:
        raise GeneralErrorExcpetion('Did testament date type only dateTime')
    return v

def check_contact_organization(v)->str:
    if string_common_check(v,0,255):
        raise GeneralErrorExcpetion('Contact organization exceeds 255 characters or less than 1 character')
    return v    