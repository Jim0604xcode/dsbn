from fastapi.exceptions import RequestValidationError
from src.loggerServices import log_error
from ..schemas import ApiSuccessResponseModel, ApiErrorResponseModel, ErrorDetail
import uuid
from typing import List, Any
from ..constants import STATUS_SUCCESS, STATUS_ERRPR,SUCCESS_CODE_200

def create_success_response(data: Any) -> ApiSuccessResponseModel:
    return ApiSuccessResponseModel(
        status=STATUS_SUCCESS,
        statusCode=SUCCESS_CODE_200,
        data=data,
        requestId=str(uuid.uuid4()),
    ).dict()

def create_error_response(statusCode:int, code: str, message: str, details: str, path: str) -> ApiErrorResponseModel:
    return ApiErrorResponseModel(
        status=STATUS_ERRPR,
        statusCode=statusCode,
        error=ErrorDetail(
            code=code,
            message=message,
            details=details,
            path=path,
        ),
        requestId=str(uuid.uuid4()),
    ).dict()

def get_error_messages(exc: RequestValidationError) -> str:
    print(exc.errors())
    error_messages = exc.errors()[0]["msg"]
    return error_messages        