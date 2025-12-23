from pydantic import BaseModel,AfterValidator
from typing import Optional, TypedDict
from datetime import datetime
from typing_extensions import Annotated
from src.personalLifeOverviewChart.validators import check_ago, check_content,check_date, check_picture



class DescribeYourselfTenSentencesBaseInputRequest(BaseModel):
    content:Annotated[str,AfterValidator(check_content)]
    updated_at:Annotated[datetime,AfterValidator(check_date)]
    class Config:
        from_attributes = True
        extra = extra='forbid'

class ValueOfLifeBaseInputRequest(BaseModel):
    content:Annotated[str,AfterValidator(check_content)]
    updated_at:Annotated[datetime,AfterValidator(check_date)]
    class Config:
        from_attributes = True
        extra = extra='forbid'


class LifeInsightsBaseInputRequest(BaseModel):
    content:Annotated[str,AfterValidator(check_content)]
    updated_at:Annotated[datetime,AfterValidator(check_date)]
    class Config:
        from_attributes = True
        extra = extra='forbid'

class EpitaphBaseInputRequest(BaseModel):
    content:Annotated[str,AfterValidator(check_content)]
    updated_at:Annotated[datetime,AfterValidator(check_date)]
    class Config:
        from_attributes = True
        extra = extra='forbid'

class FavoriteHeadshotBaseInputRequest(BaseModel):
    picture:Annotated[str,AfterValidator(check_picture)]
    ago:Annotated[int,AfterValidator(check_ago)]
    updated_at:Annotated[datetime,AfterValidator(check_date)]
    class Config:
        from_attributes = True
        extra = extra='forbid'


# class FavoriteHeadshotPictureBaseInputRequest(BaseModel):
#     picture:Annotated[str,AfterValidator(check_picture)]
#     updated_at:Annotated[datetime,AfterValidator(check_date)]
#     class Config:
#         from_attributes = True
#         extra = extra='forbid'

# class FavoriteHeadshotAgoBaseInputRequest(BaseModel):
#     ago:Annotated[int,AfterValidator(check_ago)]
#     updated_at:Annotated[datetime,AfterValidator(check_date)]
#     class Config:
#         from_attributes = True
#         extra = extra='forbid'
