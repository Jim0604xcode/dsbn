from src.oss.service import download_file
from src.posts.models import PostMaster
from src.posts.response import MediaResponseModel
from src.loggerServices import log_error
from src.exceptions import BadReqExpection
from fastapi import UploadFile
from ..constants import FILE_SIZE_EXCEEDS_LIMIT_CODE

async def get_media_urls(post_master: PostMaster) -> MediaResponseModel:
    images_url = []
    videos_url = []
    voices_url = []

    if post_master.images_name:
        images_url = await download_file(post_master.images_name)
    if post_master.videos_name:    
        videos_url = await download_file(post_master.videos_name)
    if post_master.voices_name:    
        voices_url = await download_file(post_master.voices_name)

    return {"images_url":images_url, "videos_url":videos_url, "voices_url":voices_url}

async def checkFileSize(file: UploadFile) -> None:
    # Check file size (5MB = 5 * 1024 * 1024 bytes)
    file_content = await file.read()
    file_size = len(file_content)
    file.file.seek(0)  # Reset file pointer after reading
    if file_size > 5 * 1024 * 1024:
        raise BadReqExpection(code=FILE_SIZE_EXCEEDS_LIMIT_CODE, details="File size exceeds 5MB limit")
    
async def get_file_type(file: UploadFile) -> str:
    # Get file type
    file_extension = file.filename.split(".")[-1].lower()
    return file_extension    