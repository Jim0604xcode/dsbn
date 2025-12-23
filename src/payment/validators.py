from src.exceptions import GeneralErrorExcpetion
from src.loggerServices import log_error, log_info
from datetime import datetime
from src.payment.models import PaymentServiceProviderEnum,PaymentStatusEnum,PaymentTypeEnum
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


def check_subscription_expire_date(v)->str:    
    if datetime_common_check(v) == False:
        raise GeneralErrorExcpetion('Subscription expire date type only dateTime')
    return v
def check_purchase_date(v)->str:
    if datetime_common_check(v) == False:
        raise GeneralErrorExcpetion('Purchase date type only dateTime')
    return v



def check_receipt(v)->str:
    # if string_common_check(v,1,100000):
    #     raise GeneralErrorExcpetion('Receipt exceeds 100 characters or less than 1 character')
    return v    
def check_purchase_token(v)->str:
    if string_common_check(v,1,1000):
        raise GeneralErrorExcpetion('Purchase token exceeds 1000 characters or less than 1 character')
    return v    
def check_product_id(v)->str:
    if string_common_check(v,1,100):
        raise GeneralErrorExcpetion('Product ID exceeds 100 characters or less than 1 character')
    return v    
def check_transaction_id(v)->str:
    if string_common_check(v,1,100):
        raise GeneralErrorExcpetion('Transaction ID exceeds 100 characters or less than 1 character')
    return v    
def check_google_purchase_token(v)->str:
    if string_common_check(v,1,100):
        raise GeneralErrorExcpetion('Google purchase token exceeds 100 characters or less than 1 character')
    return v    
def check_payment_service_provider(v)->str:
    if v not in {PaymentServiceProviderEnum.APPLE, PaymentServiceProviderEnum.GOOGLE}:
        raise GeneralErrorExcpetion('Payment service provider only between APPLE and GOOGLE')
    return v
def check_payment_status(v)->str:
    if v not in {PaymentStatusEnum.PENDING, PaymentStatusEnum.COMPLETED, PaymentStatusEnum.FAILED}:
        raise GeneralErrorExcpetion('Payment status only between PENDING and COMPLETED AND FAILED')
    return v
def check_payment_type(v)->str:
    if v not in {PaymentTypeEnum.CONSUMPTION, PaymentTypeEnum.SUBSCRIPTION}:
        raise GeneralErrorExcpetion('Payment type only between CONSUMPTION and SUBSCRIPTION')
    return v