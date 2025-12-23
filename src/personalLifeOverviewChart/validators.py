from src.exceptions import GeneralErrorExcpetion
from src.loggerServices import log_error, log_info
from datetime import datetime
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
    

def check_content(v)->str:
    if string_common_check(v,1,1000):
        raise GeneralErrorExcpetion('Content exceeds 1000 characters or less than 1 character')
    return v    

def check_picture(v)->str:
    if string_common_check(v,1,6000):
        raise GeneralErrorExcpetion('Picture exceeds 6000 characters or less than 1 character')
    return v    

def check_ago(v)->str:
    if int_common_check(v) == False:
        raise GeneralErrorExcpetion('Ago type only accept integer')
    return v        

def check_date(v)->str:
    if datetime_common_check(v) == False:
        raise GeneralErrorExcpetion('Did testament date type only dateTime')
    return v
