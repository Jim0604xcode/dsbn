from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from src.constants import BAD_REQUEST_CODE_400, INVALID_REQUEST_DATA_CODE_422, INTERNAL_SERVER_ERROR_CODE_500,UNAUTHORIZED_CODE_401,FORBIDDEN_CODE_403
import functools
from src.loggerServices import log_error
from src.utils.response import create_error_response, get_error_messages
import time
class CustomHttpException(Exception):
    def __init__(self, status_code: int, code: str, message: str, details: str = None,timestamp:int = None):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details
        self.timestamp = timestamp
        super().__init__(self.message)

class BadReqExpection(CustomHttpException):
    def __init__(self,details: str = "A Bad request error occurred",timestamp: int = None,code:str="null"):
        super().__init__(
            status_code=BAD_REQUEST_CODE_400,
            code=code,
            message="Bad Request",
            details=details,
            timestamp=timestamp,
        )
class DatabaseErrorException(CustomHttpException):
    def __init__(self,details: str = "A database error occurred",timestamp: int = None,code:str="null"):
        super().__init__(
            status_code=INTERNAL_SERVER_ERROR_CODE_500,
            code=code,
            message="DB Error",
            details=details,
            timestamp=timestamp,
        )

class GeneralErrorExcpetion(CustomHttpException):
    def __init__(self,details: str = "A general error occurred",timestamp: int = None,code:str="null"):
        super().__init__(
            status_code=INTERNAL_SERVER_ERROR_CODE_500,
            code=code,
            message="general error",
            details=details,
            timestamp=timestamp,
        )

class UserNotFoundErrorExpection(CustomHttpException):
    def __init__(self,details: str = "A User not found error occurred",timestamp: int = None,code:str="null"):
        super().__init__(
            status_code=UNAUTHORIZED_CODE_401,
            code=code,
            message="user not found error",
            details=details,
            timestamp=timestamp,
        )

class TokenInvalidExpection(CustomHttpException):
    def __init__(self,details: str = "A token invalid error occurred",timestamp: int = None,code:str="null"):
        super().__init__(
            status_code=FORBIDDEN_CODE_403,
            code=code,
            message="Token error",
            details=details,
            timestamp=timestamp,
        )


# 修正 validation_exception_handler，確保參數順序正確
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    code = "INVALID_REQUEST_DATA"
    message = "Invalid request data"
    error_messages = get_error_messages(exc)
    timestamp = int(time.time())
    details = f"{error_messages} (timestamp: {timestamp})" if isinstance(error_messages, str) else f"{'; '.join(error_messages)} (timestamp: {timestamp})"
    error_response = create_error_response(
        INVALID_REQUEST_DATA_CODE_422,
        code,
        message,
        details,
        request.url.path
    )
    return JSONResponse(status_code=INVALID_REQUEST_DATA_CODE_422, content=error_response)

async def custom_http_exception_handler(request: Request, exc: CustomHttpException):
    details = f"{exc.details} (timestamp: {exc.timestamp})" if exc.details and exc.timestamp else exc.details or f"timestamp: {exc.timestamp}"
    # details = f"{exc.details} (timestamp: {exc.timestamp})"
    error_response = create_error_response(
        exc.status_code,
        exc.code,
        exc.message,
        details,
        request.url.path
    )
    return JSONResponse(status_code=exc.status_code, content=error_response)

# This function is a decorator that wraps an endpoint and catches exceptions.
def handle_exceptions(endpoint):
    @functools.wraps(endpoint)
    async def wrapper(*args, **kwargs):
        # 提取 request 物件
        request = next((arg for arg in args if isinstance(arg, Request)), None)
        if not request:
            request = kwargs.get('request')
        api_path = request.url.path if request else 'N/A'
        timestamp = int(time.time())
        try:
            
            return await endpoint(*args, **kwargs)
        except BadReqExpection as e:
            
            log_error(f"BadRequestException -> {endpoint.__name__} -> {e.details} -> api_path={api_path} -> timestamp={timestamp}")
            raise BadReqExpection(timestamp=timestamp)  # 添加 timestamp
        except DatabaseErrorException as e:
            
            log_error(f"DatabaseErrorException -> {endpoint.__name__} -> {e.details} -> api_path={api_path} -> timestamp={timestamp}")
            raise DatabaseErrorException(timestamp=timestamp)  # 確保傳遞 timestamp
        except TokenInvalidExpection as e:
            log_error(f"TokenInvalidExpection -> {endpoint.__name__} -> {e.details} -> api_path={api_path} -> timestamp={timestamp}")
            raise TokenInvalidExpection(timestamp=timestamp)  # 確保傳遞 timestamp
        
        except GeneralErrorExcpetion as e:
            log_error(f"GeneralErrorExcpetion -> {endpoint.__name__} -> {e.details} -> api_path={api_path} -> timestamp={timestamp}")
            raise GeneralErrorExcpetion(timestamp=timestamp)  # 確保傳遞 timestamp

        except Exception as e:
            log_error(f"Unexpected Exception -> {endpoint.__name__} -> {str(e)} -> api_path={api_path} -> timestamp={timestamp}")
            raise GeneralErrorExcpetion(timestamp=timestamp)

    return wrapper