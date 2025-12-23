import requests
from fastapi import UploadFile
from src.authgear.generateAuthgearJWT import generateAuthgearJWT
from src.config import AUTHGEAR_ENDPOINT
from src.authgear.constants import API_AUTHGEAR_GET_PRE_SIGNED_URL


def get_presigned_upload_url() -> str:
    """
    Get the pre-signed upload URL.
    """
    try:
        response = requests.get(
            AUTHGEAR_ENDPOINT+API_AUTHGEAR_GET_PRE_SIGNED_URL,
            headers={"Authorization": f"Bearer {generateAuthgearJWT()}"}
        )
        response.raise_for_status()

        response_json = response.json()
        
        upload_url = response_json["result"]["upload_url"]

        return upload_url
    except Exception as e:
        raise

def upload_image_to_presigned_url(upload_url: str, file: UploadFile, userID: str) -> str:
    """
    Upload the image file to the pre-signed URL.
    """
    try:
        files = {'file': (file.filename+userID, file.file, file.content_type)}
        response = requests.post(upload_url, files=files)
        response.raise_for_status()
        result_url = response.json()["result"]["url"]
        return result_url
    except Exception as e:
        raise