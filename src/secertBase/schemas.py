from pydantic import BaseModel,AfterValidator
from typing import Optional, TypedDict
from datetime import datetime
from typing_extensions import Annotated
from src.secertBase.validators import check_asset_type, check_bank_account_name,check_bank_account_number,check_currency, check_event_details, check_event_name, check_product_id,check_property_name,check_property_address,check_remarks, check_safety_deposit_box_address, check_safety_deposit_box_name, check_safety_deposit_box_open_method, check_user_id
from src.secertBase.models import AssetTypeEnum

class SecretBaseInputRequest(BaseModel):
    asset_type:Annotated[AssetTypeEnum,AfterValidator(check_asset_type)]
    user_id:Annotated[str,AfterValidator(check_user_id)]
    product_id:Annotated[str,AfterValidator(check_product_id)]
    class Config:
        from_attributes = True
        extra = extra='forbid'
class BankAccountBaseInputRequest(BaseModel):
    bank_account_name:Annotated[str,AfterValidator(check_bank_account_name)] # encrypt
    bank_account_number:Annotated[str,AfterValidator(check_bank_account_number)] # encrypt
    currency:Annotated[str,AfterValidator(check_currency)]
    class Config:
        from_attributes = True
        extra = extra='forbid'

class PropertyBaseInputRequest(BaseModel):
    property_name:Annotated[str,AfterValidator(check_property_name)] # encrypt
    property_address:Annotated[str,AfterValidator(check_property_address)] # encrypt
    remarks:Annotated[str,AfterValidator(check_remarks)] # encrypt
    class Config:
        from_attributes = True
        extra = extra='forbid'

class SafetyDepositBoxBaseInputRequest(BaseModel):
    safety_deposit_box_name:Annotated[str,AfterValidator(check_safety_deposit_box_name)] # encrypt
    safety_deposit_box_open_method:Annotated[str,AfterValidator(check_safety_deposit_box_open_method)] # encrypt
    safety_deposit_box_address:Annotated[str,AfterValidator(check_safety_deposit_box_address)] # encrypt
    remarks:Annotated[str,AfterValidator(check_remarks)] # encrypt
    class Config:
        from_attributes = True
        extra = extra='forbid'

class ConfidentialEventBaseInputRequest(BaseModel):
    event_name:Annotated[str,AfterValidator(check_event_name)] # encrypt
    event_details:Annotated[str,AfterValidator(check_event_details)] # encrypt
    class Config:
        from_attributes = True
        extra = extra='forbid'
