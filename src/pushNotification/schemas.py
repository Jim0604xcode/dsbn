from pydantic import BaseModel,AfterValidator
from typing import Optional, TypedDict
from datetime import datetime
from typing_extensions import Annotated
from src.pushNotification.validators import check_device_uuid, check_token


class PushNotificationBaseInputRequest(BaseModel):
    token:Annotated[str,AfterValidator(check_token)]
    device_uuid:Annotated[str,AfterValidator(check_device_uuid)]
    
    class Config:
        from_attributes = True
        extra = extra='forbid'

