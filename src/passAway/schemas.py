from pydantic import BaseModel,AfterValidator
from typing import Optional, TypedDict
from datetime import datetime
from typing_extensions import Annotated
from src.passAway.models import ApprovalStatusEnum
from src.passAway.validators import (check_approval_at, check_approval_comments, check_approval_status, check_death_certificate, check_death_time, check_id_card_copy, check_inheritor_id_proof, check_relationship_proof)
class ReqData(BaseModel):
    death_time:Annotated[datetime,AfterValidator(check_death_time)]
    class Config:
        from_attributes = True
        extra = extra='forbid'    
class OSSData(BaseModel):
    death_certificate:Annotated[str,AfterValidator(check_death_certificate)]
    id_card_copy:Annotated[str,AfterValidator(check_id_card_copy)]
    relationship_proof:Annotated[str,AfterValidator(check_relationship_proof)]
    inheritor_id_proof:Annotated[str,AfterValidator(check_inheritor_id_proof)]
    class Config:
        from_attributes = True
        extra = extra='forbid'            

class PrePassAwayInfoMetaBaseInputRequest(BaseModel):
    approval_status:Annotated[ApprovalStatusEnum,AfterValidator(check_approval_status)]
    class Config:
        from_attributes = True
        extra = extra='forbid'

class PassAwayInfoMetaBaseInputRequest(BaseModel):
    approval_status:Annotated[ApprovalStatusEnum,AfterValidator(check_approval_status)]
    approval_comments:Annotated[str,AfterValidator(check_approval_comments)]
    approved_at:Annotated[datetime,AfterValidator(check_approval_at)]
    class Config:
        from_attributes = True
        extra = extra='forbid'



