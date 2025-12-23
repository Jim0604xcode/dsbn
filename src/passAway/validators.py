from src.exceptions import GeneralErrorExcpetion
from src.loggerServices import log_error, log_info
from datetime import datetime
from src.passAway.models import ApprovalStatusEnum
def int_common_check(v) -> bool:
    try:
        return isinstance(v,int)    
    except ValueError as e:
        log_error(v)
        return False
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


def check_approval_status(v)->str:    
    if v not in {ApprovalStatusEnum.VERIFY,ApprovalStatusEnum.APPROVAL,ApprovalStatusEnum.REJECT}:
        raise GeneralErrorExcpetion('Approval status only between ACTIVE and DEAD and VERIFY')
    return v.value
def check_approval_comments(v)->str:    
    if string_common_check(v,1,500):
        raise GeneralErrorExcpetion('Approval comments exceeds 500 characters or less than 1 character')
    return v    
def check_approval_at(v)->str:    
    if datetime_common_check(v) == False:
        raise GeneralErrorExcpetion('Approval at type only dateTime')
    return v
def check_death_time(v)->str:    
    if datetime_common_check(v) == False:
        raise GeneralErrorExcpetion('Death time type only dateTime')
    return v
def check_death_certificate(v)->str:    
    if string_common_check(v,1,5000):
        raise GeneralErrorExcpetion('Death certificate exceeds 200 characters or less than 1 character')
    return v    
def check_id_card_copy(v)->str:    
    if string_common_check(v,1,5000):
        raise GeneralErrorExcpetion('ID card copy exceeds 200 characters or less than 1 character')
    return v    
def check_relationship_proof(v)->str:    
    if string_common_check(v,1,5000):
        raise GeneralErrorExcpetion('Relationship proof exceeds 200 characters or less than 1 character')
    return v    
def check_inheritor_id_proof(v)->str:    
    if string_common_check(v,1,5000):
        raise GeneralErrorExcpetion('Inheritor id proof exceeds 200 characters or less than 1 character')
    return v    

def check_user_id(v)->str:    
    if string_common_check(v,36,36):
        raise GeneralErrorExcpetion('User ID exceeds 36 characters or less than 36 character')
    return v    
def check_meta_id(v)->str:    
    if int_common_check(v) == False:
        raise GeneralErrorExcpetion('meta_id type only int')
    return v
