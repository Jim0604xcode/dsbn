from .schemas import ApiErrorResponseModel
from .constants import INTERNAL_SERVER_ERROR_CODE_500,BAD_REQUEST_CODE_400,INVALID_REQUEST_DATA_CODE_422
from typing import Any, Dict, List, Optional, Union, TypeVar, Generic, Type,TypedDict
from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase

get_error_response_model =  { BAD_REQUEST_CODE_400: {"model":ApiErrorResponseModel}, INVALID_REQUEST_DATA_CODE_422: {"model": ApiErrorResponseModel}, INTERNAL_SERVER_ERROR_CODE_500: {"model": ApiErrorResponseModel}}

class SqlUpdateOperation(TypedDict):
    sql: str
    isExist: bool
    params: Dict[str, Any]

ResultList = List[SqlUpdateOperation]



# Define types for operation parameters
ModelType = TypeVar('ModelType')
FilterType = Dict[str, Any]
ValuesType = Union[Dict[str, Any], BaseModel]

# Base operation type
class Operation:
    pass

# Standard ORM operations
class OrmOperation(Operation):
    model: Type[DeclarativeBase]
    filter: FilterType
    values: ValuesType
    check_exists: bool
    type: str  # ORM_OPERATION_TYPE value

# Custom operation
class CustomOperation(Operation):
    type: str  # ORM_OPERATION_TYPE.CUSTOM.value
    function: str
    params: Dict[str, Any]

# List of operations
OperationsList = List[Union[OrmOperation, CustomOperation]]