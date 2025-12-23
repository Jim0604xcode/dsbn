from src.exceptions import GeneralErrorExcpetion
from src.loggerServices import log_error

def string_common_check(v,less_than, more_than) -> bool:
    if not isinstance(v, str):
        raise GeneralErrorExcpetion("输入必须是字符串")
    length_of_string = len(v)
    if length_of_string > more_than or length_of_string < less_than:
        return True
    return False

def check_title(v) -> str: 
    if string_common_check(v,0,225):
        raise GeneralErrorExcpetion('Title exceeds 225 characters or less than 1 character')
    return v
    
def check_content(v) -> str:
    if string_common_check(v,1,1000):
        raise GeneralErrorExcpetion('Content exceeds 1000 characters or less than 1 character')
    return v

def check_post_content(v) -> str:
    if string_common_check(v,1,5000):
        raise GeneralErrorExcpetion('Content exceeds 5000 characters or less than 1 character')
    return v

def check_type_name(v) -> str:
    if string_common_check(v,1,225):
        raise GeneralErrorExcpetion('Type Name exceeds 225 characters or less than 1 character')
    return v

def check_type_description(v) -> str:
    if string_common_check(v,1,1000):
        raise GeneralErrorExcpetion('Type Description exceeds 1000 characters or less than 1 character')
    return v

def check_motion_rate(v) -> int:
    if v < -10 or v > 10:
        raise GeneralErrorExcpetion('Motion Rate value is not vaild')
    return v

def check_age(v) -> int:
    if v < 0 or v > 150:
        raise GeneralErrorExcpetion('Age value is not vaild')
    return v

def check_post_type_code(v) -> str:
    if string_common_check(v,1,225):
        raise GeneralErrorExcpetion('Post Type Code exceeds 225 characters or less than 1 character')
    return v

def check_group_name(v) -> str:
    if string_common_check(v,1,225):
        raise GeneralErrorExcpetion('Group Name exceeds 225 characters or less than 1 character')
    return v

def check_group_member_name(v) -> str:
    if string_common_check(v,1,225):
        raise GeneralErrorExcpetion('Group Member Name exceeds 225 characters or less than 1 character')
    return v

def check_common_string(v) -> str:
    if string_common_check(v,1,225):
        raise GeneralErrorExcpetion('Common String exceeds 225 characters or less than 1 character')
    return v