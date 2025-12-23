from fastapi import APIRouter, Request
from src.utils.response import create_success_response
from src.oss.schemas import  (
    GetPostFilesPostPolicyRequest,
    GetPostFilesPostPolicyResponse,
    PostFilePostPolicyResponseItem,
)

from src.oss.service import  get_client_post_policy_upload_data

from src.models import get_error_response_model
from src.schemas import ApiSuccessResponseModel
from src.exceptions import handle_exceptions

router = APIRouter()

@router.post(
    "/get/post-files-presigned-urls",
    status_code=200,
    response_model=ApiSuccessResponseModel,
    responses=get_error_response_model,
)
@handle_exceptions
async def get_post_files_post_policy(
    request: Request,
    body: GetPostFilesPostPolicyRequest,
):
    """
    Get OSS PostPolicy form data for multiple file types for uploading posts.
    Frontend should upload with multipart/form-data to upload_url with fields + file.
    """
    user_info = request.state.user_info

    items: list[PostFilePostPolicyResponseItem] = []
    for file_group in body.files:
        # Prefer stronger size enforcement when `files` is provided.
        file_metas = None
        file_names = None
        if file_group.files is not None and len(file_group.files) > 0:
            file_metas = [f.model_dump() for f in file_group.files]
        elif file_group.file_names is not None and len(file_group.file_names) > 0:
            file_names = file_group.file_names
        else:
            file_names = []

        policy_items = await get_client_post_policy_upload_data(
            user_id=user_info.sub,
            file_type=file_group.file_type.value,
            action_type="posts",
            file_names=file_names,
            file_metas=file_metas,
            expiration=3600,
        )
        items.append(
            PostFilePostPolicyResponseItem(
                file_type=file_group.file_type,
                items=policy_items,
            )
        )

    response_model = GetPostFilesPostPolicyResponse(items=items)
    return create_success_response(response_model)