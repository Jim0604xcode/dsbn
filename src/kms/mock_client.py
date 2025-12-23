import base64
import json
import os
import pickle
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

from src.exceptions import GeneralErrorExcpetion


class MockKMSClient:
    """
    Mock KMS Client for local development that simulates Alibaba Cloud KMS behavior.
    This allows testing encryption/decryption without requiring actual KMS credentials.
    Master keys are persisted to ensure consistency across application restarts.
    """
    
    def __init__(self, dkms_instance_id: str = None, client_key_file: str = None, client_key_password: str = None, dkms_client_end_point: str = None):
        """
        初始化 mock KMS client，参数与 KMSClient 保持一致。
        """
        self.dkms_instance_id = dkms_instance_id or None
        self.client_key_file = client_key_file
        self.client_key_password = client_key_password
        self.dkms_client_end_point = dkms_client_end_point
        # mock client 不需要实际连接 DKMS，只做本地密钥管理
        self.master_keys_file = os.path.join(os.getcwd(), '.mock_kms_keys.pkl')
        self.master_keys = {}
        self._load_master_keys()
    
    def _load_master_keys(self):
        """Load master keys from persistent storage or create defaults."""
        try:
            if os.path.exists(self.master_keys_file):
                with open(self.master_keys_file, 'rb') as f:
                    self.master_keys = pickle.load(f)
                # print(f" Loaded {len(self.master_keys)} master keys from {self.master_keys_file}")
            else:
                # Initialize a default master key for testing
                self._init_default_master_key()
                self._save_master_keys()
                # print(f" Created new master keys file: {self.master_keys_file}")
        except Exception as e:
            print(f"Failed to load master keys: {e}, creating new ones")
            self.master_keys = {}
            self._init_default_master_key()
            self._save_master_keys()
    
    def _save_master_keys(self):
        """Save master keys to persistent storage."""
        try:
            with open(self.master_keys_file, 'wb') as f:
                pickle.dump(self.master_keys, f)
        except Exception as e:
            print(f"Failed to save master keys: {e}")
    
    def _init_default_master_key(self):
        """Initialize a default master key for testing purposes."""
        default_key_id = "mock-master-key-001"
        # Generate a 256-bit master key
        master_key = get_random_bytes(32)
        self.master_keys[default_key_id] = master_key
    
    def get_client(self):
        """Return self to maintain compatibility with the real KMS client interface."""
        return self
    
    def generate_data_key(self, key_id: str, number_of_bytes: int = 32) -> dict:
        """
        生成数据密钥，模拟 KMS GenerateDataKey 操作。
        :param key_id: KMS 密钥 ID
        :param number_of_bytes: 密钥字节数（默认 32 字节/AES-256）
        :return: Dict，包含 'Plaintext'（base64）、'CiphertextBlob'、'KeyId'、'Iv'
        """
        if key_id not in self.master_keys:
            self.master_keys[key_id] = get_random_bytes(32)
            self._save_master_keys()
            # print(f" Generated new master key for key_id: {key_id}")
        master_key = self.master_keys[key_id]
        data_key = get_random_bytes(number_of_bytes)
        # 使用 AES-GCM 加密 data_key
        cipher = AES.new(master_key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(data_key)
        ciphertext_blob_data = {
            'key_id': key_id,
            'nonce': base64.b64encode(cipher.nonce).decode(),
            'tag': base64.b64encode(tag).decode(),
            'ciphertext': base64.b64encode(ciphertext).decode()
        }
        ciphertext_blob = base64.b64encode(json.dumps(ciphertext_blob_data).encode()).decode()
        return {
            'Plaintext': base64.b64encode(data_key).decode(),
            'CiphertextBlob': ciphertext_blob,
            'KeyId': key_id,
            'Iv': cipher.nonce
        }
    
    def encrypt(self, key_id: str, plaintext: str) -> dict:
        """
        使用指定 key_id 的主密钥加密明文，模拟 KMS Encrypt 操作。
        :param key_id: KMS 密钥 ID
        :param plaintext: 明文（base64 字符串或 bytes）
        :return: Dict，包含 'CiphertextBlob'、'KeyId'
        """
        if key_id not in self.master_keys:
            raise GeneralErrorExcpetion(f"Master key not found for key_id: {key_id}")
        master_key = self.master_keys[key_id]
        if isinstance(plaintext, str):
            try:
                plaintext_bytes = base64.b64decode(plaintext)
            except Exception:
                plaintext_bytes = plaintext.encode()
        else:
            plaintext_bytes = plaintext
        cipher = AES.new(master_key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(plaintext_bytes)
        blob = {
            'key_id': key_id,
            'nonce': base64.b64encode(cipher.nonce).decode(),
            'tag': base64.b64encode(tag).decode(),
            'ciphertext': base64.b64encode(ciphertext).decode()
        }
        ciphertext_blob = base64.b64encode(json.dumps(blob).encode()).decode()
        return {
            'CiphertextBlob': ciphertext_blob,
            'KeyId': key_id
        }
    
    def decrypt(self, ciphertext_blob: str, data_key_iv: bytes = None) -> dict:
        """
        解密密文，模拟 KMS Decrypt 操作。
        :param ciphertext_blob: 密文（base64 字符串）
        :param data_key_iv: 可选，IV（未用，兼容接口）
        :return: Dict，包含 'Plaintext'（base64）、'KeyId'
        """
        try:
            blob_data = json.loads(base64.b64decode(ciphertext_blob).decode())
            key_id = blob_data['key_id']
            nonce = base64.b64decode(blob_data['nonce'])
            tag = base64.b64decode(blob_data['tag'])
            ciphertext = base64.b64decode(blob_data['ciphertext'])
            if key_id not in self.master_keys:
                raise GeneralErrorExcpetion(f"Master key not found for key_id: {key_id}")
            master_key = self.master_keys[key_id]
            cipher = AES.new(master_key, AES.MODE_GCM, nonce=nonce)
            plaintext = cipher.decrypt_and_verify(ciphertext, tag)
            return {
                'Plaintext': base64.b64encode(plaintext).decode(),
                'KeyId': key_id
            }
        except Exception as e:
            raise GeneralErrorExcpetion(f"Failed to decrypt ciphertext blob: {str(e)}")
    
    def add_master_key(self, key_id: str, master_key: bytes = None):
        """
        Add a custom master key for testing purposes.
        
        :param key_id: The key ID to associate with the master key
        :param master_key: The master key bytes (if None, generates a random one)
        """
        if master_key is None:
            master_key = get_random_bytes(32)
        self.master_keys[key_id] = master_key
        self._save_master_keys()  # Persist the new key
    
    def list_master_keys(self) -> list:
        """
        List all available master key IDs (for debugging/testing).
        """
        return list(self.master_keys.keys())
    
    def clear_master_keys(self):
        """
        Clear all master keys and delete the persistence file.
        Useful for testing or when you want to start fresh.
        """
        self.master_keys = {}
        if os.path.exists(self.master_keys_file):
            os.remove(self.master_keys_file)
        # print(f"🧹 Cleared all master keys and deleted {self.master_keys_file}")
    
    def get_master_keys_file_path(self) -> str:
        """
        Get the path to the master keys persistence file.
        """
        return self.master_keys_file 