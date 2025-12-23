import base64
from src.config import (DKMS_CA_CERT, DKMS_CLIENT_END_POINT, DKMS_CLIENT_KEY_FILE,
    DKMS_CLIENT_KEY_PASSWORD, DKMS_MASTER_CRYPTO_KEY)
from openapi.models import Config as DKMSConfig
from sdk.client import Client as DKMSClient
from sdk.models import GenerateDataKeyRequest, EncryptRequest, DecryptRequest, GetSecretValueRequest
from openapi_util.models import RuntimeOptions
from src.loggerServices import log_error
from src.exceptions import GeneralErrorExcpetion
class KMSClient:
    """
    Aliyun DKMS Client (KMS 3.0) using official DKMS SDK.
    """
    def __init__(self, dkms_instance_id: str, client_key_file: str , client_key_password: str , dkms_client_end_point: str ):
        self.dkms_instance_id = dkms_instance_id or None
        self.client_key_file = client_key_file or DKMS_CLIENT_KEY_FILE
        self.client_key_password = client_key_password or DKMS_CLIENT_KEY_PASSWORD
        self.dkms_client_end_point = dkms_client_end_point or DKMS_CLIENT_END_POINT
        self.dkms_client = None
        self._init_dkms_client()

    def _init_dkms_client(self):
        config = DKMSConfig()
        config.protocol = "https"
        config.client_key_file = self.client_key_file
        config.password = self.client_key_password
        config.endpoint = self.dkms_client_end_point
        self.dkms_client = DKMSClient(config)

    def _get_runtime_options(self):
        if DKMS_CA_CERT:
            runtime_options = RuntimeOptions()
            runtime_options.verify = DKMS_CA_CERT
            return runtime_options
        return None

    def generate_data_key(self, key_id: str, number_of_bytes: int = 32) -> dict:
        """
        Generate a data key using DKMS SDK.
        :param key_id: The KMS key ID.
        :param key_spec: The type of key to generate (default: AES_256).
        :return: Dict with 'Plaintext' (base64) and 'CiphertextBlob'.
        """
        if not self.dkms_client:
            raise RuntimeError("DKMS client not initialized")
            
        request = GenerateDataKeyRequest()
        request.key_id = key_id
        request.number_of_bytes = number_of_bytes
        
        runtime_options = self._get_runtime_options()
        
        try:
            if runtime_options:
                response = self.dkms_client.generate_data_key_with_options(request, runtime_options)
            else:
                response = self.dkms_client.generate_data_key(request)
        except Exception as e:
            log_error(f"Failed to generate data key: {e}")
            response = self.dkms_client.generate_data_key(request)
        
        result = {
            'Plaintext': response.plaintext,
            'CiphertextBlob': response.ciphertext_blob,
            'KeyId': response.key_id,
            'Iv': getattr(response, 'iv', None) or getattr(response, 'Iv', None)  # 兼容不同SDK字段
        }
        
        return result

    def encrypt(self, key_id: str, plaintext: str) -> dict:
        if not self.dkms_client:
            raise RuntimeError("DKMS client not initialized")
            
        request = EncryptRequest()
        request.key_id = key_id
        request.plaintext = plaintext.encode() if isinstance(plaintext, str) else plaintext
        
        runtime_options = self._get_runtime_options()
        
        try:
            if runtime_options:
                response = self.dkms_client.encrypt_with_options(request, runtime_options)
            else:
                response = self.dkms_client.encrypt(request)
        except Exception as e:
            log_error(f"Failed to encrypt: {e}")
            response = self.dkms_client.encrypt(request)
        
        return {
            'CiphertextBlob': response.ciphertext_blob,
            'KeyId': response.key_id
        }

    def decrypt(self, ciphertext_blob: str, data_key_iv: bytes = None) -> dict:
        """
        Decrypt a ciphertext blob to get the plaintext key.
        :param ciphertext_blob: The encrypted key (base64 string).
        :return: Dict with 'Plaintext' (base64).
        """
        if not self.dkms_client:
            raise RuntimeError("DKMS client not initialized")
            
        request = DecryptRequest()
        if isinstance(ciphertext_blob, str):
            try:
                request.ciphertext_blob = base64.b64decode(ciphertext_blob)
                request.key_id = DKMS_MASTER_CRYPTO_KEY
            except Exception as e:
                log_error(f"Failed to decode ciphertext_blob: {e}")
                raise GeneralErrorExcpetion(f"Invalid ciphertext_blob: {e}")
        else:
            request.ciphertext_blob = ciphertext_blob
        if data_key_iv:
            request.iv = data_key_iv
          
        runtime_options = self._get_runtime_options()
        
        try:
            if runtime_options:
                response = self.dkms_client.decrypt_with_options(request, runtime_options)
            else:
                response = self.dkms_client.decrypt(request)
        except Exception as e:
            log_error(f"Failed to decrypt: {e}")
            response = self.dkms_client.decrypt(request)
        
        return {
            'Plaintext': response.plaintext,
            'KeyId': response.key_id
        }
    
    def get_secret_data(self, secret_name: str) -> str:
        """
        Use DKMS SDK to get Secret (such as database password, etc.), only return SecretData.
        :param secret_name: Secret name
        :return: SecretData (plaintext) in json format  
        Example:
            {
            "SecretName":"uat_rds_access",
            "SecretType":"Rds",
            "SecretData":"{\"AccountName\":\"DB_NAME\",\"AccountPassword\":\"DB_PW\"}",
            "SecretDataType":"text",
            "VersionStages":[
                "ACSCurrent"
            ],
            "VersionId":"491c64bb-9619-4e1a-bd16-93e0752dab8f",
            "CreateTime":"2025-05-30 02:01:01Z",
            "RequestId":"71cf8444-039c-49b7-845c-74313d298d4f",
            "LastRotationDate":"2025-06-02T02:03:12Z",
            "NextRotationDate":"2025-06-03T02:03:12Z",
            "ExtendedConfig":"",
            "AutomaticRotation":"Enabled",
            "RotationInterval":"86400s",
            "responseHeaders":{
                
            }
            }
        """
        if not self.dkms_client:
            raise RuntimeError("DKMS client not initialized")
        
        request = GetSecretValueRequest()
        request.secret_name = secret_name
        
        runtime_options = self._get_runtime_options()
        try:
            if runtime_options:
                response = self.dkms_client.get_secret_value_with_options(request, runtime_options)
            else:
                response = self.dkms_client.get_secret_value(request)
        except Exception as e:
            log_error(f"[KMS][get_secret_data] Failed to get secret value: {e}; secret_name={secret_name}")
            raise
        if not response.secret_data:
            log_error(f"[KMS][get_secret_data] Got empty secret_data for secret={secret_name}!")

        # print(f"***** response.secret_data: {response}")
        return response.secret_data