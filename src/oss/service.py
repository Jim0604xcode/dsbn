from fastapi import UploadFile, HTTPException

from typing import List, Dict, Optional, Set, Tuple
from src.oss.schemas import PresignedUrlInfo, ClientPostPolicyUploadItem
from .ossUtils import get_object_name
from src.ossConfig import get_oss
from src.loggerServices import log_error

client = get_oss()

# Import crypto helpers
from src.crypto.services import encrypt_file_for_oss
import os
import re
import uuid
from pathlib import PurePosixPath
from src.utils.commonUtil import get_unix_timestamp

# STS token cache
_sts_token_cache: Dict = {
    "token": None,
    "expiration_time": None,
    "creation_time": None
}

async def upload_multiple_files(userID:str, files: List[UploadFile], file_type:str,action_type:str,mapping_dict:dict=None, encrypt:bool=False) -> List[str]:
    """
    Upload multiple files to the OSS bucket, with optional encryption.
    """
    if mapping_dict:
        presigned_urls,new_mapping_dict = await get_presigned_upload_urls(files,file_type, userID,action_type,3600,mapping_dict,encrypt)
        await upload_files_to_presigned_urls(presigned_urls, encrypt=encrypt)
        return new_mapping_dict
    else:
        presigned_urls = await get_presigned_upload_urls(files,file_type, userID,action_type,3600)
        fileNameList =  await upload_files_to_presigned_urls(presigned_urls, encrypt=encrypt)
        return fileNameList
    
async def get_presigned_upload_urls( files: List[UploadFile],  file_type: str,user_id: str,action_type:str,expiration: int = 3600,mapping_dict:dict=None,encrypt:bool=False) -> List[PresignedUrlInfo]:
    """
    Get pre-signed upload URLs for multiple files.
    """
    try:
        presigned_urls = []
        for file in files:
            object_name = get_object_name(user_id, file_type, file.filename,action_type)
            signed_url = client.generate_presigned_url(object_name, expiration)
            presigned_urls.append({"signed_url": signed_url, "object_name": object_name, "file":file})
            if mapping_dict:
                if encrypt:
                    mapping_dict[file.filename.split(".")[0]] = object_name + ".enc"
                else:
                    mapping_dict[file.filename.split(".")[0]] = object_name
            
        if mapping_dict:    
            return presigned_urls,mapping_dict
        else:
            return presigned_urls

    except Exception as e:
        log_error(f"Error occurred while getting pre-signed signed_url URLs: {e}")
        raise HTTPException(status_code=500, detail="Failed to get pre-signed signed_url URLs")

async def upload_files_to_presigned_urls(upload_file_objects: List[PresignedUrlInfo], encrypt:bool=False) -> List[str]:
    """
    Upload multiple files to the pre-signed URLs, with optional encryption.
    """
    uploaded_urls = []

    
    for obj in upload_file_objects:
        try:
            if not encrypt:
                client.upload_file(obj["file"], obj["signed_url"])
                uploaded_urls.append(obj["object_name"])
            else:
                # Encrypt file, upload .enc and .key
                enc_path, key_path = encrypt_file_for_oss(obj["file"])
                
                # Upload .enc
                with open(enc_path, 'rb') as f:
                    import io
                    enc_upload = UploadFile(filename=os.path.basename(enc_path), file=io.BytesIO(f.read()))
                enc_url = client.generate_presigned_url(obj["object_name"] + ".enc")
                client.upload_file(enc_upload, enc_url)
                
                # Upload .key - read as text since it was saved as text
                with open(key_path, 'r') as f:
                    key_content = f.read()
                    key_upload = UploadFile(filename=os.path.basename(key_path), file=io.BytesIO(key_content.encode('utf-8')))
                key_url = client.generate_presigned_url(obj["object_name"] + ".key")
                client.upload_file(key_upload, key_url)
                
                uploaded_urls.append(obj["object_name"] + ".enc")
                
                # Clean up temp files
                os.remove(enc_path)
                os.remove(key_path)
                
        except Exception as e:
            log_error(f"Error occurred while uploading: {e}")
            raise
    return uploaded_urls

def delete_single_file(filename:str):
    if filename.endswith(".enc"):
        try:
            # delete key file
            key_filename = filename.replace(".enc", ".key")
            client.delete_file(key_filename)
        except Exception as e:
            log_error(f"Error occurred while deleting file {filename}: {e}")
            raise
    return client.delete_file(filename)

async def download_single_file(filename: str, decrypt: bool = False, expiration: int = 3600) -> dict:
    """
    Download a single file from OSS.
    
    Args:
        filename: Name of the file to download
        decrypt: Whether to decrypt the file (if True, returns temp download URL with 5-min cleanup)
        expiration: URL expiration time in seconds
        
    Returns:
        Dictionary containing download URL and metadata
    """
    try:
        if decrypt:
            # Use 5-minute auto-cleanup for decrypted files
            from src.oss.auto_cleanup_service import download_with_5min_cleanup
            download_url = await download_with_5min_cleanup(filename, expiration)
            return download_url
        else:
            # Original behavior for non-decrypted files
            oss_client = get_oss()
            download_url = oss_client.download_file(filename, expiration)
            return download_url
            
    except Exception as e:
        log_error(f"Failed to download file {filename}: {e}")
        raise

async def download_file(object_name_list: List[str], decrypt:bool=False, expiration: int = 3600):
    """
    Download multiple files from OSS, with optional decryption.
    If decrypt=False, returns list of pre-signed URLs (original behavior).
    If decrypt=True, returns list of download URLs for decrypted temporary files.
    """
    try:
        results = []
        for obj_name in object_name_list:
            result = await download_single_file(obj_name, decrypt=decrypt, expiration=expiration)
            results.append(result)
        return results
    except Exception as e:
        log_error(f"Failed to download files: {e}")
        raise HTTPException(status_code=500, detail="Failed to download files")

async def get_client_post_policy_upload_data(
    user_id: str,
    file_type: str,
    action_type: str,
    file_names: Optional[List[str]] = None,
    file_metas: Optional[List[dict]] = None,
    expiration: int = 3600,
) -> List[ClientPostPolicyUploadItem]:
    """
    Generate OSS PostPolicy upload data for the frontend (multipart/form-data direct upload).

    Important security properties vs "starts-with key":
    - Use exact-match (eq) key per file, so client cannot change object key/file name.
    - Enforce content-length-range (size limit) in policy.
    """
    try:
        MAX_FILES_PER_REQUEST = 30
        MAX_FILENAME_LEN = 200

        allowed_ext_map: Dict[str, Set[str]] = {
            "images": {"jpg", "jpeg", "png", "webp", "gif"},
            "videos": {"mp4", "mov", "m4v"},
            "voices_msg": {"m4a", "mp3", "wav", "aac"},
        }
        max_size_map: Dict[str, int] = {
            # Tune as needed
            "images": 10 * 1024 * 1024,       # 10MB
            "videos": 200 * 1024 * 1024,      # 200MB
            "voices_msg": 20 * 1024 * 1024,   # 20MB
        }

        if file_type not in allowed_ext_map:
            raise HTTPException(status_code=400, detail=f"Unsupported file_type: {file_type}")

        if (not file_names) and (not file_metas):
            raise HTTPException(status_code=400, detail="files is empty")

        if file_metas is not None:
            if len(file_metas) > MAX_FILES_PER_REQUEST:
                raise HTTPException(status_code=400, detail=f"Too many files. max={MAX_FILES_PER_REQUEST}")
        if file_names is not None:
            if len(file_names) > MAX_FILES_PER_REQUEST:
                raise HTTPException(status_code=400, detail=f"Too many files. max={MAX_FILES_PER_REQUEST}")

        invalid_chars = re.compile(r"[\\/\x00]")
        results: List[ClientPostPolicyUploadItem] = []

        # Optional extra exact-match fields (also returned to client as form fields)
        extra_eq_fields = {
            # Prevent overwriting existing objects
            "x-oss-forbid-overwrite": "true",
        }

        # Normalize inputs into a list of (file_name, optional_size)
        normalized: List[Tuple[str, Optional[int]]] = []
        if file_metas is not None:
            for m in file_metas:
                if not isinstance(m, dict):
                    raise HTTPException(status_code=400, detail="files meta is invalid")
                normalized.append((m.get("file_name"), m.get("file_size")))
        elif file_names is not None:
            for n in file_names:
                normalized.append((n, None))

        for file_name, file_size in normalized:
            if not isinstance(file_name, str) or not file_name.strip():
                raise HTTPException(status_code=400, detail="file_name is invalid")
            if len(file_name) > MAX_FILENAME_LEN:
                raise HTTPException(status_code=400, detail="file_name is too long")
            if invalid_chars.search(file_name):
                raise HTTPException(status_code=400, detail="file_name contains invalid characters")

            suffix = PurePosixPath(file_name).suffix.lower()
            ext = suffix[1:] if suffix.startswith(".") else ""
            if not ext:
                raise HTTPException(status_code=400, detail=f"file_name missing extension: {file_name}")
            if ext not in allowed_ext_map[file_type]:
                raise HTTPException(status_code=400, detail=f"file extension not allowed: {ext}")

            safe_base = f"{get_unix_timestamp()}_{uuid.uuid4().hex}"
            object_name = f"{user_id}/{action_type}/{file_type}/{safe_base}.{ext}"

            # Size enforcement:
            # - If frontend provided file_size, lock content-length-range to exact size (min=max=size).
            # - Always cap by max_size_map[file_type].
            max_allowed = max_size_map[file_type]
            if file_size is None:
                size_range = (0, max_allowed)
            else:
                try:
                    size_int = int(file_size)
                except Exception:
                    raise HTTPException(status_code=400, detail="file_size is invalid")
                if size_int <= 0:
                    raise HTTPException(status_code=400, detail="file_size must be > 0")
                if size_int > max_allowed:
                    raise HTTPException(status_code=400, detail="file_size exceeds max allowed")
                size_range = (size_int, size_int)

            policy_data = client.generate_post_policy_fields(
                object_name=object_name,
                expiration=expiration,
                content_length_range=size_range,
                # If you want to constrain further, you can set an exact Content-Type here.
                content_type=None,
                extra_eq_fields=extra_eq_fields,
                success_action_status="200",
            )
            results.append(
                ClientPostPolicyUploadItem(
                    file_name=file_name,
                    object_name=object_name,
                    upload_url=policy_data["upload_url"],
                    fields=policy_data["fields"],
                )
            )

        return results
    except HTTPException:
        raise
    except Exception as e:
        log_error(f"Error occurred while getting client PostPolicy upload data: {e}")
        raise HTTPException(status_code=500, detail="Failed to get PostPolicy upload data")
