
import requests
from fastapi import UploadFile
import oss2
# from oss2 import ObjectIteratorV2
from tenacity import retry, stop_after_attempt, wait_fixed
from src.loggerServices import log_error
import base64
import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse


class OSSClient:
    def __init__(self, access_key: str, secret_key: str, endpoint: str, bucket_name: str,region:str, sts_role_arn:str,accelerate_region:str,region_id:str):
        self.access_key = access_key
        self.secret_key = secret_key
        if not endpoint.startswith('https://') and not endpoint.startswith('http://'):
            self.endpoint = f'https://{endpoint}'
        else:
            self.endpoint = endpoint

        self.bucket_name = bucket_name
        self.region = region
        self.sts_role_arn = sts_role_arn
        self.accelerate_region = accelerate_region
        self.auth = oss2.Auth(self.access_key, self.secret_key)
        self.bucket = oss2.Bucket(
            self.auth, 
            self.endpoint, 
            self.bucket_name,
            session=oss2.Session(),
        )
        self.region_id = region_id

    def generate_presigned_url(self, object_name: str,  expiration: int = 3600, headers: dict = None) -> str:
        """
        Generate a pre-signed URL for a file.
        """
        try:
            presigned_url = self.bucket.sign_url("PUT", object_name, expiration,
                headers=headers, 
             slash_safe=True)
            return presigned_url
        except oss2.exceptions.OssError as e:
            log_error(f"Failed to generate pre-signed URL for {object_name}: {e}")
            raise

    def upload_file(self, file: UploadFile, signed_url: str) -> str:
        """
        Upload a file to OSS using a pre-signed URL.
        """
        try:
            file.file.seek(0)  # Ensure the file pointer is at the beginning
            file_content = file.file.read()
            response = requests.put(signed_url, data=file_content)
            response.raise_for_status()
            return signed_url
        except Exception as e:
            log_error(f"Failed to upload file {signed_url} to OSS: {e}")
            raise

    def download_file(self, object_name: str, expiration: int = 3600) -> str:
        """
        Generate a pre-signed URL for downloading a file from OSS.
        """
        try:

            download_url = self.bucket.sign_url("GET", object_name, expiration, slash_safe=True)  
            return download_url
        except Exception as e:
            log_error(f"Failed to generate pre-signed URL for downloading {object_name} from OSS: {e}")
            raise

    def delete_file(self, object_name: str) -> bool:
        """
        Delete a file from OSS.
        """
        try:
            # log_info(f"File Start to delete: {object_name}")
            self.bucket.delete_object(object_name)
            # log_info(f"File {object_name} deleted from bucket {self.bucket_name}")
            return True
        except oss2.exceptions.OssError as e:
            log_error(f"Failed to delete file {object_name} from OSS: {e}")
            return False

    def _get_post_upload_url(self) -> str:
        """
        Build the OSS form upload endpoint:
        https://{bucket}.{endpoint_host}
        """
        parsed = urlparse(self.endpoint)
        scheme = parsed.scheme or "https"
        netloc = parsed.netloc or parsed.path  # urlparse may put host in path if scheme missing
        if not netloc:
            raise ValueError(f"Invalid OSS endpoint: {self.endpoint}")

        if netloc.startswith(f"{self.bucket_name}."):
            return f"{scheme}://{netloc}"
        return f"{scheme}://{self.bucket_name}.{netloc}"

    def generate_post_policy_fields(
        self,
        object_name: str,
        expiration: int = 3600,
        content_length_range: Tuple[int, int] = (0, 10 * 1024 * 1024),
        content_type: Optional[str] = None,
        extra_eq_fields: Optional[Dict[str, str]] = None,
        success_action_status: str = "200",
    ) -> Dict[str, object]:
        """
        Generate PostPolicy form fields for browser/mobile direct upload (multipart/form-data).

        Returns:
        {
          "upload_url": "...",
          "fields": { "key": "...", "policy": "...", "OSSAccessKeyId": "...", "signature": "...", ... }
        }
        """
        try:
            now = datetime.now(timezone.utc)
            expire_at = now + timedelta(seconds=expiration)
            expiration_str = expire_at.strftime("%Y-%m-%dT%H:%M:%S.000Z")

            min_len, max_len = content_length_range
            conditions = [
                ["eq", "$key", object_name],
                ["content-length-range", int(min_len), int(max_len)],
            ]

            fields: Dict[str, str] = {
                "key": object_name,
                "success_action_status": success_action_status,
            }

            if content_type:
                # OSS supports restricting Content-Type via policy conditions (S3-compatible style).
                conditions.append(["eq", "$Content-Type", content_type])
                fields["Content-Type"] = content_type

            if extra_eq_fields:
                for k, v in extra_eq_fields.items():
                    # Put as exact-match condition.
                    conditions.append(["eq", f"${k}", v])
                    fields[k] = v

            policy_dict = {"expiration": expiration_str, "conditions": conditions}
            policy_json = json.dumps(policy_dict, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
            policy_b64 = base64.b64encode(policy_json)

            # Sign with "client" access key (intended for direct upload use-case)
            access_key_id = self.access_key
            access_key_secret = self.secret_key
            if not access_key_id or not isinstance(access_key_id, str):
                raise ValueError("OSS AccessKeyId is empty/invalid")
            if not access_key_secret or not isinstance(access_key_secret, str):
                raise ValueError("OSS AccessKeySecret is empty/invalid")

            signature = base64.b64encode(
                hmac.new(access_key_secret.encode("utf-8"), policy_b64, hashlib.sha1).digest()
            ).decode("utf-8")

            fields.update(
                {
                    "policy": policy_b64.decode("utf-8"),
                    "OSSAccessKeyId": access_key_id,
                    "Signature": signature,
                }
            )

            return {"upload_url": self._get_post_upload_url(), "fields": fields}
        except Exception as e:
            log_error(f"Failed to generate PostPolicy fields for {object_name}: {e}")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def upload_to_oss(self, file_name: str, content: bytes) -> None:
        """
        Upload content to OSS.
        """
        try:
            self.bucket.put_object(file_name, content)
            # log_info(f"File {file_name} uploaded to bucket {self.bucket_name}")
        except oss2.exceptions.OssError as e:
            log_error(f"Failed to upload file {file_name} to OSS: {e}")
            raise
