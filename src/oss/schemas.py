from fastapi import UploadFile
from pydantic import BaseModel
from typing import Dict, List, Optional, TypedDict

from src.posts.schemas import PostFileType


class OSSfileDownloadRequest(BaseModel):
    filesName: List[str]
    decrypt: bool = False


class PresignedUrlInfo(TypedDict):
    signed_url: str
    object_name: str
    file: UploadFile

class ClientPresignedUploadUrlItem(BaseModel):
    """
    return a single file's presigned URL information to the frontend
    """

    file_name: str
    object_name: str
    signed_url: str
    # Optional headers that the client MUST include when uploading to the signed_url.
    # Keep this optional for backward compatibility with existing clients.
    headers: Optional[Dict[str, str]] = None


class ClientPostPolicyUploadItem(BaseModel):
    """
    Return a single file's PostPolicy upload information to the frontend.
    Frontend should upload with multipart/form-data to upload_url with fields + file.
    """

    file_name: str
    object_name: str
    upload_url: str
    fields: Dict[str, str]


class ClientUploadFileMeta(BaseModel):
    """
    File metadata from frontend used for tighter PostPolicy constraints.
    file_size is in bytes.
    """

    file_name: str
    file_size: int



class PostFilePresignedUrlRequestItem(BaseModel):
    """
    a list of file names for a single file type, used to batch get the presigned URL of the type
    """

    file_type: PostFileType
    file_names: List[str]


class PostFilePresignedUrlResponseItem(BaseModel):
    """
    a response item for a single file type, containing the presigned URLs for the files of the type
    """

    file_type: PostFileType
    urls: List[ClientPresignedUploadUrlItem]


class PostFilePostPolicyResponseItem(BaseModel):
    """
    a response item for a single file type, containing the PostPolicy form info for the files of the type
    """

    file_type: PostFileType
    items: List[ClientPostPolicyUploadItem]

class PostFilePostPolicyRequestItem(BaseModel):
    """
    Request item for PostPolicy endpoint.
    Prefer `files` (with file_size) for stronger size enforcement.
    `file_names` is kept for backward compatibility (size limit will be max-only).
    """

    file_type: PostFileType
    files: Optional[List[ClientUploadFileMeta]] = None
    file_names: Optional[List[str]] = None


class GetPostFilesPostPolicyRequest(BaseModel):
    """
    Request model for PostPolicy endpoint.
    """

    files: List[PostFilePostPolicyRequestItem]


class GetPostFilesPostPolicyResponse(BaseModel):
    """
    a response model to return PostPolicy form upload info of multiple file types
    """

    items: List[PostFilePostPolicyResponseItem]

