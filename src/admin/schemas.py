from pydantic import BaseModel,AfterValidator
from typing import List, Optional, TypedDict
from datetime import datetime
from typing_extensions import Annotated
from src.admin.validators import check_sound, check_title,check_body


class SendPushNotificationBaseInputRequest(BaseModel):
    sound:Annotated[str,AfterValidator(check_sound)]
    en_title:Annotated[str,AfterValidator(check_title)]
    en_body:Annotated[str,AfterValidator(check_body)]
    zh_hans_title:Annotated[str,AfterValidator(check_title)]
    zh_hans_body:Annotated[str,AfterValidator(check_body)]
    zh_hk_title:Annotated[str,AfterValidator(check_title)]
    zh_hk_body:Annotated[str,AfterValidator(check_body)]

    class Config:
        from_attributes = True
        extra='forbid'



class SendPushNotificationToSpecificMemberBaseInputRequest(SendPushNotificationBaseInputRequest):
    row_id_list: List[int]

    class Config:
        from_attributes = True
        extra = 'forbid'


class Pagination(BaseModel):
    page:int
    perPage:int
class Sort(BaseModel):
    field:str
    order:str    

class FilterByPost(BaseModel):
    searchAuthgearID:str
    postSubType:List[str]
    createAtStartDate:str    
    createAtEndDate:str
    eventAtStartDate:str
    eventAtEndDate:str
    numberOfRecipientsFrom:int
    numberOfRecipientsTo:int
class FilterByUser(BaseModel):
    searchAuthgearID:str
    postSubType:List[str]
    numberOfPostSubTypeFrom:int
    numberOfPostSubTypeTo:int
    numberOfAIFeedBackSubTypeFrom:int
    numberOfAIFeedBackSubTypeTo:int

class FilterByPreDeathPlan(BaseModel):    
    searchAuthgearID:str
    lifePlanningSubType:List[str]
    didArrange:bool
    latestUpdateAtFrom:str
    latestUpdateAtTo:str

class FilterByLifeSummary(BaseModel):    
    searchAuthgearID:str
    lifeSummaryType:List[str]
    numberOfDidFrom:int
    numberOfDidTo:int
    latestUpdateAtFrom:str
    latestUpdateAtTo:str

class FilterByUserStorage(BaseModel):    
    searchAuthgearID:str
    textGigaBytesFrom:int
    textGigaBytesTo:int
class reqParam(BaseModel):
    filter:FilterByPost | FilterByUser | FilterByPreDeathPlan | FilterByLifeSummary | FilterByUserStorage | dict 
    pagination: Pagination
    sort: Sort
    class Config:
        from_attributes = True
        extra='forbid'
