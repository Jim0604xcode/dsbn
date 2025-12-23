from datetime import datetime,date,timedelta
from sqlalchemy.orm import Session
from src.exceptions import GeneralErrorExcpetion
from src.auth.models import User,LanguageEnum,AckTypeEnum
from src.loggerServices import log_error

def string_common_check(v,less_than, more_than) -> bool:
    if not isinstance(v, str):
        raise GeneralErrorExcpetion("输入必须是字符串")
    length_of_string = len(v)
    if length_of_string > more_than or length_of_string < less_than:
        return True
    return False

def check_phone_number(v: str) -> str:
    if string_common_check(v,1,100):
        raise GeneralErrorExcpetion('phone number exceeds 100 characters or less than 1 character')
    return v    
    
def check_gender(gender: str) -> str:

    if gender and gender not in ['male', 'female', 'other']:
        raise GeneralErrorExcpetion('Gender must be one of: male, female, other')
    return gender

def check_multi_user_id_is_valid(user_id_list: list, db: Session) -> list:
    if not user_id_list:
        return []
    valid_ids = db.query(User.id).filter(User.id.in_(user_id_list)).all()
    if not valid_ids:
        log_error('Contains invalid user IDs -> {}'.format(user_id_list))
        raise GeneralErrorExcpetion('Contains invalid user IDs')
    return user_id_list


def check_language(v:str) -> str:
    if v not in {LanguageEnum.en, LanguageEnum.zh_hans, LanguageEnum.zh_hk}:
        raise GeneralErrorExcpetion('Language type only between en and zh_hans and zh_hk')
    return v

def check_ack(v:str) -> str:
    if v not in {AckTypeEnum.PRIVACY, AckTypeEnum.TNC}:
        raise GeneralErrorExcpetion('Ack type only between PRIVACY and TNC')
    return v
