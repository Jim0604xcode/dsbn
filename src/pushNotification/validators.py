from src.exceptions import GeneralErrorExcpetion
from src.loggerServices import log_error, log_info

def string_common_check(v,less_than, more_than) -> bool:
    if not isinstance(v, str):
        raise GeneralErrorExcpetion("输入必须是字符串")
    length_of_string = len(v)
    if length_of_string > more_than or length_of_string < less_than:
        return True
    return False
    
# def check_notification_enabled(v) -> str:
#     if isinstance(v,bool) == False:
#         raise GeneralErrorExcpetion('Field only between True and False')
#     return v
def check_token(v)->str:
    if string_common_check(v,10,100):
        raise GeneralErrorExcpetion('Token exceeds 100 characters or less than 10 character')
    return v    
def check_device_uuid(v)->str:
    if string_common_check(v,10,100):
        raise GeneralErrorExcpetion('device uuid exceeds 100 characters or less than 10 character')
    return v    