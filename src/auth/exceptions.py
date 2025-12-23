# from ..exceptions import CustomHttpException
# from .constants import USER_ALREADY_EXISTS,ERROR_USER_ALREADY_EXISTS
# from ..constants import INTERNAL_SERVER_ERROR_CODE_500,BAD_REQUEST_CODE_400,INVALID_REQUEST_DATA_CODE_422

# class RegisterIdUserIsExistError(CustomHttpException):
#     def __init__(self):
#         super().__init__(
#             status_code=BAD_REQUEST_CODE_400,
#             code=ERROR_USER_ALREADY_EXISTS,
#             message=USER_ALREADY_EXISTS,
#             details="The user with the provided ID already exists in the database",
#         )
