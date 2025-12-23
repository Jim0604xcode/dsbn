from pydantic import BaseModel
from typing import Generic, TypeVar, Optional,List,Union

T = TypeVar('T')

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[str] = None
    path: str


class ApiErrorResponseModel(BaseModel):
    status: str
    statusCode: int
    error: Optional[ErrorDetail] = None

class ApiSuccessResponseModel(BaseModel, Generic[T]):
    status: str
    statusCode: int
    data: Optional[Union[T, List[T]]]
    requestId: str

class PaginatedRequestModel(BaseModel):
    page: Optional[int] = 1  # Default limit
    page_size: Optional[int] = 10  # Default offset        