from typing import List
from src.exceptions import GeneralErrorExcpetion

def string_common_check(v, less_than) -> bool:
    if not isinstance(v, str):
        raise GeneralErrorExcpetion("输入必须是字符串")
    if len(v) < less_than:
        return True
    return False


def check_sound(v)->str:
    if string_common_check(v,1):
        raise GeneralErrorExcpetion('Sound less than 1 character')
    return v    
def check_title(v)->str:
    if string_common_check(v,1):
        raise GeneralErrorExcpetion('Title less than 1 character')
    return v    

def check_body(v)->str:
    if string_common_check(v,1):
        raise GeneralErrorExcpetion('Body less than 1 character')
    return v    


