from pydantic import BaseModel,AfterValidator
from typing import Optional, TypedDict
from datetime import datetime
from typing_extensions import Annotated
from src.payment.models import PaymentServiceProviderEnum,PaymentStatusEnum,PaymentTypeEnum


from src.payment.validators import check_payment_service_provider, check_payment_status, check_payment_type, check_product_id, check_purchase_date, check_purchase_token, check_receipt, check_subscription_expire_date, check_transaction_id

class SubscriptionMetaBaseInputRequest():
    subscription_expire_date:Optional[Annotated[datetime,AfterValidator(check_subscription_expire_date)]]
class TransactionWithSubBaseInputRequest(BaseModel,SubscriptionMetaBaseInputRequest):
    payment_service_provider:Annotated[PaymentServiceProviderEnum,AfterValidator(check_payment_service_provider)]
    payment_status:Annotated[PaymentStatusEnum,AfterValidator(check_payment_status)]
    payment_type:Annotated[PaymentTypeEnum,AfterValidator(check_payment_type)]
    transaction_id:Annotated[str,AfterValidator(check_transaction_id)]
    purchase_date:Annotated[datetime,AfterValidator(check_purchase_date)]
    product_id:Annotated[str,AfterValidator(check_product_id)]
    class Config:
        from_attributes = True
        extra = extra='forbid'

class TransactionWithoutSubBaseInputRequest(BaseModel):
    payment_service_provider:Annotated[PaymentServiceProviderEnum,AfterValidator(check_payment_service_provider)]
    payment_status:Annotated[PaymentStatusEnum,AfterValidator(check_payment_status)]
    payment_type:Annotated[PaymentTypeEnum,AfterValidator(check_payment_type)]
    transaction_id:Annotated[str,AfterValidator(check_transaction_id)]
    purchase_date:Annotated[datetime,AfterValidator(check_purchase_date)]
    product_id:Annotated[str,AfterValidator(check_product_id)]
    class Config:
        from_attributes = True
        extra = extra='forbid'


class OptionalTransactionBaseInputRequest(BaseModel):
    payment_service_provider:Optional[Annotated[PaymentServiceProviderEnum,AfterValidator(check_payment_service_provider)]]
    payment_status:Optional[Annotated[PaymentStatusEnum,AfterValidator(check_payment_status)]]
    product_id:Optional[Annotated[str,AfterValidator(check_product_id)]]

    
    class Config:
        from_attributes = True
        extra = extra='forbid'

class PreTransactionBaseInputRequest(BaseModel):
    payment_service_provider:Annotated[PaymentServiceProviderEnum,AfterValidator(check_payment_service_provider)]
    payment_status:Annotated[PaymentStatusEnum,AfterValidator(check_payment_status)]
    payment_type:Annotated[PaymentTypeEnum,AfterValidator(check_payment_type)]
    product_id:Annotated[str,AfterValidator(check_product_id)]
    class Config:
        from_attributes = True
        extra = extra='forbid'
class AppleReceiptRequest(BaseModel):
    receipt:Annotated[str,AfterValidator(check_receipt)]
    product_id:Annotated[str,AfterValidator(check_product_id)]
    transaction_id:Annotated[str,AfterValidator(check_transaction_id)]
    
    class Config:
        from_attributes = True
        extra = extra='forbid'
class GoogleReceiptRequest(BaseModel):
    purchase_token: Annotated[str,AfterValidator(check_purchase_token)]
    product_id:Annotated[str,AfterValidator(check_product_id)]
    
    class Config:
        from_attributes = True
        extra = extra='forbid'
