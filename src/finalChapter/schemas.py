from pydantic import BaseModel,AfterValidator
from typing import Optional, TypedDict
from datetime import datetime
from typing_extensions import Annotated
from src.finalChapter.validators import check_a_did_arrange, check_c_did_arrange, check_contact_organization, check_cp_did_arrange, check_date, check_epoa_did_arrange, check_f_did_arrange, check_mp_did_arrange, check_notes,check_custom, check_pc_did_arrange
from src.finalChapter.models import ADidArrangeTypeEnum, CDidArrangeTypeEnum,CPDidArrangeTypeEnum, EPOADidArrangeTypeEnum,FDidArrangeTypeEnum, MPDidArrangeTypeEnum, PCDidArrangeTypeEnum


class PalliativeCareBaseInputRequest(BaseModel):
    did_arrange:Annotated[PCDidArrangeTypeEnum,AfterValidator(check_pc_did_arrange)]
    contact_organization:Annotated[str,AfterValidator(check_contact_organization)]
    notes:Annotated[str,AfterValidator(check_notes)]
    updated_at:Annotated[datetime,AfterValidator(check_date)]
    class Config:
        from_attributes = True
        extra = extra='forbid'

class MedicalPreferenceBaseInputRequest(BaseModel):
    did_arrange:Annotated[MPDidArrangeTypeEnum,AfterValidator(check_mp_did_arrange)]
    notes:Annotated[str,AfterValidator(check_notes)]
    updated_at:Annotated[datetime,AfterValidator(check_date)]
    class Config:
        from_attributes = True
        extra = extra='forbid'

class EnduringPowerOfAttorneyBaseInputRequest(BaseModel):
    did_arrange:Annotated[EPOADidArrangeTypeEnum,AfterValidator(check_epoa_did_arrange)]
    notes:Annotated[str,AfterValidator(check_notes)]
    updated_at:Annotated[datetime,AfterValidator(check_date)]
    class Config:
        from_attributes = True
        extra = extra='forbid'

class CeremonyPreferenceBaseInputRequest(BaseModel):
    did_arrange:Annotated[CPDidArrangeTypeEnum,AfterValidator(check_cp_did_arrange)]
    notes:Annotated[str,AfterValidator(check_notes)]
    custom:Annotated[str,AfterValidator(check_custom)]
    updated_at:Annotated[datetime,AfterValidator(check_date)]
    class Config:
        from_attributes = True
        extra = extra='forbid'

class CoffinBaseInputRequest(BaseModel):
    did_arrange:Annotated[CDidArrangeTypeEnum,AfterValidator(check_c_did_arrange)]
    notes:Annotated[str,AfterValidator(check_notes)]
    custom:Annotated[str,AfterValidator(check_custom)]
    updated_at:Annotated[datetime,AfterValidator(check_date)]
    class Config:
        from_attributes = True
        extra = extra='forbid'


class FuneralBaseInputRequest(BaseModel):
    did_arrange:Annotated[FDidArrangeTypeEnum,AfterValidator(check_f_did_arrange)]
    notes:Annotated[str,AfterValidator(check_notes)]
    custom:Annotated[str,AfterValidator(check_custom)]
    updated_at:Annotated[datetime,AfterValidator(check_date)]
    class Config:
        from_attributes = True
        extra = extra='forbid'

class AshesBaseInputRequest(BaseModel):
    did_arrange:Annotated[ADidArrangeTypeEnum,AfterValidator(check_a_did_arrange)]
    notes:Annotated[str,AfterValidator(check_notes)]
    custom:Annotated[str,AfterValidator(check_custom)]
    updated_at:Annotated[datetime,AfterValidator(check_date)]
    class Config:
        from_attributes = True
        extra = extra='forbid'

