from pydantic import BaseModel
from typing import List, Union, Optional
from src.posts.response import (LifeMomentResponseModel, LifeTrajectoryResponseModel,
    MessageToYouResponseModel, SharedLifeMomentResponseModel, SharedLifeTrajectoryResponseModel)

class PaginatedResponseModel(BaseModel):
    total_items: int
    total_pages: int
    current_page: int
    page_size: int
    items: Union[List[LifeMomentResponseModel],
                 List[LifeTrajectoryResponseModel],
                 List[MessageToYouResponseModel],
                 List[SharedLifeMomentResponseModel],
                 List[SharedLifeTrajectoryResponseModel]
                 ]